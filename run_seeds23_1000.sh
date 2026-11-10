#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
MODELS="aya-expanse:8b,qwen3.5:9b"
SEEDS="2,3"
py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test --arm graph_walk \
    --models "$MODELS" --seeds "$SEEDS"
py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test --arm retrieval \
    --embedding-model "intfloat/multilingual-e5-large" --models "$MODELS" --seeds "$SEEDS"
echo "SEEDS23_COMPLETE"
