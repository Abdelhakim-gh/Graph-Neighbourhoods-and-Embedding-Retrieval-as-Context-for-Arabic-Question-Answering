#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
MODELS="aya-expanse:8b,qwen3.5:9b"
py -3.14 scripts/04_run_answer_generation.py --scale 4000 --split test --arm no_retrieval --models "$MODELS"
py -3.14 scripts/04_run_answer_generation.py --scale 4000 --split test --arm graph_walk   --models "$MODELS"
py -3.14 scripts/04_run_answer_generation.py --scale 4000 --split test --arm retrieval \
    --embedding-model "intfloat/multilingual-e5-large" --models "$MODELS"
echo "STAGE4_4000_COMPLETE"
