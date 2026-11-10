"""Covers retrieval_hit.

Retrieval hit rate is reported as its own metric and is used to choose the
embedding models for answer generation (scripts/02b).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.retrieval import retrieval_hit  # noqa: E402


def fact(sentence="x - y - z", head="Q1", tail="Q2"):
    return {"sentence": sentence, "head_qid": head, "tail_qid": tail}


def test_entity_answer_hits_when_gold_is_the_object():
    got = retrieval_hit([fact(head="Q1", tail="Q7245")], "entity", ("Q7245",), None)
    assert got is True


def test_entity_answer_hits_when_gold_is_the_subject():
    """"Mark Twain - occupation - author" names Mark Twain just as much as
    "Tom Sawyer - author - Mark Twain" does."""
    got = retrieval_hit([fact(head="Q7245", tail="Q1")], "entity", ("Q7245",), None)
    assert got is True


def test_entity_answer_misses_when_gold_is_absent():
    assert retrieval_hit([fact(head="Q1", tail="Q2")], "entity", ("Q7245",), None) is False


def test_any_one_of_several_gold_entities_counts():
    got = retrieval_hit([fact(head="Q1", tail="Q99")], "entity", ("Q7245", "Q99"), None)
    assert got is True


def test_boolean_answers_are_skipped_not_scored_as_misses():
    """A yes/no cannot appear in a retrieved Wikidata fact. Scoring these as
    misses would drag every model down by the tier's share of boolean
    questions and measure the sample instead of the model."""
    assert retrieval_hit([fact()], "boolean", (), "True") is None


def test_numerical_answer_matches_a_number_in_a_retrieved_sentence():
    got = retrieval_hit([fact(sentence="بوسطن - عدد السكان - 675647")], "numerical", (), "675647")
    assert got is True


def test_numerical_answer_misses_when_the_number_is_absent():
    got = retrieval_hit([fact(sentence="بوسطن - عدد السكان - 675647")], "numerical", (), "12")
    assert got is False


def test_date_answer_matches_across_formats():
    got = retrieval_hit([fact(sentence="بوسطن - تاريخ التأسيس - 1630-09-17")], "date", (), "1630-09-17")
    assert got is True


def test_empty_retrieved_set_is_a_miss_not_a_skip():
    assert retrieval_hit([], "entity", ("Q7245",), None) is False


def test_entity_answer_with_no_gold_qid_is_skipped():
    assert retrieval_hit([fact()], "entity", (), None) is None
