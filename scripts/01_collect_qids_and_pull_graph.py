"""Collects the QID set needed for one scale tier of Mintaka questions
(questionEntity + gold answer QIDs) and pulls a neighborhood around them via
SPARQL, expanded iteratively out to configs/graph_walk.yaml's max_hops so
the graph-walk arm (scripts/03) has more than the seeds' immediate neighbors
to walk. A per-head cap (max_neighbors_per_qid) keeps the expansion
tractable.

Caches pulled triples under configs/graph_walk.yaml's graph_cache_dir,
keyed by head QID, so a later run for a larger scale tier only pulls the
newly-needed QIDs rather than re-pulling everything already cached.

--max-hops and --stop-after-hop exist to measure the fan-out before paying
for it. The BFS frontier grows by a factor the config cannot predict.
--stop-after-hop N runs the expansion normally but halts after hop N and
reports the frontier it would have queried next, so the next hop's real
cost is known before it starts.

Usage:
    python scripts/01_collect_qids_and_pull_graph.py --scale 100 --split test
    python scripts/01_collect_qids_and_pull_graph.py --scale 100 --stop-after-hop 1
    python scripts/01_collect_qids_and_pull_graph.py --scale 1000 --max-hops 2
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))

from src.qa.graph_pull import (  # noqa: E402
    _client,
    expand_neighborhood,
    fetch_literals,
    fetch_neighborhood,
    scope_to_seeds,
)
from src.qa.mintaka_loader import collect_qids, load_split, select_scale  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Study4-AICSET-research/1.0 (academic research script)"
SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}


def load_cached_heads(cache_path: Path) -> set[str]:
    """Which head QIDs already have a pulled (possibly empty) neighborhood
    cached, so a re-run only pulls the newly-needed ones."""
    if not cache_path.exists():
        return set()
    heads = set()
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            heads.add(json.loads(line)["head"])
    return heads


def load_cached_triples_by_head(cache_path: Path) -> dict[str, list[tuple[str, str, str, str]]]:
    """Every already-pulled triple, grouped by head QID. Passed to
    src/qa/graph_pull.py::expand_neighborhood so it can keep expanding the
    BFS frontier through a node that is already cached (and therefore
    skipped from a fresh SPARQL query) instead of dropping its known
    neighbors from this run's walk; see that function's docstring.
    """
    by_head: dict[str, list[tuple[str, str, str, str]]] = {}
    if not cache_path.exists():
        return by_head
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["relation"] is None:  # the "no outgoing edges" sentinel row
                continue
            by_head.setdefault(row["head"], []).append((row["head"], row["relation"], row["tail"], row["tail_label"]))
    return by_head


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    parser.add_argument(
        "--max-hops", type=int, default=None,
        help="override configs/graph_walk.yaml's max_hops for this run",
    )
    parser.add_argument(
        "--stop-after-hop", type=int, default=None,
        help="halt after this hop and report the frontier the next hop would query, "
             "without querying it. Keeps everything pulled so far.",
    )
    parser.add_argument(
        "--skip-literals", action="store_true",
        help="skip the date/quantity pull, e.g. when only measuring the entity fan-out",
    )
    args = parser.parse_args()

    with open(ROOT / "configs" / "graph_walk.yaml", encoding="utf-8") as f:
        walk_cfg = yaml.safe_load(f)

    max_hops = args.max_hops if args.max_hops is not None else walk_cfg["max_hops"]
    if args.max_hops is not None:
        logger.info("max_hops overridden on the command line: %d (config says %d)", max_hops, walk_cfg["max_hops"])

    split_path = DATASETS_ROOT / SPLIT_FILES[args.split]
    questions = load_split(split_path)
    questions = select_scale(questions, args.scale)
    logger.info("%s split, scale %s: %d questions loaded", args.split, args.scale, len(questions))

    seed_qids = collect_qids(questions)
    logger.info("%d distinct QIDs referenced (questionEntity + gold answers)", len(seed_qids))

    cache_dir = ROOT / walk_cfg["graph_cache_dir"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "triples.jsonl"

    already_cached = load_cached_heads(cache_path)
    cached_triples_by_head = load_cached_triples_by_head(cache_path)
    logger.info("%d heads already cached", len(already_cached))

    sparql = _client(SPARQL_ENDPOINT, USER_AGENT)

    def fetch_fn(qids: list[str]) -> tuple[list[tuple[str, str, str, str]], set[str]]:
        return fetch_neighborhood(sparql, qids)

    new_triples, queried_heads = expand_neighborhood(
        fetch_fn, seed_qids, already_cached, cached_triples_by_head,
        max_hops, walk_cfg["max_neighbors_per_qid"],
        stop_after_hop=args.stop_after_hop,
    )
    logger.info("expansion done: %d new triples across %d newly-queried heads", len(new_triples), len(queried_heads))

    with open(cache_path, "a", encoding="utf-8") as f:
        for head, rel, tail, label in new_triples:
            f.write(json.dumps({"head": head, "relation": rel, "tail": tail, "tail_label": label}, ensure_ascii=False) + "\n")
        # A queried head with zero outgoing entity-valued edges still
        # counts as "done", so it is not re-queried on the next run.
        fetched_heads = {t[0] for t in new_triples}
        for qid in queried_heads - fetched_heads:
            f.write(json.dumps({"head": qid, "relation": None, "tail": None, "tail_label": None}, ensure_ascii=False) + "\n")

    logger.info("wrote %s", cache_path)

    if args.skip_literals:
        logger.info("--skip-literals given; not pulling dates and quantities")
        return

    # Literal-valued claims, cached separately from triples.jsonl: keeping
    # them out of the file scripts/03 builds its adjacency from guarantees
    # they stay retrievable but not walkable.
    literals_path = cache_dir / "literals.jsonl"
    already_have = load_cached_heads(literals_path)
    all_triples = [
        (row["head"], row["relation"], row["tail"], row["tail_label"])
        for row in (json.loads(line) for line in open(cache_path, encoding="utf-8"))
        if row["relation"] is not None
    ]
    tier_heads = {t[0] for t in scope_to_seeds(all_triples, seed_qids, max_hops)} | seed_qids
    need_literals = sorted(tier_heads - already_have)
    logger.info(
        "literals: %d heads in this tier's graph, %d already pulled, %d to fetch",
        len(tier_heads), len(tier_heads & already_have), len(need_literals),
    )

    if need_literals:
        literals, failed = fetch_literals(sparql, need_literals)
        if failed:
            logger.warning("%d QIDs failed the literal pull and stay eligible for retry", len(failed))
        with open(literals_path, "a", encoding="utf-8") as f:
            for head, rel, value in literals:
                f.write(json.dumps({"head": head, "relation": rel, "value": value}, ensure_ascii=False) + "\n")
            for qid in set(need_literals) - failed - {lit[0] for lit in literals}:
                f.write(json.dumps({"head": qid, "relation": None, "value": None}, ensure_ascii=False) + "\n")
        logger.info("wrote %d literal facts to %s", len(literals), literals_path)


if __name__ == "__main__":
    main()
