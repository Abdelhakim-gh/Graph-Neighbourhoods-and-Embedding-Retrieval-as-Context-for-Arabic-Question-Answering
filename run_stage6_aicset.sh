#!/usr/bin/env bash
# Stage 6: the six-model check at 1,000 questions on the question-only store
# (graph-walk and pooled-retrieval arms; the no-context control does not
# depend on the store and is reused from the earlier runs).
#
# Usage:  bash run_stage6_aicset.sh
# Safe to stop and restart: same resume rules as run_stage5_aicset.sh.
set -u
cd "$(dirname "$0")"
export PYTHONHASHSEED=0

for MODE in walk pooled; do
  CTX="results/contexts/1000/${MODE}_question.jsonl"
  if [ ! -f "$CTX" ]; then
    echo "=== $(date) building $CTX"
    py -3.14 scripts/11_build_contexts.py --mode "$MODE" --store question --scale 1000 \
      || { echo "FAILED building $CTX"; exit 1; }
  fi
done

for MODEL in "aya-expanse:8b" "command-r7b-arabic:latest" "gemma4:12b" "mistral-nemo:12b" "qwen3.5:4b" "qwen3.5:9b"; do
  for MODE in walk pooled; do
    echo "=== $(date) answering ${MODE}_question at 1000 with $MODEL"
    py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test \
      --arm contexts --context-name "${MODE}_question" --models "$MODEL" \
      || { echo "FAILED ${MODE}_question 1000 $MODEL"; exit 1; }
  done
done
echo "STAGE6_COMPLETE $(date)"
