# Study 4 results, scale 100

## Overall accuracy, per run (arm|LLM|seed)

`Truncated` is the share of answers that ended exactly at `max_tokens`.
A high rate means that run was scored on cut-off answers, which is a
pipeline finding rather than a model finding: raise the cap for that
model and re-run it alone. `Errors` are excluded from accuracy rather
than counted wrong.

| Run | Accuracy | N | Truncated | Errors | Mean s/call | Energy Wh |
|---|---|---|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | 38.0% | 100 | 0.0% | 0 | 3.09 | 5.9 |
| graph_walk_command-r7b-arabic_latest|seed1 | 34.0% | 100 | 0.0% | 0 | 3.31 | 6.3 |
| graph_walk_gemma4_12b|seed1 | 31.0% | 100 | 0.0% | 0 | 5.87 | 11.2 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | 29.0% | 100 | 4.0% | 0 | 6.61 | 12.9 |
| graph_walk_llama3.1_8b|seed1 | 29.0% | 100 | 0.0% | 0 | 3.35 | 6.4 |
| graph_walk_mistral-nemo_12b|seed1 | 25.0% | 100 | 0.0% | 0 | 3.80 | 7.4 |
| graph_walk_qwen3.5_4b|seed1 | 34.0% | 100 | 0.0% | 0 | 2.61 | 4.9 |
| graph_walk_qwen3.5_9b|seed1 | 33.0% | 100 | 2.0% | 0 | 3.84 | 7.4 |
| no_retrieval_aya-expanse_8b|seed1 | 34.0% | 100 | 0.0% | 0 | 0.83 | 1.3 |
| no_retrieval_command-r7b-arabic_latest|seed1 | 22.0% | 100 | 0.0% | 0 | 0.81 | 1.2 |
| no_retrieval_gemma4_12b|seed1 | 24.0% | 100 | 0.0% | 0 | 1.64 | 2.7 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | 25.0% | 100 | 7.0% | 0 | 3.26 | 6.4 |
| no_retrieval_llama3.1_8b|seed1 | 16.0% | 100 | 0.0% | 0 | 0.68 | 1.1 |
| no_retrieval_mistral-nemo_12b|seed1 | 23.0% | 100 | 0.0% | 0 | 0.62 | 1.0 |
| no_retrieval_qwen3.5_4b|seed1 | 18.0% | 100 | 0.0% | 0 | 0.92 | 1.5 |
| no_retrieval_qwen3.5_9b|seed1 | 25.0% | 100 | 2.0% | 0 | 1.26 | 2.1 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | 37.0% | 100 | 0.0% | 0 | 3.60 | 6.9 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | 34.0% | 100 | 0.0% | 0 | 3.83 | 7.3 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | 28.0% | 100 | 0.0% | 0 | 7.00 | 13.3 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | 28.0% | 100 | 5.0% | 0 | 7.67 | 14.9 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | 32.0% | 100 | 0.0% | 0 | 3.81 | 7.4 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | 35.0% | 100 | 0.0% | 0 | 4.41 | 8.6 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | 22.0% | 100 | 0.0% | 0 | 2.91 | 5.6 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | 37.0% | 100 | 0.0% | 0 | 4.17 | 8.0 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | 39.0% | 100 | 0.0% | 0 | 3.65 | 7.0 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | 38.0% | 100 | 0.0% | 0 | 3.88 | 7.3 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | 35.0% | 100 | 0.0% | 0 | 6.73 | 13.0 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | 33.0% | 100 | 10.0% | 0 | 7.70 | 14.9 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | 26.0% | 100 | 0.0% | 0 | 3.68 | 7.1 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | 32.0% | 100 | 0.0% | 0 | 4.35 | 8.6 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | 29.0% | 100 | 0.0% | 0 | 2.91 | 5.6 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | 42.0% | 100 | 0.0% | 0 | 4.18 | 8.0 |

## Accuracy per arm, averaged over the LLM roster

The three-arm comparison this study exists to make. `no_retrieval`
is the control: the gap between it and the other two is what
retrieval and graph-walking actually buy. A gap smaller than about
0.02 should be read as inconclusive rather than as a result, since
this tier runs a single seed at temperature 0.2 and does not
measure its own run-to-run spread.

| Arm | Mean accuracy | LLMs |
|---|---|---|
| retrieval (intfloat/multilingual-e5-large) | 34.2% | 8 |
| graph_walk | 31.6% | 8 |
| retrieval (Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2) | 31.6% | 8 |
| no_retrieval | 23.4% | 8 |

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
| graph_walk_aya-expanse_8b|seed1 | boolean | 33.3% | 15 |
| graph_walk_aya-expanse_8b|seed1 | date | 81.8% | 11 |
| graph_walk_aya-expanse_8b|seed1 | entity | 36.4% | 55 |
| graph_walk_aya-expanse_8b|seed1 | numerical | 21.1% | 19 |
| graph_walk_command-r7b-arabic_latest|seed1 | boolean | 53.3% | 15 |
| graph_walk_command-r7b-arabic_latest|seed1 | date | 45.5% | 11 |
| graph_walk_command-r7b-arabic_latest|seed1 | entity | 34.5% | 55 |
| graph_walk_command-r7b-arabic_latest|seed1 | numerical | 10.5% | 19 |
| graph_walk_gemma4_12b|seed1 | boolean | 66.7% | 15 |
| graph_walk_gemma4_12b|seed1 | date | 18.2% | 11 |
| graph_walk_gemma4_12b|seed1 | entity | 32.7% | 55 |
| graph_walk_gemma4_12b|seed1 | numerical | 5.3% | 19 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | boolean | 73.3% | 15 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | date | 72.7% | 11 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | entity | 7.3% | 55 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | numerical | 31.6% | 19 |
| graph_walk_llama3.1_8b|seed1 | boolean | 66.7% | 15 |
| graph_walk_llama3.1_8b|seed1 | date | 36.4% | 11 |
| graph_walk_llama3.1_8b|seed1 | entity | 23.6% | 55 |
| graph_walk_llama3.1_8b|seed1 | numerical | 10.5% | 19 |
| graph_walk_mistral-nemo_12b|seed1 | boolean | 60.0% | 15 |
| graph_walk_mistral-nemo_12b|seed1 | date | 54.5% | 11 |
| graph_walk_mistral-nemo_12b|seed1 | entity | 16.4% | 55 |
| graph_walk_mistral-nemo_12b|seed1 | numerical | 5.3% | 19 |
| graph_walk_qwen3.5_4b|seed1 | boolean | 86.7% | 15 |
| graph_walk_qwen3.5_4b|seed1 | date | 27.3% | 11 |
| graph_walk_qwen3.5_4b|seed1 | entity | 27.3% | 55 |
| graph_walk_qwen3.5_4b|seed1 | numerical | 15.8% | 19 |
| graph_walk_qwen3.5_9b|seed1 | boolean | 73.3% | 15 |
| graph_walk_qwen3.5_9b|seed1 | date | 36.4% | 11 |
| graph_walk_qwen3.5_9b|seed1 | entity | 27.3% | 55 |
| graph_walk_qwen3.5_9b|seed1 | numerical | 15.8% | 19 |
| no_retrieval_aya-expanse_8b|seed1 | boolean | 66.7% | 15 |
| no_retrieval_aya-expanse_8b|seed1 | date | 72.7% | 11 |
| no_retrieval_aya-expanse_8b|seed1 | entity | 14.5% | 55 |
| no_retrieval_aya-expanse_8b|seed1 | numerical | 42.1% | 19 |
| no_retrieval_command-r7b-arabic_latest|seed1 | boolean | 53.3% | 15 |
| no_retrieval_command-r7b-arabic_latest|seed1 | date | 45.5% | 11 |
| no_retrieval_command-r7b-arabic_latest|seed1 | entity | 10.9% | 55 |
| no_retrieval_command-r7b-arabic_latest|seed1 | numerical | 15.8% | 19 |
| no_retrieval_gemma4_12b|seed1 | boolean | 73.3% | 15 |
| no_retrieval_gemma4_12b|seed1 | date | 54.5% | 11 |
| no_retrieval_gemma4_12b|seed1 | entity | 10.9% | 55 |
| no_retrieval_gemma4_12b|seed1 | numerical | 5.3% | 19 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | boolean | 46.7% | 15 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | date | 63.6% | 11 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | entity | 7.3% | 55 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | numerical | 36.8% | 19 |
| no_retrieval_llama3.1_8b|seed1 | boolean | 40.0% | 15 |
| no_retrieval_llama3.1_8b|seed1 | date | 27.3% | 11 |
| no_retrieval_llama3.1_8b|seed1 | entity | 9.1% | 55 |
| no_retrieval_llama3.1_8b|seed1 | numerical | 10.5% | 19 |
| no_retrieval_mistral-nemo_12b|seed1 | boolean | 33.3% | 15 |
| no_retrieval_mistral-nemo_12b|seed1 | date | 45.5% | 11 |
| no_retrieval_mistral-nemo_12b|seed1 | entity | 16.4% | 55 |
| no_retrieval_mistral-nemo_12b|seed1 | numerical | 21.1% | 19 |
| no_retrieval_qwen3.5_4b|seed1 | boolean | 46.7% | 15 |
| no_retrieval_qwen3.5_4b|seed1 | date | 9.1% | 11 |
| no_retrieval_qwen3.5_4b|seed1 | entity | 14.5% | 55 |
| no_retrieval_qwen3.5_4b|seed1 | numerical | 10.5% | 19 |
| no_retrieval_qwen3.5_9b|seed1 | boolean | 60.0% | 15 |
| no_retrieval_qwen3.5_9b|seed1 | date | 18.2% | 11 |
| no_retrieval_qwen3.5_9b|seed1 | entity | 20.0% | 55 |
| no_retrieval_qwen3.5_9b|seed1 | numerical | 15.8% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | boolean | 53.3% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | date | 81.8% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | entity | 29.1% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | numerical | 21.1% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | boolean | 53.3% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | date | 63.6% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | entity | 32.7% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | numerical | 5.3% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | boolean | 60.0% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | date | 54.5% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | entity | 21.8% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | numerical | 5.3% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | boolean | 53.3% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | date | 81.8% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | entity | 12.7% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | numerical | 21.1% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | boolean | 66.7% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | date | 36.4% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | entity | 27.3% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | numerical | 15.8% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | boolean | 40.0% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | date | 72.7% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | entity | 32.7% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | numerical | 15.8% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | boolean | 46.7% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | date | 36.4% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | entity | 18.2% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | numerical | 5.3% | 19 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | boolean | 60.0% | 15 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | date | 45.5% | 11 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | entity | 36.4% | 55 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | numerical | 15.8% | 19 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | boolean | 53.3% | 15 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | date | 63.6% | 11 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | entity | 38.2% | 55 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | numerical | 15.8% | 19 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | boolean | 60.0% | 15 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | date | 63.6% | 11 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | entity | 36.4% | 55 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | numerical | 10.5% | 19 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | boolean | 73.3% | 15 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | date | 54.5% | 11 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | entity | 29.1% | 55 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | numerical | 10.5% | 19 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | boolean | 73.3% | 15 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | date | 72.7% | 11 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | entity | 18.2% | 55 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | numerical | 21.1% | 19 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | boolean | 60.0% | 15 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | date | 36.4% | 11 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | entity | 18.2% | 55 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | numerical | 15.8% | 19 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | boolean | 33.3% | 15 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | date | 54.5% | 11 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | entity | 29.1% | 55 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | numerical | 26.3% | 19 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | boolean | 60.0% | 15 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | date | 36.4% | 11 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | entity | 25.5% | 55 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | numerical | 10.5% | 19 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | boolean | 60.0% | 15 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | date | 63.6% | 11 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | entity | 36.4% | 55 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | numerical | 31.6% | 19 |

## Accuracy by question complexity type, per run

This is the study's actual finding: the graph-walk arm is expected to win here on multihop/intersection questions and add nothing on generic/yesno ones.

| Run | Complexity type | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | comparative | 50.0% | 16 |
| graph_walk_aya-expanse_8b|seed1 | count | 33.3% | 12 |
| graph_walk_aya-expanse_8b|seed1 | difference | 12.5% | 8 |
| graph_walk_aya-expanse_8b|seed1 | generic | 37.5% | 24 |
| graph_walk_aya-expanse_8b|seed1 | intersection | 37.5% | 8 |
| graph_walk_aya-expanse_8b|seed1 | multihop | 62.5% | 8 |
| graph_walk_aya-expanse_8b|seed1 | ordinal | 50.0% | 8 |
| graph_walk_aya-expanse_8b|seed1 | superlative | 25.0% | 8 |
| graph_walk_aya-expanse_8b|seed1 | yesno | 25.0% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | comparative | 62.5% | 16 |
| graph_walk_command-r7b-arabic_latest|seed1 | count | 16.7% | 12 |
| graph_walk_command-r7b-arabic_latest|seed1 | difference | 12.5% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | generic | 25.0% | 24 |
| graph_walk_command-r7b-arabic_latest|seed1 | intersection | 37.5% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | multihop | 37.5% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | ordinal | 37.5% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | superlative | 12.5% | 8 |
| graph_walk_command-r7b-arabic_latest|seed1 | yesno | 62.5% | 8 |
| graph_walk_gemma4_12b|seed1 | comparative | 50.0% | 16 |
| graph_walk_gemma4_12b|seed1 | count | 0.0% | 12 |
| graph_walk_gemma4_12b|seed1 | difference | 12.5% | 8 |
| graph_walk_gemma4_12b|seed1 | generic | 25.0% | 24 |
| graph_walk_gemma4_12b|seed1 | intersection | 37.5% | 8 |
| graph_walk_gemma4_12b|seed1 | multihop | 25.0% | 8 |
| graph_walk_gemma4_12b|seed1 | ordinal | 25.0% | 8 |
| graph_walk_gemma4_12b|seed1 | superlative | 25.0% | 8 |
| graph_walk_gemma4_12b|seed1 | yesno | 87.5% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | comparative | 25.0% | 16 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | count | 41.7% | 12 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | difference | 25.0% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | generic | 29.2% | 24 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | intersection | 12.5% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | multihop | 12.5% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | ordinal | 25.0% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | superlative | 0.0% | 8 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | yesno | 87.5% | 8 |
| graph_walk_llama3.1_8b|seed1 | comparative | 56.2% | 16 |
| graph_walk_llama3.1_8b|seed1 | count | 0.0% | 12 |
| graph_walk_llama3.1_8b|seed1 | difference | 12.5% | 8 |
| graph_walk_llama3.1_8b|seed1 | generic | 20.8% | 24 |
| graph_walk_llama3.1_8b|seed1 | intersection | 50.0% | 8 |
| graph_walk_llama3.1_8b|seed1 | multihop | 12.5% | 8 |
| graph_walk_llama3.1_8b|seed1 | ordinal | 37.5% | 8 |
| graph_walk_llama3.1_8b|seed1 | superlative | 12.5% | 8 |
| graph_walk_llama3.1_8b|seed1 | yesno | 62.5% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | comparative | 31.2% | 16 |
| graph_walk_mistral-nemo_12b|seed1 | count | 8.3% | 12 |
| graph_walk_mistral-nemo_12b|seed1 | difference | 0.0% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | generic | 29.2% | 24 |
| graph_walk_mistral-nemo_12b|seed1 | intersection | 12.5% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | multihop | 12.5% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | ordinal | 25.0% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | superlative | 12.5% | 8 |
| graph_walk_mistral-nemo_12b|seed1 | yesno | 87.5% | 8 |
| graph_walk_qwen3.5_4b|seed1 | comparative | 81.2% | 16 |
| graph_walk_qwen3.5_4b|seed1 | count | 16.7% | 12 |
| graph_walk_qwen3.5_4b|seed1 | difference | 12.5% | 8 |
| graph_walk_qwen3.5_4b|seed1 | generic | 20.8% | 24 |
| graph_walk_qwen3.5_4b|seed1 | intersection | 37.5% | 8 |
| graph_walk_qwen3.5_4b|seed1 | multihop | 0.0% | 8 |
| graph_walk_qwen3.5_4b|seed1 | ordinal | 37.5% | 8 |
| graph_walk_qwen3.5_4b|seed1 | superlative | 0.0% | 8 |
| graph_walk_qwen3.5_4b|seed1 | yesno | 87.5% | 8 |
| graph_walk_qwen3.5_9b|seed1 | comparative | 62.5% | 16 |
| graph_walk_qwen3.5_9b|seed1 | count | 8.3% | 12 |
| graph_walk_qwen3.5_9b|seed1 | difference | 12.5% | 8 |
| graph_walk_qwen3.5_9b|seed1 | generic | 33.3% | 24 |
| graph_walk_qwen3.5_9b|seed1 | intersection | 25.0% | 8 |
| graph_walk_qwen3.5_9b|seed1 | multihop | 12.5% | 8 |
| graph_walk_qwen3.5_9b|seed1 | ordinal | 25.0% | 8 |
| graph_walk_qwen3.5_9b|seed1 | superlative | 12.5% | 8 |
| graph_walk_qwen3.5_9b|seed1 | yesno | 87.5% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | comparative | 37.5% | 16 |
| no_retrieval_aya-expanse_8b|seed1 | count | 41.7% | 12 |
| no_retrieval_aya-expanse_8b|seed1 | difference | 25.0% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | generic | 29.2% | 24 |
| no_retrieval_aya-expanse_8b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | multihop | 25.0% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | ordinal | 25.0% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | superlative | 25.0% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | yesno | 87.5% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | comparative | 50.0% | 16 |
| no_retrieval_command-r7b-arabic_latest|seed1 | count | 16.7% | 12 |
| no_retrieval_command-r7b-arabic_latest|seed1 | difference | 0.0% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | generic | 16.7% | 24 |
| no_retrieval_command-r7b-arabic_latest|seed1 | intersection | 12.5% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | multihop | 12.5% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | ordinal | 25.0% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | superlative | 12.5% | 8 |
| no_retrieval_command-r7b-arabic_latest|seed1 | yesno | 37.5% | 8 |
| no_retrieval_gemma4_12b|seed1 | comparative | 56.2% | 16 |
| no_retrieval_gemma4_12b|seed1 | count | 8.3% | 12 |
| no_retrieval_gemma4_12b|seed1 | difference | 12.5% | 8 |
| no_retrieval_gemma4_12b|seed1 | generic | 20.8% | 24 |
| no_retrieval_gemma4_12b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_gemma4_12b|seed1 | multihop | 0.0% | 8 |
| no_retrieval_gemma4_12b|seed1 | ordinal | 0.0% | 8 |
| no_retrieval_gemma4_12b|seed1 | superlative | 12.5% | 8 |
| no_retrieval_gemma4_12b|seed1 | yesno | 75.0% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | comparative | 31.2% | 16 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | count | 41.7% | 12 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | difference | 0.0% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | generic | 25.0% | 24 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | intersection | 12.5% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | multihop | 25.0% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | ordinal | 12.5% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | superlative | 12.5% | 8 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | yesno | 50.0% | 8 |
| no_retrieval_llama3.1_8b|seed1 | comparative | 18.8% | 16 |
| no_retrieval_llama3.1_8b|seed1 | count | 8.3% | 12 |
| no_retrieval_llama3.1_8b|seed1 | difference | 12.5% | 8 |
| no_retrieval_llama3.1_8b|seed1 | generic | 16.7% | 24 |
| no_retrieval_llama3.1_8b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_llama3.1_8b|seed1 | multihop | 12.5% | 8 |
| no_retrieval_llama3.1_8b|seed1 | ordinal | 0.0% | 8 |
| no_retrieval_llama3.1_8b|seed1 | superlative | 12.5% | 8 |
| no_retrieval_llama3.1_8b|seed1 | yesno | 50.0% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | comparative | 50.0% | 16 |
| no_retrieval_mistral-nemo_12b|seed1 | count | 16.7% | 12 |
| no_retrieval_mistral-nemo_12b|seed1 | difference | 12.5% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | generic | 33.3% | 24 |
| no_retrieval_mistral-nemo_12b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | multihop | 0.0% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | ordinal | 0.0% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | superlative | 0.0% | 8 |
| no_retrieval_mistral-nemo_12b|seed1 | yesno | 37.5% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | comparative | 56.2% | 16 |
| no_retrieval_qwen3.5_4b|seed1 | count | 16.7% | 12 |
| no_retrieval_qwen3.5_4b|seed1 | difference | 0.0% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | generic | 4.2% | 24 |
| no_retrieval_qwen3.5_4b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | multihop | 0.0% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | ordinal | 12.5% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | superlative | 0.0% | 8 |
| no_retrieval_qwen3.5_4b|seed1 | yesno | 50.0% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | comparative | 50.0% | 16 |
| no_retrieval_qwen3.5_9b|seed1 | count | 16.7% | 12 |
| no_retrieval_qwen3.5_9b|seed1 | difference | 12.5% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | generic | 12.5% | 24 |
| no_retrieval_qwen3.5_9b|seed1 | intersection | 12.5% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | multihop | 12.5% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | ordinal | 12.5% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | superlative | 25.0% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | yesno | 75.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | comparative | 50.0% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | count | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | difference | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | generic | 45.8% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | intersection | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | multihop | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | ordinal | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | superlative | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | yesno | 50.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | comparative | 56.2% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | count | 8.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | difference | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | generic | 41.7% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | intersection | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | multihop | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | ordinal | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | superlative | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | yesno | 62.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | comparative | 37.5% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | count | 0.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | difference | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | generic | 37.5% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | intersection | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | multihop | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | ordinal | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | superlative | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | yesno | 75.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | comparative | 31.2% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | count | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | difference | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | generic | 41.7% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | intersection | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | multihop | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | ordinal | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | superlative | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | yesno | 62.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | comparative | 56.2% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | count | 8.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | difference | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | generic | 25.0% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | intersection | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | multihop | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | ordinal | 50.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | superlative | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | yesno | 62.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | comparative | 62.5% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | count | 16.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | difference | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | generic | 45.8% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | intersection | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | multihop | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | ordinal | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | superlative | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | yesno | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | comparative | 50.0% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | count | 0.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | difference | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | generic | 29.2% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | intersection | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | multihop | 0.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | ordinal | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | superlative | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | yesno | 62.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | comparative | 68.8% | 16 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | count | 8.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | difference | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | generic | 33.3% | 24 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | intersection | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | multihop | 12.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | ordinal | 37.5% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | superlative | 25.0% | 8 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | yesno | 75.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | comparative | 68.8% | 16 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | count | 16.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | difference | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | generic | 41.7% | 24 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | intersection | 62.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | multihop | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | ordinal | 50.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | superlative | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | yesno | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | comparative | 50.0% | 16 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | count | 8.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | difference | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | generic | 41.7% | 24 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | intersection | 62.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | multihop | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | ordinal | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | superlative | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | yesno | 87.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | comparative | 43.8% | 16 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | count | 8.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | difference | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | generic | 33.3% | 24 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | intersection | 62.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | multihop | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | ordinal | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | superlative | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | yesno | 100.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | comparative | 25.0% | 16 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | count | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | difference | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | generic | 33.3% | 24 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | intersection | 50.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | multihop | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | ordinal | 50.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | superlative | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | yesno | 87.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | comparative | 43.8% | 16 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | count | 8.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | difference | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | generic | 29.2% | 24 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | intersection | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | multihop | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | ordinal | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | superlative | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | yesno | 50.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | comparative | 43.8% | 16 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | count | 16.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | difference | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | generic | 41.7% | 24 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | intersection | 50.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | multihop | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | ordinal | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | superlative | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | yesno | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | comparative | 50.0% | 16 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | count | 8.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | difference | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | generic | 33.3% | 24 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | intersection | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | multihop | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | ordinal | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | superlative | 12.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | yesno | 62.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | comparative | 56.2% | 16 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | count | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | difference | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | generic | 37.5% | 24 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | intersection | 62.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | multihop | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | ordinal | 37.5% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | superlative | 25.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | yesno | 87.5% | 8 |

## Accuracy by category, per run

| Run | Category | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | books | 46.2% | 13 |
| graph_walk_aya-expanse_8b|seed1 | geography | 23.1% | 13 |
| graph_walk_aya-expanse_8b|seed1 | history | 61.5% | 13 |
| graph_walk_aya-expanse_8b|seed1 | movies | 23.1% | 13 |
| graph_walk_aya-expanse_8b|seed1 | music | 33.3% | 12 |
| graph_walk_aya-expanse_8b|seed1 | politics | 33.3% | 12 |
| graph_walk_aya-expanse_8b|seed1 | sports | 33.3% | 12 |
| graph_walk_aya-expanse_8b|seed1 | videogames | 50.0% | 12 |
| graph_walk_command-r7b-arabic_latest|seed1 | books | 30.8% | 13 |
| graph_walk_command-r7b-arabic_latest|seed1 | geography | 15.4% | 13 |
| graph_walk_command-r7b-arabic_latest|seed1 | history | 38.5% | 13 |
| graph_walk_command-r7b-arabic_latest|seed1 | movies | 15.4% | 13 |
| graph_walk_command-r7b-arabic_latest|seed1 | music | 41.7% | 12 |
| graph_walk_command-r7b-arabic_latest|seed1 | politics | 41.7% | 12 |
| graph_walk_command-r7b-arabic_latest|seed1 | sports | 33.3% | 12 |
| graph_walk_command-r7b-arabic_latest|seed1 | videogames | 58.3% | 12 |
| graph_walk_gemma4_12b|seed1 | books | 46.2% | 13 |
| graph_walk_gemma4_12b|seed1 | geography | 30.8% | 13 |
| graph_walk_gemma4_12b|seed1 | history | 38.5% | 13 |
| graph_walk_gemma4_12b|seed1 | movies | 7.7% | 13 |
| graph_walk_gemma4_12b|seed1 | music | 33.3% | 12 |
| graph_walk_gemma4_12b|seed1 | politics | 33.3% | 12 |
| graph_walk_gemma4_12b|seed1 | sports | 25.0% | 12 |
| graph_walk_gemma4_12b|seed1 | videogames | 33.3% | 12 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | books | 38.5% | 13 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | geography | 7.7% | 13 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | history | 30.8% | 13 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | movies | 23.1% | 13 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | music | 25.0% | 12 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | politics | 25.0% | 12 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | sports | 41.7% | 12 |
| graph_walk_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | videogames | 41.7% | 12 |
| graph_walk_llama3.1_8b|seed1 | books | 15.4% | 13 |
| graph_walk_llama3.1_8b|seed1 | geography | 15.4% | 13 |
| graph_walk_llama3.1_8b|seed1 | history | 15.4% | 13 |
| graph_walk_llama3.1_8b|seed1 | movies | 23.1% | 13 |
| graph_walk_llama3.1_8b|seed1 | music | 33.3% | 12 |
| graph_walk_llama3.1_8b|seed1 | politics | 50.0% | 12 |
| graph_walk_llama3.1_8b|seed1 | sports | 41.7% | 12 |
| graph_walk_llama3.1_8b|seed1 | videogames | 41.7% | 12 |
| graph_walk_mistral-nemo_12b|seed1 | books | 38.5% | 13 |
| graph_walk_mistral-nemo_12b|seed1 | geography | 23.1% | 13 |
| graph_walk_mistral-nemo_12b|seed1 | history | 23.1% | 13 |
| graph_walk_mistral-nemo_12b|seed1 | movies | 15.4% | 13 |
| graph_walk_mistral-nemo_12b|seed1 | music | 25.0% | 12 |
| graph_walk_mistral-nemo_12b|seed1 | politics | 33.3% | 12 |
| graph_walk_mistral-nemo_12b|seed1 | sports | 16.7% | 12 |
| graph_walk_mistral-nemo_12b|seed1 | videogames | 25.0% | 12 |
| graph_walk_qwen3.5_4b|seed1 | books | 38.5% | 13 |
| graph_walk_qwen3.5_4b|seed1 | geography | 23.1% | 13 |
| graph_walk_qwen3.5_4b|seed1 | history | 23.1% | 13 |
| graph_walk_qwen3.5_4b|seed1 | movies | 15.4% | 13 |
| graph_walk_qwen3.5_4b|seed1 | music | 41.7% | 12 |
| graph_walk_qwen3.5_4b|seed1 | politics | 58.3% | 12 |
| graph_walk_qwen3.5_4b|seed1 | sports | 41.7% | 12 |
| graph_walk_qwen3.5_4b|seed1 | videogames | 33.3% | 12 |
| graph_walk_qwen3.5_9b|seed1 | books | 15.4% | 13 |
| graph_walk_qwen3.5_9b|seed1 | geography | 23.1% | 13 |
| graph_walk_qwen3.5_9b|seed1 | history | 46.2% | 13 |
| graph_walk_qwen3.5_9b|seed1 | movies | 15.4% | 13 |
| graph_walk_qwen3.5_9b|seed1 | music | 41.7% | 12 |
| graph_walk_qwen3.5_9b|seed1 | politics | 41.7% | 12 |
| graph_walk_qwen3.5_9b|seed1 | sports | 41.7% | 12 |
| graph_walk_qwen3.5_9b|seed1 | videogames | 41.7% | 12 |
| no_retrieval_aya-expanse_8b|seed1 | books | 69.2% | 13 |
| no_retrieval_aya-expanse_8b|seed1 | geography | 7.7% | 13 |
| no_retrieval_aya-expanse_8b|seed1 | history | 61.5% | 13 |
| no_retrieval_aya-expanse_8b|seed1 | movies | 23.1% | 13 |
| no_retrieval_aya-expanse_8b|seed1 | music | 16.7% | 12 |
| no_retrieval_aya-expanse_8b|seed1 | politics | 41.7% | 12 |
| no_retrieval_aya-expanse_8b|seed1 | sports | 16.7% | 12 |
| no_retrieval_aya-expanse_8b|seed1 | videogames | 33.3% | 12 |
| no_retrieval_command-r7b-arabic_latest|seed1 | books | 46.2% | 13 |
| no_retrieval_command-r7b-arabic_latest|seed1 | geography | 15.4% | 13 |
| no_retrieval_command-r7b-arabic_latest|seed1 | history | 38.5% | 13 |
| no_retrieval_command-r7b-arabic_latest|seed1 | movies | 7.7% | 13 |
| no_retrieval_command-r7b-arabic_latest|seed1 | music | 8.3% | 12 |
| no_retrieval_command-r7b-arabic_latest|seed1 | politics | 33.3% | 12 |
| no_retrieval_command-r7b-arabic_latest|seed1 | sports | 16.7% | 12 |
| no_retrieval_command-r7b-arabic_latest|seed1 | videogames | 8.3% | 12 |
| no_retrieval_gemma4_12b|seed1 | books | 30.8% | 13 |
| no_retrieval_gemma4_12b|seed1 | geography | 23.1% | 13 |
| no_retrieval_gemma4_12b|seed1 | history | 46.2% | 13 |
| no_retrieval_gemma4_12b|seed1 | movies | 15.4% | 13 |
| no_retrieval_gemma4_12b|seed1 | music | 0.0% | 12 |
| no_retrieval_gemma4_12b|seed1 | politics | 25.0% | 12 |
| no_retrieval_gemma4_12b|seed1 | sports | 8.3% | 12 |
| no_retrieval_gemma4_12b|seed1 | videogames | 41.7% | 12 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | books | 23.1% | 13 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | geography | 15.4% | 13 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | history | 53.8% | 13 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | movies | 30.8% | 13 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | music | 16.7% | 12 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | politics | 25.0% | 12 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | sports | 8.3% | 12 |
| no_retrieval_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | videogames | 25.0% | 12 |
| no_retrieval_llama3.1_8b|seed1 | books | 7.7% | 13 |
| no_retrieval_llama3.1_8b|seed1 | geography | 23.1% | 13 |
| no_retrieval_llama3.1_8b|seed1 | history | 38.5% | 13 |
| no_retrieval_llama3.1_8b|seed1 | movies | 7.7% | 13 |
| no_retrieval_llama3.1_8b|seed1 | music | 0.0% | 12 |
| no_retrieval_llama3.1_8b|seed1 | politics | 25.0% | 12 |
| no_retrieval_llama3.1_8b|seed1 | sports | 8.3% | 12 |
| no_retrieval_llama3.1_8b|seed1 | videogames | 16.7% | 12 |
| no_retrieval_mistral-nemo_12b|seed1 | books | 30.8% | 13 |
| no_retrieval_mistral-nemo_12b|seed1 | geography | 23.1% | 13 |
| no_retrieval_mistral-nemo_12b|seed1 | history | 38.5% | 13 |
| no_retrieval_mistral-nemo_12b|seed1 | movies | 0.0% | 13 |
| no_retrieval_mistral-nemo_12b|seed1 | music | 33.3% | 12 |
| no_retrieval_mistral-nemo_12b|seed1 | politics | 25.0% | 12 |
| no_retrieval_mistral-nemo_12b|seed1 | sports | 16.7% | 12 |
| no_retrieval_mistral-nemo_12b|seed1 | videogames | 16.7% | 12 |
| no_retrieval_qwen3.5_4b|seed1 | books | 7.7% | 13 |
| no_retrieval_qwen3.5_4b|seed1 | geography | 23.1% | 13 |
| no_retrieval_qwen3.5_4b|seed1 | history | 38.5% | 13 |
| no_retrieval_qwen3.5_4b|seed1 | movies | 7.7% | 13 |
| no_retrieval_qwen3.5_4b|seed1 | music | 8.3% | 12 |
| no_retrieval_qwen3.5_4b|seed1 | politics | 33.3% | 12 |
| no_retrieval_qwen3.5_4b|seed1 | sports | 16.7% | 12 |
| no_retrieval_qwen3.5_4b|seed1 | videogames | 8.3% | 12 |
| no_retrieval_qwen3.5_9b|seed1 | books | 7.7% | 13 |
| no_retrieval_qwen3.5_9b|seed1 | geography | 46.2% | 13 |
| no_retrieval_qwen3.5_9b|seed1 | history | 30.8% | 13 |
| no_retrieval_qwen3.5_9b|seed1 | movies | 15.4% | 13 |
| no_retrieval_qwen3.5_9b|seed1 | music | 8.3% | 12 |
| no_retrieval_qwen3.5_9b|seed1 | politics | 50.0% | 12 |
| no_retrieval_qwen3.5_9b|seed1 | sports | 8.3% | 12 |
| no_retrieval_qwen3.5_9b|seed1 | videogames | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | books | 38.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | geography | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | history | 53.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | movies | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | music | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | politics | 50.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | sports | 16.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_aya-expanse_8b|seed1 | videogames | 41.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | books | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | geography | 23.1% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | history | 46.2% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | movies | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | music | 41.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | politics | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | sports | 41.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_command-r7b-arabic_latest|seed1 | videogames | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | books | 46.2% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | geography | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | history | 38.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | movies | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | music | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | politics | 41.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | sports | 8.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_gemma4_12b|seed1 | videogames | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | books | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | geography | 7.7% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | history | 46.2% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | movies | 38.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | music | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | politics | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | sports | 8.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | videogames | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | books | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | geography | 23.1% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | history | 53.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | movies | 23.1% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | music | 16.7% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | politics | 50.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | sports | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_llama3.1_8b|seed1 | videogames | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | books | 53.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | geography | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | history | 38.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | movies | 38.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | music | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | politics | 50.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | sports | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_mistral-nemo_12b|seed1 | videogames | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | books | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | geography | 30.8% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | history | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | movies | 7.7% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | music | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | politics | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | sports | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_4b|seed1 | videogames | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | books | 46.2% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | geography | 23.1% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | history | 61.5% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | movies | 15.4% | 13 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | music | 33.3% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | politics | 50.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | sports | 25.0% | 12 |
| retrieval_Omartificial-Intelligence-Space_Arabic-Triplet-Matryoshka-V2_qwen3.5_9b|seed1 | videogames | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | books | 46.2% | 13 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | geography | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | history | 46.2% | 13 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | movies | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | music | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | politics | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | sports | 33.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | books | 38.5% | 13 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | geography | 7.7% | 13 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | history | 38.5% | 13 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | movies | 38.5% | 13 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | music | 33.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | politics | 58.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | sports | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_command-r7b-arabic_latest|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | books | 53.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | geography | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | history | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | movies | 23.1% | 13 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | music | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | politics | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | sports | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_gemma4_12b|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | books | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | geography | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | history | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | movies | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | music | 16.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | politics | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | sports | 33.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_hf.co_mradermacher_Fanar-1-9B-Instruct-GGUF_Q4_K_M|seed1 | videogames | 58.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | books | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | geography | 23.1% | 13 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | history | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | movies | 23.1% | 13 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | music | 16.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | politics | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | sports | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_llama3.1_8b|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | books | 46.2% | 13 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | geography | 7.7% | 13 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | history | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | movies | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | music | 33.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | politics | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | sports | 33.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_mistral-nemo_12b|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | books | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | geography | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | history | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | movies | 15.4% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | music | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | politics | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | sports | 8.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_4b|seed1 | videogames | 50.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | books | 46.2% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | geography | 30.8% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | history | 61.5% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | movies | 23.1% | 13 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | music | 41.7% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | politics | 58.3% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | sports | 25.0% | 12 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | videogames | 50.0% | 12 |
