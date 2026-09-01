"""Phase 12 P12.2 reusable governed public adapter framework.

The framework is additive over the validated M7 live-source collector. It provides
bounded read-only HTTPS acquisition, deterministic RSS/Atom/JSON parsing,
explicit adapter identity/version, P12.1 source-portfolio enforcement and a
collector surface compatible with the existing reproducibility wrapper.

The framework does not activate sources by itself and does not change evidence,
verification, provenance-independence or coverage truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import html
import json
import re
from typing import Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .controlled_pilot import APPROVED_SOURCE_CLASSES
from .live_sources import HttpResponse, LiveSourceCollector, LiveSourceItem
from .operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService


ADAPTER_FRAMEWORK_VERSION = "P12.2-2.0"
ALLOWED_OPERATIONAL_STATES = {"ACTIVE", "DEGRADED"}
FORBIDDEN_PUBLIC_HEADERS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "x-api-key",
}


class PublicHttpTransport(Protocol):
    def get(self, url: str, *, headers: dict[str, str] | None = None) -> HttpResponse: ...


@dataclass(frozen=True)
class AdapterRequest:
    url: str
    headers: Mapping[str, str]

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme != "https":
            raise ValueError("P12.2 public adapter requests require HTTPS")
        if not parsed.hostname:
            raise ValueError("P12.2 public adapter request requires a hostname")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("P12.2 public adapter request URL must not contain credentials")
        if parsed.fragment:
            raise ValueError("P12.2 public adapter request URL must not contain a fragment")
        forbidden = {
            str(name).strip().lower()
            for name in self.headers
            if str(name).strip().lower() in FORBIDDEN_PUBLIC_HEADERS
        }
        if forbidden:
            raise ValueError(
                "P12.2 public anonymous adapter request contains credential-bearing header(s): "
                + ", ".join(sorted(forbidden))
            )


class ReadOnlyHttpsTransportV2:
    """Bounded GET-only transport for public anonymous source acquisition."""

    def __init__(self, *, timeout_seconds: float = 15.0, max_bytes: int = 2_000_000):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self.timeout_seconds = float(timeout_seconds)
        self.max_bytes = int(max_bytes)

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> HttpResponse:
        request_spec = AdapterRequest(url=url, headers=headers or {})
        request = Request(
            request_spec.url,
            headers=dict(request_spec.headers),
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read(self.max_bytes + 1)
                if len(body) > self.max_bytes:
                    raise RuntimeError("P12.2 source response exceeds configured size limit")
                return HttpResponse(
                    body=body,
                    content_type=response.headers.get("Content-Type", ""),
                )
        except HTTPError as exc:
            raise RuntimeError(f"P12.2 source HTTP error: {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"P12.2 source network error: {exc.reason}") from exc


@dataclass(frozen=True)
class FeedRecord:
    title: str
    summary: str
    url: str
    published_raw: str | None
    feed_format: str


def _clean_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return " ".join(html.unescape(without_tags).split())


def _local_name(tag: str) -> str:
    return str(tag).rsplit("}", 1)[-1].lower()


def _child_text(element: ET.Element, names: tuple[str, ...]) -> str:
    for child in element:
        if _local_name(child.tag) in names:
            return _clean_text("".join(child.itertext()))
    return ""


def _atom_link(element: ET.Element) -> str:
    for child in element:
        if _local_name(child.tag) != "link":
            continue
        href = str(child.attrib.get("href") or "").strip()
        rel = str(child.attrib.get("rel") or "alternate").strip().lower()
        if href and rel in {"", "alternate"}:
            return href
    return ""


def parse_rss_atom(body: bytes, *, max_entries: int = 200) -> tuple[FeedRecord, ...]:
    if not 1 <= int(max_entries) <= 1000:
        raise ValueError("max_entries must be between 1 and 1000")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        raise RuntimeError("P12.2 feed payload is not valid XML") from exc

    root_name = _local_name(root.tag)
    if root_name == "rss":
        feed_format = "RSS"
        entries = [node for node in root.iter() if _local_name(node.tag) == "item"]
    elif root_name == "feed":
        feed_format = "ATOM"
        entries = [node for node in root if _local_name(node.tag) == "entry"]
    else:
        raise RuntimeError("P12.2 feed payload is neither RSS nor Atom")

    records: list[FeedRecord] = []
    for entry in entries[: int(max_entries)]:
        title = _child_text(entry, ("title",))
        if feed_format == "RSS":
            summary = _child_text(entry, ("description", "summary", "content"))
            url = _child_text(entry, ("link",))
            published_raw = _child_text(entry, ("pubdate", "published", "updated")) or None
        else:
            summary = _child_text(entry, ("summary", "content", "description"))
            url = _atom_link(entry)
            published_raw = _child_text(entry, ("published", "updated")) or None
        if not title or not url:
            continue
        records.append(
            FeedRecord(
                title=title,
                summary=summary or title,
                url=url,
                published_raw=published_raw,
                feed_format=feed_format,
            )
        )
    return tuple(records)


def parse_json_list(
    body: bytes,
    *,
    list_field: str,
    max_records: int = 200,
) -> tuple[dict[str, object], ...]:
    if not str(list_field).strip():
        raise ValueError("list_field must not be empty")
    if not 1 <= int(max_records) <= 1000:
        raise ValueError("max_records must be between 1 and 1000")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("P12.2 JSON payload is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("P12.2 JSON payload root must be an object")
    records = payload.get(list_field)
    if not isinstance(records, list):
        raise RuntimeError(f"P12.2 JSON payload does not contain list field: {list_field}")
    normalized = [record for record in records[: int(max_records)] if isinstance(record, dict)]
    return tuple(normalized)


def _required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_item_id(source_id: str, original_url: str) -> str:
    digest = sha256(f"{source_id}\n{original_url}".encode("utf-8")).hexdigest()[:24]
    return f"p122-{digest}"


def _matches_query(title: str, summary: str, query: str) -> bool:
    terms = [term for term in re.split(r"\s+", query.lower().strip()) if term]
    searchable = f"{title}\n{summary}".lower()
    return bool(terms) and all(term in searchable for term in terms)


class PublicFeedAdapterV2:
    """Reusable RSS/Atom adapter with deterministic source and adapter identity."""

    def __init__(
        self,
        transport: PublicHttpTransport,
        *,
        source_id: str,
        source_name: str,
        source_class: str,
        source_role: str,
        feed_url: str,
        adapter_id: str,
        adapter_version: str,
        reliability: str = "external",
        max_entries: int = 200,
        query_filter: bool = True,
    ) -> None:
        self.transport = transport
        self.source_id = _required(source_id, "source_id")
        self.source_name = _required(source_name, "source_name")
        self.source_class = _required(source_class, "source_class")
        if self.source_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {self.source_class}")
        self.source_role = _required(source_role, "source_role").upper()
        self.feed_url = AdapterRequest(
            url=_required(feed_url, "feed_url"),
            headers={},
        ).url
        self.adapter_id = _required(adapter_id, "adapter_id")
        self.adapter_version = _required(adapter_version, "adapter_version")
        self.reliability = _required(reliability, "reliability")
        if not 1 <= int(max_entries) <= 1000:
            raise ValueError("max_entries must be between 1 and 1000")
        self.max_entries = int(max_entries)
        self.query_filter = bool(query_filter)
        self.last_request_locator: str | None = None

    @property
    def request_base_url(self) -> str:
        return self.feed_url

    @property
    def adapter_identity(self) -> str:
        return f"{self.adapter_id}@{self.adapter_version}"

    def fetch(self, watch: MonitoringWatch, collected_at) -> list[LiveSourceItem]:
        timestamp = _normalize_time(collected_at)
        request = AdapterRequest(
            url=self.feed_url,
            headers={
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
                "User-Agent": f"K-Geopolitical-Monitor adapter-framework/{ADAPTER_FRAMEWORK_VERSION}",
            },
        )
        self.last_request_locator = request.url
        response = self.transport.get(request.url, headers=dict(request.headers))
        records = parse_rss_atom(response.body, max_entries=self.max_entries)

        items: list[LiveSourceItem] = []
        for record in records:
            if self.query_filter and not _matches_query(
                record.title,
                record.summary,
                watch.query,
            ):
                continue
            metadata: dict[str, object] = {
                "adapter_framework_version": ADAPTER_FRAMEWORK_VERSION,
                "adapter_id": self.adapter_id,
                "adapter_version": self.adapter_version,
                "feed_format": record.feed_format,
            }
            if record.published_raw:
                metadata["published_at_raw"] = record.published_raw
            items.append(
                LiveSourceItem(
                    item_id=_stable_item_id(self.source_id, record.url),
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title=record.title,
                    summary=record.summary,
                    original_url=record.url,
                    collected_at=timestamp,
                    metadata=metadata,
                    reliability=self.reliability,
                )
            )
        return sorted(items, key=lambda item: item.item_id)


class PublicJsonListAdapterV2:
    """Base class for bounded public JSON-list adapters."""

    list_field = ""

    def __init__(
        self,
        transport: PublicHttpTransport,
        *,
        source_id: str,
        source_name: str,
        source_class: str,
        source_role: str,
        endpoint: str,
        adapter_id: str,
        adapter_version: str,
        reliability: str = "external",
        max_records: int = 200,
    ) -> None:
        self.transport = transport
        self.source_id = _required(source_id, "source_id")
        self.source_name = _required(source_name, "source_name")
        self.source_class = _required(source_class, "source_class")
        if self.source_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {self.source_class}")
        self.source_role = _required(source_role, "source_role").upper()
        self.endpoint = AdapterRequest(
            url=_required(endpoint, "endpoint"),
            headers={},
        ).url
        self.adapter_id = _required(adapter_id, "adapter_id")
        self.adapter_version = _required(adapter_version, "adapter_version")
        self.reliability = _required(reliability, "reliability")
        if not 1 <= int(max_records) <= 1000:
            raise ValueError("max_records must be between 1 and 1000")
        self.max_records = int(max_records)
        self.last_request_locator: str | None = None

    @property
    def request_base_url(self) -> str:
        return self.endpoint

    @property
    def adapter_identity(self) -> str:
        return f"{self.adapter_id}@{self.adapter_version}"

    def query_parameters(self, watch: MonitoringWatch) -> Mapping[str, object]:
        return {}

    def map_record(self, record: Mapping[str, object], collected_at) -> LiveSourceItem | None:
        raise NotImplementedError

    def fetch(self, watch: MonitoringWatch, collected_at) -> list[LiveSourceItem]:
        timestamp = _normalize_time(collected_at)
        parameters = [
            (str(key), str(value))
            for key, value in self.query_parameters(watch).items()
            if value is not None
        ]
        parameters.sort()
        url = self.endpoint
        if parameters:
            url = f"{self.endpoint}?{urlencode(parameters)}"
        request = AdapterRequest(
            url=url,
            headers={
                "Accept": "application/json",
                "User-Agent": f"K-Geopolitical-Monitor adapter-framework/{ADAPTER_FRAMEWORK_VERSION}",
            },
        )
        self.last_request_locator = request.url
        response = self.transport.get(request.url, headers=dict(request.headers))
        records = parse_json_list(
            response.body,
            list_field=_required(self.list_field, "list_field"),
            max_records=self.max_records,
        )
        items: list[LiveSourceItem] = []
        for record in records:
            item = self.map_record(record, timestamp)
            if item is not None:
                if item.source_id != self.source_id:
                    raise RuntimeError("P12.2 JSON adapter emitted mismatched source_id")
                if item.source_name != self.source_name:
                    raise RuntimeError("P12.2 JSON adapter emitted mismatched source_name")
                if item.source_class != self.source_class:
                    raise RuntimeError("P12.2 JSON adapter emitted mismatched source_class")
                items.append(item)
        return sorted(items, key=lambda item: item.item_id)


class ConsiliumPressReleaseAdapterV2(PublicFeedAdapterV2):
    def __init__(self, transport: PublicHttpTransport, *, max_entries: int = 200) -> None:
        super().__init__(
            transport,
            source_id="consilium-press-releases",
            source_name="Council of the EU / European Council Press Releases",
            source_class="Official sources",
            source_role="OFFICIAL",
            feed_url="https://www.consilium.europa.eu/en/rss/pressreleases.ashx",
            adapter_id="consilium-rss-atom",
            adapter_version=ADAPTER_FRAMEWORK_VERSION,
            reliability="official",
            max_entries=max_entries,
            query_filter=True,
        )


class GdeltDoc2AdapterV2(PublicJsonListAdapterV2):
    list_field = "articles"

    def __init__(
        self,
        transport: PublicHttpTransport,
        *,
        max_records: int = 25,
        timespan: str = "24h",
    ) -> None:
        if not 1 <= int(max_records) <= 100:
            raise ValueError("max_records must be between 1 and 100 for controlled live use")
        self.timespan = _required(timespan, "timespan")
        super().__init__(
            transport,
            source_id="gdelt-doc-2",
            source_name="GDELT DOC 2.0",
            source_class="Structured data",
            source_role="DISCOVERY",
            endpoint="https://api.gdeltproject.org/api/v2/doc/doc",
            adapter_id="gdelt-doc-json",
            adapter_version=ADAPTER_FRAMEWORK_VERSION,
            reliability="discovery-only",
            max_records=max_records,
        )

    def query_parameters(self, watch: MonitoringWatch) -> Mapping[str, object]:
        return {
            "format": "json",
            "maxrecords": self.max_records,
            "mode": "artlist",
            "query": watch.query,
            "sort": "datedesc",
            "timespan": self.timespan,
        }

    def map_record(self, record: Mapping[str, object], collected_at) -> LiveSourceItem | None:
        title = str(record.get("title") or "").strip()
        original_url = str(record.get("url") or "").strip()
        if not title or not original_url:
            return None
        domain = str(record.get("domain") or "").strip()
        metadata = {
            key: record[key]
            for key in ("domain", "seendate", "language", "sourcecountry", "tone")
            if key in record
        }
        metadata.update(
            {
                "adapter_framework_version": ADAPTER_FRAMEWORK_VERSION,
                "adapter_id": self.adapter_id,
                "adapter_version": self.adapter_version,
            }
        )
        return LiveSourceItem(
            item_id=_stable_item_id(self.source_id, original_url),
            source_id=self.source_id,
            source_name=self.source_name,
            source_class=self.source_class,
            title=title,
            summary=(
                "Discovered by GDELT DOC 2.0; publisher domain: "
                f"{domain or 'unknown'}."
            ),
            original_url=original_url,
            collected_at=collected_at,
            metadata=metadata,
            reliability=self.reliability,
        )


def validate_portfolio_for_adapter(
    record: SourcePortfolioRecord,
    adapter: object,
) -> None:
    source_id = _required(getattr(adapter, "source_id", ""), "adapter.source_id")
    source_name = _required(getattr(adapter, "source_name", ""), "adapter.source_name")
    source_class = _required(getattr(adapter, "source_class", ""), "adapter.source_class")
    adapter_id = _required(getattr(adapter, "adapter_id", ""), "adapter.adapter_id")
    adapter_version = _required(
        getattr(adapter, "adapter_version", ""),
        "adapter.adapter_version",
    )
    request_base_url = _required(
        getattr(adapter, "request_base_url", ""),
        "adapter.request_base_url",
    )

    if record.source_id != source_id:
        raise RuntimeError("P12.2 portfolio source_id does not match adapter")
    if record.source_name != source_name or record.source_class != source_class:
        raise RuntimeError("P12.2 portfolio canonical source identity does not match adapter")
    if record.review_status != "APPROVED":
        raise RuntimeError("P12.2 adapter source portfolio is not APPROVED")
    if record.availability_state not in ALLOWED_OPERATIONAL_STATES:
        raise RuntimeError("P12.2 adapter source portfolio is not operational")
    if record.access_mode != "PUBLIC_ANONYMOUS":
        raise RuntimeError("P12.2 public adapter framework requires PUBLIC_ANONYMOUS access")
    if record.authentication_mode != "NONE":
        raise RuntimeError("P12.2 public adapter framework requires authentication NONE")
    if record.data_classification != "PUBLIC":
        raise RuntimeError("P12.2 public adapter framework requires PUBLIC data classification")
    if record.cost_mode == "PAID" and not record.paid_provider_approved:
        raise RuntimeError("P12.2 paid source is not separately approved")
    if record.adapter_id != adapter_id or record.adapter_version != adapter_version:
        raise RuntimeError("P12.2 portfolio adapter identity/version mismatch")
    if "HTTPS" not in record.outbound_protocols:
        raise RuntimeError("P12.2 portfolio does not approve HTTPS egress")

    parsed = urlparse(request_base_url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not hostname:
        raise RuntimeError("P12.2 adapter request base must be HTTPS")
    if hostname not in set(record.outbound_domains):
        raise RuntimeError("P12.2 adapter outbound hostname is not approved by portfolio")


class FrameworkLiveSourceCollector:
    """P12.2 governed facade over the validated M7 LiveSourceCollector."""

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        adapters: list[object],
        *,
        portfolio_service: SourcePortfolioService | None = None,
    ) -> None:
        if not adapters:
            raise ValueError("P12.2 framework collector requires at least one adapter")
        source_ids = [_required(getattr(a, "source_id", ""), "adapter.source_id") for a in adapters]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("P12.2 framework adapter source_id values must be unique")
        self.runtime = runtime
        self.adapters = list(adapters)
        self.portfolio = portfolio_service or SourcePortfolioService(runtime)
        self._collector = LiveSourceCollector(runtime, self.adapters)
        self.audit = self._collector.audit
        self.ingestion = self._collector.ingestion
        self._validate_governance()

    def _validate_governance(self) -> None:
        for adapter in self.adapters:
            record = self.portfolio.current(str(getattr(adapter, "source_id", "")))
            if record is None:
                raise RuntimeError("P12.2 framework adapter has no source-portfolio record")
            validate_portfolio_for_adapter(record, adapter)

    def collect(self, watch_id: str, now):
        self._validate_governance()
        return self._collector.collect(watch_id, now)
