import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.qa_scorer import (  # noqa: E402
    ScoredItem,
    aggregate_accuracy,
    answer_correct_boolean,
    answer_correct_entity,
    answer_correct_text,
    normalize_arabic,
    parse_arabic_boolean,
    score_answer,
)


def test_normalize_arabic_unifies_alef_hamza_forms():
    assert normalize_arabic("أحمد") == normalize_arabic("إحمد") == normalize_arabic("احمد")


def test_answer_correct_entity_exact_match():
    assert answer_correct_entity("مارك توين", ("مارك توين",)) is True


def test_answer_correct_entity_matches_any_of_multiple_gold_labels():
    assert answer_correct_entity("مصر", ("المغرب", "مصر", "تونس")) is True


def test_answer_correct_entity_no_match():
    assert answer_correct_entity("اليابان", ("مصر",)) is False


def test_answer_correct_entity_fuzzy_near_miss():
    assert answer_correct_entity("مارك توين", ("مارك توبن",), fuzzy_threshold=70.0) is True


def test_answer_correct_entity_empty_generated_text():
    assert answer_correct_entity("", ("مصر",)) is False


def test_parse_arabic_boolean_yes():
    assert parse_arabic_boolean("نعم، هذا صحيح") is True


def test_parse_arabic_boolean_no():
    assert parse_arabic_boolean("لا") is False


def test_parse_arabic_boolean_unrecognised_text_is_none():
    assert parse_arabic_boolean("ربما") is None


def test_parse_arabic_boolean_negative_phrasing_wins_over_embedded_yes_word():
    # "غير صحيح" contains "صحيح" (a yes-word) but means "not correct"
    assert parse_arabic_boolean("غير صحيح") is False


def test_parse_arabic_boolean_does_not_match_no_word_as_a_substring():
    # "لا" (no) is also the trailing two letters of ordinary words like
    # "طويلاً" (long) and "أولاً" (firstly); a plain substring check would
    # wrongly read these as a "no" answer. Neither sentence answers yes/no.
    assert parse_arabic_boolean("كان طويلاً جداً") is None
    assert parse_arabic_boolean("وُلِد أولاً في مصر") is None


def test_parse_arabic_boolean_still_matches_no_word_with_surrounding_punctuation():
    assert parse_arabic_boolean("لا، هذا غير صحيح") is False
    assert parse_arabic_boolean("لا.") is False


def test_answer_correct_boolean_true_case():
    assert answer_correct_boolean("نعم", True) is True
    assert answer_correct_boolean("لا", True) is False


def test_answer_correct_boolean_unrecognised_answer_is_incorrect():
    assert answer_correct_boolean("ربما", True) is False


def test_answer_correct_text_fuzzy_match():
    assert answer_correct_text("1981", "1981") is True
    assert answer_correct_text("1982", "1981") is False


def test_score_answer_dispatches_by_answer_type_entity():
    assert score_answer("مارك توين", "entity", ("مارك توين",), None) is True


def test_score_answer_dispatches_by_answer_type_boolean():
    assert score_answer("نعم", "boolean", (), "True") is True
    assert score_answer("لا", "boolean", (), "True") is False


def test_score_answer_dispatches_by_answer_type_date():
    assert score_answer("1981", "date", (), "1981") is True


def test_score_answer_missing_answer_text_for_non_entity_is_incorrect():
    assert score_answer("1981", "date", (), None) is False


def test_aggregate_accuracy_overall_and_by_group():
    items = [
        ScoredItem(item_id="1", correct=True, complexity_type="multihop", category="movies"),
        ScoredItem(item_id="2", correct=False, complexity_type="multihop", category="movies"),
        ScoredItem(item_id="3", correct=True, complexity_type="yesno", category="geography"),
    ]
    result = aggregate_accuracy(items)
    assert result["overall_accuracy"] == 2 / 3
    assert result["n_items"] == 3
    assert result["by_complexity_type"]["multihop"] == {"accuracy": 0.5, "n": 2}
    assert result["by_complexity_type"]["yesno"] == {"accuracy": 1.0, "n": 1}
    assert result["by_category"]["movies"]["n"] == 2
    assert result["by_category"]["geography"]["accuracy"] == 1.0


def test_aggregate_accuracy_empty_list():
    result = aggregate_accuracy([])
    assert result["overall_accuracy"] == 0.0
    assert result["n_items"] == 0
    assert result["by_complexity_type"] == {}


# --- refusals and free-text gold answers

def test_refusal_phrasing_not_scored_as_a_definite_no():
    """"There is no information in the provided text" is a refusal, not "no".

    Every such phrasing opens with the no-word. Mintaka's boolean gold skews
    toward "no", so scoring these as "no" would bias boolean accuracy upward.
    """
    from src.qa.qa_scorer import parse_arabic_boolean
    for text in (
        "لا توجد معلومات حول الطول في النص المقدم",
        "لا يوجد معلومات في النص المقدم لمقارنة الطول",
        "لا توجد معلومات في النص عن قائمة القيد",
        "غير مذكور في النص",
        "لا يمكن تحديد ذلك من المعلومات المتاحة",
    ):
        assert parse_arabic_boolean(text) is None, text

    # and the ordinary answers must still parse
    assert parse_arabic_boolean("لا") is False
    assert parse_arabic_boolean("نعم") is True


def test_entity_answer_with_only_a_free_text_mention_is_scoreable():
    """1.7% of Mintaka's test split is answerType "entity" with a null answer
    list and the gold held in answer.mention. Without the mention, no answer
    to those questions could ever score as correct.
    """
    from src.qa.qa_scorer import score_answer
    assert score_answer("Elvis Presto", "entity", (), "Elvis Presto") is True
    assert score_answer("شيء آخر", "entity", (), "Elvis Presto") is False
    # a genuinely label-less row with no mention either stays wrong
    assert score_answer("أي شيء", "entity", (), None) is False
