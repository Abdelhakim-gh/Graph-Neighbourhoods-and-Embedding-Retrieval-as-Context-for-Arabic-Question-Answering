"""Covers drop_excluded_properties.

5.92% of the unfiltered scale-100 retrieval corpus is Wikimedia bookkeeping: category,
template and WikiProject pages reached through a small set of administrative
properties. The ordering guarantee is the part worth testing, since getting
it wrong silently leaves most of the noise in place.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qa.graph_pull import drop_excluded_properties, scope_to_seeds  # noqa: E402

# Q1 (a country) points at a real fact and at its Wikimedia category, and
# that category page has its own outgoing edges.
TRIPLES = [
    ("Q1", "P17", "Q2", "country"),
    ("Q1", "P910", "Q900", "Category:Q1"),
    ("Q900", "P971", "Q901", "Category:combines"),
    ("Q900", "P31", "Q4167836", "Wikimedia category"),
]


def test_excluded_edges_are_removed():
    kept = drop_excluded_properties(TRIPLES, ["P910", "P971"])
    assert ("Q1", "P910", "Q900", "Category:Q1") not in kept
    assert ("Q1", "P17", "Q2", "country") in kept


def test_filtering_before_scoping_removes_the_whole_category_subtree():
    """The ordering that matters: dropping the edge into a category page is
    what makes the page unreachable, so its own edges leave with it."""
    filtered = drop_excluded_properties(TRIPLES, ["P910", "P971"])
    scoped = scope_to_seeds(filtered, {"Q1"}, max_hops=3)
    assert {t[0] for t in scoped} == {"Q1"}
    assert not any(t[0] == "Q900" for t in scoped)


def test_filtering_after_scoping_would_leave_the_subtree_behind():
    """The mistake this ordering avoids, asserted so the reason stays visible.
    Scope first and the category's own P31 edge is already in the tier."""
    scoped = scope_to_seeds(TRIPLES, {"Q1"}, max_hops=3)
    late = drop_excluded_properties(scoped, ["P910", "P971"])
    assert any(t[0] == "Q900" for t in late)  # the category survived


def test_empty_or_missing_exclusion_list_is_a_no_op():
    assert drop_excluded_properties(TRIPLES, None) == TRIPLES
    assert drop_excluded_properties(TRIPLES, []) == TRIPLES


def test_accepts_a_set_as_well_as_a_list():
    assert len(drop_excluded_properties(TRIPLES, {"P910"})) == len(TRIPLES) - 1


def test_a_property_not_present_changes_nothing():
    assert drop_excluded_properties(TRIPLES, ["P9999"]) == TRIPLES
