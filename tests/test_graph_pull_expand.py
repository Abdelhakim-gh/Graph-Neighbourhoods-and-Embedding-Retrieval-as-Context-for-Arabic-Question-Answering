import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_pull import expand_neighborhood  # noqa: E402


def make_fetch_fn(edges: dict[str, list[tuple[str, str, str, str]]], failing: set[str] = frozenset()):
    """A fake fetch_fn: edges maps head QID -> the triples fetch_neighborhood
    would have returned for it. Records every batch it is called with, so a
    test can assert an already-cached QID is never re-queried. failing names
    QIDs that fetch_neighborhood would have reported as a failed batch
    (matching its (triples, failed_qids) return shape), for exercising
    expand_neighborhood's handling of that case separately from a genuine
    zero-edge result.
    """
    calls: list[list[str]] = []

    def fetch_fn(qids: list[str]) -> tuple[list[tuple[str, str, str, str]], set[str]]:
        calls.append(list(qids))
        out = []
        failed = set()
        for q in qids:
            if q in failing:
                failed.add(q)
            else:
                out.extend(edges.get(q, []))
        return out, failed

    fetch_fn.calls = calls
    return fetch_fn


def test_expand_neighborhood_reaches_exactly_max_hops():
    # Q1 -> Q2 -> Q3 -> Q4 -> Q5, a straight chain; max_hops=3 should reach
    # Q4 (3 hops from Q1) but the query volume should stop expanding beyond
    # that, i.e. Q4's own neighbors (Q5) are never queried.
    edges = {
        "Q1": [("Q1", "P1", "Q2", "b")],
        "Q2": [("Q2", "P1", "Q3", "c")],
        "Q3": [("Q3", "P1", "Q4", "d")],
        "Q4": [("Q4", "P1", "Q5", "e")],
    }
    fetch_fn = make_fetch_fn(edges)
    triples, queried = expand_neighborhood(
        fetch_fn, seed_qids={"Q1"}, already_cached=set(), cached_triples_by_head={},
        max_hops=3, max_neighbors_per_qid=50,
    )
    tails = {t[2] for t in triples}
    assert tails == {"Q2", "Q3", "Q4"}  # reached within 3 hops
    assert "Q5" not in tails  # would need a 4th hop
    assert queried == {"Q1", "Q2", "Q3"}  # Q4 discovered as a tail, never queried itself


def test_expand_neighborhood_does_not_requery_already_cached_heads():
    edges = {"Q1": [("Q1", "P1", "Q2", "b")], "Q2": [("Q2", "P1", "Q3", "c")]}
    fetch_fn = make_fetch_fn(edges)
    expand_neighborhood(
        fetch_fn, seed_qids={"Q1"}, already_cached={"Q1"},
        cached_triples_by_head={"Q1": [("Q1", "P1", "Q2", "b")]},
        max_hops=2, max_neighbors_per_qid=50,
    )
    queried_qids = {q for batch in fetch_fn.calls for q in batch}
    assert "Q1" not in queried_qids  # already cached, must not be re-queried


def test_expand_neighborhood_continues_the_frontier_through_a_cached_seed():
    """A seed that is already cached (its own edges were pulled by an
    earlier, smaller-scale run) must still let the walk reach its
    neighbors' neighbors in this run, using the cached tails to keep the
    BFS frontier going rather than stopping at the cache hit. Without
    cached_triples_by_head, hop 2 (Q3) would never be reached even though
    max_hops=2 allows it.
    """
    # Q1 (already cached, edges known) -> Q2 -> Q3, only Q2's edges need
    # a real fetch_fn call this run.
    edges = {"Q2": [("Q2", "P1", "Q3", "c")]}
    fetch_fn = make_fetch_fn(edges)
    triples, queried = expand_neighborhood(
        fetch_fn,
        seed_qids={"Q1"},
        already_cached={"Q1"},
        cached_triples_by_head={"Q1": [("Q1", "P1", "Q2", "b")]},
        max_hops=2,
        max_neighbors_per_qid=50,
    )
    tails = {t[2] for t in triples}
    assert tails == {"Q3"}  # newly fetched this run, via Q2
    assert queried == {"Q2"}  # Q1 was reused from cache, not re-queried
    queried_qids = {q for batch in fetch_fn.calls for q in batch}
    assert queried_qids == {"Q2"}


def test_expand_neighborhood_applies_cap_at_every_hop_not_just_the_first():
    edges = {
        "Q1": [("Q1", f"P{i}", f"Q1{i}", "x") for i in range(5)],
        "Q10": [("Q10", f"P{i}", f"Q10{i}", "x") for i in range(5)],
    }
    fetch_fn = make_fetch_fn(edges)
    triples, _queried = expand_neighborhood(
        fetch_fn, seed_qids={"Q1"}, already_cached=set(), cached_triples_by_head={},
        max_hops=2, max_neighbors_per_qid=2,
    )
    hop1 = [t for t in triples if t[0] == "Q1"]
    hop2 = [t for t in triples if t[0] == "Q10"]
    assert len(hop1) == 2  # capped at hop 1
    assert len(hop2) == 2  # cap still applied at hop 2, not just the first hop


def test_expand_neighborhood_stops_early_when_frontier_is_exhausted():
    edges = {"Q1": [("Q1", "P1", "Q2", "b")]}  # Q2 is a dead end
    fetch_fn = make_fetch_fn(edges)
    triples, queried = expand_neighborhood(
        fetch_fn, seed_qids={"Q1"}, already_cached=set(), cached_triples_by_head={},
        max_hops=5, max_neighbors_per_qid=50,
    )
    assert {t[2] for t in triples} == {"Q2"}
    assert queried == {"Q1", "Q2"}  # Q2 queried (came back empty), no crash on early stop


def test_expand_neighborhood_does_not_mark_a_failed_qid_as_queried():
    """A QID whose batch failed every retry must not end up in the returned
    queried set, since scripts/01_collect_qids_and_pull_graph.py writes a
    permanent "no outgoing edges" sentinel row for every
    queried-but-not-fetched head. Otherwise a failed QID would be cached as
    a false "confirmed empty" and never retried.
    """
    edges = {"Q1": [("Q1", "P1", "Q2", "b")]}
    fetch_fn = make_fetch_fn(edges, failing={"Q3"})
    triples, queried = expand_neighborhood(
        fetch_fn, seed_qids={"Q1", "Q3"}, already_cached=set(), cached_triples_by_head={},
        max_hops=1, max_neighbors_per_qid=50,
    )
    assert {t[2] for t in triples} == {"Q2"}
    assert queried == {"Q1"}  # Q3 failed and must be excluded, not treated as "queried, zero edges"


def test_stop_after_hop_halts_the_expansion_but_keeps_what_it_pulled():
    """--stop-after-hop is a measurement mode: it must stop querying, and
    it must still return the hops it did complete, so a stopped run leaves
    a smaller *finished* pull on disk rather than a discarded one.
    """
    edges = {
        "Q1": [("Q1", "P1", "Q2", "b")],
        "Q2": [("Q2", "P1", "Q3", "c")],
        "Q3": [("Q3", "P1", "Q4", "d")],
    }
    fetch_fn = make_fetch_fn(edges)
    triples, queried = expand_neighborhood(
        fetch_fn, seed_qids={"Q1"}, already_cached=set(), cached_triples_by_head={},
        max_hops=3, max_neighbors_per_qid=50, stop_after_hop=1,
    )
    assert {t[2] for t in triples} == {"Q2"}  # hop 1 kept
    assert queried == {"Q1"}  # Q2 was discovered but never queried
    assert fetch_fn.calls == [["Q1"]]


def test_stop_after_hop_beyond_max_hops_changes_nothing():
    edges = {"Q1": [("Q1", "P1", "Q2", "b")], "Q2": [("Q2", "P1", "Q3", "c")]}
    unstopped = expand_neighborhood(
        make_fetch_fn(edges), seed_qids={"Q1"}, already_cached=set(),
        cached_triples_by_head={}, max_hops=2, max_neighbors_per_qid=50,
    )
    stopped = expand_neighborhood(
        make_fetch_fn(edges), seed_qids={"Q1"}, already_cached=set(),
        cached_triples_by_head={}, max_hops=2, max_neighbors_per_qid=50, stop_after_hop=9,
    )
    assert unstopped == stopped


def test_expand_neighborhood_no_seeds_returns_nothing():
    fetch_fn = make_fetch_fn({})
    triples, queried = expand_neighborhood(
        fetch_fn, seed_qids=set(), already_cached=set(), cached_triples_by_head={},
        max_hops=3, max_neighbors_per_qid=50,
    )
    assert triples == []
    assert queried == set()
