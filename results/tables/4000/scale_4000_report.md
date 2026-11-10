# Study 4 results, scale 4000

## Overall accuracy, per run (arm|LLM|seed)

`Truncated` is the share of answers that ended exactly at `max_tokens`.
A high rate means that run was scored on cut-off answers, which is a
pipeline finding rather than a model finding: raise the cap for that
model and re-run it alone. `Errors` are excluded from accuracy rather
than counted wrong.

| Run | Accuracy | N | Truncated | Errors | Mean s/call | Energy Wh |
|---|---|---|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | 36.4% | 4000 | 0.0% | 0 | 3.11 | 236.5 |
| graph_walk_qwen3.5_9b|seed1 | 30.4% | 4000 | 1.0% | 0 | 3.95 | 303.0 |
| no_retrieval_aya-expanse_8b|seed1 | 30.5% | 4000 | 0.0% | 0 | 0.88 | 56.5 |
| no_retrieval_qwen3.5_9b|seed1 | 18.9% | 4000 | 1.6% | 0 | 1.19 | 81.3 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | 31.7% | 4000 | 0.0% | 0 | 3.81 | 292.1 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | 31.9% | 4000 | 0.3% | 0 | 4.35 | 336.7 |

## Accuracy per arm, averaged over the LLM roster

The three-arm comparison this study exists to make. `no_retrieval`
is the control: the gap between it and the other two is what
retrieval and graph-walking actually buy. A gap smaller than about
0.02 should be read as inconclusive rather than as a result, since
this tier runs a single seed at temperature 0.2 and does not
measure its own run-to-run spread.

| Arm | Mean accuracy | LLMs |
|---|---|---|
| graph_walk | 33.4% | 2 |
| retrieval (intfloat/multilingual-e5-large) | 31.8% | 2 |
| no_retrieval | 24.7% | 2 |

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
| graph_walk_aya-expanse_8b|seed1 | boolean | 59.9% | 573 |
| graph_walk_aya-expanse_8b|seed1 | date | 53.6% | 265 |
| graph_walk_aya-expanse_8b|seed1 | entity | 31.2% | 2499 |
| graph_walk_aya-expanse_8b|seed1 | numerical | 29.0% | 655 |
| graph_walk_aya-expanse_8b|seed1 | string | 0.0% | 8 |
| graph_walk_qwen3.5_9b|seed1 | boolean | 63.0% | 573 |
| graph_walk_qwen3.5_9b|seed1 | date | 34.7% | 265 |
| graph_walk_qwen3.5_9b|seed1 | entity | 25.3% | 2499 |
| graph_walk_qwen3.5_9b|seed1 | numerical | 20.0% | 655 |
| graph_walk_qwen3.5_9b|seed1 | string | 0.0% | 8 |
| no_retrieval_aya-expanse_8b|seed1 | boolean | 66.0% | 573 |
| no_retrieval_aya-expanse_8b|seed1 | date | 56.6% | 265 |
| no_retrieval_aya-expanse_8b|seed1 | entity | 19.4% | 2499 |
| no_retrieval_aya-expanse_8b|seed1 | numerical | 31.6% | 655 |
| no_retrieval_aya-expanse_8b|seed1 | string | 0.0% | 8 |
| no_retrieval_qwen3.5_9b|seed1 | boolean | 62.5% | 573 |
| no_retrieval_qwen3.5_9b|seed1 | date | 23.0% | 265 |
| no_retrieval_qwen3.5_9b|seed1 | entity | 10.4% | 2499 |
| no_retrieval_qwen3.5_9b|seed1 | numerical | 11.5% | 655 |
| no_retrieval_qwen3.5_9b|seed1 | string | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | boolean | 60.4% | 573 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | date | 44.2% | 265 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | entity | 27.1% | 2499 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | numerical | 19.7% | 655 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | string | 0.0% | 8 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | boolean | 66.0% | 573 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | date | 40.4% | 265 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | entity | 27.3% | 2499 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | numerical | 16.9% | 655 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | string | 0.0% | 8 |

## Accuracy by question complexity type, per run

This is the study's actual finding: the graph-walk arm is expected to win here on multihop/intersection questions and add nothing on generic/yesno ones.

| Run | Complexity type | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | comparative | 57.0% | 400 |
| graph_walk_aya-expanse_8b|seed1 | count | 32.5% | 400 |
| graph_walk_aya-expanse_8b|seed1 | difference | 17.5% | 400 |
| graph_walk_aya-expanse_8b|seed1 | generic | 40.1% | 800 |
| graph_walk_aya-expanse_8b|seed1 | intersection | 36.8% | 400 |
| graph_walk_aya-expanse_8b|seed1 | multihop | 25.0% | 400 |
| graph_walk_aya-expanse_8b|seed1 | ordinal | 31.5% | 400 |
| graph_walk_aya-expanse_8b|seed1 | superlative | 23.0% | 400 |
| graph_walk_aya-expanse_8b|seed1 | yesno | 60.2% | 400 |
| graph_walk_qwen3.5_9b|seed1 | comparative | 55.2% | 400 |
| graph_walk_qwen3.5_9b|seed1 | count | 24.2% | 400 |
| graph_walk_qwen3.5_9b|seed1 | difference | 12.8% | 400 |
| graph_walk_qwen3.5_9b|seed1 | generic | 30.5% | 800 |
| graph_walk_qwen3.5_9b|seed1 | intersection | 32.0% | 400 |
| graph_walk_qwen3.5_9b|seed1 | multihop | 12.5% | 400 |
| graph_walk_qwen3.5_9b|seed1 | ordinal | 22.5% | 400 |
| graph_walk_qwen3.5_9b|seed1 | superlative | 18.5% | 400 |
| graph_walk_qwen3.5_9b|seed1 | yesno | 65.0% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | comparative | 54.2% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | count | 34.5% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | difference | 14.0% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | generic | 26.2% | 800 |
| no_retrieval_aya-expanse_8b|seed1 | intersection | 23.5% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | multihop | 19.8% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | ordinal | 24.8% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | superlative | 15.0% | 400 |
| no_retrieval_aya-expanse_8b|seed1 | yesno | 67.0% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | comparative | 50.5% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | count | 13.8% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | difference | 4.2% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | generic | 13.9% | 800 |
| no_retrieval_qwen3.5_9b|seed1 | intersection | 10.5% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | multihop | 5.2% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | ordinal | 8.0% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | superlative | 6.2% | 400 |
| no_retrieval_qwen3.5_9b|seed1 | yesno | 62.3% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | comparative | 56.2% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | count | 24.5% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | difference | 13.5% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | generic | 34.5% | 800 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | intersection | 34.2% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | multihop | 16.2% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | ordinal | 24.2% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | superlative | 19.5% | 400 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | yesno | 59.8% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | comparative | 59.8% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | count | 21.8% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | difference | 17.0% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | generic | 32.8% | 800 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | intersection | 32.8% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | multihop | 14.0% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | ordinal | 21.2% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | superlative | 20.8% | 400 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | yesno | 66.8% | 400 |

## Accuracy by category, per run

| Run | Category | Accuracy | N |
|---|---|---|---|
| graph_walk_aya-expanse_8b|seed1 | books | 30.4% | 500 |
| graph_walk_aya-expanse_8b|seed1 | geography | 41.4% | 500 |
| graph_walk_aya-expanse_8b|seed1 | history | 44.2% | 500 |
| graph_walk_aya-expanse_8b|seed1 | movies | 31.6% | 500 |
| graph_walk_aya-expanse_8b|seed1 | music | 31.8% | 500 |
| graph_walk_aya-expanse_8b|seed1 | politics | 41.0% | 500 |
| graph_walk_aya-expanse_8b|seed1 | sports | 34.8% | 500 |
| graph_walk_aya-expanse_8b|seed1 | videogames | 35.8% | 500 |
| graph_walk_qwen3.5_9b|seed1 | books | 30.4% | 500 |
| graph_walk_qwen3.5_9b|seed1 | geography | 36.8% | 500 |
| graph_walk_qwen3.5_9b|seed1 | history | 35.0% | 500 |
| graph_walk_qwen3.5_9b|seed1 | movies | 26.6% | 500 |
| graph_walk_qwen3.5_9b|seed1 | music | 26.0% | 500 |
| graph_walk_qwen3.5_9b|seed1 | politics | 30.8% | 500 |
| graph_walk_qwen3.5_9b|seed1 | sports | 26.4% | 500 |
| graph_walk_qwen3.5_9b|seed1 | videogames | 31.0% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | books | 27.8% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | geography | 37.2% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | history | 39.6% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | movies | 27.2% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | music | 24.2% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | politics | 40.8% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | sports | 27.0% | 500 |
| no_retrieval_aya-expanse_8b|seed1 | videogames | 20.4% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | books | 16.0% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | geography | 27.6% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | history | 26.4% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | movies | 15.6% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | music | 13.0% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | politics | 23.8% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | sports | 13.4% | 500 |
| no_retrieval_qwen3.5_9b|seed1 | videogames | 15.0% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | books | 26.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | geography | 36.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | history | 39.0% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | movies | 28.2% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | music | 23.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | politics | 35.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | sports | 28.8% | 500 |
| retrieval_intfloat_multilingual-e5-large_aya-expanse_8b|seed1 | videogames | 35.4% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | books | 29.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | geography | 38.0% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | history | 40.2% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | movies | 30.4% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | music | 23.8% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | politics | 33.4% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | sports | 26.6% | 500 |
| retrieval_intfloat_multilingual-e5-large_qwen3.5_9b|seed1 | videogames | 33.6% | 500 |
