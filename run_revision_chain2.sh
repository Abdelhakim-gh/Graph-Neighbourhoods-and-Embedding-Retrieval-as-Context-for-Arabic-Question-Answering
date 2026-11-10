#!/usr/bin/env bash
# Camera-ready answer runs, ordered so that the runs the reviewer's points
# depend on most finish first:
#   1. question-only store: graph and pooled arms   (reviewer point 1)
#   2. predicted entities: graph arm                 (reviewer point 1)
#   3. 50-line budget: graph and pooled              (reviewer point 3)
#   4. one hop: graph                                (reviewer point 3)
#   5. question-only store: scoped arm               (completes point 1; can be dropped)
# Contexts and mentions are already built (run_revision_chain.sh). One GPU job
# at a time. Safe to stop and re-run: scripts/04 resumes by item_id.
set -u
cd "$(dirname "$0")"
export PYTHONHASHSEED=0

until curl -s -m 5 http://localhost:11434/api/version >/dev/null; do sleep 10; done

answer () {   # $1 = context name under results/contexts/1000/
  for MODEL in "aya-expanse:8b" "qwen3.5:9b"; do
    echo "=== $(date) answering $1 with $MODEL"
    py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test \
      --arm contexts --context-name "$1" --models "$MODEL" \
      || { echo "FAILED $1 $MODEL"; exit 1; }
  done
}

for NAME in walk_question pooled_question scoped_question walk_answered_h1; do
  [ -f "results/contexts/1000/$NAME.jsonl" ] || py -3.14 scripts/15_revision_contexts.py subset --names "$NAME" \
    || { echo "FAILED subset $NAME"; exit 1; }
done

echo "=== $(date) START reordered revision runs"
answer walk_question
answer pooled_question
answer walk_predicted
echo "REVISION_POINT1_CORE_COMPLETE $(date)"
answer walk_answered_k50
answer pooled_answered_k50
answer walk_answered_h1
echo "REVISION_POINT3_COMPLETE $(date)"
answer scoped_question
echo "REVISION_RUNS_COMPLETE $(date)"
echo "PREDICTED_RUNS_COMPLETE $(date)"
