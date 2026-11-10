"""Covers qa_scorer.py's non-entity matching.

The cases use the answer shapes an instruction-tuned model actually
produces, not the bare gold token. 45 of the scale-100 tier's 100 questions
are scored by these rules.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.qa_scorer import (  # noqa: E402
    extract_numbers,
    parse_arabic_boolean,
    score_answer,
)

HEIGHT_5_7 = "5" + chr(0x27) + "7" + chr(0x22)
HEIGHT_6_6 = "6" + chr(0x27) + "6" + chr(0x22)


# --- boolean ---------------------------------------------------------------

def test_refusal_is_not_scored_as_a_no():
    """"لا أعرف" (I do not know) opens with the no-word. Scoring it False
    credits the model on every boolean question it declines to answer."""
    assert parse_arabic_boolean("لا أعرف") is None
    assert parse_arabic_boolean("لا أستطيع الإجابة") is None
    assert score_answer("لا أعرف", "boolean", (), "False") is False


def test_negation_with_lays_is_recognised():
    """"ليس" (is not) is in the no-word list, so "ليس صحيحا" reads as no."""
    assert parse_arabic_boolean("ليس صحيحا") is False


def test_no_words_still_win_over_an_embedded_yes_word():
    assert parse_arabic_boolean("غير صحيح") is False
    assert parse_arabic_boolean("لا، ليس كذلك") is False


def test_plain_yes_and_no_still_parse():
    assert parse_arabic_boolean("نعم") is True
    assert parse_arabic_boolean("أجل") is True
    assert parse_arabic_boolean("لا") is False
    assert parse_arabic_boolean("كلا") is False


def test_english_answers_parse_in_either_case():
    """A multilingual model asked in Arabic may still answer in English."""
    assert parse_arabic_boolean("Yes") is True
    assert parse_arabic_boolean("no") is False
    assert parse_arabic_boolean("True") is True


def test_word_ending_in_the_no_word_is_still_not_a_no():
    """The no-word is matched on word boundaries, not as a substring."""
    assert parse_arabic_boolean("هذا طويلاً") is None
    assert parse_arabic_boolean("أولاً") is None


# --- numerical -------------------------------------------------------------

def test_number_inside_a_sentence_counts():
    assert score_answer("تم ترشيحه لجائزة أوسكار واحدة", "numerical", (), "1") is True
    assert score_answer("الجواب: 1", "numerical", (), "1") is True
    assert score_answer("1 جائزة", "numerical", (), "1") is True


def test_arabic_indic_digits_count():
    assert score_answer("١", "numerical", (), "1") is True
    assert score_answer("٢٥", "numerical", (), "25") is True


def test_spelled_out_numbers_count_in_both_genders():
    assert score_answer("واحد", "numerical", (), "1") is True
    assert score_answer("ثلاث جوائز", "numerical", (), "3") is True


def test_a_wrong_number_is_still_wrong():
    assert score_answer("2", "numerical", (), "1") is False
    assert score_answer("لم يُرشَّح لأي جائزة", "numerical", (), "4") is False


def test_thousands_separator_reads_as_one_number():
    assert extract_numbers("1,500") == {1500.0}
    assert score_answer("1,500", "numerical", (), "1500") is True


def test_only_the_number_the_answer_leads_with_counts():
    """Crediting the gold anywhere in the answer would favour arms that
    state more numbers: the no-context arm hedges and explains, so (for
    aya-expanse:8b) 15.9% of its numerical answers name more than one number,
    against 5.3% for graph-walk and 3.7% for retrieval."""
    assert score_answer("4 ميداليات فضية وميدالية برونزية واحدة", "numerical", (), "1") is False
    assert score_answer("4 ميداليات فضية وميدالية برونزية واحدة", "numerical", (), "4") is True


def test_a_spelled_out_number_before_a_digit_still_leads():
    """Reading order, not digits first: this answers "three", and the years
    are supporting detail."""
    text = "ثلاثة أفلام: (2007)، (2009)، (2014)"
    assert score_answer(text, "numerical", (), "3") is True
    assert score_answer(text, "numerical", (), "2007") is False


def test_imperial_height_gold_is_compared_as_a_height_not_as_loose_digits():
    """Read as the digits {5, 7}, gold 5'7" would credit an answer of
    6 feet 7 inches because of the 7."""
    assert score_answer("1.80 متر (6 أقدام و 7 بوصات)", "numerical", (), HEIGHT_5_7) is False
    assert score_answer("5 أقدام و 7 بوصات", "numerical", (), HEIGHT_5_7) is True
    assert score_answer("1.70 متر", "numerical", (), HEIGHT_5_7) is True
    assert score_answer("170 سم", "numerical", (), HEIGHT_5_7) is True
    assert score_answer("198 سم", "numerical", (), HEIGHT_6_6) is True
    assert score_answer("170 سم", "numerical", (), HEIGHT_6_6) is False


def test_a_multi_value_gold_needs_every_value():
    """"Which years did Brazil reach a World Cup final without winning" has
    gold "1950 1998". Naming one of the two is not the answer."""
    assert score_answer("1950، 1998، 2014.", "numerical", (), "1950 1998") is True
    assert score_answer("1950 فقط", "numerical", (), "1950 1998") is False


def test_an_empty_answer_is_never_numerically_correct():
    assert score_answer("", "numerical", (), "1") is False

# --- date ------------------------------------------------------------------

def test_iso_gold_date_does_not_parse_its_separators_as_minus_signs():
    """Parsed as {1969, -7, -20}, "1969-07-20" could never match a date
    written any other way."""
    assert extract_numbers("1969-07-20") == {1969.0, 7.0, 20.0}


def test_written_out_arabic_date_matches_the_iso_gold():
    assert score_answer("20 يوليو 1969", "date", (), "1969-07-20") is True
    assert score_answer("٢٠ تموز ١٩٦٩", "date", (), "1969-07-20") is True


def test_year_alone_does_not_match_a_full_gold_date():
    """Strict on purpose: a year is not an answer to a full-date question."""
    assert score_answer("1969", "date", (), "1969-07-20") is False


def test_wrong_date_is_wrong():
    assert score_answer("21 يوليو 1969", "date", (), "1969-07-20") is False
