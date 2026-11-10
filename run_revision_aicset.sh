#!/usr/bin/env bash
# Camera-ready revision runs (reviewer 1, points 1 and 3).
#
# All runs use the 1,000-question tier, a subset of the 4,000 questions already
# answered, so each is paired with the existing run on the same questions.
#   1. walk_answered_k50, pooled_answered_k50  budget 50 instead of 150
#   2. walk_question, pooled_question, scoped_question
#                                              question-only store (no answer seeds)
#   3. walk_answered_h1                        one hop instead of two
# The predicted-entity run (walk_predicted) is queued separately once
# scripts/16 has built its contexts.
#
# Usage: bash run_revision_aicset.sh     (safe to stop and re-run: scripts/04
# resumes by item_id; a context file that exists is not rebuilt)
set -u
cd "$(dirname "$0")"
export PYTHONHASHSEED=0

answer () {   # $1 = context name under results/contexts/1000/
  for MODEL in "aya-expanse:8b" "qwen3.5:9b"; do
    echo "=== $(date) answering $1 with $MODEL"
    py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test \
      --arm contexts --context-name "$1" --models "$MODEL" \
      || { echo "FAILED $1 $MODEL"; exit 1; }
  done
}

wait_and_subset () {   # $1 = context name written by scripts/11 at scale 4000
  until [ -f "results/contexts/4000/$1.jsonl" ]; do
    if grep -q "^FAILED" results/logs/revision_contexts.log 2>/dev/null; then
      echo "context build failed; stopping"; exit 1
    fi
    sleep 60
  done
  [ -f "results/contexts/1000/$1.jsonl" ] || py -3.14 scripts/15_revision_contexts.py subset --names "$1" \
    || { echo "FAILED subset $1"; exit 1; }
}

echo "=== $(date) START revision runs"
answer walk_answered_k50
answer pooled_answered_k50
for NAME in walk_question pooled_question scoped_question walk_answered_h1; do
  wait_and_subset "$NAME"
  answer "$NAME"
done
echo "REVISION_RUNS_COMPLETE $(date)"
