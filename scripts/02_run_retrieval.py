"""Plain-retrieval arm: turn the pulled graph's facts into one sentence
each, embed with every model in configs/embedding_models.yaml, retrieve the
top-k most similar to each question, and write them for
scripts/04_run_answer_generation.py to feed to the answer LLM.

Usage:
    python scripts/02_run_retrieval.py --scale 100 --split test
    python scripts/02_run_retrieval.py --scale 100 --split test --embedding-models bge-m3
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))

from src.common.job_runner import run_job  # noqa: E402
from src.qa.graph_pull import (  # noqa: E402
    _client,
    drop_excluded_properties,
    fetch_property_labels,
    scope_to_seeds,
)
from src.qa.mintaka_loader import collect_qids, load_split, select_scale  # noqa: E402
from src.qa.retrieval import (  # noqa: E402
    build_literal_facts,
    build_retrievable_facts,
    normalize_matrix,
    top_k_by_similarity_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Study4-AICSET-research/1.0 (academic research script)"
SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}
RESULTS_DIR = ROOT / "results" / "retrieval"
PROPERTY_LABELS_PATH = ROOT / "data" / "processed" / "graph_cache" / "property_labels.json"


def load_cached_literals(cache_path: Path, tier_heads: set[str]) -> list[tuple[str, str, str]]:
    """Date and quantity facts for the heads in this tier's graph. Kept in
    their own file so the graph-walk arm, which reads triples.jsonl, cannot
    accidentally walk through a date (src/qa/retrieval.py::build_literal_facts).
    """
    if not cache_path.exists():
        return []
    literals = []
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["relation"] is None:  # the "no literal claims" sentinel row
                continue
            if row["head"] in tier_heads:
                literals.append((row["head"], row["relation"], row["value"]))
    return literals


def load_cached_triples(cache_path: Path) -> list[tuple[str, str, str, str]]:
    triples = []
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["relation"] is None:  # scripts/01's "no outgoing edges" sentinel row
                continue
            triples.append((row["head"], row["relation"], row["tail"], row["tail_label"]))
    return triples


def build_head_labels(questions: list, triples: list[tuple[str, str, str, str]]) -> dict[str, str]:
    """Arabic labels for every QID that could appear as a triple's head:
    gold answer entities carry a label directly (mintaka_loader already
    extracted it); anything else that shows up as a head is only labelled
    if it also appeared as a tail somewhere in the pulled graph, which
    multi-hop expansion (scripts/01) makes true for most non-seed heads.

    English is the last resort, and only for question entities, which are
    the only QIDs with an English label on hand (mintaka_loader reads it
    from questionEntity). Without it the renderers would print a bare
    "Q1234" inside an otherwise Arabic prompt, which is worse than the
    English name for both the embedding model and the answer LLM.

    Why any are missing: build_neighborhood_query requires the tail to have
    an Arabic label, so an entity with no Arabic label never enters the
    graph as a tail and never picks one up. Question entities are queried as
    heads, so they are the QIDs this affects. On the stratified scale-100
    tier, 84.9% of question entities have an Arabic label, from 100% for
    geography, history and politics down to 63.2% for music and 68.2% for
    videogames.
    """
    labels: dict[str, str] = {}
    for q in questions:
        for qid, label in zip(q.answer_qids, q.answer_labels_ar):
            if label:
                labels[qid] = label
    for _head, _rel, tail, tail_label in triples:
        labels.setdefault(tail, tail_label)
    for q in questions:
        for entity in q.question_entities:
            if entity.label_en:
                labels.setdefault(entity.qid, entity.label_en)
    return labels


def ensure_property_labels(triples: list[tuple[str, str, str, str]], cache_path: Path) -> dict[str, str]:
    """Incremental rather than all-or-nothing: fetches only the PIDs the
    cache is missing and merges them in.

    Returning a cached file whole would miss properties added later: P569
    and other literal properties never appear in an entity-valued triple,
    so a cache built from triples alone would leave every literal fact
    rendered with a raw "P569".

    Two passes, Arabic then English. Without the English pass, 712 of
    85,288 scale-100 sentences (0.83%) would read like
    "إفريقيا - P13574 - لاغوس", and a raw identifier means nothing to an
    embedding model or the answer LLM. An English relation name inside an
    Arabic fact line is imperfect but much better than an identifier.

    A PID with no label in either language stays an empty string, so the
    English pass retries it on the next run, in case a later Wikidata edit
    has filled it.
    """
    cached: dict[str, str] = {}
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            cached = json.load(f)

    wanted = {rel for _h, rel, _t, _l in triples}
    never_seen = sorted(wanted - cached.keys())
    sparql = None

    if never_seen:
        logger.info("fetching Arabic labels for %d properties not yet cached", len(never_seen))
        sparql = _client(SPARQL_ENDPOINT, USER_AGENT)
        arabic = fetch_property_labels(sparql, never_seen)
        cached.update({pid: arabic.get(pid, "") for pid in never_seen})

    # Everything still blank, including PIDs an earlier run already recorded
    # as having no Arabic label.
    blank = sorted(pid for pid in wanted if not cached.get(pid))
    if blank:
        logger.info("%d properties have no Arabic label; falling back to English", len(blank))
        sparql = sparql or _client(SPARQL_ENDPOINT, USER_AGENT)
        english = fetch_property_labels(sparql, blank, labels_language="en")
        found = {pid: label for pid, label in english.items() if label}
        cached.update(found)
        logger.info("  %d of %d resolved in English; %d remain unlabelled and render as the PID",
                    len(found), len(blank), len(blank) - len(found))

    if never_seen or blank:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cached, f, ensure_ascii=False, indent=1)
    return cached


def _embed_batch_with_retry(client, model_name: str, batch: list[str], max_retries: int = 6):
    """One Ollama embed call, retried through transient socket failures.

    Ollama opens an internal HTTP connection to its own model runner per
    request, so a long embedding job accumulates Windows sockets in
    TIME_WAIT until the ephemeral port range is exhausted, and the client
    sees the model runner refuse a connection ("bind: An operation on a
    socket could not be performed because the system lacked sufficient
    buffer space or because a queue was full"). It is a rate problem, not a
    size problem: every batch size from 1 to 256 succeeds in isolation.

    Waiting fixes it, since TIME_WAIT entries drain on their own. The
    backoff starts at 15 s and grows, longer than a typical retry, because
    it waits on a kernel timer rather than a busy server.
    """
    import time as _time

    for attempt in range(1, max_retries + 1):
        try:
            return client.embed(model=model_name, input=batch)["embeddings"]
        except Exception as exc:
            if attempt == max_retries:
                raise
            wait_s = 15.0 * attempt
            logger.warning(
                "embed batch failed (attempt %d/%d): %s. Waiting %.0fs for sockets to drain.",
                attempt, max_retries, str(exc)[:160], wait_s,
            )
            _time.sleep(wait_s)


def load_embedder(model_name: str, backend: str) -> Callable[[list[str]], list[list[float]]]:
    """The one model-loading function in this script; everything else is
    plain data wiring (src/qa/retrieval.py's ranking logic never needs to
    know which backend produced a vector). Loaded once per model, not once
    per text, so the per-question worker never reloads the model.
    """
    if backend == "sentence-transformers":
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        return lambda texts: model.encode(texts, batch_size=64, show_progress_bar=len(texts) > 1000)

    if backend == "ollama":
        import ollama

        client = ollama.Client()

        def embed(texts: list[str], batch_size: int = 128):
            """Batched, and accumulated as float32 numpy rather than Python
            lists.

            Batched because Ollama's embed endpoint takes a list, and one call
            per sentence would mean a separate HTTP round trip for every fact
            in the corpus: about 75,000 per model at scale 100, and 180,000 at
            scale 1,000.

            numpy per batch because of qwen3-embedding:8b. It returns
            4,096-dimensional vectors, so an 85,288-fact corpus is 349 million
            floats; as Python lists that is roughly 10 GB of boxed objects,
            against 1.4 GB as float32. Throughput on the test machine: bge-m3
            about 106 texts/s, embeddinggemma:300m 73, qwen3-embedding:8b 17.
            """
            import numpy as np

            chunks = []
            for i in range(0, len(texts), batch_size):
                batch = _embed_batch_with_retry(client, model_name, texts[i : i + batch_size])
                chunks.append(np.asarray(batch, dtype=np.float32))
                if i and i % (batch_size * 40) == 0:
                    logger.info("  %s: embedded %d/%d", model_name, i, len(texts))
            return np.vstack(chunks) if chunks else np.zeros((0, 0), dtype=np.float32)

        return embed

    raise ValueError(f"unknown embedding backend: {backend!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    parser.add_argument("--embedding-models", type=str, default=None, help="Comma-separated model names, default every model in configs/embedding_models.yaml")
    parser.add_argument(
        "--overwrite", action="store_true",
        help="delete a model's existing output before running. Required when re-running "
             "a model after changing what it embeds, since run_job resumes by item_id "
             "and would otherwise skip every question and leave the old results in place.",
    )
    args = parser.parse_args()

    with open(ROOT / "configs" / "embedding_models.yaml", encoding="utf-8") as f:
        embed_cfg = yaml.safe_load(f)
    with open(ROOT / "configs" / "graph_walk.yaml", encoding="utf-8") as f:
        walk_cfg = yaml.safe_load(f)

    questions = load_split(DATASETS_ROOT / SPLIT_FILES[args.split])
    questions = select_scale(questions, args.scale)
    logger.info("%d questions loaded", len(questions))

    cache_path = ROOT / walk_cfg["graph_cache_dir"] / "triples.jsonl"
    all_triples = load_cached_triples(cache_path)
    logger.info("%d cached triples loaded", len(all_triples))
    before = len(all_triples)
    all_triples = drop_excluded_properties(all_triples, walk_cfg.get("excluded_properties"))
    logger.info("%d Wikimedia-bookkeeping edges dropped (%d remain)", before - len(all_triples), len(all_triples))
    triples = scope_to_seeds(all_triples, collect_qids(questions), walk_cfg["max_hops"])
    logger.info("%d triples in this tier's own %d-hop graph (the cache is cumulative "
                "across tiers; the rest belongs to other question sets)",
                len(triples), walk_cfg["max_hops"])

    # Labels from the whole cache, corpus from the scoped subset: see
    # scripts/03's own comment on the same split.
    head_labels = build_head_labels(questions, all_triples)

    literals = load_cached_literals(cache_path.parent / "literals.jsonl", {t[0] for t in triples})
    relation_labels = ensure_property_labels(
        triples + [(h, r, "", "") for h, r, _v in literals], PROPERTY_LABELS_PATH
    )

    facts = build_retrievable_facts(triples, head_labels, relation_labels)
    logger.info("%d retrievable facts built (of %d triples; the rest had an unlabelled head)", len(facts), len(triples))
    literal_facts = build_literal_facts(literals, head_labels, relation_labels)
    logger.info("%d date/quantity facts added; these are retrievable but not walkable", len(literal_facts))
    facts = facts + literal_facts

    model_specs = embed_cfg["models"]
    if args.embedding_models:
        requested = set(args.embedding_models.split(","))
        model_specs = [m for m in model_specs if m["name"] in requested]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    items = [{"item_id": q.id, "question_ar": q.question_ar} for q in questions]

    for spec in model_specs:
        # Three of the seven models are trained to be given a prefix and
        # score worse without one, each in its own format; the other four
        # take the bare text. Applied per model, so the fact sentences have
        # to be rebuilt inside this loop rather than once outside it.
        query_prefix = spec.get("query_prefix", "")
        document_prefix = spec.get("document_prefix", "")
        fact_sentences = [document_prefix + f.sentence for f in facts]

        logger.info("=== embedding %d facts with %s ===", len(facts), spec["name"])
        if query_prefix or document_prefix:
            logger.info("  prefixes: query %r, document %r", query_prefix, document_prefix)
        embed = load_embedder(spec["name"], spec["backend"])
        t0 = time.time()
        fact_embeddings = embed(fact_sentences) if fact_sentences else []
        logger.info("  embedded %d facts in %.1f s", len(fact_sentences), time.time() - t0)
        normalized = normalize_matrix(fact_embeddings) if fact_sentences else None
        # qwen3-embedding:8b returns 4,096 dimensions, so the raw matrix is
        # 1.4 GB and the normalised copy another 1.4. Drop the raw one
        # before the per-question loop rather than holding both.
        del fact_embeddings

        safe_name = spec["name"].replace("/", "_").replace(":", "_")
        out_dir = RESULTS_DIR / str(args.scale)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}_{args.scale}.jsonl"
        # src/common/job_runner.py resumes by item_id, which is what makes a
        # multi-hour run safe to interrupt. It also means that re-running a
        # model after changing what it embeds silently does nothing: every
        # question is already present, so the old results stay on disk.
        # --overwrite clears them first.
        if args.overwrite and out_path.exists():
            out_path.unlink()
            logger.info("  --overwrite: deleted the previous %s", out_path.name)

        def worker(item, embed=embed, normalized=normalized, query_prefix=query_prefix):
            question_embedding = embed([query_prefix + item["question_ar"]])[0]
            top = top_k_by_similarity_matrix(question_embedding, facts, normalized, k=embed_cfg["top_k"])
            return {
                "retrieved": [
                    {"sentence": f.sentence, "score": score, "head_qid": f.head_qid, "tail_qid": f.tail_qid} for f, score in top
                ]
            }

        run_job(items, worker, out_path)


if __name__ == "__main__":
    main()
