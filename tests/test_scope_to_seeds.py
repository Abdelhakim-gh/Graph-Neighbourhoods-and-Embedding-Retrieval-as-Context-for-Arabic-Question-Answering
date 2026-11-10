"""Covers scope_to_seeds.

The cache is cumulative across scale tiers on purpose, so it is a union of
every question set ever pulled on a machine. Using it directly as the
retrieval corpus would make that corpus depend on run history: at scale 100
the tier's own graph was 69,704 triples inside a 437,861-triple cache.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_pull import scope_to_seeds  # noqa: E402

# Q1 -> Q2 -> Q3 -> Q4, plus an unrelated component another tier pulled.
TRIPLES = [
    ("Q1", "P1", "Q2", "b"),
    ("Q2", "P1", "Q3", "c"),
    ("Q3", "P1", "Q4", "d"),
    ("Q90", "P1", "Q91", "x"),   # different question set
    ("Q91", "P1", "Q92", "y"),
]


def test_scope_keeps_only_the_tier_reachable_edges():
    kept = scope_to_seeds(TRIPLES, {"Q1"}, max_hops=2)
    assert set(kept) == {("Q1", "P1", "Q2", "b"), ("Q2", "P1", "Q3", "c")}


def test_scope_excludes_another_tiers_component_entirely():
    kept = scope_to_seeds(TRIPLES, {"Q1"}, max_hops=3)
    heads = {t[0] for t in kept}
    assert "Q90" not in heads and "Q91" not in heads


def test_scope_respects_max_hops():
    assert len(scope_to_seeds(TRIPLES, {"Q1"}, max_hops=1)) == 1
    assert len(scope_to_seeds(TRIPLES, {"Q1"}, max_hops=2)) == 2
    assert len(scope_to_seeds(TRIPLES, {"Q1"}, max_hops=3)) == 3


def test_scope_matches_the_directed_pull_not_the_undirected_walk():
    """The pull stores outgoing edges from queried heads. Seeding at Q2
    must not pull in Q1 -> Q2, which the walk can traverse backward but the
    pull never fetched from Q2."""
    kept = scope_to_seeds(TRIPLES, {"Q2"}, max_hops=1)
    assert set(kept) == {("Q2", "P1", "Q3", "c")}


def test_scope_handles_several_seeds_without_duplicating_shared_edges():
    kept = scope_to_seeds(TRIPLES, {"Q1", "Q2"}, max_hops=2)
    assert len(kept) == len(set(kept))
    assert set(kept) == {
        ("Q1", "P1", "Q2", "b"), ("Q2", "P1", "Q3", "c"), ("Q3", "P1", "Q4", "d"),
    }


def test_scope_of_an_unknown_seed_is_empty():
    assert scope_to_seeds(TRIPLES, {"Q999"}, max_hops=3) == []
