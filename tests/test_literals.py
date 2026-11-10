"""Covers the date/quantity pull.

Without it, comparative questions ("who is older, X or Y") score 0%
gold-in-context under every path ranking tried, because they need P569
date of birth and build_neighborhood_query's ISIRI(?tail) filter keeps every
literal out of the graph. 45 of the stratified scale-100 tier's 100
questions have a numerical, boolean or date gold answer.

The load-bearing property is that these facts are retrievable but never
walkable, which is enforced structurally: scripts/01 writes them to
literals.jsonl, and scripts/03 builds its adjacency from triples.jsonl.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_pull import build_literal_query, parse_literal_rows  # noqa: E402
from src.qa.graph_walk import build_adjacency  # noqa: E402
from src.qa.retrieval import build_literal_facts  # noqa: E402


def test_query_excludes_external_ids_and_keeps_quantity_and_time():
    q = build_literal_query(["Q1", "Q2"])
    assert "wikibase:Quantity" in q and "wikibase:Time" in q
    assert "ExternalId" not in q          # excluded by not being listed
    assert "FILTER(!ISIRI(?value))" in q  # the complement of the entity query
    assert "wd:Q1" in q and "wd:Q2" in q


def test_dates_are_trimmed_to_the_day():
    """A date-precision Wikidata claim always carries a midnight time, so
    the time half is noise in every fact sentence it appears in."""
    rows = [{
        "head": {"value": "http://www.wikidata.org/entity/Q42"},
        "prop": {"value": "http://www.wikidata.org/entity/P569"},
        "value": {"value": "1952-03-11T00:00:00Z", "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"},
    }]
    assert parse_literal_rows(rows) == [("Q42", "P569", "1952-03-11")]


def test_positive_quantities_lose_the_leading_plus():
    rows = [{
        "head": {"value": "http://www.wikidata.org/entity/Q42"},
        "prop": {"value": "http://www.wikidata.org/entity/P2048"},
        "value": {"value": "+1.88", "datatype": "http://www.w3.org/2001/XMLSchema#decimal"},
    }]
    assert parse_literal_rows(rows) == [("Q42", "P2048", "1.88")]


def test_negative_quantities_keep_their_sign():
    rows = [{
        "head": {"value": "http://www.wikidata.org/entity/Q42"},
        "prop": {"value": "http://www.wikidata.org/entity/P2044"},
        "value": {"value": "-430", "datatype": "http://www.w3.org/2001/XMLSchema#decimal"},
    }]
    assert parse_literal_rows(rows) == [("Q42", "P2044", "-430")]


def test_literal_facts_render_like_entity_facts():
    facts = build_literal_facts(
        [("Q42", "P569", "1952-03-11")], {"Q42": "دوغلاس آدمز"}, {"P569": "تاريخ الميلاد"}
    )
    assert len(facts) == 1
    assert facts[0].sentence == "دوغلاس آدمز - تاريخ الميلاد - 1952-03-11"


def test_literal_facts_carry_no_tail_qid_so_nothing_can_walk_them():
    facts = build_literal_facts([("Q42", "P569", "1952-03-11")], {"Q42": "x"}, {"P569": "y"})
    assert facts[0].tail_qid == ""


def test_a_literal_fact_cannot_become_a_graph_edge():
    """The structural guarantee, asserted rather than assumed: build_adjacency
    only ever sees 4-tuples from triples.jsonl, and a literal fact is not one."""
    facts = build_literal_facts([("Q42", "P569", "1952-03-11")], {"Q42": "x"}, {"P569": "y"})
    adjacency = build_adjacency([(f.head_qid, f.relation_pid, f.tail_qid, f.sentence) for f in facts])
    # even if someone force-fed them in, the tail is empty, not a QID
    assert "1952-03-11" not in adjacency


def test_unlabelled_head_is_skipped_rather_than_rendered_as_a_qid():
    assert build_literal_facts([("Q42", "P569", "1952-03-11")], {}, {"P569": "y"}) == []


def test_property_with_no_arabic_label_falls_back_to_the_pid():
    """ensure_property_labels records a missing Arabic label as "", so it is
    not re-queried; that must not render as a blank gap."""
    facts = build_literal_facts([("Q42", "P569", "1952-03-11")], {"Q42": "x"}, {"P569": ""})
    assert facts[0].sentence == "x - P569 - 1952-03-11"
