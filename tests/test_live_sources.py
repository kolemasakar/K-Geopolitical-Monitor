import json
import sqlite3
from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.live_sources import (
    ConsiliumRssAdapter,
    GdeltDoc2Adapter,
    HttpResponse,
    LiveSourceCollector,
    LiveSourceItem,
    UrllibHttpTransport,
)
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime


class FakeTransport:
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


def _watch(now):
    return MonitoringWatch(
        watch_id="watch-live",
        name="Ukraine security",
        query="Ukraine security",
        cadence_minutes=60,
        created_at=now,
    )


def test_gdelt_adapter_maps_discovery_metadata_without_article_body():
    now = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    payload = {
        "articles": [
            {
                "url": "https://example.org/article-1",
                "title": "Ukraine security update",
                "domain": "example.org",
                "seendate": "20260826T095500Z",
                "language": "English",
                "sourcecountry": "United States",
            }
        ]
    }
    transport = FakeTransport(
        HttpResponse(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
    )
    adapter = GdeltDoc2Adapter(transport, max_records=5, timespan="24h")

    items = adapter.fetch(_watch(now), now)

    assert len(items) == 1
    item = items[0]
    assert item.source_id == "gdelt-doc-2"
    assert item.source_class == "Structured data"
    assert item.original_url == "https://example.org/article-1"
    assert item.summary == "Discovered by GDELT DOC 2.0; publisher domain: example.org."
    assert item.metadata["seendate"] == "20260826T095500Z"
    assert "query=Ukraine+security" in transport.urls[0]
    assert "maxrecords=5" in transport.urls[0]
    assert transport.headers[0]["Accept"] == "application/json"


def test_gdelt_adapter_fails_closed_on_non_json_response():
    now = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    adapter = GdeltDoc2Adapter(
        FakeTransport(HttpResponse(body=b"rate limited", content_type="text/plain"))
    )

    with pytest.raises(RuntimeError, match="not valid JSON"):
        adapter.fetch(_watch(now), now)


def test_consilium_rss_adapter_filters_watch_and_preserves_official_url():
    now = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    xml = b"""<?xml version='1.0' encoding='UTF-8'?>
    <rss version='2.0'><channel>
      <item>
        <title>Ukraine security support statement</title>
        <description><![CDATA[Council statement on Ukraine security support.]]></description>
        <link>https://www.consilium.europa.eu/en/press/example-ukraine/</link>
        <pubDate>Wed, 26 Aug 2026 09:30:00 GMT</pubDate>
      </item>
      <item>
        <title>Agriculture meeting</title>
        <description>Unrelated policy item.</description>
        <link>https://www.consilium.europa.eu/en/press/example-agri/</link>
      </item>
    </channel></rss>"""
    adapter = ConsiliumRssAdapter(
        FakeTransport(HttpResponse(body=xml, content_type="application/rss+xml"))
    )

    items = adapter.fetch(_watch(now), now)

    assert len(items) == 1
    item = items[0]
    assert item.source_id == "consilium-press-releases"
    assert item.source_class == "Official sources"
    assert item.original_url.endswith("example-ukraine/")
    assert item.metadata["published_at"] == "2026-08-26T09:30:00+00:00"


def test_live_source_collector_isolates_failure_and_persists_provenance(tmp_path):
    now = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-live",
        created_at=now,
    )

    class GoodAdapter:
        source_id = "good-official"
        source_name = "Good Official"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return [
                LiveSourceItem(
                    item_id="live-item-1",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title="Ukraine security official update",
                    summary="Official controlled live-source test payload.",
                    original_url="https://official.example/item-1",
                    collected_at=collected_at,
                    metadata={"kind": "test"},
                    reliability="official",
                )
            ]

    class FailingAdapter:
        source_id = "failing-structured"
        source_name = "Failing Structured"
        source_class = "Structured data"

        def fetch(self, watch, collected_at):
            raise RuntimeError("source unavailable")

    collector = LiveSourceCollector(runtime, [GoodAdapter(), FailingAdapter()])
    report = collector.collect("watch-live", now)

    assert report.status == "PARTIAL"
    assert report.item_count == 1
    assert report.source_success_count == 1
    assert report.source_failure_count == 1
    assert report.failures == (
        {"source_id": "failing-structured", "error": "source unavailable"},
    )

    persisted = collector.audit.get(report.collection_id)
    assert persisted == report

    with sqlite3.connect(runtime.database_path) as connection:
        raw = connection.execute(
            "SELECT source_id, title FROM raw_items WHERE id = ?",
            ("live-item-1",),
        ).fetchone()
        provenance = connection.execute(
            """
            SELECT original_url, metadata_json
            FROM live_source_provenance
            WHERE raw_item_id = ? AND collection_id = ?
            """,
            ("live-item-1", report.collection_id),
        ).fetchone()
    assert raw == ("good-official", "Ukraine security official update")
    assert provenance[0] == "https://official.example/item-1"
    assert json.loads(provenance[1]) == {"kind": "test"}


def test_repeated_collection_reuses_raw_item_but_keeps_collection_context(tmp_path):
    now = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-live",
        created_at=now,
    )

    class StableAdapter:
        source_id = "stable-source"
        source_name = "Stable Source"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return [
                LiveSourceItem(
                    item_id="stable-item",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title="Ukraine security update",
                    summary="Stable item.",
                    original_url="https://stable.example/item",
                    collected_at=collected_at,
                    metadata={},
                    reliability="official",
                )
            ]

    collector = LiveSourceCollector(runtime, [StableAdapter()])
    first = collector.collect("watch-live", now)
    second = collector.collect("watch-live", now)

    assert first.status == "COMPLETED"
    assert second.status == "COMPLETED"
    assert first.collection_id != second.collection_id

    with sqlite3.connect(runtime.database_path) as connection:
        raw_count = connection.execute(
            "SELECT COUNT(*) FROM raw_items WHERE id = 'stable-item'"
        ).fetchone()[0]
        provenance_count = connection.execute(
            "SELECT COUNT(*) FROM live_source_provenance WHERE raw_item_id = 'stable-item'"
        ).fetchone()[0]
    assert raw_count == 1
    assert provenance_count == 2


def test_live_transport_rejects_non_https_before_network_access():
    transport = UrllibHttpTransport()

    with pytest.raises(ValueError, match="requires HTTPS"):
        transport.get("http://example.org/feed")
