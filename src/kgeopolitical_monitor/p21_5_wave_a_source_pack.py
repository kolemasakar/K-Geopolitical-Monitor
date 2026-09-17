"""P21.5 Wave-A governed public/free Ukrainian source pack.

Repository activation only. Deployed runtime mutation remains out of scope.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.parse import urlparse

from .adapter_framework import ADAPTER_FRAMEWORK_VERSION, PublicFeedAdapterV2, PublicHttpTransport
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService

P21_5_WAVE_A_VERSION = "P21.5-WAVE-A-1.0"

@dataclass(frozen=True)
class WaveASourceSpec:
    source_id: str
    source_name: str
    publisher_name: str
    source_type: str
    source_class: str
    source_role: str
    feed_url: str
    adapter_id: str
    region_scope: tuple[str, ...]
    language_scope: tuple[str, ...]
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    reliability: str
    origin_characteristics: str
    independence_constraints: str
    terms_notes: str

    @property
    def outbound_domain(self) -> str:
        return str(urlparse(self.feed_url).hostname or "").lower()

OFFICIAL_INDEPENDENCE = (
    "Direct institutional publication stream. It establishes what the institution published; "
    "it does not automatically establish the truth of every underlying event claim. "
    "Independent-origin credit remains evidence-bound downstream."
)
MEDIA_INDEPENDENCE = (
    "Publisher/domain/language identity is not underlying-origin independence. Item-level provenance "
    "must distinguish original reporting, official statements, wires, citations and syndication."
)

WAVE_A_SOURCES: tuple[WaveASourceSpec, ...] = (
    WaveASourceSpec(
        source_id="ukraine-government-kmu-uk",
        source_name="Cabinet of Ministers of Ukraine — News RSS",
        publisher_name="Cabinet of Ministers of Ukraine",
        source_type="OFFICIAL_GOVERNMENT",
        source_class="Official sources",
        source_role="OFFICIAL",
        feed_url="https://www.kmu.gov.ua/api/rss",
        adapter_id="kmu-uk-rss",
        region_scope=("UKRAINE",),
        language_scope=("uk",),
        expected_freshness_minutes=240,
        collection_cadence_minutes=120,
        reliability="official",
        origin_characteristics="Direct official Cabinet of Ministers publication stream.",
        independence_constraints=OFFICIAL_INDEPENDENCE,
        terms_notes="Public anonymous Ukrainian-language RSS endpoint published by kmu.gov.ua; read-only discovery/statement evidence.",
    ),
    WaveASourceSpec(
        source_id="suspilne-uk",
        source_name="Suspilne — Ukrainian News RSS",
        publisher_name="Suspilne Ukraine",
        source_type="NATIONAL_MEDIA",
        source_class="Regional media",
        source_role="MEDIA",
        feed_url="https://suspilne.media/rss/all.rss",
        adapter_id="suspilne-uk-rss",
        region_scope=("UKRAINE",),
        language_scope=("uk",),
        expected_freshness_minutes=120,
        collection_cadence_minutes=60,
        reliability="media-discovery",
        origin_characteristics="National media publication stream with potentially mixed underlying origins.",
        independence_constraints=MEDIA_INDEPENDENCE,
        terms_notes="Public anonymous Ukrainian-language RSS endpoint published by suspilne.media; preserve original URL/text and resolve item provenance separately.",
    ),
)

def wave_a_by_id() -> dict[str, WaveASourceSpec]:
    return {s.source_id: s for s in WAVE_A_SOURCES}

def build_wave_a_adapters(transport: PublicHttpTransport, *, enabled_source_ids: Iterable[str] | None = None, max_entries: int = 100) -> list[PublicFeedAdapterV2]:
    enabled = set(wave_a_by_id()) if enabled_source_ids is None else {str(x) for x in enabled_source_ids}
    unknown = enabled - set(wave_a_by_id())
    if unknown:
        raise ValueError(f"unknown P21.5 Wave-A source id(s): {sorted(unknown)}")
    return [PublicFeedAdapterV2(transport, source_id=s.source_id, source_name=s.source_name, source_class=s.source_class, source_role=s.source_role, feed_url=s.feed_url, adapter_id=s.adapter_id, adapter_version=ADAPTER_FRAMEWORK_VERSION, reliability=s.reliability, max_entries=max_entries, query_filter=False) for s in WAVE_A_SOURCES if s.source_id in enabled]

def _matches(record: SourcePortfolioRecord, s: WaveASourceSpec) -> bool:
    return record.source_id==s.source_id and record.source_name==s.source_name and record.publisher_name==s.publisher_name and record.source_class==s.source_class and record.source_role==s.source_role and record.region_scope==tuple(sorted(set(s.region_scope))) and record.language_scope==tuple(sorted(set(s.language_scope))) and record.access_mode=="PUBLIC_ANONYMOUS" and record.cost_mode=="FREE" and record.authentication_mode=="NONE" and record.expected_freshness_minutes==s.expected_freshness_minutes and record.collection_cadence_minutes==s.collection_cadence_minutes and record.adapter_id==s.adapter_id and record.adapter_version==ADAPTER_FRAMEWORK_VERSION and record.outbound_domains==(s.outbound_domain,) and record.outbound_protocols==("HTTPS",) and record.availability_state=="ACTIVE" and record.data_classification=="PUBLIC" and record.review_status=="APPROVED" and not record.paid_provider_approved

def install_wave_a_governance(runtime: OperationalMonitoringRuntime, *, reviewed_at: datetime, owner: str="KGM owner", reviewer: str="KGM owner") -> tuple[SourcePortfolioRecord, ...]:
    t=_normalize_time(reviewed_at); svc=SourcePortfolioService(runtime); out=[]
    for s in WAVE_A_SOURCES:
        svc.register_source_identity(s.source_id, source_name=s.source_name, source_class=s.source_class, reliability=s.reliability)
        current=svc.current(s.source_id)
        if current is not None:
            if not _matches(current,s):
                raise RuntimeError(f"P21.5 Wave-A source portfolio drift requires explicit review: {s.source_id}")
            out.append(current); continue
        out.append(svc.record_version(s.source_id, source_name=s.source_name, publisher_name=s.publisher_name, source_class=s.source_class, source_role=s.source_role, region_scope=s.region_scope, language_scope=s.language_scope, access_mode="PUBLIC_ANONYMOUS", cost_mode="FREE", authentication_mode="NONE", expected_freshness_minutes=s.expected_freshness_minutes, collection_cadence_minutes=s.collection_cadence_minutes, adapter_id=s.adapter_id, adapter_version=ADAPTER_FRAMEWORK_VERSION, outbound_domains=(s.outbound_domain,), outbound_protocols=("HTTPS",), fallback_source_ids=(), availability_state="ACTIVE", data_classification="PUBLIC", origin_characteristics=s.origin_characteristics, independence_constraints=s.independence_constraints, terms_notes=s.terms_notes, owner=owner, reviewer=reviewer, review_status="APPROVED", paid_provider_approved=False, reviewed_at=t, created_at=t))
    return tuple(out)
