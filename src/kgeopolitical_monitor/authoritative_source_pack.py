"""Phase 12 P12.3 priority authoritative public-source pack.

This module defines an explicit, public/free-first source pack over the validated
P12.1 source-portfolio contract and P12.2 governed adapter framework. It does
not make source count an independent-origin count and does not promote factual
verification, coverage confidence or production/live state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping
from urllib.parse import urlparse

from .adapter_framework import (
    ADAPTER_FRAMEWORK_VERSION,
    FrameworkLiveSourceCollector,
    PublicFeedAdapterV2,
    PublicHttpTransport,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService


AUTHORITATIVE_SOURCE_PACK_VERSION = "P12.3-1.1"


@dataclass(frozen=True)
class AuthoritativeSourceSpec:
    source_id: str
    source_name: str
    publisher_name: str
    source_class: str
    source_role: str
    feed_url: str
    adapter_id: str
    adapter_version: str
    region_scope: tuple[str, ...]
    language_scope: tuple[str, ...]
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    reliability: str
    availability_state: str
    origin_characteristics: str
    independence_constraints: str
    terms_notes: str

    def __post_init__(self) -> None:
        if self.availability_state not in {"ACTIVE", "DEGRADED"}:
            raise ValueError("P12.3 pack availability_state must be ACTIVE or DEGRADED")

    @property
    def outbound_domain(self) -> str:
        return str(urlparse(self.feed_url).hostname or "").lower()

    @property
    def access_mode(self) -> str:
        return "PUBLIC_ANONYMOUS"

    @property
    def cost_mode(self) -> str:
        return "FREE"

    @property
    def data_classification(self) -> str:
        return "PUBLIC"

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def changes_coverage_confidence(self) -> bool:
        return False


_COMMON_ORIGIN = (
    "Official institutional publisher; an item establishes what the institution "
    "published or stated, not automatically the truth of every underlying event claim."
)
_COMMON_INDEPENDENCE = (
    "Publication/source identity is not independent-origin credit. Reposts, citations, "
    "translations and statements derived from the same underlying origin must be clustered."
)


AUTHORITATIVE_SOURCE_PACK: tuple[AuthoritativeSourceSpec, ...] = (
    AuthoritativeSourceSpec(
        source_id="eu-commission-press-corner",
        source_name="European Commission Press Corner",
        publisher_name="European Commission",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url="https://ec.europa.eu/commission/presscorner/api/rss",
        adapter_id="ec-presscorner-rss-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("EU", "EUROPE"),
        language_scope=("en",),
        expected_freshness_minutes=120,
        collection_cadence_minutes=60,
        reliability="official",
        availability_state="ACTIVE",
        origin_characteristics=_COMMON_ORIGIN,
        independence_constraints=_COMMON_INDEPENDENCE,
        terms_notes="Public European Commission press-corner syndication endpoint; public/non-sensitive only.",
    ),
    AuthoritativeSourceSpec(
        source_id="eu-parliament-press-releases",
        source_name="European Parliament Press Releases",
        publisher_name="European Parliament",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url="https://www.europarl.europa.eu/rss/doc/press-releases/en.xml",
        adapter_id="ep-press-releases-rss-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("EU", "EUROPE"),
        language_scope=("en",),
        expected_freshness_minutes=240,
        collection_cadence_minutes=120,
        reliability="official",
        availability_state="DEGRADED",
        origin_characteristics=_COMMON_ORIGIN,
        independence_constraints=_COMMON_INDEPENDENCE,
        terms_notes=(
            "Official European Parliament press-release RSS endpoint. Controlled-live "
            "validation on 2026-09-01 returned anti-bot HTML to the unattended runner, so "
            "the source remains governed but DEGRADED for unattended RSS acquisition."
        ),
    ),
    AuthoritativeSourceSpec(
        source_id="uk-government-news-communications",
        source_name="UK Government News and Communications",
        publisher_name="Government of the United Kingdom",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url="https://www.gov.uk/search/news-and-communications.atom",
        adapter_id="govuk-news-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("UNITED_KINGDOM", "EUROPE"),
        language_scope=("en",),
        expected_freshness_minutes=120,
        collection_cadence_minutes=60,
        reliability="official",
        availability_state="ACTIVE",
        origin_characteristics=_COMMON_ORIGIN,
        independence_constraints=_COMMON_INDEPENDENCE,
        terms_notes="Public GOV.UK news-and-communications Atom feed; broad government scope is filtered by watch query.",
    ),
    AuthoritativeSourceSpec(
        source_id="osce-latest-news",
        source_name="OSCE Latest News",
        publisher_name="Organization for Security and Co-operation in Europe",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url="https://feeds.osce.org/OSCELatestNews",
        adapter_id="osce-latest-rss-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("OSCE", "EUROPE", "EURASIA"),
        language_scope=("en",),
        expected_freshness_minutes=180,
        collection_cadence_minutes=60,
        reliability="official",
        availability_state="ACTIVE",
        origin_characteristics=_COMMON_ORIGIN,
        independence_constraints=_COMMON_INDEPENDENCE,
        terms_notes="Public OSCE latest-news syndication endpoint; availability remains measurable operational state.",
    ),
)


def source_pack_specs() -> tuple[AuthoritativeSourceSpec, ...]:
    return AUTHORITATIVE_SOURCE_PACK


def source_pack_by_id() -> Mapping[str, AuthoritativeSourceSpec]:
    return {spec.source_id: spec for spec in AUTHORITATIVE_SOURCE_PACK}


def build_source_pack_adapters(
    transport: PublicHttpTransport,
    *,
    max_entries: int = 200,
) -> list[PublicFeedAdapterV2]:
    adapters: list[PublicFeedAdapterV2] = []
    for spec in AUTHORITATIVE_SOURCE_PACK:
        adapters.append(
            PublicFeedAdapterV2(
                transport,
                source_id=spec.source_id,
                source_name=spec.source_name,
                source_class=spec.source_class,
                source_role=spec.source_role,
                feed_url=spec.feed_url,
                adapter_id=spec.adapter_id,
                adapter_version=spec.adapter_version,
                reliability=spec.reliability,
                max_entries=max_entries,
                query_filter=True,
            )
        )
    return adapters


def _record_matches_spec(record: SourcePortfolioRecord, spec: AuthoritativeSourceSpec) -> bool:
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
        and record.adapter_version == spec.adapter_version
        and record.outbound_domains == (spec.outbound_domain,)
        and record.outbound_protocols == ("HTTPS",)
        and record.availability_state == spec.availability_state
        and record.data_classification == "PUBLIC"
        and record.origin_characteristics == spec.origin_characteristics
        and record.independence_constraints == spec.independence_constraints
        and record.review_status == "APPROVED"
        and not record.paid_provider_approved
    )


def install_source_pack_governance(
    runtime: OperationalMonitoringRuntime,
    *,
    reviewed_at: datetime,
    owner: str = "KGM owner",
    reviewer: str = "KGM owner",
) -> tuple[SourcePortfolioRecord, ...]:
    """Install exact P12.3 governance records; fail closed on pre-existing drift.

    The operation is idempotent. Existing matching records are reused. Existing
    mismatched records are never silently superseded because source activation
    and governance changes must remain explicit.
    """

    timestamp = _normalize_time(reviewed_at)
    service = SourcePortfolioService(runtime)
    records: list[SourcePortfolioRecord] = []

    for spec in AUTHORITATIVE_SOURCE_PACK:
        service.register_source_identity(
            spec.source_id,
            source_name=spec.source_name,
            source_class=spec.source_class,
            reliability=spec.reliability,
        )
        current = service.current(spec.source_id)
        if current is not None:
            if not _record_matches_spec(current, spec):
                raise RuntimeError(
                    f"P12.3 source portfolio drift requires explicit review: {spec.source_id}"
                )
            records.append(current)
            continue

        records.append(
            service.record_version(
                spec.source_id,
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
                adapter_version=spec.adapter_version,
                outbound_domains=(spec.outbound_domain,),
                outbound_protocols=("HTTPS",),
                fallback_source_ids=(),
                availability_state=spec.availability_state,
                data_classification="PUBLIC",
                origin_characteristics=spec.origin_characteristics,
                independence_constraints=spec.independence_constraints,
                terms_notes=spec.terms_notes,
                owner=owner,
                reviewer=reviewer,
                review_status="APPROVED",
                paid_provider_approved=False,
                reviewed_at=timestamp,
                created_at=timestamp,
            )
        )

    return tuple(records)


def build_governed_source_pack_collector(
    runtime: OperationalMonitoringRuntime,
    transport: PublicHttpTransport,
    *,
    max_entries: int = 200,
) -> FrameworkLiveSourceCollector:
    """Build a collector only after P12.3 governance has been explicitly installed."""

    return FrameworkLiveSourceCollector(
        runtime,
        build_source_pack_adapters(transport, max_entries=max_entries),
    )
