from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.p22_3_b1_source_pack import (
    B1_SOURCES,
    P22_3_B1_VERSION,
    build_b1_adapters,
    b1_by_id,
)

NOW = datetime(2026, 9, 19, 14, 0, tzinfo=timezone.utc)
FIX = Path(__file__).parent / "fixtures" / "p22_3_b1"


class FixtureTransport:
    def get(self, url, *, headers=None):
        if "ofac.treasury.gov" in url:
            name, ctype = "ofac.html", "text/html"
        elif "sanctionslist.fcdo.gov.uk" in url:
            name, ctype = "uk-sanctions.csv", "text/csv"
        elif "government.ru" in url:
            name, ctype = "russian-government.html", "text/html"
        elif "whitehouse.gov" in url:
            name, ctype = "white-house.html", "text/html"
        else:
            raise AssertionError(url)
        return HttpResponse(body=(FIX / name).read_bytes(), content_type=ctype)


def test_b1_specs_are_exact_authorized_public_free_targets():
    assert P22_3_B1_VERSION == "P22.3-B1-1.0"
    by_id = b1_by_id()
    assert set(by_id) == {
        "ofac-recent-actions-en",
        "uk-sanctions-list-en",
        "russian-government-news-ru",
        "white-house-briefings-en",
    }
    assert len(B1_SOURCES) == 4
    assert all(s.endpoint.startswith("https://") for s in B1_SOURCES)
    assert all(s.source_class == "Official sources" for s in B1_SOURCES)
    assert {s.source_type for s in B1_SOURCES} == {"OFFICIAL_GOVERNMENT", "SANCTIONS_REGULATORY"}


def test_b1_fixture_parsers_emit_deterministic_source_bound_items():
    adapters = build_b1_adapters(FixtureTransport(), max_entries=10)
    watch = type("Watch", (), {"query": "unused"})()
    by_source = {}
    for adapter in adapters:
        items = adapter.fetch(watch, NOW)
        assert items
        assert all(i.source_id == adapter.source_id for i in items)
        assert all(i.metadata["adapter_id"] == adapter.adapter_id for i in items)
        assert all(i.metadata["official_statement_boundary"] is True for i in items)
        by_source[adapter.source_id] = items

    assert by_source["ofac-recent-actions-en"][0].original_url.startswith("https://ofac.treasury.gov/recent-actions/")
    assert by_source["russian-government-news-ru"][0].original_url.startswith("https://government.ru/news/")
    assert by_source["white-house-briefings-en"][0].original_url.startswith("https://www.whitehouse.gov/briefings-statements/")
    assert by_source["uk-sanctions-list-en"][0].metadata["unique_id"]


def test_b1_disable_rollback_is_deterministic_and_unknown_ids_fail_closed():
    assert build_b1_adapters(FixtureTransport(), enabled_source_ids=[]) == []
    only = build_b1_adapters(FixtureTransport(), enabled_source_ids=["uk-sanctions-list-en"])
    assert [a.source_id for a in only] == ["uk-sanctions-list-en"]
    with pytest.raises(ValueError, match="unknown P22.3 B1 source"):
        build_b1_adapters(FixtureTransport(), enabled_source_ids=["unknown"])


def test_b1_html_parsers_reject_external_and_index_links():
    adapters = {a.source_id: a for a in build_b1_adapters(FixtureTransport())}
    watch = type("Watch", (), {"query": "unused"})()
    for source_id in ("ofac-recent-actions-en", "russian-government-news-ru", "white-house-briefings-en"):
        items = adapters[source_id].fetch(watch, NOW)
        assert items
        host = {
            "ofac-recent-actions-en": "ofac.treasury.gov",
            "russian-government-news-ru": "government.ru",
            "white-house-briefings-en": "www.whitehouse.gov",
        }[source_id]
        assert all(host in i.original_url for i in items)
