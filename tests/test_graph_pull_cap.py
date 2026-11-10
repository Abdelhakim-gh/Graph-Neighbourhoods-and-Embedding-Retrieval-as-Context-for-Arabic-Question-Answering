import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_pull import cap_triples_per_head  # noqa: E402


def test_cap_triples_per_head_keeps_at_most_n_per_head():
    triples = [("Q1", f"P{i}", f"Q{i}", "label") for i in range(10)]
    capped = cap_triples_per_head(triples, max_per_head=3)
    assert len(capped) == 3


def test_cap_triples_per_head_keeps_first_seen_order():
    triples = [("Q1", "P1", "Q2", "a"), ("Q1", "P2", "Q3", "b"), ("Q1", "P3", "Q4", "c")]
    capped = cap_triples_per_head(triples, max_per_head=2)
    assert capped == [("Q1", "P1", "Q2", "a"), ("Q1", "P2", "Q3", "b")]


def test_cap_triples_per_head_applies_independently_per_head():
    triples = [
        ("Q1", "P1", "Q2", "a"),
        ("Q1", "P2", "Q3", "b"),
        ("Q9", "P1", "Q10", "c"),
    ]
    capped = cap_triples_per_head(triples, max_per_head=1)
    assert capped == [("Q1", "P1", "Q2", "a"), ("Q9", "P1", "Q10", "c")]


def test_cap_triples_per_head_below_cap_is_unaffected():
    triples = [("Q1", "P1", "Q2", "a")]
    assert cap_triples_per_head(triples, max_per_head=5) == triples


def test_cap_triples_per_head_empty_input():
    assert cap_triples_per_head([], max_per_head=5) == []
