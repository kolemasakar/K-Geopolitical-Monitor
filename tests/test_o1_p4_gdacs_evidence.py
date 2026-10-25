from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.on_demand_evidence_assessment import assess_evidence
from kgeopolitical_monitor.on_demand_gdacs import GdacsRssAdapter
from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.on_demand_source_policy import validate_source_url
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch

NOW = datetime(2026, 10, 25, 20, tzinfo=timezone.utc)


class StubTransport:
    def __init__(self, body):
        self.body = body
        self.calls = []
    def get(self, url, *, headers=None):
        self.calls.append(url)
        return HttpResponse(body=self.body, content_type="application/rss+xml")


def _watch():
    return MonitoringWatch("fixture-watch", "Test", "earthquake", 60, created_at=NOW)


def _xml(pub="Sun, 25 Oct 2026 18:00:00 GMT", url="https://www.gdacs.org/report.aspx"):
    return (f'<rss version="2.0"><channel><item><title>Earthquake event</title>'
            f'<description>Earthquake alert</description><guid>gdacs-001</guid>'
            f'<link>{url}</link><pubDate>{pub}</pubDate></item></channel></rss>').encode()


def test_gdacs_rss_offline_adapter_and_time_metadata():
    transport = StubTransport(_xml())
    adapter = GdacsRssAdapter(transport)
    items = adapter.fetch(_watch(), NOW)
    assert len(items) == 1
    assert transport.calls == ["https://www.gdacs.org/xml/rss.xml"]
    assert items[0].source_id == "gdacs-rss"
    assert items[0].metadata["published_at"].startswith("2026-10-25T18:00")
    evidence = assess_evidence(items, observed_at=NOW, freshness_hours=48)
    assert evidence.freshness == "FRESH_BY_PUBLISHED_TIMESTAMP"
    assert evidence.origins_independence == "NOT_ATTESTED_OWNERSHIP_OR_SYNDICATION"


def test_gdacs_invalid_xml_fails_closed():
    with pytest.raises(RuntimeError, match="invalid"):
        GdacsRssAdapter(StubTransport(b"not-xml")).fetch(_watch(), NOW)


def test_gdacs_skips_untrusted_http_link():
    assert GdacsRssAdapter(StubTransport(_xml(url="http://example.com/item"))).fetch(_watch(), NOW) == []


def test_gdacs_endpoint_allowlisted():
    validate_source_url("https://www.gdacs.org/xml/rss.xml")
    with pytest.raises(ValueError):
        validate_source_url("https://www.gdacs.org/xml/other")


def test_evidence_undated_is_unknown():
    item = GdacsRssAdapter(StubTransport(_xml(pub="not date"))).fetch(_watch(), NOW)[0]
    verdict = assess_evidence([item], observed_at=NOW)
    assert verdict.freshness == "UNKNOWN_INCOMPLETE_DATES"
    assert verdict.undated_records == 1


def test_stale_and_future_fail_conservative():
    adapter = GdacsRssAdapter(StubTransport(_xml()))
    stale = adapter.fetch(_watch(), NOW)
    assert assess_evidence(stale, observed_at=NOW + timedelta(days=5)).freshness == "STALE"
    assert assess_evidence(stale, observed_at=NOW - timedelta(days=3)).freshness == "INVALID_FUTURE_TIMESTAMP"


def test_different_adapters_not_automatically_independent():
    a = GdacsRssAdapter(StubTransport(_xml())).fetch(_watch(), NOW)[0]
    verdict = assess_evidence([a, a], observed_at=NOW)
    assert verdict.source_records == 2
    assert verdict.source_ids == 1
    assert verdict.valid_origin_hosts == 1
    assert verdict.origins_independence == "NOT_ATTESTED_OWNERSHIP_OR_SYNDICATION"
