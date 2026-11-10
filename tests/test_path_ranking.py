"""Covers rank_paths_shortest_then_question_overlap, and the baseline
shortest-then-relation-frequency ranking it is compared with.

Preferring the *most frequent* relation in the corpus means preferring P31
(instance of) and P106 (occupation), which took 63% of the top-5 slots on
the real pull and almost never lead to the answer.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_walk import (  # noqa: E402
    build_adjacency,
    build_relation_frequency,
    find_paths,
    rank_paths_shortest_then_question_overlap,
    rank_paths_shortest_then_relation_frequency,
)

# Drake and The Weeknd, the shape of the real "who is older" failure: the
# hub relations (instance of, occupation) are far more frequent in the
# corpus than the one relation the question is about.
TRIPLES = [
    ("Q1", "P31", "Q5", "إنسان"),           # The Weeknd, instance of, human
    ("Q1", "P106", "Q177", "مغنٍّ"),          # The Weeknd, occupation, singer
    ("Q1", "P106", "Q178", "ممثل"),          # The Weeknd, occupation, actor
    ("Q1", "P800", "Q99", "أغنية مشهورة"),   # The Weeknd, notable work, a song
] + [
    # bulk, so P31/P106 dominate the corpus frequency the way they really do
    (f"Q{i}", "P31", "Q5", "إنسان") for i in range(100, 160)
] + [
    (f"Q{i}", "P106", "Q177", "مغنٍّ") for i in range(200, 250)
]

ENTITY_LABELS = {
    "Q5": "إنسان", "Q177": "مغنٍّ", "Q178": "ممثل", "Q99": "أغنية مشهورة", "Q1": "ذا ويكند",
}
RELATION_LABELS = {
    "P31": "نموذج من", "P106": "المهنة", "P800": "عمل بارز",
}


def ranked_targets(ranker):
    adjacency = build_adjacency(TRIPLES)
    freq = build_relation_frequency(TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    return [p.target_qid for p in ranker(candidates, freq)]


def test_the_replaced_ranking_puts_the_hub_relations_first():
    """Not a test of desired behaviour: shows why the baseline is not used."""
    order = ranked_targets(rank_paths_shortest_then_relation_frequency)
    assert order[0] in {"Q5", "Q177", "Q178"}   # instance-of / occupation
    assert order[-1] == "Q99"                    # the notable work, ranked last


def test_question_overlap_promotes_the_path_the_question_is_about():
    adjacency = build_adjacency(TRIPLES)
    freq = build_relation_frequency(TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    ranked = rank_paths_shortest_then_question_overlap(
        candidates, "ما هي أشهر أغنية مشهورة لذا ويكند؟", ENTITY_LABELS, RELATION_LABELS, freq
    )
    assert ranked[0].target_qid == "Q99"  # the question names it; the baseline ranks it last


def test_shorter_paths_still_outrank_longer_ones_regardless_of_overlap():
    """Hop count stays the primary key: a 2-hop path that happens to share a
    word with the question must not jump ahead of a 1-hop path."""
    triples = [("Q1", "P800", "Q2", "شيء"), ("Q2", "P800", "Q3", "أغنية مشهورة")]
    adjacency = build_adjacency(triples)
    paths = find_paths(adjacency, ["Q1"], max_hops=2)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    ranked = rank_paths_shortest_then_question_overlap(
        candidates, "أغنية مشهورة", {"Q2": "شيء", "Q3": "أغنية مشهورة"}, {"P800": "عمل بارز"}
    )
    assert ranked[0].n_hops == 1
    assert ranked[0].target_qid == "Q2"


def test_short_arabic_particles_do_not_count_as_overlap():
    """من/في/ما match nearly every label and would make the overlap term
    noise if they counted."""
    triples = [("Q1", "P1", "Q2", "من"), ("Q1", "P1", "Q3", "أغنية")]
    adjacency = build_adjacency(triples)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    ranked = rank_paths_shortest_then_question_overlap(
        candidates, "من هي أغنية", {"Q2": "من", "Q3": "أغنية"}, {"P1": "علاقة"}
    )
    assert ranked[0].target_qid == "Q3"  # matched on أغنية, not on من


def test_ranking_without_relation_frequency_still_works():
    adjacency = build_adjacency(TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    ranked = rank_paths_shortest_then_question_overlap(
        candidates, "أغنية مشهورة", ENTITY_LABELS, RELATION_LABELS, relation_frequency=None
    )
    assert ranked[0].target_qid == "Q99"
    assert len(ranked) == len(candidates)


def test_ranking_is_stable_when_nothing_overlaps():
    adjacency = build_adjacency(TRIPLES)
    freq = build_relation_frequency(TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    candidates = [p for p in paths.values() if p.n_hops > 0]
    ranked = rank_paths_shortest_then_question_overlap(
        candidates, "سؤال لا يشبه أي تسمية", ENTITY_LABELS, RELATION_LABELS, freq
    )
    # with zero overlap everywhere, the rarest relation wins the tiebreak
    assert ranked[0].target_qid == "Q99"  # P800 occurs once; P31/P106 in bulk
    assert isinstance(freq, Counter)
