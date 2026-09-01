"""Phase 12 P12.4 local-language and media discovery source pack.

The pack expands public/free media discovery in an initial uk/ru/pl/tr language
slice over the validated P12.1 source-portfolio contract and P12.2 governed
adapter framework. Original-language text is preserved. Translation remains a
separate derived representation and source/media count is not independent-origin
credit, verification promotion or proof of global language coverage.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping
from urllib.parse import urlparse

from .adapter_framework import (
    ADAPTER_FRAMEWORK_VERSION,
    FrameworkLiveSourceCollector,
    PublicFeedAdapterV2,
    PublicHttpTransport,
)
from .live_sources import LiveSourceItem
from .operational_monitoring import MonitoringWatch, OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService


LOCAL_LANGUAGE_DISCOVERY_PACK_VERSION = "P12.4-1.0"
INITIAL_LANGUAGE_SLICE = ("pl", "ru", "tr", "uk")
LANGUAGE_SLICE_GAP_STATEMENT = (
    "The initial P12.4 pack covers only uk/ru/pl/tr discovery. Languages, regions, "
    "publishers, blocked/removed material and not-yet-indexed publications outside this "
    "configured slice remain explicit coverage gaps; GLOBAL is not implied."
)


@dataclass(frozen=True)
class LocalLanguageDiscoverySourceSpec:
    source_id: str
    source_name: str
    publisher_name: str
    source_class: str
    source_role: str
    feed_url: str
    adapter_id: str
    adapter_version: str
    region_scope: tuple[str, ...]
    content_language: str
    native_query_term: str
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    reliability: str
    availability_state: str
    origin_characteristics: str
    independence_constraints: str
    terms_notes: str

    def __post_init__(self) -> None:
        if self.source_role != "MEDIA":
            raise ValueError("P12.4 source_role must be MEDIA")
        if self.content_language not in set(INITIAL_LANGUAGE_SLICE):
            raise ValueError("P12.4 content_language is outside the approved initial slice")
        if not self.native_query_term.strip():
            raise ValueError("P12.4 native_query_term must not be empty")
        if self.availability_state not in {"ACTIVE", "DEGRADED"}:
            raise ValueError("P12.4 availability_state must be ACTIVE or DEGRADED")

    @property
    def language_scope(self) -> tuple[str, ...]:
        return (self.content_language,)

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
    def creates_translation(self) -> bool:
        return False

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def changes_coverage_confidence(self) -> bool:
        return False


_MEDIA_ORIGIN = (
    "Media publisher/discovery source. A publication establishes that the publisher "
    "published the item; the underlying origin may be the outlet's reporting, an official "
    "statement, a wire service, another publisher or an unknown/combined origin and must be "
    "resolved separately."
)
_MEDIA_INDEPENDENCE = (
    "Publisher, domain, language, translation or adapter identity is not independent-origin "
    "credit. Reposts, syndication, citations, wire copy and translations derived from the "
    "same underlying origin must be clustered before corroboration is assessed."
)


LOCAL_LANGUAGE_DISCOVERY_PACK: tuple[LocalLanguageDiscoverySourceSpec, ...] = (
    LocalLanguageDiscoverySourceSpec(
        source_id="ukrainska-pravda-uk",
        source_name="Ukrainska Pravda — Ukrainian News",
        publisher_name="Ukrainska Pravda / UP Media Plus",
        source_class="Regional media",
        source_role="MEDIA",
        feed_url="https://www.pravda.com.ua/rss/view_news/",
        adapter_id="ukrainska-pravda-uk-rss",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("UKRAINE", "EASTERN_EUROPE"),
        content_language="uk",
        native_query_term="Україна",
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        reliability="media-discovery",
        availability_state="ACTIVE",
        origin_characteristics=_MEDIA_ORIGIN,
        independence_constraints=_MEDIA_INDEPENDENCE,
        terms_notes=(
            "Public Ukrainian-language news RSS. Preserve original-language text and URL; "
            "respect publisher usage terms and do not treat feed inclusion as event proof."
        ),
    ),
    LocalLanguageDiscoverySourceSpec(
        source_id="meduza-ru",
        source_name="Meduza — Russian RSS",
        publisher_name="Meduza",
        source_class="International media",
        source_role="MEDIA",
        feed_url="https://meduza.io/rss/all",
        adapter_id="meduza-ru-rss",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("RUSSIA", "EURASIA", "EASTERN_EUROPE"),
        content_language="ru",
        native_query_term="Украина",
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        reliability="media-discovery",
        availability_state="ACTIVE",
        origin_characteristics=_MEDIA_ORIGIN,
        independence_constraints=_MEDIA_INDEPENDENCE,
        terms_notes=(
            "Public Russian-language Meduza RSS. Source access may vary by network/jurisdiction; "
            "preserve original language and do not infer underlying-origin independence."
        ),
    ),
    LocalLanguageDiscoverySourceSpec(
        source_id="rmf24-pl",
        source_name="RMF24 — Polish News",
        publisher_name="RMF24",
        source_class="Regional media",
        source_role="MEDIA",
        feed_url="https://www.rmf24.pl/feed",
        adapter_id="rmf24-pl-rss",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("POLAND", "CENTRAL_EUROPE"),
        content_language="pl",
        native_query_term="Ukraina",
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        reliability="media-discovery",
        availability_state="ACTIVE",
        origin_characteristics=_MEDIA_ORIGIN,
        independence_constraints=_MEDIA_INDEPENDENCE,
        terms_notes=(
            "Public Polish-language RMF24 main RSS feed. Discovery only; original-language "
            "publication and underlying evidence/origin remain separate concepts."
        ),
    ),
    LocalLanguageDiscoverySourceSpec(
        source_id="haberturk-tr",
        source_name="Haberturk — Turkish News",
        publisher_name="Haberturk",
        source_class="Regional media",
        source_role="MEDIA",
        feed_url="https://www.haberturk.com/rss",
        adapter_id="haberturk-tr-rss",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("TURKEY", "BLACK_SEA", "MIDDLE_EAST"),
        content_language="tr",
        native_query_term="Ukrayna",
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        reliability="media-discovery",
        availability_state="ACTIVE",
        origin_characteristics=_MEDIA_ORIGIN,
        independence_constraints=_MEDIA_INDEPENDENCE,
        terms_notes=(
            "Public Turkish-language Haberturk RSS service. Discovery only; preserve original "
            "language and keep translation/provenance/verification as separate downstream work."
        ),
    ),
)


class LocalLanguageFeedAdapter(PublicFeedAdapterV2):
    """Feed adapter that preserves explicit source language/discovery metadata."""

    def __init__(
        self,
        transport: PublicHttpTransport,
        spec: LocalLanguageDiscoverySourceSpec,
        *,
        max_entries: int = 200,
        query_filter: bool = False,
    ) -> None:
        self.spec = spec
        self.content_language = spec.content_language
        self.native_query_term = spec.native_query_term
        self.region_scope = spec.region_scope
        super().__init__(
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
            query_filter=query_filter,
        )

    def fetch(self, watch: MonitoringWatch, collected_at) -> list[LiveSourceItem]:
        items = super().fetch(watch, collected_at)
        enriched: list[LiveSourceItem] = []
        for item in items:
            metadata = dict(item.metadata)
            metadata.update(
                {
                    "content_language": self.content_language,
                    "native_query_term": self.native_query_term,
                    "region_scope": list(self.region_scope),
                    "discovery_role": "MEDIA",
                    "translation_state": "ORIGINAL_NOT_TRANSLATED",
                    "language_pack_version": LOCAL_LANGUAGE_DISCOVERY_PACK_VERSION,
                }
            )
            enriched.append(replace(item, metadata=metadata))
        return enriched


def local_language_specs() -> tuple[LocalLanguageDiscoverySourceSpec, ...]:
    return LOCAL_LANGUAGE_DISCOVERY_PACK


def local_language_by_id() -> Mapping[str, LocalLanguageDiscoverySourceSpec]:
    return {spec.source_id: spec for spec in LOCAL_LANGUAGE_DISCOVERY_PACK}


def build_local_language_adapter(
    transport: PublicHttpTransport,
    spec: LocalLanguageDiscoverySourceSpec,
    *,
    max_entries: int = 200,
    query_filter: bool = False,
) -> LocalLanguageFeedAdapter:
    return LocalLanguageFeedAdapter(
        transport,
        spec,
        max_entries=max_entries,
        query_filter=query_filter,
    )


def build_local_language_adapters(
    transport: PublicHttpTransport,
    *,
    max_entries: int = 200,
    query_filter: bool = False,
) -> list[LocalLanguageFeedAdapter]:
    return [
        build_local_language_adapter(
            transport,
            spec,
            max_entries=max_entries,
            query_filter=query_filter,
        )
        for spec in LOCAL_LANGUAGE_DISCOVERY_PACK
    ]


def _record_matches_spec(
    record: SourcePortfolioRecord,
    spec: LocalLanguageDiscoverySourceSpec,
) -> bool:
    return (
        record.source_id == spec.source_id
        and record.source_name == spec.source_name
        and record.publisher_name == spec.publisher_name
        and record.source_class == spec.source_class
        and record.source_role == spec.source_role
        and record.region_scope == tuple(sorted(set(spec.region_scope)))
        and record.language_scope == spec.language_scope
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


def install_local_language_governance(
    runtime: OperationalMonitoringRuntime,
    *,
    reviewed_at: datetime,
    owner: str = "KGM owner",
    reviewer: str = "KGM owner",
) -> tuple[SourcePortfolioRecord, ...]:
    """Install exact P12.4 records; reuse exact matches and fail closed on drift."""

    timestamp = _normalize_time(reviewed_at)
    service = SourcePortfolioService(runtime)
    records: list[SourcePortfolioRecord] = []

    for spec in LOCAL_LANGUAGE_DISCOVERY_PACK:
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
                    f"P12.4 source portfolio drift requires explicit review: {spec.source_id}"
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


def build_governed_local_language_collector(
    runtime: OperationalMonitoringRuntime,
    transport: PublicHttpTransport,
    *,
    max_entries: int = 200,
) -> FrameworkLiveSourceCollector:
    """Build broad bounded discovery collection after explicit P12.4 governance."""

    return FrameworkLiveSourceCollector(
        runtime,
        build_local_language_adapters(
            transport,
            max_entries=max_entries,
            query_filter=False,
        ),
    )
