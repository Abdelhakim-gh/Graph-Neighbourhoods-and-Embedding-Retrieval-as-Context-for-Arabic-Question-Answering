"""Does the fact store contain facts that were pulled because of the answer?

`src/qa/mintaka_loader.py::collect_qids` returns question entities AND gold
answer entities, and scripts/01-03 all scope the fact store with it. The store
therefore holds the outgoing statements of every gold answer entity (and of
its one-hop neighbours). The walk is undirected (`build_adjacency`), so from a
question entity it can step backwards along an answer entity's own statement:
"John Adams - position held - President of the United States" is reachable
from the president entity only because John Adams was a seed.

A deployed system does not know the answer, so it could only pull around the
question entities. This script measures how much each arm's coverage depends
on the answer-seeded part of the store.

1. Builds the store two ways from the same cache: seeded by question and
   answer entities (as used), and seeded by question entities only.
2. Re-runs the graph walk on both stores with the configured ranking and
   budget, after checking that the as-used store reproduces
   results/graph_walk/4000/walk_4000.jsonl.
3. Coverage (normalised Arabic gold label in the context) on the entity
   questions with an Arabic gold label, for the walk on each store.
4. For the existing retrieval contexts: how many coverage hits survive if
   lines from outside the question-only store are removed. This is a lower
   bound on question-only retrieval coverage, since a re-run would put other
   lines in their place.

Run: py -3.14 scripts/10_answer_seed_check.py
"""

import json
import sys
from importlib import import_module
from pathlib import Path

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
from src.qa.mintaka_loader import collect_qids, load_split  # noqa: E402
from src.qa.qa_scorer import normalize_arabic  # noqa: E402

run_retrieval = import_module("02_run_retrieval")


def walk_contexts(questions, triples, entity_labels, relation_labels, top_paths, max_hops):
    adjacency = build_adjacency(triples)
    relation_frequency = build_relation_frequency(triples)
    out = {}
    for q in questions:
        starts = [e.qid for e in q.question_entities]
        if not starts:
            out[q.id] = []
            continue
        paths = find_paths(adjacency, starts, max_hops=max_hops)
        candidates = [p for p in paths.values() if p.n_hops > 0]
        ranked = rank_paths_shortest_then_question_overlap(
            candidates, q.question_ar, entity_labels, relation_labels, relation_frequency)[:top_paths]
        seen, lines = set(), []
        for p in ranked:
            for s in path_to_sentences(p, entity_labels, relation_labels):
                if s not in seen:
                    seen.add(s)
                    lines.append(s)
        out[q.id] = lines
    return out


def covered(lines, q):
    ctx = normalize_arabic("\n".join(lines))
    return any(l and normalize_arabic(l) in ctx for l in q.answer_labels_ar if l)


def main():
    walk_cfg = yaml.safe_load(open(ROOT / "configs" / "graph_walk.yaml", encoding="utf-8"))
    assert walk_cfg["path_ranking"] == "shortest_then_question_overlap"
    questions = load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")
    print(f"questions: {len(questions)}")

    cache = ROOT / walk_cfg["graph_cache_dir"] / "triples.jsonl"
    all_triples = drop_excluded_properties(run_retrieval.load_cached_triples(cache),
                                           walk_cfg.get("excluded_properties"))
    seeds_full = collect_qids(questions)
    seeds_q = {e.qid for q in questions for e in q.question_entities}
    store_full = scope_to_seeds(all_triples, seeds_full, walk_cfg["max_hops"])
    store_q = scope_to_seeds(all_triples, seeds_q, walk_cfg["max_hops"])
    print(f"seeds: question+answer {len(seeds_full)}, question only {len(seeds_q)}")
    print(f"store: as used {len(store_full)} triples, question-seeded only {len(store_q)} "
          f"({100 * len(store_q) / len(store_full):.1f}%)")

    entity_labels = run_retrieval.build_head_labels(questions, all_triples)
    relation_labels = run_retrieval.ensure_property_labels(store_full, run_retrieval.PROPERTY_LABELS_PATH)
    top, hops = walk_cfg["top_paths"], walk_cfg["max_hops"]

    walk_full = walk_contexts(questions, store_full, entity_labels, relation_labels, top, hops)
    # Reproduction check against the file the paper's runs used.
    existing = {}
    for line in open(ROOT / "results" / "graph_walk" / "4000" / "walk_4000.jsonl", encoding="utf-8"):
        row = json.loads(line)
        seen, lines = set(), []
        for p in row.get("paths", []):
            for s in p["sentences"]:
                if s not in seen:
                    seen.add(s)
                    lines.append(s)
        existing[row["item_id"]] = lines
    same = sum(1 for q in questions if walk_full[q.id] == existing.get(q.id))
    print(f"reproduction: recomputed walk equals walk_4000.jsonl for {same} of {len(questions)} questions")

    walk_q = walk_contexts(questions, store_q, entity_labels, relation_labels, top, hops)

    ent = [q for q in questions if q.answer_type == "entity" and any(q.answer_labels_ar)]
    cov_full = sum(covered(existing[q.id], q) for q in ent)
    cov_rec = sum(covered(walk_full[q.id], q) for q in ent)
    cov_q = sum(covered(walk_q[q.id], q) for q in ent)
    print(f"\nGRAPH ARM coverage on {len(ent)} entity questions")
    print(f"   as run (walk_4000.jsonl):     {cov_full:5d}  {100 * cov_full / len(ent):5.1f}%")
    print(f"   recomputed, as-used store:     {cov_rec:5d}  {100 * cov_rec / len(ent):5.1f}%")
    print(f"   recomputed, question-only:     {cov_q:5d}  {100 * cov_q / len(ent):5.1f}%")
    lens = sorted(len(walk_q[q.id]) for q in questions)
    print(f"   question-only context lines: median {lens[len(lens) // 2]}, "
          f"empty {sum(1 for x in lens if x == 0)}, under 150: {sum(1 for x in lens if x < 150)}")

    # Retrieval: which gold-hit lines come from outside the question-only store?
    pairs_q = {(h, t) for h, _r, t, _l in store_q}
    heads_q = {h for h, _r, _t, _l in store_q}
    retr = {}
    for line in open(ROOT / "results" / "retrieval" / "4000" / "intfloat_multilingual-e5-large_4000.jsonl",
                     encoding="utf-8"):
        row = json.loads(line)
        retr[row["item_id"]] = row.get("retrieved", [])
    hit = survive = 0
    for q in ent:
        gold = [normalize_arabic(l) for l in q.answer_labels_ar if l]
        rows = [r for r in retr[q.id] if any(g in normalize_arabic(r["sentence"]) for g in gold)]
        if not rows:
            continue
        hit += 1
        keep = [r for r in rows if (r.get("tail_qid") and (r["head_qid"], r["tail_qid"]) in pairs_q)
                or (not r.get("tail_qid") and r["head_qid"] in heads_q)]
        survive += bool(keep)
    print(f"\nRETRIEVAL ARM, existing contexts, {len(ent)} entity questions")
    print(f"   coverage as run:                         {hit:5d}  {100 * hit / len(ent):5.1f}%")
    print(f"   hits whose gold line is question-seeded: {survive:5d}  {100 * survive / len(ent):5.1f}%"
          f"  (lower bound for a question-only store)")

    out = ROOT / "results" / "graph_walk" / "4000" / "walk_4000_question_seeded.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps({"item_id": q.id, "lines": walk_q[q.id]}, ensure_ascii=False) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
