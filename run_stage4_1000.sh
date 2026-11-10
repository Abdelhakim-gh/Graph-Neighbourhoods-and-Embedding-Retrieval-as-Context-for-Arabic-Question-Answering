#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
for spec in "no_retrieval:" "graph_walk:" "retrieval:intfloat/multilingual-e5-large" "retrieval:Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2"; do
  arm="${spec%%:*}"; emb="${spec#*:}"
  if [ -n "$emb" ]; then
    py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test --arm "$arm" --embedding-model "$emb"
  else
    py -3.14 scripts/04_run_answer_generation.py --scale 1000 --split test --arm "$arm"
  fi
done
echo "STAGE4_1000_COMPLETE"
