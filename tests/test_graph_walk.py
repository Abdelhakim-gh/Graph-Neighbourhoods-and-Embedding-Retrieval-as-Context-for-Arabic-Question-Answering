import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_walk import (  # noqa: E402
    build_adjacency,
    build_relation_frequency,
    find_paths,
    path_to_sentences,
    rank_paths_shortest_then_relation_frequency,
    reached_target,
)

# Q1 --P57(directed)--> Q2 --P161(cast member)--> Q3
# i.e. Q1 is a film directed by Q2, who also directed Q4; Q3 acted in Q1.
INCEPTION_LIKE_TRIPLES = [
    ("Q1", "P57", "Q2", "Nolan"),          # Q1 (film) directed by Q2 (person)
    ("Q2", "P57_inv", "Q4", "OtherFilm"),  # Q2 also directed Q4
    ("Q1", "P161", "Q3", "Actor"),         # Q1 has cast member Q3
]


def test_build_adjacency_is_bidirectional():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    out_from_q1 = {e.other_qid for e in adjacency["Q1"]}
    assert "Q2" in out_from_q1 and "Q3" in out_from_q1
    in_to_q2 = {e.other_qid for e in adjacency["Q2"]}
    assert "Q1" in in_to_q2  # walkable backward too


def test_find_paths_reaches_direct_neighbor_at_one_hop():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    assert paths["Q2"].n_hops == 1
    assert paths["Q2"].edges[0].relation_pid == "P57"


def test_find_paths_reaches_a_two_hop_neighbor():
    # Q4 is only reachable from Q1 by going Q1 -> Q2 -> Q4
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    assert paths["Q4"].n_hops == 2
    assert [e.relation_pid for e in paths["Q4"].edges] == ["P57", "P57_inv"]


def test_find_paths_respects_max_hops_bound():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    assert "Q2" in paths  # 1 hop, within bound
    assert "Q4" not in paths  # 2 hops, outside a max_hops=1 bound


def test_find_paths_multi_source_finds_the_shortest_path_across_starts():
    # Starting from both Q1 and Q4: Q1->Q2 is 1 hop, Q4->Q2 is also 1 hop,
    # so Q2 should be reached at 1 hop regardless of which start finds it.
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1", "Q4"], max_hops=3)
    assert paths["Q2"].n_hops == 1


def test_find_paths_start_qid_itself_has_zero_hops():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    assert paths["Q1"].n_hops == 0
    assert paths["Q1"].edges == ()


def test_find_paths_unreachable_qid_is_absent():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    assert "Q999" not in paths


def test_build_relation_frequency_counts_relation_occurrences():
    freq = build_relation_frequency(INCEPTION_LIKE_TRIPLES)
    assert freq["P57"] == 1
    assert freq["P161"] == 1


def test_rank_paths_prefers_fewer_hops():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    freq = build_relation_frequency(INCEPTION_LIKE_TRIPLES)
    ranked = rank_paths_shortest_then_relation_frequency([paths["Q4"], paths["Q2"]], freq)
    assert ranked[0].target_qid == "Q2"  # 1 hop beats 2 hops regardless of frequency


def test_rank_paths_breaks_ties_by_relation_frequency():
    triples = [
        ("Q1", "COMMON", "Q2", "a"),
        ("Q1", "RARE", "Q3", "b"),
        ("Q9", "COMMON", "Q10", "c"),  # makes COMMON appear twice, RARE once
    ]
    adjacency = build_adjacency(triples)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    freq = build_relation_frequency(triples)
    ranked = rank_paths_shortest_then_relation_frequency([paths["Q3"], paths["Q2"]], freq)
    assert ranked[0].target_qid == "Q2"  # both 1 hop; COMMON (freq 2) ranks above RARE (freq 1)


def test_reached_target_returns_the_shortest_matching_path():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    result = reached_target(paths, ("Q4", "Q2"))
    assert result.target_qid == "Q2"  # 1 hop beats Q4's 2 hops


def test_reached_target_returns_none_when_nothing_reached():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=1)
    assert reached_target(paths, ("Q999",)) is None


def test_path_to_sentences_one_hop_out_direction():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    labels = {"Q1": "إنسبشن", "Q2": "نولان"}
    relations = {"P57": "أخرج"}
    assert path_to_sentences(paths["Q2"], labels, relations) == ["إنسبشن - أخرج - نولان"]


def test_path_to_sentences_two_hops_tracks_position_correctly():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    labels = {"Q1": "إنسبشن", "Q2": "نولان", "Q4": "فيلم آخر"}
    relations = {"P57": "أخرج", "P57_inv": "أخرج أيضا"}
    sentences = path_to_sentences(paths["Q4"], labels, relations)
    assert sentences == ["إنسبشن - أخرج - نولان", "نولان - أخرج أيضا - فيلم آخر"]


def test_path_to_sentences_missing_label_falls_back_to_qid():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    sentences = path_to_sentences(paths["Q2"], entity_labels={}, relation_labels={})
    assert sentences == ["Q1 - P57 - Q2"]


def test_path_to_sentences_zero_hop_path_is_empty():
    adjacency = build_adjacency(INCEPTION_LIKE_TRIPLES)
    paths = find_paths(adjacency, ["Q1"], max_hops=3)
    assert path_to_sentences(paths["Q1"], {}, {}) == []
