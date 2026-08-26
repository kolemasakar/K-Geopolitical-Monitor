"""M7 live public-source adapters and collection audit."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256
import html
import json
import re
import sqlite3
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4
import xml.etree.ElementTree as ET

from .controlled_pilot import APPROVED_SOURCE_CLASSES
from .operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime, _normalize_time


@dataclass(frozen=True)
class HttpResponse:
    body: bytes
    content_type: str


class HttpTransport(Protocol):
    def get(self, url: str, *, headers: dict[str, str] | None = None) -> HttpResponse: ...


class UrllibHttpTransport:
    def __init__(self, *, timeout_seconds: float = 15.0, max_bytes: int = 2_000_000):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> HttpResponse:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError("live public-source transport requires HTTPS")

        request = Request(url, headers=headers or {}, method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read(self.max_bytes + 1)
                if len(body) > self.max_bytes:
                    raise RuntimeError("live source response exceeds configured size limit")
                content_type = response.headers.get("Content-Type", "")
                return HttpResponse(body=body, content_type=content_type)
        except HTTPError as exc:
            raise RuntimeError(f"live source HTTP error: {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"live source network error: {exc.reason}") from exc


@dataclass(frozen=True)
class LiveSourceItem:
    item_id: str
    source_id: str
    source_name: str
    source_class: str
    title: str
    summary: str
    original_url: str
    collected_at: datetime
    metadata: dict[str, object] = field(default_factory=dict)
    reliability: str = "external"

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.item_id, "item_id"),
            (self.source_id, "source_id"),
            (self.source_name, "source_name"),
            (self.title, "title"),
            (self.original_url, "original_url"),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.source_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {self.source_class}")
        if urlparse(self.original_url).scheme not in {"http", "https"}:
            raise ValueError("original_url must be HTTP or HTTPS")
        _normalize_time(self.collected_at)


class LiveSourceAdapter(Protocol):
    source_id: str
    source_name: str
    source_class: str

    def fetch(self, watch: MonitoringWatch, collected_at: datetime) -> list[LiveSourceItem]: ...


def _stable_item_id(prefix: str, identity: str) -> str:
    digest = sha256(identity.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _clean_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return " ".join(html.unescape(without_tags).split())


def _matches_query(title: str, summary: str, query: str) -> bool:
    terms = [term for term in re.split(r"\s+", query.lower().strip()) if term]
    searchable = f"{title}\n{summary}".lower()
    return bool(terms) and all(term in searchable for term in terms)


class GdeltDoc2Adapter:
    source_id = "gdelt-doc-2"
    source_name = "GDELT DOC 2.0"
    source_class = "Structured data"
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(
        self,
        transport: HttpTransport,
        *,
        max_records: int = 25,
        timespan: str = "24h",
    ):
        if not 1 <= max_records <= 100:
            raise ValueError("max_records must be between 1 and 100 for controlled pilot")
        if not timespan.strip():
            raise ValueError("timespan must not be empty")
        self.transport = transport
        self.max_records = max_records
        self.timespan = timespan

    def fetch(self, watch: MonitoringWatch, collected_at: datetime) -> list[LiveSourceItem]:
        timestamp = _normalize_time(collected_at)
        params = urlencode(
            {
                "query": watch.query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": self.max_records,
                "timespan": self.timespan,
                "sort": "datedesc",
            }
        )
        response = self.transport.get(
            f"{self.endpoint}?{params}",
            headers={
                "Accept": "application/json",
                "User-Agent": "K-Geopolitical-Monitor controlled-pilot/1.0",
            },
        )
        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("GDELT response is not valid JSON") from exc

        articles = payload.get("articles") if isinstance(payload, dict) else None
        if not isinstance(articles, list):
            raise RuntimeError("GDELT response does not contain an articles list")

        items: list[LiveSourceItem] = []
        for article in articles:
            if not isinstance(article, dict):
                continue
            title = str(article.get("title") or "").strip()
            original_url = str(article.get("url") or "").strip()
            if not title or not original_url:
                continue
            domain = str(article.get("domain") or "").strip()
            summary = f"Discovered by GDELT DOC 2.0; publisher domain: {domain or 'unknown'}."
            metadata = {
                key: article[key]
                for key in ("domain", "seendate", "language", "sourcecountry", "tone")
                if key in article
            }
            items.append(
                LiveSourceItem(
                    item_id=_stable_item_id("gdelt", original_url),
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title=title,
                    summary=summary,
                    original_url=original_url,
                    collected_at=timestamp,
                    metadata=metadata,
                    reliability="discovery-only",
                )
            )
        return sorted(items, key=lambda item: item.item_id)


class ConsiliumRssAdapter:
    source_id = "consilium-press-releases"
    source_name = "Council of the EU / European Council Press Releases"
    source_class = "Official sources"
    feed_url = "https://www.consilium.europa.eu/en/rss/pressreleases.ashx"

    def __init__(self, transport: HttpTransport):
        self.transport = transport

    def fetch(self, watch: MonitoringWatch, collected_at: datetime) -> list[LiveSourceItem]:
        timestamp = _normalize_time(collected_at)
        response = self.transport.get(
            self.feed_url,
            headers={
                "Accept": "application/rss+xml, application/xml, text/xml",
                "User-Agent": "K-Geopolitical-Monitor controlled-pilot/1.0",
            },
        )
        try:
            root = ET.fromstring(response.body)
        except ET.ParseError as exc:
            raise RuntimeError("Consilium RSS response is not valid XML") from exc

        items: list[LiveSourceItem] = []
        for entry in root.findall(".//item"):
            title = _clean_text(entry.findtext("title") or "")
            description = _clean_text(entry.findtext("description") or "")
            link = (entry.findtext("link") or "").strip()
            if not title or not link:
                continue
            if not _matches_query(title, description, watch.query):
                continue

            metadata: dict[str, object] = {}
            published_raw = (entry.findtext("pubDate") or "").strip()
            if published_raw:
                try:
                    metadata["published_at"] = _normalize_time(
                        parsedate_to_datetime(published_raw)
                    ).isoformat()
                except (TypeError, ValueError, OverflowError):
                    metadata["published_at_raw"] = published_raw

            items.append(
                LiveSourceItem(
                    item_id=_stable_item_id("consilium", link),
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title=title,
                    summary=description or title,
                    original_url=link,
                    collected_at=timestamp,
                    metadata=metadata,
                    reliability="official",
                )
            )
        return sorted(items, key=lambda item: item.item_id)


@dataclass(frozen=True)
class SourceCollectionReport:
    collection_id: str
    watch_id: str
    status: str
    item_count: int
    source_success_count: int
    source_failure_count: int
    failures: tuple[dict[str, str], ...]
    started_at: datetime
    completed_at: datetime


class LiveSourceIngestionStore:
    def __init__(self, database_path):
        self.database_path = database_path

    def persist(self, collection_id: str, items: list[LiveSourceItem]) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for item in items:
                connection.execute(
                    """
                    INSERT INTO sources(id, name, source_class, reliability)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        source_class = excluded.source_class,
                        reliability = excluded.reliability
                    """,
                    (item.source_id, item.source_name, item.source_class, item.reliability),
                )
                connection.execute(
                    """
                    INSERT INTO raw_items(id, source_id, title, content, collected_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    (
                        item.item_id,
                        item.source_id,
                        item.title,
                        item.summary,
                        _normalize_time(item.collected_at).isoformat(),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO live_source_provenance(
                        raw_item_id, collection_id, original_url, metadata_json
                    ) VALUES (?, ?, ?, ?)
                    ON CONFLICT(raw_item_id, collection_id) DO NOTHING
                    """,
                    (
                        item.item_id,
                        collection_id,
                        item.original_url,
                        json.dumps(item.metadata, sort_keys=True),
                    ),
                )


class SourceCollectionAuditStore:
    def __init__(self, database_path):
        self.database_path = database_path

    def start(self, collection_id: str, watch_id: str, started_at: datetime) -> None:
        timestamp = _normalize_time(started_at).isoformat()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO source_collection_runs(
                    collection_id, watch_id, status, started_at, completed_at,
                    item_count, source_success_count, source_failure_count, failures
                ) VALUES (?, ?, 'RUNNING', ?, ?, 0, 0, 0, '[]')
                """,
                (collection_id, watch_id, timestamp, timestamp),
            )

    def finish(self, report: SourceCollectionReport) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE source_collection_runs
                SET status = ?, completed_at = ?, item_count = ?,
                    source_success_count = ?, source_failure_count = ?, failures = ?
                WHERE collection_id = ?
                """,
                (
                    report.status,
                    _normalize_time(report.completed_at).isoformat(),
                    report.item_count,
                    report.source_success_count,
                    report.source_failure_count,
                    json.dumps(report.failures, sort_keys=True),
                    report.collection_id,
                ),
            )

    def get(self, collection_id: str) -> SourceCollectionReport | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT collection_id, watch_id, status, item_count,
                       source_success_count, source_failure_count, failures,
                       started_at, completed_at
                FROM source_collection_runs
                WHERE collection_id = ?
                """,
                (collection_id,),
            ).fetchone()
        if row is None:
            return None
        return SourceCollectionReport(
            collection_id=row[0],
            watch_id=row[1],
            status=row[2],
            item_count=int(row[3]),
            source_success_count=int(row[4]),
            source_failure_count=int(row[5]),
            failures=tuple(json.loads(row[6])),
            started_at=datetime.fromisoformat(row[7]),
            completed_at=datetime.fromisoformat(row[8]),
        )


class LiveSourceCollector:
    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        adapters: list[LiveSourceAdapter],
    ):
        if not adapters:
            raise ValueError("live source collector requires at least one adapter")
        source_ids = [adapter.source_id for adapter in adapters]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("live source adapter source_id values must be unique")
        self.runtime = runtime
        self.adapters = list(adapters)
        self.ingestion = LiveSourceIngestionStore(runtime.database_path)
        self.audit = SourceCollectionAuditStore(runtime.database_path)

    def collect(self, watch_id: str, now: datetime) -> SourceCollectionReport:
        current = _normalize_time(now)
        watch = self.runtime.repository.get_watch(watch_id)
        if watch is None:
            raise ValueError("watch does not exist")
        if not watch.enabled:
            raise ValueError("disabled watch cannot collect live sources")

        collection_id = f"collection-{uuid4().hex}"
        self.audit.start(collection_id, watch.watch_id, current)

        item_count = 0
        success_count = 0
        failures: list[dict[str, str]] = []
        for adapter in self.adapters:
            try:
                items = list(adapter.fetch(watch, current))
                self.ingestion.persist(collection_id, items)
                item_count += len(items)
                success_count += 1
            except Exception as exc:
                failures.append(
                    {
                        "source_id": adapter.source_id,
                        "error": str(exc).strip() or exc.__class__.__name__,
                    }
                )

        failure_count = len(failures)
        if success_count == 0:
            status = "FAILED"
        elif failure_count:
            status = "PARTIAL"
        else:
            status = "COMPLETED"

        report = SourceCollectionReport(
            collection_id=collection_id,
            watch_id=watch.watch_id,
            status=status,
            item_count=item_count,
            source_success_count=success_count,
            source_failure_count=failure_count,
            failures=tuple(failures),
            started_at=current,
            completed_at=current,
        )
        self.audit.finish(report)
        return report
