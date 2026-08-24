"""Tests for intelligence query layer."""

from kgeopolitical_monitor.intelligence_query import IntelligenceQuery


def test_query_initialization():
    query = IntelligenceQuery(None)
    assert query.graph is None
