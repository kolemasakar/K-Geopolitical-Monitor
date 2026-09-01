"""Phase 12 P12.5 source-health, freshness and egress inventory.

This module is a read-only assessment layer over existing P12.1 portfolio and
M7/P12.2 collection audit/provenance state. Operational health/freshness does
not promote or demote factual verification, evidence independence or coverage
confidence. A missing observation remains UNMEASURED rather than inferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import re
from typing import Iterable
from urllib.parse import urlparse

from .adapter_framework import (
    ADAPTER_FRAMEWORK_VERSION,
    GdeltDoc2AdapterV2,
    PublicFeedAdapterV2,
    PublicHttpTransport,
)
from .authoritative_source_pack import (
    install_source_pack_governance,
    source_pack_specs,
)
from .database import runtime_database_connection
from .local_language_discovery_pack import (
    build_local_language_adapters,
    install_local_language_governance,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .source_portfolio import SourcePortfolioRecord, SourcePortfolioService


SOURCE_HEALTH_VERSION = "P12.5-1.0"
OPERATIONAL_STATES = {"UNMEASURED", "HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE"}
MEASUREMENT_FRESHNESS_STATES = {"UNMEASURED", "CURRENT", "STALE"}
CONTENT_FRESHNESS_STATES = {"UNKNOWN", "FRESH", "STALE"}
ERROR_CLASSES = {"NONE", "TRANSPORT", "PARSER", "GOVERNANCE", "UNKNOWN"}


@dataclass(frozen=True)
class BaselineSourceSpec:
    source_id: str
    source_name: str
    publisher_name: str
    source_class: str
    source_role: str
    endpoint: str
    adapter_id: str
    adapter_version: str
    region_scope: tuple[str, ...]
    language_scope: tuple[str, ...]
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    reliability: str

    @property
    def outbound_domain(self) -> str:
        return str(urlparse(self.endpoint).hostname or "").lower()


BASELINE_SOURCE_SPECS: tuple[BaselineSourceSpec, ...] = (
    BaselineSourceSpec(
        source_id="consilium-press-releases",
        source_name="Council of the EU / European Council Press Releases",
        publisher_name="Council of the European Union / European Council",
        source_class="Official sources",
        source_role="OFFICIAL",
        endpoint="https://www.consilium.europa.eu/en/rss/pressreleases.ashx",
        adapter_id="consilium-rss-atom",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("EU", "EUROPE"),
        language_scope=("en",),
        expected_freshness_minutes=240,
        collection_cadence_minutes=120,
        reliability="official",
    ),
    BaselineSourceSpec(
        source_id="gdelt-doc-2",
        source_name="GDELT DOC 2.0",
        publisher_name="GDELT Project",
        source_class="Structured data",
        source_role="DISCOVERY",
        endpoint="https://api.gdeltproject.org/api/v2/doc/doc",
        adapter_id="gdelt-doc-json",
        adapter_version=ADAPTER_FRAMEWORK_VERSION,
        region_scope=("GLOBAL",),
        language_scope=("multi",),
        expected_freshness_minutes=60,
        collection_cadence_minutes=30,
        reliability="discovery-only",
    ),
)


@dataclass(frozen=True)
class EgressInventoryEntry:
    source_id: str
    source_name: str
    adapter_identity: str
    hostname: str
    protocol: str
    access_mode: str
    data_classification: str
    portfolio_availability_state: str

    @property
    def changes_verification_state(self) -> bool:
        return False


@dataclass(frozen=True)
class SourceHealthAssessment:
    source_id: str
    source_name: str
    source_class: str
    adapter_identity: str
    portfolio_availability_state: str
    operational_state: str
    measurement_freshness: str
    content_freshness: str
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    last_attempt_status: str | None
    last_attempt_at: datetime | None
    attempt_age_minutes: float | None
    latest_content_at: datetime | None
    content_age_minutes: float | None
    content_timestamp_basis: str | None
    last_item_count: int | None
    error_class: str
    error: str | None
    outbound_domains: tuple[str, ...]
    outbound_protocols: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.operational_state not in OPERATIONAL_STATES:
            raise ValueError("unsupported operational_state")
        if self.measurement_freshness not in MEASUREMENT_FRESHNESS_STATES:
            raise ValueError("unsupported measurement_freshness")
        if self.content_freshness not in CONTENT_FRESHNESS_STATES:
            raise ValueError("unsupported content_freshness")
        if self.error_class not in ERROR_CLASSES:
            raise ValueError("unsupported error_class")

    @property
    def changes_claim_truth(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_coverage_confidence(self) -> bool:
        return False


@dataclass(frozen=True)
class SourceHealthSnapshot:
    assessed_at: datetime
    assessments: tuple[SourceHealthAssessment, ...]
    egress_entries: tuple[EgressInventoryEntry, ...]

    @property
    def unique_outbound_hosts(self) -> tuple[str, ...]:
        return tuple(sorted({entry.hostname for entry in self.egress_entries}))

    @property
    def unique_outbound_protocols(self) -> tuple[str, ...]:
        return tuple(sorted({entry.protocol for entry in self.egress_entries}))

    @property
    def measured_source_count(self) -> int:
        return sum(a.operational_state != "UNMEASURED" for a in self.assessments)

    @property
    def unmeasured_source_count(self) -> int:
        return sum(a.operational_state == "UNMEASURED" for a in self.assessments)


def _baseline_record_matches(record: SourcePortfolioRecord, spec: BaselineSourceSpec) -> bool:
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
        and record.availability_state == "ACTIVE"
        and record.data_classification == "PUBLIC"
        and record.review_status == "APPROVED"
        and not record.paid_provider_approved
    )


def install_baseline_v2_governance(
    runtime: OperationalMonitoringRuntime,
    *,
    reviewed_at: datetime,
    owner: str = "KGM owner",
    reviewer: str = "KGM owner",
) -> tuple[SourcePortfolioRecord, ...]:
    """Govern the two pre-P12 baseline integrations for controlled P12.5 v2 probing.

    This records governance in the supplied runtime only. It does not switch or
    activate an owner production runtime.
    """

    timestamp = _normalize_time(reviewed_at)
    service = SourcePortfolioService(runtime)
    records: list[SourcePortfolioRecord] = []
    for spec in BASELINE_SOURCE_SPECS:
        service.register_source_identity(
            spec.source_id,
            source_name=spec.source_name,
            source_class=spec.source_class,
            reliability=spec.reliability,
        )
        current = service.current(spec.source_id)
        if current is not None:
            if not _baseline_record_matches(current, spec):
                raise RuntimeError(
                    f"P12.5 baseline source portfolio drift requires explicit review: {spec.source_id}"
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
                availability_state="ACTIVE",
                data_classification="PUBLIC",
                origin_characteristics=(
                    "Validated baseline publisher/discovery integration; publisher/index identity "
                    "does not by itself establish the underlying origin or event truth."
                ),
                independence_constraints=(
                    "Baseline source/domain/adapter observations are not independent-origin credit; "
                    "reposts, indexing and citations require origin resolution."
                ),
                terms_notes="Public/free pre-P12 validated integration governed for P12.5 measurement.",
                owner=owner,
                reviewer=reviewer,
                review_status="APPROVED",
                paid_provider_approved=False,
                reviewed_at=timestamp,
                created_at=timestamp,
            )
        )
    return tuple(records)


def install_phase12_health_probe_governance(
    runtime: OperationalMonitoringRuntime,
    *,
    reviewed_at: datetime,
) -> tuple[SourcePortfolioRecord, ...]:
    """Install exact governance for all ten P12.5 measured network paths."""

    return (
        *install_baseline_v2_governance(runtime, reviewed_at=reviewed_at),
        *install_source_pack_governance(runtime, reviewed_at=reviewed_at),
        *install_local_language_governance(runtime, reviewed_at=reviewed_at),
    )


def build_health_probe_adapters(
    transport: PublicHttpTransport,
    *,
    max_feed_entries: int = 100,
    gdelt_max_records: int = 25,
) -> list[object]:
    """Build the ten controlled read-only adapters used by P12.5 measurement."""

    adapters: list[object] = [
        PublicFeedAdapterV2(
            transport,
            source_id="consilium-press-releases",
            source_name="Council of the EU / European Council Press Releases",
            source_class="Official sources",
            source_role="OFFICIAL",
            feed_url="https://www.consilium.europa.eu/en/rss/pressreleases.ashx",
            adapter_id="consilium-rss-atom",
            adapter_version=ADAPTER_FRAMEWORK_VERSION,
            reliability="official",
            max_entries=max_feed_entries,
            query_filter=False,
        ),
        GdeltDoc2AdapterV2(
            transport,
            max_records=gdelt_max_records,
            timespan="24h",
        ),
    ]
    for spec in source_pack_specs():
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
                max_entries=max_feed_entries,
                query_filter=False,
            )
        )
    adapters.extend(
        build_local_language_adapters(
            transport,
            max_entries=max_feed_entries,
            query_filter=False,
        )
    )
    return adapters


def _parse_timestamp(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    candidates = [raw]
    if raw.endswith("Z"):
        candidates.append(raw[:-1] + "+00:00")
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return _normalize_time(parsed)
        except ValueError:
            pass
    try:
        return _normalize_time(parsedate_to_datetime(raw))
    except (TypeError, ValueError, OverflowError):
        pass
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _content_timestamp_from_metadata(metadata: dict[str, object]) -> tuple[datetime | None, str | None]:
    for field in ("published_at", "published_at_raw", "seendate"):
        if field not in metadata:
            continue
        parsed = _parse_timestamp(metadata[field])
        if parsed is not None:
            return parsed, field
    return None, None


def classify_attempt_error(error: str | None) -> str:
    if not str(error or "").strip():
        return "NONE"
    text = str(error).lower()
    if any(token in text for token in ("portfolio", "governance", "identity/version", "hostname is not approved")):
        return "GOVERNANCE"
    if any(token in text for token in ("not valid xml", "not valid json", "feed payload", "parser", "neither rss nor atom", "does not contain")):
        return "PARSER"
    if any(token in text for token in ("http error", "network error", "timeout", "timed out", "connection", "unavailable", "urlopen", "name or service")):
        return "TRANSPORT"
    return "UNKNOWN"


class SourceHealthEgressService:
    """Read current portfolio + persisted collection observations without mutation."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.portfolio = SourcePortfolioService(runtime)

    def egress_inventory(self) -> tuple[EgressInventoryEntry, ...]:
        entries: list[EgressInventoryEntry] = []
        for record in self.portfolio.current_entries():
            if record.review_status != "APPROVED":
                continue
            for protocol in record.outbound_protocols:
                for hostname in record.outbound_domains:
                    entries.append(
                        EgressInventoryEntry(
                            source_id=record.source_id,
                            source_name=record.source_name,
                            adapter_identity=f"{record.adapter_id}@{record.adapter_version}",
                            hostname=hostname,
                            protocol=protocol,
                            access_mode=record.access_mode,
                            data_classification=record.data_classification,
                            portfolio_availability_state=record.availability_state,
                        )
                    )
        return tuple(sorted(entries, key=lambda e: (e.hostname, e.source_id, e.protocol)))

    def _latest_attempt(self, source_id: str):
        with runtime_database_connection(self.database_path) as connection:
            return connection.execute(
                """
                SELECT status, item_count, error, attempted_at
                FROM source_collection_attempts
                WHERE source_id = ?
                ORDER BY attempted_at DESC, rowid DESC
                LIMIT 1
                """,
                (source_id,),
            ).fetchone()

    def _latest_content_observation(self, source_id: str, assessed_at: datetime):
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT p.metadata_json, r.collected_at
                FROM live_source_provenance p
                JOIN raw_items r ON r.id = p.raw_item_id
                WHERE r.source_id = ?
                ORDER BY r.collected_at DESC, r.id DESC
                """,
                (source_id,),
            ).fetchall()
        latest: tuple[datetime, str] | None = None
        for metadata_json, collected_at in rows:
            try:
                metadata = json.loads(metadata_json or "{}")
            except json.JSONDecodeError:
                metadata = {}
            published_at, basis = _content_timestamp_from_metadata(metadata if isinstance(metadata, dict) else {})
            if published_at is None:
                continue
            if published_at > assessed_at:
                continue
            if latest is None or published_at > latest[0]:
                latest = (published_at, str(basis))
        return latest

    def assess_source(self, record: SourcePortfolioRecord, *, assessed_at: datetime) -> SourceHealthAssessment:
        now = _normalize_time(assessed_at)
        attempt = self._latest_attempt(record.source_id)
        if attempt is None:
            last_status = None
            last_item_count = None
            error = None
            error_class = "NONE"
            last_attempt_at = None
            attempt_age = None
            measurement_freshness = "UNMEASURED"
            operational_state = "UNMEASURED"
        else:
            last_status = str(attempt[0])
            last_item_count = int(attempt[1])
            error = None if attempt[2] is None else str(attempt[2])
            error_class = classify_attempt_error(error)
            last_attempt_at = _normalize_time(datetime.fromisoformat(str(attempt[3])))
            attempt_age = max(0.0, (now - last_attempt_at).total_seconds() / 60.0)
            measurement_limit = max(
                float(record.collection_cadence_minutes * 2),
                float(record.expected_freshness_minutes),
            )
            measurement_freshness = "CURRENT" if attempt_age <= measurement_limit else "STALE"
            if measurement_freshness == "STALE":
                operational_state = "STALE"
            elif last_status == "FAILED":
                operational_state = "UNAVAILABLE"
            elif record.availability_state == "DEGRADED":
                operational_state = "DEGRADED"
            else:
                operational_state = "HEALTHY"

        content = self._latest_content_observation(record.source_id, now)
        if content is None:
            latest_content_at = None
            content_age = None
            content_basis = None
            content_freshness = "UNKNOWN"
        else:
            latest_content_at, content_basis = content
            content_age = max(0.0, (now - latest_content_at).total_seconds() / 60.0)
            content_freshness = (
                "FRESH"
                if content_age <= float(record.expected_freshness_minutes)
                else "STALE"
            )

        return SourceHealthAssessment(
            source_id=record.source_id,
            source_name=record.source_name,
            source_class=record.source_class,
            adapter_identity=f"{record.adapter_id}@{record.adapter_version}",
            portfolio_availability_state=record.availability_state,
            operational_state=operational_state,
            measurement_freshness=measurement_freshness,
            content_freshness=content_freshness,
            expected_freshness_minutes=record.expected_freshness_minutes,
            collection_cadence_minutes=record.collection_cadence_minutes,
            last_attempt_status=last_status,
            last_attempt_at=last_attempt_at,
            attempt_age_minutes=attempt_age,
            latest_content_at=latest_content_at,
            content_age_minutes=content_age,
            content_timestamp_basis=content_basis,
            last_item_count=last_item_count,
            error_class=error_class,
            error=error,
            outbound_domains=record.outbound_domains,
            outbound_protocols=record.outbound_protocols,
        )

    def snapshot(self, *, assessed_at: datetime) -> SourceHealthSnapshot:
        now = _normalize_time(assessed_at)
        records = tuple(
            record
            for record in self.portfolio.current_entries()
            if record.review_status == "APPROVED"
        )
        assessments = tuple(
            self.assess_source(record, assessed_at=now) for record in records
        )
        return SourceHealthSnapshot(
            assessed_at=now,
            assessments=assessments,
            egress_entries=self.egress_inventory(),
        )


def snapshot_to_jsonable(snapshot: SourceHealthSnapshot) -> dict[str, object]:
    return {
        "source_health_version": SOURCE_HEALTH_VERSION,
        "assessed_at": snapshot.assessed_at.isoformat(),
        "measured_source_count": snapshot.measured_source_count,
        "unmeasured_source_count": snapshot.unmeasured_source_count,
        "unique_outbound_hosts": list(snapshot.unique_outbound_hosts),
        "unique_outbound_protocols": list(snapshot.unique_outbound_protocols),
        "sources": [
            {
                "source_id": a.source_id,
                "source_name": a.source_name,
                "adapter_identity": a.adapter_identity,
                "portfolio_availability_state": a.portfolio_availability_state,
                "operational_state": a.operational_state,
                "measurement_freshness": a.measurement_freshness,
                "content_freshness": a.content_freshness,
                "expected_freshness_minutes": a.expected_freshness_minutes,
                "collection_cadence_minutes": a.collection_cadence_minutes,
                "last_attempt_status": a.last_attempt_status,
                "last_attempt_at": None if a.last_attempt_at is None else a.last_attempt_at.isoformat(),
                "attempt_age_minutes": a.attempt_age_minutes,
                "latest_content_at": None if a.latest_content_at is None else a.latest_content_at.isoformat(),
                "content_age_minutes": a.content_age_minutes,
                "content_timestamp_basis": a.content_timestamp_basis,
                "last_item_count": a.last_item_count,
                "error_class": a.error_class,
                "error": a.error,
                "outbound_domains": list(a.outbound_domains),
                "outbound_protocols": list(a.outbound_protocols),
            }
            for a in snapshot.assessments
        ],
        "egress": [
            {
                "source_id": e.source_id,
                "adapter_identity": e.adapter_identity,
                "hostname": e.hostname,
                "protocol": e.protocol,
                "access_mode": e.access_mode,
                "data_classification": e.data_classification,
                "portfolio_availability_state": e.portfolio_availability_state,
            }
            for e in snapshot.egress_entries
        ],
        "epistemic_note": (
            "Source health/freshness/egress state is operational evidence only. It does not "
            "change factual verification, independent-origin count or prove coverage completeness."
        ),
    }
