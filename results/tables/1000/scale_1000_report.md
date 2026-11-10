# Study 4 results, scale 1000

## Overall accuracy, per run (arm|LLM|seed)

`Truncated` is the share of answers that ended exactly at `max_tokens`.
A high rate means that run was scored on cut-off answers, which is a
pipeline finding rather than a model finding: raise the cap for that
model and re-run it alone. `Errors` are excluded from accuracy rather
than counted wrong.

| Run | Accuracy | N | Truncated | Errors | Mean s/call | Energy Wh |
|---|---|---|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | 37.5% | 1000 | 0.0% | 0 | 3.18 | 60.5 |
| graph_walk_aya-expanse_8b|seed2 | 37.6% | 1000 | 0.0% | 0 | 3.16 | 60.3 |
| graph_walk_aya-expanse_8b|seed3 | 37.8% | 1000 | 0.0% | 0 | 3.17 | 60.2 |
| graph_walk_command-r7b-arabic_latest|seed1 | 30.0% | 1000 | 0.0% | 0 | 3.42 | 65.0 |
| graph_walk_gemma4_12b|seed1 | 28.3% | 1000 | 0.2% | 0 | 5.78 | 111.0 |
| graph_walk_mistral-nemo_12b|seed1 | 27.5% | 1000 | 0.0% | 0 | 3.85 | 74.9 |
| graph_walk_qwen3.5_4b|seed1 | 24.1% | 1000 | 0.4% | 0 | 2.81 | 53.8 |
| graph_walk_qwen3.5_9b|seed1 | 29.9% | 1000 | 1.7% | 0 | 4.14 | 79.1 |
| graph_walk_qwen3.5_9b|seed2 *(partial)* | 34.1% | 85 | 1.2% | 0 | 4.55 | 7.5 |
| no_retrieval_aya-expanse_8b|seed1 | 29.6% | 1000 | 0.0% | 0 | 0.85 | 13.8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | 22.8% | 1000 | 0.1% | 0 | 0.78 | 12.2 |
| no_retrieval_gemma4_12b|seed1 | 21.6% | 1000 | 0.3% | 0 | 1.78 | 30.7 |
| no_retrieval_mistral-nemo_12b|seed1 | 17.8% | 1000 | 0.0% | 0 | 0.59 | 9.5 |
| no_retrieval_qwen3.5_4b|seed1 | 14.7% | 1000 | 0.6% | 0 | 0.80 | 13.2 |
| no_retrieval_qwen3.5_9b|seed1 | 17.5% | 1000 | 1.5% | 0 | 1.15 | 19.6 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | 32.0% | 1000 | 0.0% | 0 | 3.54 | 67.9 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | 26.8% | 1000 | 0.0% | 0 | 3.82 | 72.8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | 28.1% | 1000 | 0.1% | 0 | 6.41 | 124.1 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | 27.5% | 1000 | 0.1% | 0 | 4.74 | 92.8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | 21.9% | 1000 | 0.5% | 0 | 3.00 | 57.5 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | 29.8% | 1000 | 0.4% | 0 | 4.29 | 82.8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | 32.1% | 1000 | 0.0% | 0 | 3.91 | 74.2 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | 28.0% | 1000 | 0.0% | 0 | 4.05 | 77.0 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | 30.4% | 1000 | 0.0% | 0 | 6.94 | 133.2 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | 28.8% | 1000 | 0.0% | 0 | 4.63 | 90.5 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | 23.6% | 1000 | 0.3% | 0 | 2.98 | 57.1 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | 31.5% | 1000 | 0.4% | 0 | 4.28 | 82.7 |

## Accuracy per arm, averaged over the LLM roster

The three-arm comparison this study exists to make. `no_retrieval`
is the control: the gap between it and the other two is what
retrieval and graph-walking actually buy. A gap smaller than about
0.02 should be read as inconclusive rather than as a result, since
this tier runs a single seed at temperature 0.2 and does not
measure its own run-to-run spread.

| Arm | Mean accuracy | LLMs |
|---|---|---|
| graph_walk | 29.6% | 6 |
| retrieval (intfloat/multilingual-e5-large) | 29.1% | 6 |
| retrieval (Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2) | 27.7% | 6 |
| no_retrieval | 20.7% | 6 |

Seeds averaged within a model before averaging across the arm: graph_walk/aya-expanse:8b (3 seeds). The Runs column counts models, not runs.

**1 run(s) still being written are excluded from this table:** graph_walk_qwen3.5_9b|seed2 (85 rows). A prefix of this pipeline is a biased sample, not a small one, since the questions are not shuffled against `complexityType`. Re-run scripts/05 and 06 once the file reaches its full row count.

## Accuracy by answer type, per run

Where the scorer is weakest, so read a bad number here as a possible
scoring problem before reading it as an arm result: boolean matching is
an Arabic word list, and numerical matching credits an answer whose
*leading* number is the gold value. That numerical rule replaced an
any-number-anywhere one on 2026-08-22, which had been giving the
no-context arm about three times as many chances to be right by
accident, since it hedges and states more numbers per answer.

| Run | Answer type | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | boolean | 57.6% | 139 |
| graph_walk_aya-expanse_8b|seed1 | date | 58.5% | 65 |
| graph_walk_aya-expanse_8b|seed1 | entity | 32.9% | 626 |
| graph_walk_aya-expanse_8b|seed1 | numerical | 30.0% | 170 |
| graph_walk_aya-expanse_8b|seed2 | boolean | 56.1% | 139 |
| graph_walk_aya-expanse_8b|seed2 | date | 55.4% | 65 |
| graph_walk_aya-expanse_8b|seed2 | entity | 33.5% | 626 |
| graph_walk_aya-expanse_8b|seed2 | numerical | 30.6% | 170 |
| graph_walk_aya-expanse_8b|seed3 | boolean | 56.1% | 139 |
| graph_walk_aya-expanse_8b|seed3 | date | 56.9% | 65 |
| graph_walk_aya-expanse_8b|seed3 | entity | 33.7% | 626 |
| graph_walk_aya-expanse_8b|seed3 | numerical | 30.6% | 170 |
| graph_walk_command-r7b-arabic_latest|seed1 | boolean | 50.4% | 139 |
| graph_walk_command-r7b-arabic_latest|seed1 | date | 32.3% | 65 |
| graph_walk_command-r7b-arabic_latest|seed1 | entity | 29.1% | 626 |
| graph_walk_command-r7b-arabic_latest|seed1 | numerical | 15.9% | 170 |
| graph_walk_gemma4_12b|seed1 | boolean | 56.8% | 139 |
| graph_walk_gemma4_12b|seed1 | date | 20.0% | 65 |
| graph_walk_gemma4_12b|seed1 | entity | 26.2% | 626 |
| graph_walk_gemma4_12b|seed1 | numerical | 15.9% | 170 |
| graph_walk_mistral-nemo_12b|seed1 | boolean | 47.5% | 139 |
| graph_walk_mistral-nemo_12b|seed1 | date | 52.3% | 65 |
| graph_walk_mistral-nemo_12b|seed1 | entity | 23.8% | 626 |
| graph_walk_mistral-nemo_12b|seed1 | numerical | 15.3% | 170 |
| graph_walk_qwen3.5_4b|seed1 | boolean | 64.7% | 139 |
| graph_walk_qwen3.5_4b|seed1 | date | 35.4% | 65 |
| graph_walk_qwen3.5_4b|seed1 | entity | 18.1% | 626 |
| graph_walk_qwen3.5_4b|seed1 | numerical | 8.8% | 170 |
| graph_walk_qwen3.5_9b|seed1 | boolean | 59.0% | 139 |
| graph_walk_qwen3.5_9b|seed1 | date | 30.8% | 65 |
| graph_walk_qwen3.5_9b|seed1 | entity | 25.9% | 626 |
| graph_walk_qwen3.5_9b|seed1 | numerical | 20.6% | 170 |
| graph_walk_qwen3.5_9b|seed2 | boolean | 78.6% | 14 |
| graph_walk_qwen3.5_9b|seed2 | date | 33.3% | 9 |
| graph_walk_qwen3.5_9b|seed2 | entity | 23.5% | 51 |
| graph_walk_qwen3.5_9b|seed2 | numerical | 27.3% | 11 |
| no_retrieval_aya-expanse_8b|seed1 | boolean | 64.7% | 139 |
| no_retrieval_aya-expanse_8b|seed1 | date | 53.8% | 65 |
| no_retrieval_aya-expanse_8b|seed1 | entity | 18.2% | 626 |
| no_retrieval_aya-expanse_8b|seed1 | numerical | 33.5% | 170 |
| no_retrieval_command-r7b-arabic_latest|seed1 | boolean | 56.1% | 139 |
| no_retrieval_command-r7b-arabic_latest|seed1 | date | 27.7% | 65 |
| no_retrieval_command-r7b-arabic_latest|seed1 | entity | 15.8% | 626 |
| no_retrieval_command-r7b-arabic_latest|seed1 | numerical | 19.4% | 170 |
| no_retrieval_gemma4_12b|seed1 | boolean | 63.3% | 139 |
| no_retrieval_gemma4_12b|seed1 | date | 41.5% | 65 |
| no_retrieval_gemma4_12b|seed1 | entity | 11.3% | 626 |
| no_retrieval_gemma4_12b|seed1 | numerical | 17.6% | 170 |
| no_retrieval_mistral-nemo_12b|seed1 | boolean | 44.6% | 139 |
| no_retrieval_mistral-nemo_12b|seed1 | date | 33.8% | 65 |
| no_retrieval_mistral-nemo_12b|seed1 | entity | 10.7% | 626 |
| no_retrieval_mistral-nemo_12b|seed1 | numerical | 15.9% | 170 |
| no_retrieval_qwen3.5_4b|seed1 | boolean | 56.1% | 139 |
| no_retrieval_qwen3.5_4b|seed1 | date | 18.5% | 65 |
| no_retrieval_qwen3.5_4b|seed1 | entity | 6.7% | 626 |
| no_retrieval_qwen3.5_4b|seed1 | numerical | 8.8% | 170 |
| no_retrieval_qwen3.5_9b|seed1 | boolean | 57.6% | 139 |
| no_retrieval_qwen3.5_9b|seed1 | date | 18.5% | 65 |
| no_retrieval_qwen3.5_9b|seed1 | entity | 10.2% | 626 |
| no_retrieval_qwen3.5_9b|seed1 | numerical | 11.2% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | boolean | 52.5% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | date | 46.2% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | entity | 28.1% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | numerical | 24.1% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | boolean | 55.4% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | date | 26.2% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | entity | 24.1% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | numerical | 13.5% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | boolean | 66.9% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | date | 32.3% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | entity | 22.8% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | numerical | 14.1% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | boolean | 58.3% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | date | 40.0% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | entity | 21.6% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | numerical | 19.4% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | boolean | 57.6% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | date | 24.6% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | entity | 16.8% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | numerical | 10.6% | 170 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | boolean | 63.3% | 139 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | date | 40.0% | 65 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | entity | 24.6% | 626 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | numerical | 17.6% | 170 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | boolean | 61.2% | 139 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | date | 46.2% | 65 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | entity | 27.8% | 626 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | numerical | 18.8% | 170 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | boolean | 58.3% | 139 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | date | 33.8% | 65 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | entity | 23.8% | 626 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | numerical | 16.5% | 170 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | boolean | 66.9% | 139 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | date | 40.0% | 65 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | entity | 24.6% | 626 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | numerical | 18.2% | 170 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | boolean | 55.4% | 139 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | date | 47.7% | 65 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | entity | 24.3% | 626 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | numerical | 16.5% | 170 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | boolean | 64.0% | 139 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | date | 30.8% | 65 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | entity | 17.7% | 626 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | numerical | 9.4% | 170 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | boolean | 67.6% | 139 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | date | 33.8% | 65 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | entity | 27.2% | 626 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | numerical | 17.1% | 170 |

## Accuracy by question complexity type, per run

This is the study's actual finding: the graph-walk arm is expected to win here on multihop/intersection questions and add nothing on generic/yesno ones.

| Run | Complexity type | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | comparative | 50.0% | 104 |
| graph_walk_aya-expanse_8b|seed1 | count | 35.6% | 104 |
| graph_walk_aya-expanse_8b|seed1 | difference | 18.3% | 104 |
| graph_walk_aya-expanse_8b|seed1 | generic | 40.5% | 200 |
| graph_walk_aya-expanse_8b|seed1 | intersection | 48.1% | 104 |
| graph_walk_aya-expanse_8b|seed1 | multihop | 22.9% | 96 |
| graph_walk_aya-expanse_8b|seed1 | ordinal | 32.3% | 96 |
| graph_walk_aya-expanse_8b|seed1 | superlative | 25.0% | 96 |
| graph_walk_aya-expanse_8b|seed1 | yesno | 61.5% | 96 |
| graph_walk_aya-expanse_8b|seed2 | comparative | 48.1% | 104 |
| graph_walk_aya-expanse_8b|seed2 | count | 35.6% | 104 |
| graph_walk_aya-expanse_8b|seed2 | difference | 22.1% | 104 |
| graph_walk_aya-expanse_8b|seed2 | generic | 40.5% | 200 |
| graph_walk_aya-expanse_8b|seed2 | intersection | 47.1% | 104 |
| graph_walk_aya-expanse_8b|seed2 | multihop | 19.8% | 96 |
| graph_walk_aya-expanse_8b|seed2 | ordinal | 33.3% | 96 |
| graph_walk_aya-expanse_8b|seed2 | superlative | 27.1% | 96 |
| graph_walk_aya-expanse_8b|seed2 | yesno | 61.5% | 96 |
| graph_walk_aya-expanse_8b|seed3 | comparative | 48.1% | 104 |
| graph_walk_aya-expanse_8b|seed3 | count | 35.6% | 104 |
| graph_walk_aya-expanse_8b|seed3 | difference | 22.1% | 104 |
| graph_walk_aya-expanse_8b|seed3 | generic | 40.5% | 200 |
| graph_walk_aya-expanse_8b|seed3 | intersection | 47.1% | 104 |
| graph_walk_aya-expanse_8b|seed3 | multihop | 20.8% | 96 |
| graph_walk_aya-expanse_8b|seed3 | ordinal | 33.3% | 96 |
| graph_walk_aya-expanse_8b|seed3 | superlative | 28.1% | 96 |
| graph_walk_aya-expanse_8b|seed3 | yesno | 61.5% | 96 |
| graph_walk_command-r7b-arabic_latest|seed1 | comparative | 44.2% | 104 |
| graph_walk_command-r7b-arabic_latest|seed1 | count | 20.2% | 104 |
| graph_walk_command-r7b-arabic_latest|seed1 | difference | 21.2% | 104 |
| graph_walk_command-r7b-arabic_latest|seed1 | generic | 33.0% | 200 |
| graph_walk_command-r7b-arabic_latest|seed1 | intersection | 41.3% | 104 |
| graph_walk_command-r7b-arabic_latest|seed1 | multihop | 8.3% | 96 |
| graph_walk_command-r7b-arabic_latest|seed1 | ordinal | 22.9% | 96 |
| graph_walk_command-r7b-arabic_latest|seed1 | superlative | 24.0% | 96 |
| graph_walk_command-r7b-arabic_latest|seed1 | yesno | 51.0% | 96 |
| graph_walk_gemma4_12b|seed1 | comparative | 43.3% | 104 |
| graph_walk_gemma4_12b|seed1 | count | 22.1% | 104 |
| graph_walk_gemma4_12b|seed1 | difference | 14.4% | 104 |
| graph_walk_gemma4_12b|seed1 | generic | 28.0% | 200 |
| graph_walk_gemma4_12b|seed1 | intersection | 39.4% | 104 |
| graph_walk_gemma4_12b|seed1 | multihop | 4.2% | 96 |
| graph_walk_gemma4_12b|seed1 | ordinal | 20.8% | 96 |
| graph_walk_gemma4_12b|seed1 | superlative | 18.8% | 96 |
| graph_walk_gemma4_12b|seed1 | yesno | 63.5% | 96 |
| graph_walk_mistral-nemo_12b|seed1 | comparative | 38.5% | 104 |
| graph_walk_mistral-nemo_12b|seed1 | count | 15.4% | 104 |
| graph_walk_mistral-nemo_12b|seed1 | difference | 14.4% | 104 |
| graph_walk_mistral-nemo_12b|seed1 | generic | 35.5% | 200 |
| graph_walk_mistral-nemo_12b|seed1 | intersection | 32.7% | 104 |
| graph_walk_mistral-nemo_12b|seed1 | multihop | 10.4% | 96 |
| graph_walk_mistral-nemo_12b|seed1 | ordinal | 21.9% | 96 |
| graph_walk_mistral-nemo_12b|seed1 | superlative | 14.6% | 96 |
| graph_walk_mistral-nemo_12b|seed1 | yesno | 56.2% | 96 |
| graph_walk_qwen3.5_4b|seed1 | comparative | 45.2% | 104 |
| graph_walk_qwen3.5_4b|seed1 | count | 10.6% | 104 |
| graph_walk_qwen3.5_4b|seed1 | difference | 13.5% | 104 |
| graph_walk_qwen3.5_4b|seed1 | generic | 22.5% | 200 |
| graph_walk_qwen3.5_4b|seed1 | intersection | 26.9% | 104 |
| graph_walk_qwen3.5_4b|seed1 | multihop | 5.2% | 96 |
| graph_walk_qwen3.5_4b|seed1 | ordinal | 14.6% | 96 |
| graph_walk_qwen3.5_4b|seed1 | superlative | 9.4% | 96 |
| graph_walk_qwen3.5_4b|seed1 | yesno | 70.8% | 96 |
| graph_walk_qwen3.5_9b|seed1 | comparative | 47.1% | 104 |
| graph_walk_qwen3.5_9b|seed1 | count | 23.1% | 104 |
| graph_walk_qwen3.5_9b|seed1 | difference | 18.3% | 104 |
| graph_walk_qwen3.5_9b|seed1 | generic | 34.0% | 200 |
| graph_walk_qwen3.5_9b|seed1 | intersection | 34.6% | 104 |
| graph_walk_qwen3.5_9b|seed1 | multihop | 11.5% | 96 |
| graph_walk_qwen3.5_9b|seed1 | ordinal | 14.6% | 96 |
| graph_walk_qwen3.5_9b|seed1 | superlative | 16.7% | 96 |
| graph_walk_qwen3.5_9b|seed1 | yesno | 64.6% | 96 |
| graph_walk_qwen3.5_9b|seed2 | comparative | 50.0% | 20 |
| graph_walk_qwen3.5_9b|seed2 | count | 37.5% | 8 |
| graph_walk_qwen3.5_9b|seed2 | difference | 11.1% | 9 |
| graph_walk_qwen3.5_9b|seed2 | generic | 50.0% | 2 |
| graph_walk_qwen3.5_9b|seed2 | intersection | 44.4% | 9 |
| graph_walk_qwen3.5_9b|seed2 | multihop | 0.0% | 11 |
| graph_walk_qwen3.5_9b|seed2 | ordinal | 37.5% | 8 |
| graph_walk_qwen3.5_9b|seed2 | superlative | 0.0% | 10 |
| graph_walk_qwen3.5_9b|seed2 | yesno | 87.5% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | comparative | 47.1% | 104 |
| no_retrieval_aya-expanse_8b|seed1 | count | 33.7% | 104 |
| no_retrieval_aya-expanse_8b|seed1 | difference | 17.3% | 104 |
| no_retrieval_aya-expanse_8b|seed1 | generic | 25.0% | 200 |
| no_retrieval_aya-expanse_8b|seed1 | intersection | 24.0% | 104 |
| no_retrieval_aya-expanse_8b|seed1 | multihop | 13.5% | 96 |
| no_retrieval_aya-expanse_8b|seed1 | ordinal | 25.0% | 96 |
| no_retrieval_aya-expanse_8b|seed1 | superlative | 16.7% | 96 |
| no_retrieval_aya-expanse_8b|seed1 | yesno | 68.8% | 96 |
| no_retrieval_command-r7b-arabic_latest|seed1 | comparative | 41.3% | 104 |
| no_retrieval_command-r7b-arabic_latest|seed1 | count | 25.0% | 104 |
| no_retrieval_command-r7b-arabic_latest|seed1 | difference | 9.6% | 104 |
| no_retrieval_command-r7b-arabic_latest|seed1 | generic | 20.5% | 200 |
| no_retrieval_command-r7b-arabic_latest|seed1 | intersection | 18.3% | 104 |
| no_retrieval_command-r7b-arabic_latest|seed1 | multihop | 7.3% | 96 |
| no_retrieval_command-r7b-arabic_latest|seed1 | ordinal | 15.6% | 96 |
| no_retrieval_command-r7b-arabic_latest|seed1 | superlative | 12.5% | 96 |
| no_retrieval_command-r7b-arabic_latest|seed1 | yesno | 57.3% | 96 |
| no_retrieval_gemma4_12b|seed1 | comparative | 46.2% | 104 |
| no_retrieval_gemma4_12b|seed1 | count | 21.2% | 104 |
| no_retrieval_gemma4_12b|seed1 | difference | 8.7% | 104 |
| no_retrieval_gemma4_12b|seed1 | generic | 15.0% | 200 |
| no_retrieval_gemma4_12b|seed1 | intersection | 19.2% | 104 |
| no_retrieval_gemma4_12b|seed1 | multihop | 8.3% | 96 |
| no_retrieval_gemma4_12b|seed1 | ordinal | 11.5% | 96 |
| no_retrieval_gemma4_12b|seed1 | superlative | 9.4% | 96 |
| no_retrieval_gemma4_12b|seed1 | yesno | 61.5% | 96 |
| no_retrieval_mistral-nemo_12b|seed1 | comparative | 34.6% | 104 |
| no_retrieval_mistral-nemo_12b|seed1 | count | 19.2% | 104 |
| no_retrieval_mistral-nemo_12b|seed1 | difference | 4.8% | 104 |
| no_retrieval_mistral-nemo_12b|seed1 | generic | 18.5% | 200 |
| no_retrieval_mistral-nemo_12b|seed1 | intersection | 9.6% | 104 |
| no_retrieval_mistral-nemo_12b|seed1 | multihop | 1.0% | 96 |
| no_retrieval_mistral-nemo_12b|seed1 | ordinal | 10.4% | 96 |
| no_retrieval_mistral-nemo_12b|seed1 | superlative | 7.3% | 96 |
| no_retrieval_mistral-nemo_12b|seed1 | yesno | 54.2% | 96 |
| no_retrieval_qwen3.5_4b|seed1 | comparative | 41.3% | 104 |
| no_retrieval_qwen3.5_4b|seed1 | count | 9.6% | 104 |
| no_retrieval_qwen3.5_4b|seed1 | difference | 1.9% | 104 |
| no_retrieval_qwen3.5_4b|seed1 | generic | 10.0% | 200 |
| no_retrieval_qwen3.5_4b|seed1 | intersection | 8.7% | 104 |
| no_retrieval_qwen3.5_4b|seed1 | multihop | 2.1% | 96 |
| no_retrieval_qwen3.5_4b|seed1 | ordinal | 3.1% | 96 |
| no_retrieval_qwen3.5_4b|seed1 | superlative | 3.1% | 96 |
| no_retrieval_qwen3.5_4b|seed1 | yesno | 57.3% | 96 |
| no_retrieval_qwen3.5_9b|seed1 | comparative | 43.3% | 104 |
| no_retrieval_qwen3.5_9b|seed1 | count | 12.5% | 104 |
| no_retrieval_qwen3.5_9b|seed1 | difference | 5.8% | 104 |
| no_retrieval_qwen3.5_9b|seed1 | generic | 13.5% | 200 |
| no_retrieval_qwen3.5_9b|seed1 | intersection | 13.5% | 104 |
| no_retrieval_qwen3.5_9b|seed1 | multihop | 4.2% | 96 |
| no_retrieval_qwen3.5_9b|seed1 | ordinal | 5.2% | 96 |
| no_retrieval_qwen3.5_9b|seed1 | superlative | 4.2% | 96 |
| no_retrieval_qwen3.5_9b|seed1 | yesno | 59.4% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | comparative | 48.1% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | count | 30.8% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | difference | 10.6% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | generic | 28.5% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | intersection | 39.4% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | multihop | 20.8% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | ordinal | 29.2% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | superlative | 27.1% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | yesno | 57.3% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | comparative | 48.1% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | count | 15.4% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | difference | 12.5% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | generic | 26.5% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | intersection | 36.5% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | multihop | 10.4% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | ordinal | 17.7% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | superlative | 19.8% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | yesno | 54.2% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | comparative | 49.0% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | count | 16.3% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | difference | 19.2% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | generic | 25.5% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | intersection | 34.6% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | multihop | 8.3% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | ordinal | 22.9% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | superlative | 12.5% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | yesno | 66.7% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | comparative | 41.3% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | count | 20.2% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | difference | 13.5% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | generic | 26.5% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | intersection | 30.8% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | multihop | 12.5% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | ordinal | 24.0% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | superlative | 16.7% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | yesno | 63.5% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | comparative | 45.2% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | count | 11.5% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | difference | 6.7% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | generic | 21.0% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | intersection | 21.2% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | multihop | 7.3% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | ordinal | 12.5% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | superlative | 12.5% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | yesno | 60.4% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | comparative | 51.0% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | count | 20.2% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | difference | 17.3% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | generic | 28.0% | 200 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | intersection | 29.8% | 104 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | multihop | 14.6% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | ordinal | 20.8% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | superlative | 19.8% | 96 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | yesno | 68.8% | 96 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | comparative | 53.8% | 104 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | count | 23.1% | 104 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | difference | 11.5% | 104 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | generic | 33.0% | 200 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | intersection | 40.4% | 104 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | multihop | 13.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | ordinal | 21.9% | 96 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | superlative | 28.1% | 96 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | yesno | 62.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | comparative | 41.3% | 104 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | count | 19.2% | 104 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | difference | 16.3% | 104 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | generic | 30.0% | 200 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | intersection | 36.5% | 104 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | multihop | 10.4% | 96 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | ordinal | 13.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | superlative | 19.8% | 96 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | yesno | 62.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | comparative | 51.9% | 104 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | count | 22.1% | 104 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | difference | 16.3% | 104 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | generic | 29.5% | 200 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | intersection | 38.5% | 104 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | multihop | 7.3% | 96 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | ordinal | 27.1% | 96 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | superlative | 14.6% | 96 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | yesno | 66.7% | 96 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | comparative | 42.3% | 104 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | count | 19.2% | 104 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | difference | 16.3% | 104 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | generic | 31.5% | 200 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | intersection | 37.5% | 104 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | multihop | 9.4% | 96 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | ordinal | 22.9% | 96 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | superlative | 15.6% | 96 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | yesno | 61.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | comparative | 47.1% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | count | 8.7% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | difference | 10.6% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | generic | 25.5% | 200 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | intersection | 21.2% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | multihop | 6.2% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | ordinal | 12.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | superlative | 10.4% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | yesno | 68.8% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | comparative | 57.7% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | count | 19.2% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | difference | 15.4% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | generic | 29.5% | 200 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | intersection | 37.5% | 104 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | multihop | 13.5% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | ordinal | 16.7% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | superlative | 25.0% | 96 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | yesno | 70.8% | 96 |

## Accuracy by category, per run

| Run | Category | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | books | 35.2% | 125 |
| graph_walk_aya-expanse_8b|seed1 | geography | 41.6% | 125 |
| graph_walk_aya-expanse_8b|seed1 | history | 48.8% | 125 |
| graph_walk_aya-expanse_8b|seed1 | movies | 32.0% | 125 |
| graph_walk_aya-expanse_8b|seed1 | music | 31.2% | 125 |
| graph_walk_aya-expanse_8b|seed1 | politics | 38.4% | 125 |
| graph_walk_aya-expanse_8b|seed1 | sports | 36.8% | 125 |
| graph_walk_aya-expanse_8b|seed1 | videogames | 36.0% | 125 |
| graph_walk_aya-expanse_8b|seed2 | books | 32.8% | 125 |
| graph_walk_aya-expanse_8b|seed2 | geography | 39.2% | 125 |
| graph_walk_aya-expanse_8b|seed2 | history | 48.0% | 125 |
| graph_walk_aya-expanse_8b|seed2 | movies | 31.2% | 125 |
| graph_walk_aya-expanse_8b|seed2 | music | 32.8% | 125 |
| graph_walk_aya-expanse_8b|seed2 | politics | 41.6% | 125 |
| graph_walk_aya-expanse_8b|seed2 | sports | 40.0% | 125 |
| graph_walk_aya-expanse_8b|seed2 | videogames | 35.2% | 125 |
| graph_walk_aya-expanse_8b|seed3 | books | 33.6% | 125 |
| graph_walk_aya-expanse_8b|seed3 | geography | 39.2% | 125 |
| graph_walk_aya-expanse_8b|seed3 | history | 48.8% | 125 |
| graph_walk_aya-expanse_8b|seed3 | movies | 31.2% | 125 |
| graph_walk_aya-expanse_8b|seed3 | music | 32.8% | 125 |
| graph_walk_aya-expanse_8b|seed3 | politics | 41.6% | 125 |
| graph_walk_aya-expanse_8b|seed3 | sports | 40.0% | 125 |
| graph_walk_aya-expanse_8b|seed3 | videogames | 35.2% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | books | 24.8% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | geography | 34.4% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | history | 37.6% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | movies | 23.2% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | music | 28.8% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | politics | 34.4% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | sports | 23.2% | 125 |
| graph_walk_command-r7b-arabic_latest|seed1 | videogames | 33.6% | 125 |
| graph_walk_gemma4_12b|seed1 | books | 22.4% | 125 |
| graph_walk_gemma4_12b|seed1 | geography | 34.4% | 125 |
| graph_walk_gemma4_12b|seed1 | history | 36.0% | 125 |
| graph_walk_gemma4_12b|seed1 | movies | 23.2% | 125 |
| graph_walk_gemma4_12b|seed1 | music | 20.0% | 125 |
| graph_walk_gemma4_12b|seed1 | politics | 32.0% | 125 |
| graph_walk_gemma4_12b|seed1 | sports | 27.2% | 125 |
| graph_walk_gemma4_12b|seed1 | videogames | 31.2% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | books | 28.8% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | geography | 24.8% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | history | 28.0% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | movies | 31.2% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | music | 22.4% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | politics | 32.8% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | sports | 25.6% | 125 |
| graph_walk_mistral-nemo_12b|seed1 | videogames | 26.4% | 125 |
| graph_walk_qwen3.5_4b|seed1 | books | 22.4% | 125 |
| graph_walk_qwen3.5_4b|seed1 | geography | 28.8% | 125 |
| graph_walk_qwen3.5_4b|seed1 | history | 28.8% | 125 |
| graph_walk_qwen3.5_4b|seed1 | movies | 22.4% | 125 |
| graph_walk_qwen3.5_4b|seed1 | music | 20.0% | 125 |
| graph_walk_qwen3.5_4b|seed1 | politics | 28.8% | 125 |
| graph_walk_qwen3.5_4b|seed1 | sports | 18.4% | 125 |
| graph_walk_qwen3.5_4b|seed1 | videogames | 23.2% | 125 |
| graph_walk_qwen3.5_9b|seed1 | books | 27.2% | 125 |
| graph_walk_qwen3.5_9b|seed1 | geography | 36.8% | 125 |
| graph_walk_qwen3.5_9b|seed1 | history | 33.6% | 125 |
| graph_walk_qwen3.5_9b|seed1 | movies | 27.2% | 125 |
| graph_walk_qwen3.5_9b|seed1 | music | 23.2% | 125 |
| graph_walk_qwen3.5_9b|seed1 | politics | 32.8% | 125 |
| graph_walk_qwen3.5_9b|seed1 | sports | 29.6% | 125 |
| graph_walk_qwen3.5_9b|seed1 | videogames | 28.8% | 125 |
| graph_walk_qwen3.5_9b|seed2 | movies | 32.9% | 73 |
| graph_walk_qwen3.5_9b|seed2 | music | 40.0% | 10 |
| graph_walk_qwen3.5_9b|seed2 | sports | 0.0% | 1 |
| graph_walk_qwen3.5_9b|seed2 | videogames | 100.0% | 1 |
| no_retrieval_aya-expanse_8b|seed1 | books | 28.8% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | geography | 32.8% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | history | 44.0% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | movies | 25.6% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | music | 21.6% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | politics | 43.2% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | sports | 23.2% | 125 |
| no_retrieval_aya-expanse_8b|seed1 | videogames | 17.6% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | books | 24.0% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | geography | 31.2% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | history | 22.4% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | movies | 21.6% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | music | 19.2% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | politics | 30.4% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | sports | 19.2% | 125 |
| no_retrieval_command-r7b-arabic_latest|seed1 | videogames | 14.4% | 125 |
| no_retrieval_gemma4_12b|seed1 | books | 19.2% | 125 |
| no_retrieval_gemma4_12b|seed1 | geography | 29.6% | 125 |
| no_retrieval_gemma4_12b|seed1 | history | 27.2% | 125 |
| no_retrieval_gemma4_12b|seed1 | movies | 15.2% | 125 |
| no_retrieval_gemma4_12b|seed1 | music | 15.2% | 125 |
| no_retrieval_gemma4_12b|seed1 | politics | 31.2% | 125 |
| no_retrieval_gemma4_12b|seed1 | sports | 17.6% | 125 |
| no_retrieval_gemma4_12b|seed1 | videogames | 17.6% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | books | 15.2% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | geography | 19.2% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | history | 24.0% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | movies | 16.8% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | music | 20.0% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | politics | 24.0% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | sports | 13.6% | 125 |
| no_retrieval_mistral-nemo_12b|seed1 | videogames | 9.6% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | books | 12.0% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | geography | 20.8% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | history | 20.0% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | movies | 14.4% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | music | 7.2% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | politics | 18.4% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | sports | 14.4% | 125 |
| no_retrieval_qwen3.5_4b|seed1 | videogames | 10.4% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | books | 12.0% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | geography | 35.2% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | history | 19.2% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | movies | 19.2% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | music | 11.2% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | politics | 22.4% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | sports | 8.8% | 125 |
| no_retrieval_qwen3.5_9b|seed1 | videogames | 12.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | books | 30.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | geography | 35.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | history | 43.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | movies | 28.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | music | 26.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | politics | 39.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | sports | 28.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | videogames | 24.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | books | 28.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | geography | 24.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | history | 34.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | movies | 30.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | music | 16.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | politics | 35.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | sports | 16.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | videogames | 28.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | books | 31.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | geography | 32.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | history | 37.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | movies | 30.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | music | 17.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | politics | 35.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | sports | 18.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | videogames | 21.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | books | 25.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | geography | 28.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | history | 32.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | movies | 27.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | music | 20.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | politics | 36.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | sports | 24.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | videogames | 25.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | books | 20.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | geography | 24.0% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | history | 26.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | movies | 19.2% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | music | 14.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | politics | 28.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | sports | 17.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | videogames | 24.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | books | 32.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | geography | 34.4% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | history | 37.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | movies | 28.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | music | 17.6% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | politics | 36.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | sports | 20.8% | 125 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | videogames | 29.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | books | 29.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | geography | 33.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | history | 39.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | movies | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | music | 26.4% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | politics | 35.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | sports | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | videogames | 35.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | books | 27.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | geography | 29.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | history | 31.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | movies | 32.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | music | 17.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | politics | 34.4% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | sports | 22.4% | 125 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | videogames | 29.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | books | 28.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | geography | 35.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | history | 36.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | movies | 35.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | music | 15.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | politics | 34.4% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | sports | 28.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | videogames | 30.4% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | books | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | geography | 27.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | history | 35.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | movies | 36.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | music | 20.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | politics | 29.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | sports | 24.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | videogames | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | books | 19.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | geography | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | history | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | movies | 20.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | music | 16.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | politics | 28.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | sports | 20.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | videogames | 25.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | books | 31.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | geography | 32.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | history | 40.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | movies | 36.0% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | music | 19.2% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | politics | 33.6% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | sports | 28.8% | 125 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | videogames | 30.4% | 125 |
