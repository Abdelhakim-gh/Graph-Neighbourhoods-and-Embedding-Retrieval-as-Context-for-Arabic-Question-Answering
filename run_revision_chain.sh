#!/usr/bin/env bash
# All GPU work of the camera-ready revision, strictly one job at a time.
# When the E5 query embedding (torch, scripts/11) and an Ollama model share
# the GPU, both can stall. Never start a GPU job beside this script.
#
#   1. E5 contexts on the question-only store (pooled, scoped)      GPU, torch
#   2. entity mentions for the 1,000 questions (scripts/16)          GPU, Ollama
#   3. run_revision_aicset.sh: k50, question-store, one-hop runs      GPU, Ollama
#   4. walk_predicted runs, once scripts/16 has written the contexts  GPU, Ollama
#
# The Wikidata steps of scripts/16 (link, evaluate, pull, contexts) use no
# GPU and run in a separate chain.
#
# Usage: bash run_revision_chain.sh   (safe to stop and re-run; every step
# skips work already done)
set -u
cd "$(dirname "$0")"
export PYTHONHASHSEED=0
LOG=results/logs/revision_contexts.log

until curl -s -m 5 http://localhost:11434/api/version >/dev/null; do sleep 10; done

for MODE in pooled scoped; do
  if [ ! -f "results/contexts/4000/${MODE}_question.jsonl" ]; then
    echo "=== $(date) building $MODE question" >> $LOG
    py -3.14 scripts/11_build_contexts.py --mode $MODE --store question --scale 4000 >> $LOG 2>&1 \
      || { echo "FAILED building $MODE question" | tee -a $LOG; exit 1; }
  fi
done
echo "REVISION_CONTEXTS_COMPLETE $(date)" >> $LOG

echo "=== $(date) mentions"
py -3.14 scripts/16_predicted_entities.py mentions >> results/logs/revision_linking.log 2>&1 \
  || { echo "FAILED mentions"; exit 1; }
echo "MENTIONS_COMPLETE $(date)" >> results/logs/revision_linking.log

bash run_revision_aicset.sh || { echo "FAILED run_revision_aicset.sh"; exit 1; }

until [ -f results/contexts/1000/walk_predicted.jsonl ]; do
  grep -q "^FAILED" results/logs/revision_linking.log && { echo "linking chain failed; stopping"; exit 1; }
  sleep 60
done
for MODEL in "aya-expanse:8b" "qwen3.5:9b"; do
  echo "=== $(date) answering walk_predicted with $MODEL"
  py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test \
    --arm contexts --context-name walk_predicted --models "$MODEL" \
    || { echo "FAILED walk_predicted $MODEL"; exit 1; }
done
echo "PREDICTED_RUNS_COMPLETE $(date)"
