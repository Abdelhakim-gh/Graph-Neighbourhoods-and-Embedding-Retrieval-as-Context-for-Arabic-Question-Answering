import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.mintaka_loader import collect_qids, load_split, parse_question  # noqa: E402

ENTITY_ROW = {
    "id": "fae46b21",
    "question": "What man was a famous American author and also a steamboat pilot on the Mississippi River?",
    "translations": {"ar": "من الرجل الذي كان مؤلفا امريكيا مشهورا؟"},
    "questionEntity": [
        {"name": "Q1497", "entityType": "entity", "label": "Mississippi River", "mention": "Mississippi River", "span": [72, 89]},
        {"name": "Q846570", "entityType": "entity", "label": "Americans", "mention": "American", "span": [22, 30]},
    ],
    "answer": {
        "answerType": "entity",
        "answer": [{"name": "Q7245", "label": {"en": "Mark Twain", "ar": "مارك توين"}}],
        "mention": "Mark Twain",
    },
    "category": "history",
    "complexityType": "intersection",
}

DATE_ROW_WITH_ORDINAL_ENTITY = {
    "id": "abc123",
    "question": "What year was the first Donkey Kong game released?",
    "translations": {"ar": "في أي سنة صدرت أول لعبة دونكي كونغ؟"},
    "questionEntity": [
        {"name": "Q662004", "entityType": "entity", "label": "Donkey Kong", "mention": "Donkey Kong", "span": [19, 30]},
        {"name": 1, "entityType": "ordinal", "mention": "first", "span": [13, 18]},
    ],
    "answer": {"answerType": "date", "answer": ["1981"], "mention": "1981"},
    "category": "videogames",
    "complexityType": "superlative",
}

BOOLEAN_ROW_NO_ANSWER_ENTITY = {
    "id": "xyz789",
    "question": "Is the sky green?",
    "translations": {"ar": "هل السماء خضراء؟"},
    "questionEntity": [],
    "answer": {"answerType": "boolean", "answer": [False], "mention": "No"},
    "category": "geography",
    "complexityType": "yesno",
}


def test_parse_question_entity_answer():
    q = parse_question(ENTITY_ROW)
    assert q.id == "fae46b21"
    assert q.question_ar == "من الرجل الذي كان مؤلفا امريكيا مشهورا؟"
    assert {e.qid for e in q.question_entities} == {"Q1497", "Q846570"}
    assert q.answer_type == "entity"
    assert q.answer_qids == ("Q7245",)
    assert q.answer_labels_ar == ("مارك توين",)
    assert q.answer_text is None


def test_parse_question_ordinal_entity_is_excluded_from_question_entities():
    # entityType "ordinal" has a non-QID "name" (the integer 1); including
    # it as a question entity would poison the graph-walk arm's start set
    q = parse_question(DATE_ROW_WITH_ORDINAL_ENTITY)
    assert [e.qid for e in q.question_entities] == ["Q662004"]


def test_parse_question_non_entity_answer_has_no_qids_but_has_text():
    q = parse_question(DATE_ROW_WITH_ORDINAL_ENTITY)
    assert q.answer_qids == ()
    assert q.answer_labels_ar == ()
    assert q.answer_text == "1981"


def test_parse_question_boolean_answer_and_no_question_entities():
    q = parse_question(BOOLEAN_ROW_NO_ANSWER_ENTITY)
    assert q.question_entities == ()
    assert q.answer_text == "False"


def test_collect_qids_unions_question_and_answer_entities():
    questions = [parse_question(ENTITY_ROW), parse_question(DATE_ROW_WITH_ORDINAL_ENTITY)]
    qids = collect_qids(questions)
    assert qids == {"Q1497", "Q846570", "Q7245", "Q662004"}


def test_collect_qids_ignores_non_entity_answers():
    questions = [parse_question(BOOLEAN_ROW_NO_ANSWER_ENTITY)]
    assert collect_qids(questions) == set()


def test_load_split_reads_a_json_array_of_rows():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "mintaka_test.json"
        path.write_text(json.dumps([ENTITY_ROW, BOOLEAN_ROW_NO_ANSWER_ENTITY]), encoding="utf-8")
        questions = load_split(path)
        assert len(questions) == 2
        assert questions[0].id == "fae46b21"


def test_scale_tiers_nest():
    """The 100-item tier is a strict subset of the 1,000-item tier.

    Guaranteed by the sampler rather than incidental: one Random(seed) per
    call, each stratum shuffled once in sorted order, so every n sees the
    same per-stratum permutation and takes a prefix of it.
    """
    from pathlib import Path
    from src.qa.mintaka_loader import load_split, select_scale
    path = Path(__file__).resolve().parents[1] / "datasets" / "mintaka" / "mintaka_test.json"
    if not path.exists():
        import pytest
        pytest.skip("mintaka_test.json not available")
    qs = load_split(path)
    small = {q.id for q in select_scale(qs, "100")}
    large = {q.id for q in select_scale(qs, "1000")}
    assert small <= large
    assert small == {q.id for q in select_scale(qs, "100")}   # deterministic


def test_entity_with_a_null_name_is_not_a_seed():
    """1.0% of the test split has an entity-typed questionEntity with a null
    name: a mention Mintaka never linked to a Wikidata item. str(None) would
    make it the literal QID "None", which would be queried, cached, and
    counted as present by the coverage check meant to catch missing seeds.
    """
    from src.qa.mintaka_loader import parse_question
    row = {
        "id": "x", "question": "q", "translations": {"ar": "س"},
        "questionEntity": [
            {"entityType": "entity", "name": "Q42", "label": "a", "mention": "A"},
            {"entityType": "entity", "name": None, "label": "b", "mention": "Winston"},
            {"entityType": "ordinal", "name": 1, "label": "", "mention": "first"},
        ],
        "answer": {"answerType": "string", "answer": ["z"]},
        "category": "movies", "complexityType": "generic",
    }
    q = parse_question(row)
    assert [e.qid for e in q.question_entities] == ["Q42"]
    assert "None" not in [e.qid for e in q.question_entities]
