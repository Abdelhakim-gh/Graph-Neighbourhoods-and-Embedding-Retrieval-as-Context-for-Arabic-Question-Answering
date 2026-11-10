import importlib.util
from pathlib import Path
from types import SimpleNamespace

from src.qa.graph_pull import scope_to_seeds

spec = importlib.util.spec_from_file_location("predicted_entities", Path(__file__).resolve().parents[1] / "scripts/16_predicted_entities.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def question(item_id, gold, kind="generic"):
    return SimpleNamespace(id=item_id, complexity_type=kind,
                           question_entities=tuple(SimpleNamespace(qid=q) for q in gold))


def test_parse_mentions():
    assert m.parse_mentions('```json\n["مصر", "القاهرة"]\n``` extra') == (["مصر", "القاهرة"], True)
    assert m.parse_mentions('prefix ["مصر"] trailing') == (["مصر"], True)
    assert m.parse_mentions('{"entity": "مصر"}') == ([], False)
    assert m.parse_mentions('[1, 2]') == ([], False)
    assert m.parse_mentions('["مصر", "خيال"]', 'أين مصر؟') == (["مصر"], True)


def test_link_retry_and_dedup():
    seen = []
    def search(term):
        seen.append(term)
        return {"search": {"القاهرة": [], "قاهرة": [{"id": "Q1"}],
                           "مصر": [{"id": "Q1"}], "مدينة": []}[term]}
    qids, candidates = m.link_mentions(["القاهرة", "مصر", "مدينة"], search)
    assert seen == ["القاهرة", "قاهرة", "مصر", "مدينة"]
    assert qids == ["Q1"]
    assert [s["search"] for s in candidates[0]["searches"]] == ["القاهرة", "قاهرة"]


def test_metrics():
    qs = [question("a", ["Q1", "Q2", "ordinal"]), question("b", ["Q3"]), question("c", [])]
    links = {"a": {"predicted_qids": ["Q1", "Q4"]}, "b": {"predicted_qids": []},
             "c": {"predicted_qids": ["Q5"]}}
    out = m.metrics(qs, links)
    assert out["micro_precision"] == 1 / 3
    assert out["micro_recall"] == 1 / 3
    assert out["all_gold_found"] == 0
    assert out["at_least_one_gold_found"] == 0.5
    assert out["no_gold_found"] == 0.5
    assert out["no_prediction"] == 1 / 3
    assert out["questions_without_gold"] == 1


def test_store_seeds_replace_only_tier_gold():
    qs = [question("tier", ["Q1"]), question("other", ["Q2"])]
    links = {"tier": {"predicted_qids": ["Q3"]}}
    seeds = m.build_seeds(qs, {"tier"}, links)
    assert seeds == {"Q2", "Q3"}
    triples = [("Q1", "P1", "Q4", "a"), ("Q2", "P1", "Q5", "b"),
               ("Q3", "P1", "Q6", "c"), ("Q6", "P2", "Q7", "d")]
    store = scope_to_seeds(triples, seeds, 2)
    assert store == [triples[1], triples[2], triples[3]]
