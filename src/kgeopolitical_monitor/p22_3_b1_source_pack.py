"""P22.3 B1 governed institutional source pack.

Stage-1 readiness only. Importing or building this pack does not activate the
sources in a deployed runtime. Repository governance activation is performed
separately only after measured health and full P20.5 readiness PASS.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
from hashlib import sha256
from html.parser import HTMLParser
from io import StringIO
from typing import Iterable
from urllib.parse import urljoin, urlparse

from .adapter_framework import ADAPTER_FRAMEWORK_VERSION, AdapterRequest, PublicHttpTransport
from .live_sources import LiveSourceItem
from .operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService


P22_3_B1_VERSION = "P22.3-B1-1.0"
B1_REPOSITORY_ACTIVE_SOURCE_IDS: tuple[str, ...] = (
    "ofac-recent-actions-en",
    "white-house-briefings-en",
)


@dataclass(frozen=True)
class B1SourceSpec:
    source_id: str
    source_name: str
    publisher_name: str
    source_type: str
    source_class: str
    source_role: str
    endpoint: str
    adapter_id: str
    parser_kind: str
    region_scope: tuple[str, ...]
    language_scope: tuple[str, ...]
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    origin_group_id: str
    terms_notes: str

    @property
    def outbound_domain(self) -> str:
        return str(urlparse(self.endpoint).hostname or "").lower()


B1_SOURCES: tuple[B1SourceSpec, ...] = (
    B1SourceSpec(
        source_id="ofac-recent-actions-en",
        source_name="U.S. Treasury OFAC Recent Actions",
        publisher_name="U.S. Department of the Treasury — OFAC",
        source_type="SANCTIONS_REGULATORY",
        source_class="Official sources",
        source_role="OFFICIAL",
        endpoint="https://ofac.treasury.gov/recent-actions",
        adapter_id="ofac-recent-actions-html",
        parser_kind="HTML_LINKS",
        region_scope=("GLOBAL",),
        language_scope=("en",),
        expected_freshness_minutes=480,
        collection_cadence_minutes=240,
        origin_group_id="official:us-treasury-ofac",
        terms_notes="Public anonymous official Recent Actions page. OFAC RSS retirement is preserved; this adapter does not depend on the retired feed.",
    ),
    B1SourceSpec(
        source_id="uk-sanctions-list-en",
        source_name="UK Sanctions List",
        publisher_name="UK Foreign, Commonwealth & Development Office",
        source_type="SANCTIONS_REGULATORY",
        source_class="Official sources",
        source_role="OFFICIAL",
        endpoint="https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.csv",
        adapter_id="uk-sanctions-list-csv",
        parser_kind="CSV_SANCTIONS",
        region_scope=("GLOBAL",),
        language_scope=("en",),
        expected_freshness_minutes=480,
        collection_cadence_minutes=240,
        origin_group_id="official:uk-fcdo",
        terms_notes="Public anonymous official UK Sanctions List CSV distribution.",
    ),
    B1SourceSpec(
        source_id="russian-government-news-ru",
        source_name="Government of Russia — News",
        publisher_name="Government of the Russian Federation",
        source_type="OFFICIAL_GOVERNMENT",
        source_class="Official sources",
        source_role="OFFICIAL",
        endpoint="https://government.ru/news/",
        adapter_id="russian-government-news-html",
        parser_kind="HTML_LINKS",
        region_scope=("RUSSIA",),
        language_scope=("ru",),
        expected_freshness_minutes=240,
        collection_cadence_minutes=120,
        origin_group_id="official:russian-government",
        terms_notes="Public anonymous official government news index. Item claims remain official-statement evidence only.",
    ),
    B1SourceSpec(
        source_id="white-house-briefings-en",
        source_name="The White House — Briefings & Statements",
        publisher_name="The White House",
        source_type="OFFICIAL_GOVERNMENT",
        source_class="Official sources",
        source_role="OFFICIAL",
        endpoint="https://www.whitehouse.gov/briefings-statements/",
        adapter_id="white-house-briefings-html",
        parser_kind="HTML_LINKS",
        region_scope=("UNITED_STATES",),
        language_scope=("en",),
        expected_freshness_minutes=240,
        collection_cadence_minutes=120,
        origin_group_id="official:us-white-house",
        terms_notes="Public anonymous official Briefings & Statements index. Item claims remain official-statement evidence only.",
    ),
)


def b1_by_id() -> dict[str, B1SourceSpec]:
    return {s.source_id: s for s in B1_SOURCES}


def _stable_id(source_id: str, identity: str) -> str:
    return "p223-" + sha256(f"{source_id}\n{identity}".encode("utf-8")).hexdigest()[:24]


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            title = " ".join(" ".join(self._text).split())
            if title:
                self.links.append((str(self._href), title))
            self._href = None
            self._text = []


class InstitutionalHtmlListingAdapter:
    def __init__(self, transport: PublicHttpTransport, spec: B1SourceSpec, *, max_entries: int = 100):
        self.transport = transport
        self.spec = spec
        self.source_id = spec.source_id
        self.source_name = spec.source_name
        self.source_class = spec.source_class
        self.source_role = spec.source_role
        self.endpoint = AdapterRequest(url=spec.endpoint, headers={}).url
        self.adapter_id = spec.adapter_id
        self.adapter_version = ADAPTER_FRAMEWORK_VERSION
        self.max_entries = int(max_entries)
        self.last_request_locator: str | None = None

    @property
    def request_base_url(self) -> str:
        return self.endpoint

    @property
    def adapter_identity(self) -> str:
        return f"{self.adapter_id}@{self.adapter_version}"

    def _accept_url(self, absolute_url: str) -> bool:
        p = urlparse(absolute_url)
        base = urlparse(self.endpoint)
        if p.scheme not in {"http", "https"} or p.hostname != base.hostname:
            return False
        path = p.path.rstrip("/")
        if self.source_id == "ofac-recent-actions-en":
            return path.startswith("/recent-actions/") and path != "/recent-actions"
        if self.source_id == "russian-government-news-ru":
            return path.startswith("/news/") and path != "/news"
        if self.source_id == "white-house-briefings-en":
            return path.startswith("/briefings-statements/") and path != "/briefings-statements"
        return False

    def fetch(self, watch: MonitoringWatch, collected_at) -> list[LiveSourceItem]:
        ts = _normalize_time(collected_at)
        self.last_request_locator = self.endpoint
        response = self.transport.get(
            self.endpoint,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "User-Agent": f"K-Geopolitical-Monitor/{P22_3_B1_VERSION}",
            },
        )
        text = response.body.decode("utf-8", errors="replace")
        parser = _AnchorParser()
        parser.feed(text)
        dedup: dict[str, str] = {}
        for href, title in parser.links:
            absolute = urljoin(self.endpoint, href)
            if self._accept_url(absolute):
                dedup.setdefault(absolute, title)
        items = [
            LiveSourceItem(
                item_id=_stable_id(self.source_id, url),
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=title,
                summary=title,
                original_url=url,
                collected_at=ts,
                metadata={
                    "adapter_id": self.adapter_id,
                    "adapter_version": self.adapter_version,
                    "adapter_framework_version": ADAPTER_FRAMEWORK_VERSION,
                    "origin_group_id": self.spec.origin_group_id,
                    "official_statement_boundary": True,
                },
                reliability="official",
            )
            for url, title in list(dedup.items())[: self.max_entries]
        ]
        return sorted(items, key=lambda x: x.item_id)


class UkSanctionsCsvAdapter:
    def __init__(self, transport: PublicHttpTransport, spec: B1SourceSpec, *, max_entries: int = 200):
        self.transport = transport
        self.spec = spec
        self.source_id = spec.source_id
        self.source_name = spec.source_name
        self.source_class = spec.source_class
        self.source_role = spec.source_role
        self.endpoint = AdapterRequest(url=spec.endpoint, headers={}).url
        self.adapter_id = spec.adapter_id
        self.adapter_version = ADAPTER_FRAMEWORK_VERSION
        self.max_entries = int(max_entries)
        self.last_request_locator: str | None = None

    @property
    def request_base_url(self) -> str:
        return self.endpoint

    @property
    def adapter_identity(self) -> str:
        return f"{self.adapter_id}@{self.adapter_version}"

    def fetch(self, watch: MonitoringWatch, collected_at) -> list[LiveSourceItem]:
        ts = _normalize_time(collected_at)
        self.last_request_locator = self.endpoint
        response = self.transport.get(
            self.endpoint,
            headers={
                "Accept": "text/csv,text/plain",
                "User-Agent": f"K-Geopolitical-Monitor/{P22_3_B1_VERSION}",
            },
        )
        decoded = response.body.decode("utf-8-sig", errors="strict")
        reader = csv.DictReader(StringIO(decoded))
        items: list[LiveSourceItem] = []
        for row_number, row in enumerate(reader, start=1):
            normalized = {str(k or "").strip().lower(): str(v or "").strip() for k, v in row.items()}
            name = next((normalized[k] for k in ("name 6", "name", "name_6", "individual, entity, ship") if normalized.get(k)), "")
            unique_id = next((normalized[k] for k in ("unique id", "unique_id", "uk sanctions list ref", "group id") if normalized.get(k)), "")
            regime = next((normalized[k] for k in ("regime name", "regime", "sanctions regime") if normalized.get(k)), "")
            if not name:
                continue
            identity = unique_id or f"row-{row_number}:{name}:{regime}"
            original_url = "https://www.gov.uk/government/publications/the-uk-sanctions-list"
            items.append(
                LiveSourceItem(
                    item_id=_stable_id(self.source_id, identity),
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title=name,
                    summary=f"UK Sanctions List designation; regime: {regime or 'unspecified'}.",
                    original_url=original_url,
                    collected_at=ts,
                    metadata={
                        "adapter_id": self.adapter_id,
                        "adapter_version": self.adapter_version,
                        "adapter_framework_version": ADAPTER_FRAMEWORK_VERSION,
                        "origin_group_id": self.spec.origin_group_id,
                        "unique_id": unique_id,
                        "regime": regime,
                        "official_statement_boundary": True,
                    },
                    reliability="official",
                )
            )
            if len(items) >= self.max_entries:
                break
        return sorted(items, key=lambda x: x.item_id)


def build_b1_adapters(
    transport: PublicHttpTransport,
    *,
    enabled_source_ids: Iterable[str] | None = None,
    max_entries: int = 100,
) -> list[object]:
    by_id = b1_by_id()
    enabled = set(by_id) if enabled_source_ids is None else {str(x) for x in enabled_source_ids}
    unknown = enabled - set(by_id)
    if unknown:
        raise ValueError(f"unknown P22.3 B1 source id(s): {sorted(unknown)}")
    adapters: list[object] = []
    for spec in B1_SOURCES:
        if spec.source_id not in enabled:
            continue
        if spec.parser_kind == "CSV_SANCTIONS":
            adapters.append(UkSanctionsCsvAdapter(transport, spec, max_entries=max_entries))
        else:
            adapters.append(InstitutionalHtmlListingAdapter(transport, spec, max_entries=max_entries))
    return adapters


OFFICIAL_INDEPENDENCE_CONSTRAINT = (
    "Direct institutional publication establishes what the institution published; "
    "it does not automatically establish the truth of the underlying event claim. "
    "Factual independence remains evidence-bound under P13.5/P13.6."
)


def _governance_matches(record: SourcePortfolioRecord, spec: B1SourceSpec) -> bool:
    return (
        record.source_id == spec.source_id
        and record.source_name == spec.source_name
        and record.publisher_name == spec.publisher_name
        and record.source_class == spec.source_class
        and record.source_role == spec.source_role
        and record.region_scope == tuple(sorted(set(spec.region_scope)))
        and record.language_scope == tuple(sorted(set(spec.language_scope)))
        and record.access_mode == "PUBLIC_ANONYMOUS"
        and record.cost_mode == "FREE"
        and record.authentication_mode == "NONE"
        and record.expected_freshness_minutes == spec.expected_freshness_minutes
        and record.collection_cadence_minutes == spec.collection_cadence_minutes
        and record.adapter_id == spec.adapter_id
        and record.adapter_version == ADAPTER_FRAMEWORK_VERSION
        and record.outbound_domains == (spec.outbound_domain,)
        and record.outbound_protocols == ("HTTPS",)
        and record.availability_state == "ACTIVE"
        and record.data_classification == "PUBLIC"
        and record.review_status == "APPROVED"
        and record.paid_provider_approved is False
    )


def install_b1_governance(
    runtime: OperationalMonitoringRuntime,
    *,
    reviewed_at: datetime,
    enabled_source_ids: Iterable[str] = B1_REPOSITORY_ACTIVE_SOURCE_IDS,
    owner: str = "KGM owner",
    reviewer: str = "KGM owner",
) -> tuple[SourcePortfolioRecord, ...]:
    """Install only the B1 sources that passed live-health + P20.5 readiness.

    UKSL and Government of Russia remain hard-blocked in this version. Attempting
    to activate either one fails closed even though their probe adapters remain
    available for later repair/revalidation.
    """
    enabled = {str(x) for x in enabled_source_ids}
    approved = set(B1_REPOSITORY_ACTIVE_SOURCE_IDS)
    disallowed = enabled - approved
    if disallowed:
        raise ValueError(
            "P22.3 B1 source is not approved for repository activation: "
            + ", ".join(sorted(disallowed))
        )

    specs = b1_by_id()
    t = _normalize_time(reviewed_at)
    svc = SourcePortfolioService(runtime)
    out: list[SourcePortfolioRecord] = []

    for source_id in B1_REPOSITORY_ACTIVE_SOURCE_IDS:
        if source_id not in enabled:
            continue
        spec = specs[source_id]
        svc.register_source_identity(
            source_id,
            source_name=spec.source_name,
            source_class=spec.source_class,
            reliability="official",
        )
        current = svc.current(source_id)
        if current is not None:
            if not _governance_matches(current, spec):
                raise RuntimeError(
                    f"P22.3 B1 source portfolio drift requires explicit review: {source_id}"
                )
            out.append(current)
            continue

        out.append(
            svc.record_version(
                source_id,
                source_name=spec.source_name,
                publisher_name=spec.publisher_name,
                source_class=spec.source_class,
                source_role=spec.source_role,
                region_scope=spec.region_scope,
                language_scope=spec.language_scope,
                access_mode="PUBLIC_ANONYMOUS",
                cost_mode="FREE",
                authentication_mode="NONE",
                expected_freshness_minutes=spec.expected_freshness_minutes,
                collection_cadence_minutes=spec.collection_cadence_minutes,
                adapter_id=spec.adapter_id,
                adapter_version=ADAPTER_FRAMEWORK_VERSION,
                outbound_domains=(spec.outbound_domain,),
                outbound_protocols=("HTTPS",),
                fallback_source_ids=(),
                availability_state="ACTIVE",
                data_classification="PUBLIC",
                origin_characteristics=(
                    f"Direct official institutional publication stream; "
                    f"origin_group_id={spec.origin_group_id}."
                ),
                independence_constraints=OFFICIAL_INDEPENDENCE_CONSTRAINT,
                terms_notes=spec.terms_notes,
                owner=owner,
                reviewer=reviewer,
                review_status="APPROVED",
                paid_provider_approved=False,
                reviewed_at=t,
                created_at=t,
            )
        )
    return tuple(out)
