"""Covers stratified sampling. On Mintaka's grouped file, questions[:N]
returns 92% one category and a single multihop question, so per-category and
per-complexity results could not be computed from it.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.mintaka_loader import MintakaQuestion, select_scale, stratified_sample  # noqa: E402


def make(i: int, complexity: str, category: str) -> MintakaQuestion:
    return MintakaQuestion(
        id=f"q{i}", question_en="", question_ar="", question_entities=(),
        answer_type="entity", answer_qids=(), answer_labels_ar=(), answer_text=None,
        category=category, complexity_type=complexity,
    )


def grouped_corpus() -> list[MintakaQuestion]:
    """400 questions in contiguous blocks, the shape mintaka_test.json
    actually has: 4 complexity types x 2 categories, 50 of each, never
    interleaved.
    """
    qs = []
    i = 0
    for complexity in ("generic", "multihop", "comparative", "yesno"):
        for category in ("movies", "geography"):
            for _ in range(50):
                qs.append(make(i, complexity, category))
                i += 1
    return qs


def test_slicing_the_top_of_a_grouped_file_misses_most_strata():
    """Naive slicing, asserted so the reason for stratifying stays visible."""
    qs = grouped_corpus()
    naive = qs[:100]
    assert set(c.complexity_type for c in naive) == {"generic"}
    assert Counter(c.category for c in naive)["geography"] == 50


def test_stratified_sample_covers_every_stratum_proportionally():
    qs = grouped_corpus()
    sample = stratified_sample(qs, 80)
    assert len(sample) == 80
    by_complexity = Counter(q.complexity_type for q in sample)
    by_category = Counter(q.category for q in sample)
    assert set(by_complexity) == {"generic", "multihop", "comparative", "yesno"}
    assert all(v == 20 for v in by_complexity.values())  # 4 strata, evenly split
    assert by_category == {"movies": 40, "geography": 40}


def test_stratified_sample_returns_exactly_n_when_proportions_do_not_divide():
    qs = grouped_corpus()
    for n in (7, 33, 99, 101, 399):
        assert len(stratified_sample(qs, n)) == n


def test_stratified_sample_is_deterministic_and_in_file_order():
    qs = grouped_corpus()
    a = stratified_sample(qs, 40)
    b = stratified_sample(qs, 40)
    assert [q.id for q in a] == [q.id for q in b]
    original = {q.id: i for i, q in enumerate(qs)}
    assert [original[q.id] for q in a] == sorted(original[q.id] for q in a)


def test_stratified_sample_returns_everything_when_n_exceeds_the_corpus():
    qs = grouped_corpus()
    assert len(stratified_sample(qs, 10_000)) == len(qs)


def test_select_scale_all_returns_the_whole_split():
    qs = grouped_corpus()
    assert len(select_scale(qs, "all")) == len(qs)


def test_select_scale_stratifies_rather_than_slicing():
    qs = grouped_corpus()
    sample = select_scale(qs, "100")
    assert len(sample) == 100
    assert len(set(q.complexity_type for q in sample)) == 4  # not 1, as slicing gave
