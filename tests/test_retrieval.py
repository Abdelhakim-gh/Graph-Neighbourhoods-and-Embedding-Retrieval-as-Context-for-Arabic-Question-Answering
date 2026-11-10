import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.retrieval import (  # noqa: E402
    RetrievableFact,
    build_retrievable_facts,
    cosine_similarity,
    top_k_by_similarity,
    triple_to_sentence,
)


def test_triple_to_sentence_format():
    assert triple_to_sentence("مارك توين", "مهنة", "كاتب") == "مارك توين - مهنة - كاتب"


def test_build_retrievable_facts_renders_known_heads():
    triples = [("Q7245", "P106", "Q36180", "كاتب")]
    head_labels = {"Q7245": "مارك توين"}
    relation_labels = {"P106": "مهنة"}
    facts = build_retrievable_facts(triples, head_labels, relation_labels)
    assert len(facts) == 1
    assert facts[0].sentence == "مارك توين - مهنة - كاتب"
    assert facts[0].head_qid == "Q7245"


def test_build_retrievable_facts_skips_unknown_heads():
    triples = [("Q999", "P106", "Q36180", "كاتب")]
    facts = build_retrievable_facts(triples, head_labels={}, relation_labels={"P106": "مهنة"})
    assert facts == []


def test_build_retrievable_facts_falls_back_to_raw_pid_for_unknown_relation():
    triples = [("Q7245", "P999", "Q36180", "شيء")]
    facts = build_retrievable_facts(triples, head_labels={"Q7245": "مارك توين"}, relation_labels={})
    assert "P999" in facts[0].sentence


def test_cosine_similarity_identical_vectors():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_similarity_opposite_vectors():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == -1.0


def test_cosine_similarity_zero_vector_is_zero_not_a_division_error():
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_top_k_by_similarity_ranks_closest_first():
    facts = [
        RetrievableFact(head_qid="Q1", relation_pid="P1", tail_qid="Q2", sentence="far"),
        RetrievableFact(head_qid="Q3", relation_pid="P1", tail_qid="Q4", sentence="near"),
    ]
    embeddings = [[0.0, 1.0], [1.0, 0.0]]  # "far" orthogonal to query, "near" identical
    query = [1.0, 0.0]
    ranked = top_k_by_similarity(query, facts, embeddings, k=2)
    assert ranked[0][0].sentence == "near"
    assert ranked[1][0].sentence == "far"


def test_top_k_by_similarity_respects_k():
    facts = [RetrievableFact(head_qid=f"Q{i}", relation_pid="P1", tail_qid="Q0", sentence=str(i)) for i in range(5)]
    embeddings = [[float(i), 0.0] for i in range(5)]
    ranked = top_k_by_similarity([1.0, 0.0], facts, embeddings, k=2)
    assert len(ranked) == 2


def test_top_k_by_similarity_rejects_mismatched_lengths():
    import pytest

    facts = [RetrievableFact(head_qid="Q1", relation_pid="P1", tail_qid="Q2", sentence="a")]
    with pytest.raises(ValueError):
        top_k_by_similarity([1.0], facts, [[1.0], [2.0]], k=1)
