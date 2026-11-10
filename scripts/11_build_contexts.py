"""Builds the arm contexts (walk, pooled retrieval, scoped retrieval).

Three kinds of context, each over a fact store seeded one of two ways.

  --store answered   the store used for the original three-arm runs: scoped
                     to question entities AND gold answer entities
                     (src/qa/mintaka_loader.py::collect_qids)
  --store question   scoped to question entities only, which is what a
                     system that does not know the answer could pull
                     (see scripts/10_answer_seed_check.py)

  --mode walk        the graph arm: scripts/03's walk, ranking and budget,
                     with scripts/04's order-preserving dedup
  --mode pooled      the retrieval arm: scripts/02's corpus (entity facts
                     plus date and quantity facts) for all questions at
                     once, multilingual-E5 top 150
  --mode scoped      the fourth arm: the same gold question entities as the
                     walk, and as its pool exactly the facts on the walk's
                     candidate paths (every shortest path within two hops),
                     rendered the way the walk renders them; multilingual-E5
                     top 150. No date or quantity facts, so the scoped and
                     walk pools are identical and only the choice differs.

Embeddings are cached by sentence in data/processed/e5_cache/, in chunks of
20,000 written as they finish, so an interrupted run resumes from the last
finished chunk. The output goes to
results/contexts/4000/{mode}_{store}.jsonl as one row per question:
{"item_id", "lines": [...], "pool_size"}. It is written to a temporary file
and renamed at the end, so a half-written file is never mistaken for a
finished one.

Usage:
  py -3.14 scripts/11_build_contexts.py --mode scoped --store question --limit 100
  py -3.14 scripts/11_build_contexts.py --mode scoped --store question
"""

import argparse
import json
import logging
import sys
import time
from importlib import import_module
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from src.qa.graph_pull import drop_excluded_properties, scope_to_seeds  # noqa: E402
from src.qa.graph_walk import (  # noqa: E402
    build_adjacency,
    build_relation_frequency,
    find_paths,
    path_to_sentences,
    rank_paths_shortest_then_question_overlap,
)
from src.qa.mintaka_loader import collect_qids, load_split, select_scale  # noqa: E402
from src.qa.retrieval import build_literal_facts, build_retrievable_facts  # noqa: E402

run_retrieval = import_module("02_run_retrieval")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

E5 = "intfloat/multilingual-e5-large"
CACHE_DIR = ROOT / "data" / "processed" / "e5_cache"
CHUNK = 20_000


class EmbeddingCache:
    """Sentence -> unit-norm float16 vector, persisted in chunks."""

    def __init__(self, directory: Path, embed, document_prefix: str):
        self.dir = directory
        self.dir.mkdir(parents=True, exist_ok=True)
        self.embed = embed
        self.prefix = document_prefix
        self.index: dict[str, int] = {}
        self.parts: list[np.ndarray] = []
        for meta in sorted(self.dir.glob("part_*.json")):
            vec = meta.with_suffix(".npy")
            if not vec.exists():  # chunk interrupted between the two writes
                meta.unlink()
                continue
            sentences = json.loads(meta.read_text(encoding="utf-8"))
            arr = np.load(vec)
            base = sum(len(p) for p in self.parts)
            for i, s in enumerate(sentences):
                self.index[s] = base + i
            self.parts.append(arr)
        logger.info("embedding cache: %d sentences in %d chunks", len(self.index), len(self.parts))

    def ensure(self, sentences):
        missing = [s for s in dict.fromkeys(sentences) if s not in self.index]
        logger.info("embedding %d new sentences (%d already cached)", len(missing), len(self.index))
        t0 = time.time()
        for start in range(0, len(missing), CHUNK):
            chunk = missing[start : start + CHUNK]
            vecs = np.asarray(self.embed([self.prefix + s for s in chunk]), dtype=np.float32)
            vecs /= np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-12)
            n = len(self.parts)
            np.save(self.dir / f"part_{n:04d}.npy", vecs.astype(np.float16))
            # The sentence list is written after the vectors, so its presence
            # marks a complete chunk.
            (self.dir / f"part_{n:04d}.json").write_text(json.dumps(chunk, ensure_ascii=False), encoding="utf-8")
            base = sum(len(p) for p in self.parts)
            for i, s in enumerate(chunk):
                self.index[s] = base + i
            self.parts.append(vecs.astype(np.float16))
            done = start + len(chunk)
            rate = done / max(time.time() - t0, 1e-9)
            logger.info("  embedded %d/%d (%.0f/s, about %.0f min left)", done, len(missing), rate,
                        (len(missing) - done) / rate / 60)

    def matrix(self):
        return np.vstack(self.parts) if self.parts else np.zeros((0, 1024), dtype=np.float16)


def walk_candidates(adjacency, starts, max_hops):
    paths = find_paths(adjacency, starts, max_hops=max_hops)
    return [p for p in paths.values() if p.n_hops > 0]


def dedup(lines):
    seen, out = set(), []
    for s in lines:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["walk", "pooled", "scoped"])
    ap.add_argument("--store", required=True, choices=["question", "answered"])
    ap.add_argument("--scale", default="4000")
    ap.add_argument("--limit", type=int, default=None, help="first N questions only (pilot)")
    # For the hop-count sensitivity check. The store stays the same two-hop
    # store; only the walk and the scoped pool are limited to fewer hops from
    # the question entities.
    ap.add_argument("--walk-hops", type=int, default=None,
                    help="hops the walk (and scoped pool) may take; default configs/graph_walk.yaml max_hops")
    ap.add_argument("--tag", default="", help="suffix for the output name, e.g. _h1")
    args = ap.parse_args()

    walk_cfg = yaml.safe_load(open(ROOT / "configs" / "graph_walk.yaml", encoding="utf-8"))
    embed_cfg = yaml.safe_load(open(ROOT / "configs" / "embedding_models.yaml", encoding="utf-8"))
    spec = next(m for m in embed_cfg["models"] if m["name"] == E5)
    k, top_paths, max_hops = embed_cfg["top_k"], walk_cfg["top_paths"], walk_cfg["max_hops"]
    walk_hops = args.walk_hops if args.walk_hops is not None else max_hops
    assert walk_cfg["path_ranking"] == "shortest_then_question_overlap"

    questions = select_scale(load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json"), args.scale)
    run_questions = questions[: args.limit] if args.limit else questions
    logger.info("%d questions in the tier, %d in this run", len(questions), len(run_questions))

    cache = ROOT / walk_cfg["graph_cache_dir"] / "triples.jsonl"
    all_triples = drop_excluded_properties(run_retrieval.load_cached_triples(cache), walk_cfg.get("excluded_properties"))
    seeds = collect_qids(questions) if args.store == "answered" else {e.qid for q in questions for e in q.question_entities}
    store = scope_to_seeds(all_triples, seeds, max_hops)
    logger.info("store '%s': %d seeds, %d triples", args.store, len(seeds), len(store))
    entity_labels = run_retrieval.build_head_labels(questions, all_triples)

    out_dir = ROOT / "results" / "contexts" / str(args.scale)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = args.tag + (f"_limit{args.limit}" if args.limit else "")
    out_path = out_dir / f"{args.mode}_{args.store}{suffix}.jsonl"
    rows = []

    if args.mode == "pooled":
        literals = run_retrieval.load_cached_literals(cache.parent / "literals.jsonl", {t[0] for t in store})
        relation_labels = run_retrieval.ensure_property_labels(
            store + [(h, r, "", "") for h, r, _v in literals], run_retrieval.PROPERTY_LABELS_PATH)
        facts = build_retrievable_facts(store, entity_labels, relation_labels)
        facts += build_literal_facts(literals, entity_labels, relation_labels)
        logger.info("pooled corpus: %d facts", len(facts))
    else:
        relation_labels = run_retrieval.ensure_property_labels(store, run_retrieval.PROPERTY_LABELS_PATH)
        adjacency = build_adjacency(store)

    if args.mode == "walk":
        relation_frequency = build_relation_frequency(store)
        for q in run_questions:
            starts = [e.qid for e in q.question_entities]
            cands = walk_candidates(adjacency, starts, walk_hops) if starts else []
            ranked = rank_paths_shortest_then_question_overlap(
                cands, q.question_ar, entity_labels, relation_labels, relation_frequency)[:top_paths]
            lines = dedup(s for p in ranked for s in path_to_sentences(p, entity_labels, relation_labels))
            rows.append({"item_id": q.id, "lines": lines, "pool_size": len(cands)})
    else:
        embed = run_retrieval.load_embedder(spec["name"], spec["backend"])
        ecache = EmbeddingCache(CACHE_DIR, embed, spec.get("document_prefix", ""))
        pools = {}
        if args.mode == "pooled":
            # Distinct sentences only, so the arm hands over 150 distinct lines
            # like the scoped arm. Ranking one entry per triple (as scripts/02
            # does) can return two triples that render to the same sentence,
            # which gives a mean of 148.5 distinct lines.
            corpus = list(dict.fromkeys(f.sentence for f in facts))
            logger.info("pooled corpus: %d distinct sentences", len(corpus))
            ecache.ensure(corpus)
        else:
            # Pools are stored as int32 ids into one shared sentence table.
            # Held as per-question lists of strings they would need about 11 GB
            # at 4,000 questions (about 15,000 lines each).
            sentence_id: dict[str, int] = {}
            sentences: list[str] = []

            def sid(s):
                i = sentence_id.get(s)
                if i is None:
                    i = sentence_id[s] = len(sentences)
                    sentences.append(s)
                return i

            # Check 1: every line the walk would show must be in the scoped
            # pool. True by construction (same candidates, same
            # renderer); asserted so a later edit cannot break it silently.
            relation_frequency = build_relation_frequency(store)
            walk_lines_total = 0
            for qn, q in enumerate(run_questions, 1):
                starts = [e.qid for e in q.question_entities]
                cands = walk_candidates(adjacency, starts, walk_hops) if starts else []
                ids = list(dict.fromkeys(sid(s) for p in cands for s in path_to_sentences(p, entity_labels, relation_labels)))
                pools[q.id] = np.asarray(ids, dtype=np.int32)
                ranked = rank_paths_shortest_then_question_overlap(
                    cands, q.question_ar, entity_labels, relation_labels, relation_frequency)[:top_paths]
                walk_ids = {sentence_id.get(s, -1) for p in ranked for s in path_to_sentences(p, entity_labels, relation_labels)}
                missing = walk_ids - set(ids)
                if missing:
                    raise SystemExit(f"check 1 failed for {q.id}: {len(missing)} walk lines not in the pool")
                walk_lines_total += len(walk_ids)
                if qn % 500 == 0:
                    logger.info("  pools built for %d/%d questions (%d distinct sentences so far)",
                                qn, len(run_questions), len(sentences))
            logger.info("check 1 passed: all %d walk lines are in their question's scoped pool", walk_lines_total)
            if args.store == "answered" and walk_hops == max_hops:
                # The archived graph arm (results/graph_walk/4000/walk_4000.jsonl)
                # was built before scope_to_seeds was made deterministic, so its
                # lines can differ slightly from today's walk. Measure how many
                # fall inside today's pools, since the scoped arm is compared with
                # those archived runs.
                inside = total = 0
                for line in open(ROOT / "results" / "graph_walk" / str(args.scale) / f"walk_{args.scale}.jsonl",
                                 encoding="utf-8"):
                    row = json.loads(line)
                    if row["item_id"] not in pools:
                        continue
                    pool_set = set(pools[row["item_id"]].tolist())
                    lines = dedup(s for p in row.get("paths", []) for s in p["sentences"])
                    total += len(lines)
                    inside += sum(1 for s in lines if sentence_id.get(s, -1) in pool_set)
                logger.info("archived walk lines inside today's pools: %d of %d (%.2f%%)",
                            inside, total, 100 * inside / max(total, 1))
            sizes = sorted(len(v) for v in pools.values())
            logger.info("scoped pools: median %d lines, min %d, under %d: %d of %d; %d distinct sentences overall",
                        sizes[len(sizes) // 2], sizes[0], k, sum(1 for s in sizes if s < k), len(sizes), len(sentences))
            ecache.ensure(sentences)
        matrix = ecache.matrix()
        q_vecs = np.asarray(embed([spec.get("query_prefix", "") + q.question_ar for q in run_questions]),
                            dtype=np.float32)
        q_vecs /= np.maximum(np.linalg.norm(q_vecs, axis=1, keepdims=True), 1e-12)
        if args.mode == "pooled":
            corpus_idx = np.array([ecache.index[s] for s in corpus])
            corpus_mat = matrix[corpus_idx].astype(np.float32)
        else:
            cache_row = np.array([ecache.index[s] for s in sentences], dtype=np.int64)
        for qi, q in enumerate(run_questions):
            if args.mode == "pooled":
                mat = corpus_mat
                text_of = corpus.__getitem__
                n_cand = len(corpus)
            else:
                pool = pools[q.id]
                if len(pool) == 0:
                    rows.append({"item_id": q.id, "lines": [], "pool_size": 0})
                    continue
                mat = matrix[cache_row[pool]].astype(np.float32)
                text_of = lambda j, pool=pool: sentences[pool[j]]  # noqa: E731
                n_cand = len(pool)
            scores = mat @ q_vecs[qi]
            kk = min(k, n_cand)
            top = np.argpartition(-scores, kk - 1)[:kk] if kk < n_cand else np.arange(n_cand)
            top = top[np.argsort(-scores[top])]
            rows.append({"item_id": q.id, "lines": [text_of(int(i)) for i in top], "pool_size": n_cand,
                         "scores": [round(float(scores[i]), 5) for i in top]})

    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(out_path)
    lens = sorted(len(r["lines"]) for r in rows)
    logger.info("wrote %s: %d questions, context lines median %d, empty %d",
                out_path.relative_to(ROOT), len(rows), lens[len(lens) // 2], sum(1 for x in lens if x == 0))


if __name__ == "__main__":
    main()
