"""Covers read_run_identity and the scorer's handling of gold entities with
no Arabic label, using synthetic answer files.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from importlib import import_module  # noqa: E402

from src.qa.qa_scorer import score_answer  # noqa: E402

score = import_module("05_score")


def write_rows(tmp_path, rows):
    p = tmp_path / "graph_walk_qwen3.5_4b_7_seed1.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return p


def test_identity_is_read_past_a_leading_error_row(tmp_path):
    """An errored item carries no run identity, so reading only the first
    row would report no arm for a run whose first question failed."""
    p = write_rows(tmp_path, [
        {"error": "timeout", "item_id": "a"},
        {"arm": "graph_walk", "embedding_model": None, "model": "qwen3.5:4b", "seed": 1, "item_id": "b"},
    ])
    got = score.read_run_identity(p, fallback="graph_walk_qwen3.5_4b", seed=1)
    assert got["arm"] == "graph_walk"
    assert got["model"] == "qwen3.5:4b"


def test_identity_falls_back_when_no_row_carries_it(tmp_path):
    p = write_rows(tmp_path, [{"generated_text": "x", "item_id": "a"}])
    got = score.read_run_identity(p, fallback="legacy_run", seed=3)
    assert got["arm"] is None
    assert got["identity_from"] == "legacy_run"
    assert got["seed"] == 3


def test_retrieval_identity_keeps_the_embedding_model(tmp_path):
    p = write_rows(tmp_path, [
        {"arm": "retrieval", "embedding_model": "bge-m3", "model": "gemma4:12b", "seed": 2, "item_id": "a"},
    ])
    got = score.read_run_identity(p, fallback="x", seed=2)
    assert got["arm"] == "retrieval"
    assert got["embedding_model"] == "bge-m3"


# --- gold entities with no Arabic label -----------------------------------

def test_gold_entity_with_no_arabic_label_does_not_crash_the_scorer():
    """Mintaka stores an explicit null for a language a gold entity has no
    label in, so the key is present with value None and a plain dict default
    never fires. 7.6% of the test split has at least one; passing None into
    normalize_arabic would raise AttributeError and stop the scoring run."""
    assert score_answer("أي شيء", "entity", ("",), None) is False


def test_english_label_is_used_when_the_arabic_one_is_missing():
    """"Take Me as I Am" has no Arabic label in Wikidata. Without the
    fallback these questions score 0 for every model and every arm whatever
    was answered."""
    assert score_answer("Take Me as I Am", "entity", ("",), None,
                        answer_labels_en=("Take Me as I Am",)) is True


def test_english_is_not_a_second_chance_when_arabic_exists():
    """The fallback is per entity, not per question: an entity that has an
    Arabic label is still scored against it alone."""
    assert score_answer("Mark Twain", "entity", ("مارك توين",), None,
                        answer_labels_en=("Mark Twain",)) is False


def test_multi_entity_answer_mixes_arabic_and_english_per_entity():
    assert score_answer("Sharron Angle", "entity", ("مارك توين", ""), None,
                        answer_labels_en=("Mark Twain", "Sharron Angle")) is True
