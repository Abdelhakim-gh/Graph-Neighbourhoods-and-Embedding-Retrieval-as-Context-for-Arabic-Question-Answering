import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.qa.graph_pull as graph_pull  # noqa: E402
from src.qa.graph_pull import (  # noqa: E402
    build_neighborhood_query,
    build_property_label_query,
    fetch_neighborhood,
    parse_neighborhood_rows,
    parse_property_label_rows,
    pid_from_uri,
    qid_from_uri,
)


def test_qid_from_uri():
    assert qid_from_uri("http://www.wikidata.org/entity/Q1497") == "Q1497"


def test_pid_from_uri():
    assert pid_from_uri("http://www.wikidata.org/entity/P57") == "P57"


def test_build_neighborhood_query_includes_every_qid():
    query = build_neighborhood_query(["Q1497", "Q7245"])
    assert "wd:Q1497" in query
    assert "wd:Q7245" in query
    assert "ISIRI(?tail)" in query
    assert 'LANG(?tailLabel) = "ar"' in query


def test_build_neighborhood_query_respects_labels_language():
    query = build_neighborhood_query(["Q1497"], labels_language="en")
    assert 'LANG(?tailLabel) = "en"' in query


def test_build_neighborhood_query_defaults_to_a_row_limit():
    # without a LIMIT, a large batch's combined response can be too large to
    # complete on any retry, truncated at the same byte offset each time
    query = build_neighborhood_query(["Q1497"])
    assert "LIMIT 10000" in query


def test_build_neighborhood_query_respects_row_limit():
    query = build_neighborhood_query(["Q1497"], row_limit=500)
    assert "LIMIT 500" in query


def test_parse_neighborhood_rows_extracts_qid_pid_qid_label():
    rows = [
        {
            "head": {"value": "http://www.wikidata.org/entity/Q7245"},
            "prop": {"value": "http://www.wikidata.org/entity/P106"},
            "tail": {"value": "http://www.wikidata.org/entity/Q36180"},
            "tailLabel": {"value": "كاتب"},
        }
    ]
    triples = parse_neighborhood_rows(rows)
    assert triples == [("Q7245", "P106", "Q36180", "كاتب")]


def test_parse_neighborhood_rows_empty():
    assert parse_neighborhood_rows([]) == []


def test_build_property_label_query_includes_every_pid():
    query = build_property_label_query(["P57", "P106"])
    assert "wd:P57" in query
    assert "wd:P106" in query
    assert 'LANG(?propLabel) = "ar"' in query


def test_parse_property_label_rows():
    rows = [{"prop": {"value": "http://www.wikidata.org/entity/P57"}, "propLabel": {"value": "مخرج"}}]
    assert parse_property_label_rows(rows) == {"P57": "مخرج"}


def test_parse_property_label_rows_empty():
    assert parse_property_label_rows([]) == {}


def test_fetch_neighborhood_skips_an_unrecoverable_batch_and_keeps_the_rest(monkeypatch):
    # A batch can fail every retry (one QID too expensive to query). That
    # RuntimeError must not stop the whole multi-hop expansion and discard
    # every batch already fetched: the batch is logged and skipped instead.
    calls = []

    def fake_run(sparql, query):
        calls.append(query)
        if "wd:Q2" in query:
            raise RuntimeError("SPARQL query failed after 5 attempts")
        return [
            {
                "head": {"value": "http://www.wikidata.org/entity/Q1"},
                "prop": {"value": "http://www.wikidata.org/entity/P17"},
                "tail": {"value": "http://www.wikidata.org/entity/Q99"},
                "tailLabel": {"value": "a"},
            }
        ]

    monkeypatch.setattr(graph_pull, "_run", fake_run)
    triples, failed = fetch_neighborhood(sparql=None, qids=["Q1", "Q2"], chunk_size=1, sleep_between_chunks_s=0)

    assert triples == [("Q1", "P17", "Q99", "a")]  # Q1's batch succeeded and was kept
    assert failed == {"Q2"}  # Q2's batch is reported as failed, not silently absent
    assert len(calls) == 2  # both batches were attempted; Q2's failure did not stop Q1's from running


def test_parse_neighborhood_rows_multiple():
    rows = [
        {
            "head": {"value": "http://www.wikidata.org/entity/Q1"},
            "prop": {"value": "http://www.wikidata.org/entity/P17"},
            "tail": {"value": "http://www.wikidata.org/entity/Q2"},
            "tailLabel": {"value": "a"},
        },
        {
            "head": {"value": "http://www.wikidata.org/entity/Q1"},
            "prop": {"value": "http://www.wikidata.org/entity/P19"},
            "tail": {"value": "http://www.wikidata.org/entity/Q3"},
            "tailLabel": {"value": "b"},
        },
    ]
    triples = parse_neighborhood_rows(rows)
    assert len(triples) == 2
    assert triples[0][1] == "P17"
    assert triples[1][1] == "P19"


# --- retry budgets: transient network failures get a longer budget than
# query errors.

def test_transient_errors_are_classified_apart_from_query_errors():
    from src.qa.graph_pull import _is_transient
    for msg in (
        "<urlopen error [Errno 11001] getaddrinfo failed>",
        "The read operation timed out",
        "HTTP Error 503: Service Unavailable",
        "Connection reset by peer",
    ):
        assert _is_transient(Exception(msg)), msg
    for msg in ("QueryBadFormed: syntax error", "400 Bad Request", "malformed query"):
        assert not _is_transient(Exception(msg)), msg


def test_transient_failures_get_the_longer_budget(monkeypatch):
    """A dropped connection should outlast the short budget, a bad query should not."""
    import src.qa.graph_pull as gp
    monkeypatch.setattr(gp.time, "sleep", lambda s: None)

    class Sparql:
        def __init__(self, exc): self.exc = exc; self.calls = 0
        def setQuery(self, q): pass
        def query(self): self.calls += 1; raise self.exc

    transient = Sparql(Exception("<urlopen error [Errno 11001] getaddrinfo failed>"))
    try:
        gp._run(transient, "SELECT * WHERE {}")
    except RuntimeError:
        pass
    assert transient.calls == 8, transient.calls

    permanent = Sparql(Exception("QueryBadFormed: syntax error"))
    try:
        gp._run(permanent, "SELECT * WHERE {}")
    except RuntimeError:
        pass
    assert permanent.calls == 5, permanent.calls


def test_truncated_json_response_counts_as_transient():
    """A partial response body reads as a parse error but is a transport
    failure: the query was fine and a retry succeeds.
    """
    import json
    from src.qa.graph_pull import _is_transient
    assert _is_transient(Exception("Unterminated string starting at: line 2529 column 9 (char 63656)"))
    assert _is_transient(Exception("Expecting value: line 1 column 1 (char 0)"))
    try:
        json.loads('{"a": "b')
    except json.JSONDecodeError as exc:
        assert _is_transient(exc)
