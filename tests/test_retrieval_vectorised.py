"""The vectorised ranking has to agree with the pure-Python one, since the
pure-Python one is what the rest of the suite pins the ranking semantics to.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.retrieval import (  # noqa: E402
    RetrievableFact,
    normalize_matrix,
    top_k_by_similarity,
    top_k_by_similarity_matrix,
)


def make_facts(n):
    return [RetrievableFact(f"Q{i}", "P1", f"Q{i+1}", f"fact {i}") for i in range(n)]


def test_vectorised_matches_pure_python_ordering_and_scores():
    rng = random.Random(0)
    facts = make_facts(200)
    embeddings = [[rng.uniform(-1, 1) for _ in range(48)] for _ in facts]
    query = [rng.uniform(-1, 1) for _ in range(48)]

    slow = top_k_by_similarity(query, facts, embeddings, k=10)
    fast = top_k_by_similarity_matrix(query, facts, normalize_matrix(embeddings), k=10)

    assert [f.head_qid for f, _ in slow] == [f.head_qid for f, _ in fast]
    for (_, a), (_, b) in zip(slow, fast):
        assert abs(a - b) < 1e-5


def test_k_larger_than_the_corpus_returns_everything():
    facts = make_facts(3)
    embeddings = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    out = top_k_by_similarity_matrix([1.0, 0.0], facts, normalize_matrix(embeddings), k=99)
    assert len(out) == 3


def test_zero_vectors_score_zero_rather_than_nan():
    facts = make_facts(2)
    out = top_k_by_similarity_matrix([1.0, 0.0], facts, normalize_matrix([[0.0, 0.0], [1.0, 0.0]]), k=2)
    scores = {f.head_qid: s for f, s in out}
    assert scores["Q0"] == 0.0
    assert abs(scores["Q1"] - 1.0) < 1e-6


def test_zero_query_does_not_divide_by_zero():
    facts = make_facts(3)
    out = top_k_by_similarity_matrix([0.0, 0.0], facts, normalize_matrix([[1.0, 0.0]] * 3), k=2)
    assert len(out) == 2
    assert all(s == 0.0 for _, s in out)


def test_ranking_is_descending_by_score():
    rng = random.Random(7)
    facts = make_facts(50)
    embeddings = [[rng.uniform(-1, 1) for _ in range(16)] for _ in facts]
    out = top_k_by_similarity_matrix([rng.uniform(-1, 1) for _ in range(16)],
                                     facts, normalize_matrix(embeddings), k=20)
    scores = [s for _, s in out]
    assert scores == sorted(scores, reverse=True)
