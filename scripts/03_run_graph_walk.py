"""Graph-walk arm: from each question's questionEntity QIDs, walk the
graph scripts/01 pulled out to configs/graph_walk.yaml's max_hops, rank
the paths found, and write the top-ranked facts for
scripts/04_run_answer_generation.py to feed to the answer LLM. No model
call in this script: the walk itself is pure graph traversal
(src/qa/graph_walk.py); the LLM only enters at script 04.

Reuses load_cached_triples, build_head_labels and ensure_property_labels
from scripts/02_run_retrieval.py. scripts/ has no __init__.py, so it is
imported by inserting scripts/ onto the path.

Usage:
    python scripts/03_run_graph_walk.py --scale 100 --split test
"""

import argparse
import json
import logging
import sys
from importlib import import_module
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from src.qa.graph_walk import (  # noqa: E402
    build_adjacency,
    build_relation_frequency,
    find_paths,
    path_to_sentences,
    rank_paths_shortest_then_question_overlap,
    rank_paths_shortest_then_relation_frequency,
    reached_target,
)
from src.qa.graph_pull import drop_excluded_properties, scope_to_seeds  # noqa: E402
from src.qa.mintaka_loader import collect_qids, load_split, select_scale  # noqa: E402

run_retrieval = import_module("02_run_retrieval")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}
RESULTS_DIR = ROOT / "results" / "graph_walk"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    parser.add_argument("--top-paths", type=int, default=None, help="max ranked paths kept per question, for the answer-generation prompt; default configs/graph_walk.yaml's top_paths")
    args = parser.parse_args()

    with open(ROOT / "configs" / "graph_walk.yaml", encoding="utf-8") as f:
        walk_cfg = yaml.safe_load(f)

    # Both rankings stay callable, so the baseline ranking can be compared
    # (see configs/graph_walk.yaml's path_ranking comment).
    RANKERS = {
        "shortest_then_question_overlap": rank_paths_shortest_then_question_overlap,
        "shortest_path_then_relation_frequency": rank_paths_shortest_then_relation_frequency,
    }
    if walk_cfg["path_ranking"] not in RANKERS:
        raise NotImplementedError(
            f"config requests path_ranking={walk_cfg['path_ranking']!r}; implemented: {sorted(RANKERS)}"
        )
    ranking = walk_cfg["path_ranking"]
    top_paths = args.top_paths if args.top_paths is not None else walk_cfg["top_paths"]

    questions = load_split(DATASETS_ROOT / SPLIT_FILES[args.split])
    questions = select_scale(questions, args.scale)
    logger.info("%d questions loaded", len(questions))

    cache_path = ROOT / walk_cfg["graph_cache_dir"] / "triples.jsonl"
    all_triples = run_retrieval.load_cached_triples(cache_path)
    logger.info("%d cached triples loaded", len(all_triples))
    before = len(all_triples)
    all_triples = drop_excluded_properties(all_triples, walk_cfg.get("excluded_properties"))
    logger.info("%d Wikimedia-bookkeeping edges dropped (%d remain)", before - len(all_triples), len(all_triples))
    # Same tier scoping as scripts/02, so both arms walk and retrieve over
    # one graph rather than the retrieval corpus including every other tier
    # ever pulled.
    triples = scope_to_seeds(all_triples, collect_qids(questions), walk_cfg["max_hops"])
    logger.info("%d triples in this tier's own %d-hop graph", len(triples), walk_cfg["max_hops"])

    # Labels come from the whole cache, not the scoped subset: a QID that
    # only ever appears as a head inside this tier has no label of its own
    # here, and would render as a bare "Q1234" in an otherwise Arabic
    # prompt. Labels are not corpus content, so widening their source does
    # not widen what either arm can retrieve or walk.
    entity_labels = run_retrieval.build_head_labels(questions, all_triples)
    relation_labels = run_retrieval.ensure_property_labels(triples, run_retrieval.PROPERTY_LABELS_PATH)

    adjacency = build_adjacency(triples)
    relation_frequency = build_relation_frequency(triples)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = RESULTS_DIR / str(args.scale)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"walk_{args.scale}.jsonl"

    with open(out_path, "w", encoding="utf-8") as out_f:
        for q in questions:
            start_qids = [e.qid for e in q.question_entities]
            if not start_qids:
                out_f.write(json.dumps({"item_id": q.id, "paths": [], "reached_gold": None}, ensure_ascii=False) + "\n")
                continue

            paths = find_paths(adjacency, start_qids, max_hops=walk_cfg["max_hops"])
            # the start entities themselves (n_hops == 0) are not "found
            # facts"; only paths that actually crossed at least one edge
            # are candidates for the answer-generation context
            candidates = [p for p in paths.values() if p.n_hops > 0]
            if ranking == "shortest_then_question_overlap":
                ranked = rank_paths_shortest_then_question_overlap(
                    candidates, q.question_ar, entity_labels, relation_labels, relation_frequency
                )[:top_paths]
            else:
                ranked = rank_paths_shortest_then_relation_frequency(candidates, relation_frequency)[:top_paths]

            reached = reached_target(paths, q.answer_qids) if q.answer_qids else None
            row = {
                "item_id": q.id,
                "paths": [
                    {"target_qid": p.target_qid, "n_hops": p.n_hops, "sentences": path_to_sentences(p, entity_labels, relation_labels)}
                    for p in ranked
                ],
                "reached_gold": reached.n_hops if reached is not None else None,
            }
            out_f.write(json.dumps(row, ensure_ascii=False) + "\n")

    logger.info("wrote %s", out_path)


if __name__ == "__main__":
    main()
