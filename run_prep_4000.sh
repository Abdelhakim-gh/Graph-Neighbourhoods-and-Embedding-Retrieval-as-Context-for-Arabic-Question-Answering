#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
echo "=== STAGE 1: graph pull for the full test split ==="
py -3.14 scripts/01_collect_qids_and_pull_graph.py --scale 4000 --split test --max-hops 2
echo "=== STAGE 3: graph walk (before stage 2, it is cheap and validates the pull) ==="
py -3.14 scripts/03_run_graph_walk.py --scale 4000 --split test
echo "=== STAGE 2: retrieval corpus + e5 index ==="
py -3.14 scripts/02_run_retrieval.py --scale 4000 --split test \
    --embedding-models "intfloat/multilingual-e5-large"
echo "PREP_4000_COMPLETE"
