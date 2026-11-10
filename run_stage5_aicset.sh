#!/usr/bin/env bash
# Stage 5: build the arm contexts for one evidence store, then answer them.
#
# Usage:  bash run_stage5_aicset.sh <store>      store = question | answered
#
# Safe to stop and restart at any point:
#   - a context file is rebuilt only if it does not exist yet (scripts/11
#     writes to .tmp and renames, so a finished file is always complete);
#   - E5 embeddings are cached in data/processed/e5_cache/ chunk by chunk;
#   - scripts/04 resumes by item_id, skipping questions already answered.
# Order: the fourth arm first (the comparison the paper needs most), then the
# graph and pooled-retrieval arms; aya before qwen within each.
set -u
cd "$(dirname "$0")"
STORE="${1:?usage: bash run_stage5_aicset.sh question|answered}"
export PYTHONHASHSEED=0   # scope_to_seeds also sorts its input, so contexts do not depend on the hash seed

ARMS="scoped walk pooled"
if [ "$STORE" = "answered" ]; then
  ARMS="scoped"            # the other two arms already exist for this store
fi

for MODE in $ARMS; do
  CTX="results/contexts/4000/${MODE}_${STORE}.jsonl"
  if [ ! -f "$CTX" ]; then
    echo "=== $(date) building $CTX"
    py -3.14 scripts/11_build_contexts.py --mode "$MODE" --store "$STORE" || { echo "FAILED building $CTX"; exit 1; }
  fi
done

for MODEL in "aya-expanse:8b" "qwen3.5:9b"; do
  for MODE in $ARMS; do
    echo "=== $(date) answering ${MODE}_${STORE} with $MODEL"
    py -3.14 scripts/04_run_answer_generation.py --scale 4000 --split test \
      --arm contexts --context-name "${MODE}_${STORE}" --models "$MODEL" \
      || { echo "FAILED ${MODE}_${STORE} $MODEL"; exit 1; }
  done
done
echo "STAGE5_${STORE}_COMPLETE $(date)"
