# Graph Neighbourhoods and Embedding Retrieval as Context for Arabic Question Answering

Code, data and model outputs for the AICSET 2026 paper of the same title, by Abdelhakim EL Ghayoubi, Achraf Chahboune, Imad Sassi and Said Bahassine.

On the 4,000 Arabic questions in the Mintaka test split, the study compares four answer-generation arms: no context, a graph walk, pooled dense retrieval with multilingual-E5 large, and scoped retrieval within the graph walk's candidate pool. Each context arm selects up to 150 Wikidata fact lines. The study measures answer accuracy, coverage of gold entity labels in the context, and the cost of a miss: the change in accuracy on questions whose context does not contain the gold label, compared with the same model without context. The fact store was pulled around both question and gold-answer entities as a controlled setting, so its coverage is optimistic.

## Repository layout

```
configs/            model, graph and generation settings
src/                graph, retrieval, scoring and model-calling code
scripts/            pipeline and analysis scripts
tests/              unit tests
prompts/            Arabic answer and entity-mention prompts
datasets/mintaka/   full Mintaka test split
data/processed/     Wikidata graph and optional linking caches
results/answers/    model answers at 100, 1,000 and 4,000 questions
results/contexts/   context files at 1,000 and 4,000 questions
results/graph_walk/ graph paths and fact lines
results/retrieval/  retrieved fact lines
results/linking/    predicted entity results, when available
results/tables/     scored results and analyses
results/logs/       reference output from script 12
MANIFEST.sha256     checksums for release files and unpacked data
unpack_data.py      verifies and unpacks compressed files
```

## Setup

- Python 3.14: `pip install -r requirements.txt`.
- [Ollama](https://ollama.com) 0.32.6 was used for generation. The model tags and recorded digest prefixes were `aya-expanse:8b` (65f986688a01), `qwen3.5:9b` (6488c96fa5fa), `qwen3.5:4b` (2a654d98e6fb), `gemma4:12b` (4eb23ef187e2), `mistral-nemo:12b` (e7e06d107c6c), and `command-r7b-arabic:latest` (4bbe3353e56a). Other pilot models and embedding models are listed in `configs/`.
- The runs used one 16 GB NVIDIA Quadro RTX 5000.

With NVIDIA driver 595.95 (CUDA 13.2), Ollama 0.32.6 selects its CUDA 13
backend, which crashed on this Turing GPU when loading a model. The camera-ready
runs therefore used `OLLAMA_LLM_LIBRARY=cuda_v12 ollama serve`. Before those
runs, 20 stored answers per model were generated again with this setup and
matched the stored text exactly.

## Data

The release includes the full Mintaka test file, the Wikidata graph cache with entity and literal statements, prompts, and the selected model outputs and analyses. Data and results files larger than 5 MiB are compressed. Run `python unpack_data.py` from the repository root to verify and unpack them. The script leaves the archives in place by default; `--remove-gz` removes an archive after verification.

The multilingual-E5 embedding cache is not included. Script 11 rebuilds it when it builds pooled or scoped contexts. The Mintaka training and development splits are not included; obtain them from the [Mintaka repository](https://github.com/amazon-science/mintaka) if using `--split train` or `--split dev`.

## Reproducing the results

### From the included outputs (no GPU)

Run from the repository root after installing the requirements:

```
python unpack_data.py
python scripts/12_aicset_numbers.py
python scripts/05_score.py --scale 4000 --split test
python scripts/06_report.py --scale 4000
python scripts/13_context_coverage.py --scale 4000
python scripts/14_review_scoped_runs.py
```

Compare script 12's output with `results/logs/aicset_numbers_2026-10-04.txt`. Script 12 also creates `paper-aicset-2026/figures/` for generated figure data. Script 05 writes scores in `results/tables/`; script 06 renders them. Use `--scale 100` or `--scale 1000` with scripts 05 and 06 for those tiers.

### Revision analysis

The checks in Sect. 4.6 and Table 2 of the camera-ready paper (store without
the answers' facts, predicted entities, 50 distinct lines, one hop) use the
1,000-question sample and are paired with the 4,000-question runs on the same
questions:

```
python scripts/18_revision_numbers.py
```

Compare its output with `results/logs/revision_numbers_2026-11-09.txt`. It also
writes `results/tables/1000/revision_1000.json`. The entity-linking scores are
in `results/tables/1000/entity_linking_1000.json`.

### Full rerun

A full rerun needs network access for Wikidata and the models, and Ollama for answer generation. The included outputs and caches make the scripts reuse existing work, so use a separate clean copy for a fresh run. Set `PYTHONHASHSEED=0` before running. Run one model job at a time.

1. Fact store, graph walk and pooled retrieval:

```
python scripts/01_collect_qids_and_pull_graph.py --scale 4000 --split test --max-hops 2
python scripts/03_run_graph_walk.py --scale 4000 --split test
python scripts/02_run_retrieval.py --scale 4000 --split test --embedding-models intfloat/multilingual-e5-large
python scripts/02b_retrieval_hit_rate.py --scale 4000 --split test
```

2. Answers on all 4,000 questions (no context, graph walk, pooled retrieval):

```
python scripts/04_run_answer_generation.py --scale 4000 --split test --arm no_retrieval --models aya-expanse:8b,qwen3.5:9b
python scripts/04_run_answer_generation.py --scale 4000 --split test --arm graph_walk --models aya-expanse:8b,qwen3.5:9b
python scripts/04_run_answer_generation.py --scale 4000 --split test --arm retrieval --embedding-model intfloat/multilingual-e5-large --models aya-expanse:8b,qwen3.5:9b
```

3. Six models on the 1,000-question sample (Sect. 4.5); each arm with
`--models aya-expanse:8b,command-r7b-arabic:latest,gemma4:12b,mistral-nemo:12b,qwen3.5:4b,qwen3.5:9b`:

```
python scripts/04_run_answer_generation.py --scale 1000 --split test --arm no_retrieval --models ...
python scripts/04_run_answer_generation.py --scale 1000 --split test --arm graph_walk --models ...
python scripts/04_run_answer_generation.py --scale 1000 --split test --arm retrieval --embedding-model intfloat/multilingual-e5-large --models ...
```

4. Scoped retrieval on all 4,000 questions:

```
python scripts/11_build_contexts.py --mode scoped --store answered
python scripts/04_run_answer_generation.py --scale 4000 --split test --arm contexts --context-name scoped_answered --models aya-expanse:8b,qwen3.5:9b
```

5. Camera-ready checks on the 1,000-question sample (Sect. 4.6):

```
python scripts/15_revision_contexts.py budget --k 50
python scripts/11_build_contexts.py --mode walk --store question
python scripts/11_build_contexts.py --mode pooled --store question
python scripts/11_build_contexts.py --mode scoped --store question
python scripts/11_build_contexts.py --mode walk --store answered --walk-hops 1 --tag _h1
python scripts/15_revision_contexts.py subset --names walk_question pooled_question scoped_question walk_answered_h1
python scripts/16_predicted_entities.py mentions
python scripts/16_predicted_entities.py link
python scripts/16_predicted_entities.py evaluate
python scripts/16_predicted_entities.py pull
python scripts/16_predicted_entities.py contexts
```

then, for each context name in `walk_answered_k50 pooled_answered_k50 walk_question pooled_question scoped_question walk_answered_h1 walk_predicted`:

```
python scripts/04_run_answer_generation.py --scale 1000 --split test --arm contexts --context-name NAME --models aya-expanse:8b,qwen3.5:9b
```

Script 04 and the mention step resume by `item_id`, and existing context files are reused. Do not use `--overwrite` when resuming. The September 2026 graph runs used walk tie-breaking that depended on Python's hash seed, so rerunning the walk need not reproduce every context line, as stated in the paper.

## Where each result comes from

| Paper | Script | Output |
|---|---|---|
| Sect. 4.1 to 4.4, Fig. 2, Fig. 3, Table 1 | `scripts/12_aicset_numbers.py` | `results/logs/aicset_numbers_2026-10-04.txt` |
| Sect. 4.5, Fig. 4 (six models) | `scripts/12_aicset_numbers.py` | same file, "SCALE 1000" part |
| Sect. 3.2 (question-only coverage) | `scripts/13_context_coverage.py` | printed |
| Sect. 3.3 (linker quality), Sect. 4.6, Table 2 | `scripts/18_revision_numbers.py` | `results/logs/revision_numbers_2026-11-09.txt`, `results/tables/1000/revision_1000.json` |
| Sect. 3.3 (multi-number answers) | `scripts/07_review_numbers.py` | printed |

## Licences

[Mintaka](https://github.com/amazon-science/mintaka) is released under CC BY 4.0. [Wikidata structured data](https://www.wikidata.org/wiki/Wikidata:Licensing) is available under CC0. Model outputs are shared for research use; each model's own licence applies.

## Citation

```
@inproceedings{elghayoubi2026graphqa,
  title     = {Graph Neighbourhoods and Embedding Retrieval as Context for Arabic Question Answering},
  author    = {Abdelhakim {EL Ghayoubi} and Achraf Chahboune and Imad Sassi and Said Bahassine},
  booktitle = {Proceedings of the 2nd International Conference on Artificial Intelligence and Cognitive Science for Emerging Technologies (AICSET 2026)},
  publisher = {Springer},
  year      = {2026},
  note      = {To appear}
}
```
