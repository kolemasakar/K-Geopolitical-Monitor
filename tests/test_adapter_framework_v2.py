from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pytest

from kgeopolitical_monitor.adapter_framework import (
    ADAPTER_FRAMEWORK_VERSION,
    AdapterRequest,
    FrameworkLiveSourceCollector,
    GdeltDoc2AdapterV2,
    PublicFeedAdapterV2,
    ReadOnlyHttpsTransportV2,
    parse_json_list,
    parse_rss_atom,
)
from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.reproducibility import (
    ReproducibilityInstrumentedCollector,
    ReproducibilityStore,
)
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService


NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
FIXTURES = Path(__file__).parent / "fixtures" / "p12_2"


class FixtureTransport:
    def __init__(self, response):
        self.response = response
        self.urls = []
        self.headers = []

    def get(self, url, *, headers=None):
        self.urls.append(url)
        self.headers.append(headers or {})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class _UrlOpenResponse:
    def __init__(self, body: bytes, content_type: str = "application/octet-stream"):
        self.body = body
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, amount):
        return self.body[:amount]


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "P12.2 watch",
        "Ukraine security",
        60,
        watch_id="watch-p122",
        created_at=NOW,
    )
    return runtime


def _feed_adapter(transport, *, source_id="p122-official", feed_url="https://official.example/feed"):
    return PublicFeedAdapterV2(
        transport,
        source_id=source_id,
        source_name=f"Source {source_id}",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url=feed_url,
        adapter_id=f"{source_id}-rss-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        reliability="official",
        max_entries=20,
    )


def _approve(runtime, adapter, *, adapter_version=None, domain=None, availability="ACTIVE"):
    service = SourcePortfolioService(runtime)
    service.register_source_identity(
        adapter.source_id,
        source_name=adapter.source_name,
        source_class=adapter.source_class,
        reliability=getattr(adapter, "reliability", "external"),
    )
    host = domain or urlparse(adapter.request_base_url).hostname
    return service.record_version(
        adapter.source_id,
        source_name=adapter.source_name,
        publisher_name=adapter.source_name,
        source_class=adapter.source_class,
        source_role=getattr(adapter, "source_role", "OFFICIAL"),
        region_scope=("GLOBAL",),
        language_scope=("en",),
        access_mode="PUBLIC_ANONYMOUS",
        cost_mode="FREE",
        authentication_mode="NONE",
        expected_freshness_minutes=60,
        collection_cadence_minutes=60,
        adapter_id=adapter.adapter_id,
        adapter_version=adapter_version or adapter.adapter_version,
        outbound_domains=(host,),
        outbound_protocols=("HTTPS",),
        availability_state=availability,
        data_classification="PUBLIC",
        origin_characteristics="Publisher/source identity does not by itself establish underlying origin.",
        independence_constraints="Reposts, citations and translations are not independent by default.",
        owner="KGM owner",
        reviewer="KGM owner",
        review_status="APPROVED",
        reviewed_at=NOW,
        created_at=NOW,
    )


def test_public_request_rejects_non_https_credentials_and_fragments():
    with pytest.raises(ValueError, match="require HTTPS"):
        AdapterRequest("http://example.org/feed", {})
    with pytest.raises(ValueError, match="credentials"):
        AdapterRequest("https://user:pass@example.org/feed", {})
    with pytest.raises(ValueError, match="fragment"):
        AdapterRequest("https://example.org/feed#section", {})
    with pytest.raises(ValueError, match="credential-bearing"):
        AdapterRequest("https://example.org/feed", {"Authorization": "Bearer secret"})


def test_read_only_transport_enforces_response_bound(monkeypatch):
    called = []

    def fake_urlopen(request, timeout):
        called.append((request.get_method(), request.full_url, timeout))
        return _UrlOpenResponse(b"x" * 11)

    monkeypatch.setattr("kgeopolitical_monitor.adapter_framework.urlopen", fake_urlopen)
    transport = ReadOnlyHttpsTransportV2(timeout_seconds=2, max_bytes=10)

    with pytest.raises(RuntimeError, match="exceeds configured size"):
        transport.get("https://example.org/feed")

    assert called == [("GET", "https://example.org/feed", 2.0)]


def test_rss_and_atom_fixtures_parse_deterministically():
    rss = parse_rss_atom((FIXTURES / "feed.rss.xml").read_bytes(), max_entries=10)
    atom = parse_rss_atom((FIXTURES / "feed.atom.xml").read_bytes(), max_entries=10)

    assert [record.feed_format for record in rss] == ["RSS", "RSS"]
    assert rss[0].title == "Ukraine security official update"
    assert rss[0].url == "https://official.example/items/1"
    assert rss[0].published_raw == "Tue, 01 Sep 2026 11:30:00 GMT"

    assert [record.feed_format for record in atom] == ["ATOM", "ATOM"]
    assert atom[0].title == "Ukraine security Atom update"
    assert atom[0].url == "https://official.example/atom/1"
    assert atom[0].published_raw == "2026-09-01T11:35:00Z"


def test_feed_parser_fails_closed_and_bounds_entries():
    with pytest.raises(RuntimeError, match="not valid XML"):
        parse_rss_atom(b"<rss>")
    with pytest.raises(RuntimeError, match="neither RSS nor Atom"):
        parse_rss_atom(b"<html><body>not a feed</body></html>")

    records = parse_rss_atom((FIXTURES / "feed.rss.xml").read_bytes(), max_entries=1)
    assert len(records) == 1


def test_json_fixture_is_bounded_and_shape_checked():
    body = (FIXTURES / "gdelt.json").read_bytes()
    records = parse_json_list(body, list_field="articles", max_records=1)
    assert len(records) == 1
    assert records[0]["title"] == "Ukraine security discovery item"

    with pytest.raises(RuntimeError, match="root must be an object"):
        parse_json_list(b"[]", list_field="articles")
    with pytest.raises(RuntimeError, match="does not contain list field"):
        parse_json_list(b"{}", list_field="articles")


def test_feed_adapter_filters_query_and_stable_identity():
    transport = FixtureTransport(
        HttpResponse(
            body=(FIXTURES / "feed.rss.xml").read_bytes(),
            content_type="application/rss+xml",
        )
    )
    adapter = _feed_adapter(transport)

    runtime_watch = type("Watch", (), {"query": "Ukraine security"})()
    first = adapter.fetch(runtime_watch, NOW)
    second = adapter.fetch(runtime_watch, NOW)

    assert len(first) == 1
    assert first[0].item_id == second[0].item_id
    assert first[0].source_id == adapter.source_id
    assert first[0].metadata["adapter_framework_version"] == ADAPTER_FRAMEWORK_VERSION
    assert first[0].metadata["feed_format"] == "RSS"
    assert adapter.adapter_identity.endswith(f"@{ADAPTER_FRAMEWORK_VERSION}")
    assert adapter.last_request_locator == "https://official.example/feed"


def test_gdelt_v2_request_and_mapping_are_deterministic():
    payload = HttpResponse(
        body=(FIXTURES / "gdelt.json").read_bytes(),
        content_type="application/json",
    )
    transport = FixtureTransport(payload)
    adapter = GdeltDoc2AdapterV2(transport, max_records=5, timespan="24h")
    runtime_watch = type("Watch", (), {"query": "Ukraine security"})()

    first = adapter.fetch(runtime_watch, NOW)
    second = adapter.fetch(runtime_watch, NOW)

    assert first[0].item_id == second[0].item_id
    assert first[0].summary.endswith("publisher domain: example.org.")
    assert transport.urls[0] == transport.urls[1]
    assert "query=Ukraine+security" in transport.urls[0]
    assert "maxrecords=5" in transport.urls[0]
    assert adapter.last_request_locator == transport.urls[-1]


def test_framework_collector_requires_p12_1_portfolio_record(tmp_path):
    runtime = _runtime(tmp_path)
    adapter = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        )
    )

    with pytest.raises(RuntimeError, match="no source-portfolio record"):
        FrameworkLiveSourceCollector(runtime, [adapter])


def test_framework_collector_fails_closed_on_adapter_or_domain_drift(tmp_path):
    runtime = _runtime(tmp_path)
    adapter = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        )
    )
    _approve(runtime, adapter, adapter_version="obsolete-version")

    with pytest.raises(RuntimeError, match="identity/version mismatch"):
        FrameworkLiveSourceCollector(runtime, [adapter])

    runtime2 = _runtime(tmp_path / "second")
    adapter2 = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        ),
        source_id="p122-domain",
    )
    _approve(runtime2, adapter2, domain="other.example")

    with pytest.raises(RuntimeError, match="hostname is not approved"):
        FrameworkLiveSourceCollector(runtime2, [adapter2])


def test_framework_collector_persists_approved_public_source(tmp_path):
    runtime = _runtime(tmp_path)
    adapter = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        )
    )
    record = _approve(runtime, adapter)
    collector = FrameworkLiveSourceCollector(runtime, [adapter])

    report = collector.collect("watch-p122", NOW)

    assert report.status == "COMPLETED"
    assert report.item_count == 1
    assert collector.audit.get(report.collection_id) == report
    assert record.activates_collection is False
    assert record.establishes_independence is False
    assert record.changes_verification_state is False
    assert record.changes_coverage_confidence is False


def test_framework_failure_isolation_preserves_other_source(tmp_path):
    runtime = _runtime(tmp_path)
    good = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        ),
        source_id="p122-good",
        feed_url="https://good.example/feed",
    )
    failing = _feed_adapter(
        FixtureTransport(RuntimeError("fixture source unavailable")),
        source_id="p122-failing",
        feed_url="https://failing.example/feed",
    )
    _approve(runtime, good)
    _approve(runtime, failing)

    report = FrameworkLiveSourceCollector(runtime, [good, failing]).collect(
        "watch-p122",
        NOW,
    )

    assert report.status == "PARTIAL"
    assert report.source_success_count == 1
    assert report.source_failure_count == 1
    assert report.failures == (
        {"source_id": "p122-failing", "error": "fixture source unavailable"},
    )


def test_framework_reproducibility_links_exact_query_and_adapter_version(tmp_path):
    runtime = _runtime(tmp_path)
    adapter = _feed_adapter(
        FixtureTransport(
            HttpResponse(
                body=(FIXTURES / "feed.rss.xml").read_bytes(),
                content_type="application/rss+xml",
            )
        ),
        source_id="p122-repro",
        feed_url="https://repro.example/feed",
    )
    _approve(runtime, adapter)

    instrumented = ReproducibilityInstrumentedCollector(
        FrameworkLiveSourceCollector(runtime, [adapter])
    )
    report = instrumented.collect("watch-p122", NOW)
    bundle = ReproducibilityStore(runtime.database_path).bundle_for_collection(
        report.collection_id
    )

    assert bundle is not None
    query = bundle["query_executions"][0]
    assert query["source_id"] == adapter.source_id
    assert query["adapter_version"] == ADAPTER_FRAMEWORK_VERSION
    assert query["exact_query"] == "Ukraine security"
    assert query["attempt_status"] == "SUCCESS"
    assert query["request_locator"] is None
    assert query["request_locator_capture_state"] == "NOT_INSTRUMENTED"
