"""Phase 12 P12.1 durable source-portfolio governance contract.

The portfolio is governance metadata over the canonical ``sources`` identity table.
It does not activate collection, establish evidentiary independence, or change
verification/coverage truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Iterable

from .controlled_pilot import APPROVED_SOURCE_CLASSES
from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time, utc_now


SOURCE_ROLES = {
    "PRIMARY",
    "OFFICIAL",
    "MEDIA",
    "DISCOVERY",
    "STRUCTURED_DATA",
    "OSINT",
    "SOCIAL",
    "USER_PROVIDED",
    "OTHER_APPROVED",
}
ACCESS_MODES = {
    "PUBLIC_ANONYMOUS",
    "PUBLIC_CREDENTIALED",
    "RESTRICTED",
    "USER_PROVIDED",
}
COST_MODES = {"FREE", "PAID", "UNKNOWN"}
AUTHENTICATION_MODES = {"NONE", "API_KEY", "OAUTH", "OTHER"}
AVAILABILITY_STATES = {
    "PLANNED",
    "ACTIVE",
    "DEGRADED",
    "UNAVAILABLE",
    "STALE",
    "RETIRED",
}
DATA_CLASSIFICATIONS = {"PUBLIC", "USER_PROVIDED", "RESTRICTED", "SENSITIVE"}
REVIEW_STATUSES = {"PLANNED", "APPROVED", "REJECTED", "RETIRED"}
OUTBOUND_PROTOCOLS = {"HTTPS"}
NETWORK_ACCESS_MODES = {"PUBLIC_ANONYMOUS", "PUBLIC_CREDENTIALED", "RESTRICTED"}
OPERATIONAL_AVAILABILITY_STATES = {"ACTIVE", "DEGRADED", "UNAVAILABLE", "STALE"}


@dataclass(frozen=True)
class SourcePortfolioRecord:
    portfolio_entry_id: str
    source_id: str
    portfolio_version: int
    source_name: str
    publisher_name: str
    source_class: str
    source_role: str
    region_scope: tuple[str, ...]
    language_scope: tuple[str, ...]
    access_mode: str
    cost_mode: str
    authentication_mode: str
    expected_freshness_minutes: int
    collection_cadence_minutes: int
    adapter_id: str
    adapter_version: str
    outbound_domains: tuple[str, ...]
    outbound_protocols: tuple[str, ...]
    fallback_source_ids: tuple[str, ...]
    availability_state: str
    data_classification: str
    origin_characteristics: str
    independence_constraints: str
    terms_notes: str
    owner: str
    reviewer: str
    review_status: str
    paid_provider_approved: bool
    reviewed_at: datetime
    supersedes_entry_id: str | None
    created_at: datetime

    @property
    def activates_collection(self) -> bool:
        return False

    @property
    def establishes_independence(self) -> bool:
        return False

    @property
    def changes_claim_truth(self) -> bool:
        return False

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def changes_coverage_confidence(self) -> bool:
        return False


def _required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _enum(value: object, field_name: str, allowed: set[str]) -> str:
    normalized = _required(value, field_name).upper()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
    return normalized


def _strings(
    values: Iterable[str],
    field_name: str,
    *,
    required: bool = False,
    lower: bool = False,
    upper: bool = False,
) -> tuple[str, ...]:
    normalized: set[str] = set()
    for value in values:
        item = str(value).strip()
        if not item:
            continue
        if lower:
            item = item.lower()
        elif upper:
            item = item.upper()
        normalized.add(item)
    result = tuple(sorted(normalized))
    if required and not result:
        raise ValueError(f"{field_name} must contain at least one value")
    return result


def _domains(values: Iterable[str], *, required: bool) -> tuple[str, ...]:
    domains = _strings(values, "outbound_domains", required=required, lower=True)
    for domain in domains:
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", domain):
            raise ValueError("outbound_domains must contain exact hostnames, not URLs or paths")
        if ".." in domain or "." not in domain:
            raise ValueError("outbound_domains must contain fully qualified hostnames")
    return domains


def _positive_int(value: object, field_name: str) -> int:
    normalized = int(value)
    if normalized <= 0:
        raise ValueError(f"{field_name} must be positive")
    return normalized


def _stable_entry_id(source_id: str, version: int) -> str:
    digest = sha256(f"{source_id}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"source-portfolio-{digest}"


class SourcePortfolioService:
    """Versioned, immutable-through-service source governance metadata."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def register_source_identity(
        self,
        source_id: str,
        *,
        source_name: str,
        source_class: str,
        reliability: str = "unassessed",
    ) -> None:
        normalized_id = _required(source_id, "source_id")
        normalized_name = _required(source_name, "source_name")
        normalized_class = _required(source_class, "source_class")
        if normalized_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {normalized_class}")
        normalized_reliability = _required(reliability, "reliability")

        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                "SELECT name, source_class FROM sources WHERE id = ?",
                (normalized_id,),
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO sources(id, name, source_class, reliability)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        normalized_id,
                        normalized_name,
                        normalized_class,
                        normalized_reliability,
                    ),
                )
                return
            if row[0] != normalized_name or row[1] != normalized_class:
                raise ValueError("source identity conflicts with existing canonical source")

    def _source_identity(self, source_id: str) -> tuple[str, str] | None:
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                "SELECT name, source_class FROM sources WHERE id = ?",
                (source_id,),
            ).fetchone()
        return None if row is None else (str(row[0]), str(row[1]))

    def record_version(
        self,
        source_id: str,
        *,
        source_name: str,
        publisher_name: str,
        source_class: str,
        source_role: str,
        region_scope: Iterable[str],
        language_scope: Iterable[str],
        access_mode: str,
        cost_mode: str,
        authentication_mode: str,
        expected_freshness_minutes: int,
        collection_cadence_minutes: int,
        adapter_id: str,
        adapter_version: str,
        outbound_domains: Iterable[str],
        outbound_protocols: Iterable[str] = ("HTTPS",),
        fallback_source_ids: Iterable[str] = (),
        availability_state: str,
        data_classification: str,
        origin_characteristics: str,
        independence_constraints: str,
        terms_notes: str = "",
        owner: str,
        reviewer: str,
        review_status: str,
        paid_provider_approved: bool = False,
        reviewed_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> SourcePortfolioRecord:
        normalized_id = _required(source_id, "source_id")
        normalized_name = _required(source_name, "source_name")
        normalized_publisher = _required(publisher_name, "publisher_name")
        normalized_class = _required(source_class, "source_class")
        if normalized_class not in APPROVED_SOURCE_CLASSES:
            raise ValueError(f"unsupported source_class: {normalized_class}")

        identity = self._source_identity(normalized_id)
        if identity is None:
            raise ValueError("source identity does not exist")
        if identity != (normalized_name, normalized_class):
            raise ValueError("portfolio source identity differs from canonical source")

        role = _enum(source_role, "source_role", SOURCE_ROLES)
        access = _enum(access_mode, "access_mode", ACCESS_MODES)
        cost = _enum(cost_mode, "cost_mode", COST_MODES)
        authentication = _enum(
            authentication_mode, "authentication_mode", AUTHENTICATION_MODES
        )
        availability = _enum(
            availability_state, "availability_state", AVAILABILITY_STATES
        )
        classification = _enum(
            data_classification, "data_classification", DATA_CLASSIFICATIONS
        )
        review = _enum(review_status, "review_status", REVIEW_STATUSES)

        regions = _strings(region_scope, "region_scope", required=True)
        languages = _strings(language_scope, "language_scope", required=True)
        networked = access in NETWORK_ACCESS_MODES
        domains = _domains(outbound_domains, required=networked)
        protocols = _strings(
            outbound_protocols,
            "outbound_protocols",
            required=networked,
            upper=True,
        )
        unsupported_protocols = set(protocols) - OUTBOUND_PROTOCOLS
        if unsupported_protocols:
            raise ValueError(
                "unsupported outbound protocol(s): "
                + ", ".join(sorted(unsupported_protocols))
            )
        fallbacks = _strings(fallback_source_ids, "fallback_source_ids")
        if normalized_id in fallbacks:
            raise ValueError("source cannot be its own fallback")

        if access == "PUBLIC_ANONYMOUS" and authentication != "NONE":
            raise ValueError("PUBLIC_ANONYMOUS access requires authentication_mode NONE")
        if access in {"PUBLIC_CREDENTIALED", "RESTRICTED"} and authentication == "NONE":
            raise ValueError(f"{access} access requires explicit authentication mode")
        if access == "USER_PROVIDED" and authentication != "NONE":
            raise ValueError("USER_PROVIDED access requires authentication_mode NONE")
        if classification in {"RESTRICTED", "SENSITIVE"} and access == "PUBLIC_ANONYMOUS":
            raise ValueError("restricted/sensitive data cannot use PUBLIC_ANONYMOUS access")
        if availability in OPERATIONAL_AVAILABILITY_STATES and review != "APPROVED":
            raise ValueError("operational availability requires APPROVED review status")
        if review == "RETIRED" and availability != "RETIRED":
            raise ValueError("RETIRED review status requires RETIRED availability")
        if availability == "RETIRED" and review != "RETIRED":
            raise ValueError("RETIRED availability requires RETIRED review status")
        if paid_provider_approved and cost != "PAID":
            raise ValueError("paid_provider_approved is only valid for PAID sources")
        if cost == "PAID" and review == "APPROVED" and not paid_provider_approved:
            raise ValueError(
                "PAID source approval requires a separate paid-provider approval"
            )

        freshness = _positive_int(
            expected_freshness_minutes, "expected_freshness_minutes"
        )
        cadence = _positive_int(
            collection_cadence_minutes, "collection_cadence_minutes"
        )
        normalized_adapter = _required(adapter_id, "adapter_id")
        normalized_adapter_version = _required(adapter_version, "adapter_version")
        if review == "APPROVED" and (
            normalized_adapter == "NOT_ASSIGNED"
            or normalized_adapter_version == "NOT_ASSIGNED"
        ):
            raise ValueError("APPROVED source requires assigned adapter identity/version")

        normalized_origin = _required(origin_characteristics, "origin_characteristics")
        normalized_independence = _required(
            independence_constraints, "independence_constraints"
        )
        normalized_owner = _required(owner, "owner")
        normalized_reviewer = _required(reviewer, "reviewer")
        normalized_terms = str(terms_notes).strip()
        reviewed = _normalize_time(reviewed_at or utc_now())
        created = _normalize_time(created_at or reviewed)
        if reviewed < created:
            raise ValueError("reviewed_at cannot precede created_at")

        previous = self.current(normalized_id)
        version = 1 if previous is None else previous.portfolio_version + 1
        supersedes = None if previous is None else previous.portfolio_entry_id
        entry_id = _stable_entry_id(normalized_id, version)

        with runtime_database_connection(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO source_portfolio_versions(
                    portfolio_entry_id, source_id, portfolio_version,
                    source_name, publisher_name, source_class, source_role,
                    region_scope_json, language_scope_json,
                    access_mode, cost_mode, authentication_mode,
                    expected_freshness_minutes, collection_cadence_minutes,
                    adapter_id, adapter_version,
                    outbound_domains_json, outbound_protocols_json,
                    fallback_source_ids_json, availability_state,
                    data_classification, origin_characteristics,
                    independence_constraints, terms_notes,
                    owner, reviewer, review_status, paid_provider_approved,
                    reviewed_at, supersedes_entry_id, created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    entry_id,
                    normalized_id,
                    version,
                    normalized_name,
                    normalized_publisher,
                    normalized_class,
                    role,
                    json.dumps(regions),
                    json.dumps(languages),
                    access,
                    cost,
                    authentication,
                    freshness,
                    cadence,
                    normalized_adapter,
                    normalized_adapter_version,
                    json.dumps(domains),
                    json.dumps(protocols),
                    json.dumps(fallbacks),
                    availability,
                    classification,
                    normalized_origin,
                    normalized_independence,
                    normalized_terms,
                    normalized_owner,
                    normalized_reviewer,
                    review,
                    int(paid_provider_approved),
                    reviewed.isoformat(),
                    supersedes,
                    created.isoformat(),
                ),
            )

        return SourcePortfolioRecord(
            portfolio_entry_id=entry_id,
            source_id=normalized_id,
            portfolio_version=version,
            source_name=normalized_name,
            publisher_name=normalized_publisher,
            source_class=normalized_class,
            source_role=role,
            region_scope=regions,
            language_scope=languages,
            access_mode=access,
            cost_mode=cost,
            authentication_mode=authentication,
            expected_freshness_minutes=freshness,
            collection_cadence_minutes=cadence,
            adapter_id=normalized_adapter,
            adapter_version=normalized_adapter_version,
            outbound_domains=domains,
            outbound_protocols=protocols,
            fallback_source_ids=fallbacks,
            availability_state=availability,
            data_classification=classification,
            origin_characteristics=normalized_origin,
            independence_constraints=normalized_independence,
            terms_notes=normalized_terms,
            owner=normalized_owner,
            reviewer=normalized_reviewer,
            review_status=review,
            paid_provider_approved=bool(paid_provider_approved),
            reviewed_at=reviewed,
            supersedes_entry_id=supersedes,
            created_at=created,
        )

    def current(self, source_id: str) -> SourcePortfolioRecord | None:
        normalized_id = _required(source_id, "source_id")
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT portfolio_entry_id, source_id, portfolio_version,
                       source_name, publisher_name, source_class, source_role,
                       region_scope_json, language_scope_json,
                       access_mode, cost_mode, authentication_mode,
                       expected_freshness_minutes, collection_cadence_minutes,
                       adapter_id, adapter_version,
                       outbound_domains_json, outbound_protocols_json,
                       fallback_source_ids_json, availability_state,
                       data_classification, origin_characteristics,
                       independence_constraints, terms_notes,
                       owner, reviewer, review_status, paid_provider_approved,
                       reviewed_at, supersedes_entry_id, created_at
                FROM source_portfolio_versions
                WHERE source_id = ?
                ORDER BY portfolio_version DESC
                LIMIT 1
                """,
                (normalized_id,),
            ).fetchone()
        return None if row is None else self._record_from_row(row)

    def history(self, source_id: str) -> tuple[SourcePortfolioRecord, ...]:
        normalized_id = _required(source_id, "source_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT portfolio_entry_id, source_id, portfolio_version,
                       source_name, publisher_name, source_class, source_role,
                       region_scope_json, language_scope_json,
                       access_mode, cost_mode, authentication_mode,
                       expected_freshness_minutes, collection_cadence_minutes,
                       adapter_id, adapter_version,
                       outbound_domains_json, outbound_protocols_json,
                       fallback_source_ids_json, availability_state,
                       data_classification, origin_characteristics,
                       independence_constraints, terms_notes,
                       owner, reviewer, review_status, paid_provider_approved,
                       reviewed_at, supersedes_entry_id, created_at
                FROM source_portfolio_versions
                WHERE source_id = ?
                ORDER BY portfolio_version
                """,
                (normalized_id,),
            ).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    def current_entries(self) -> tuple[SourcePortfolioRecord, ...]:
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT p.portfolio_entry_id, p.source_id, p.portfolio_version,
                       p.source_name, p.publisher_name, p.source_class, p.source_role,
                       p.region_scope_json, p.language_scope_json,
                       p.access_mode, p.cost_mode, p.authentication_mode,
                       p.expected_freshness_minutes, p.collection_cadence_minutes,
                       p.adapter_id, p.adapter_version,
                       p.outbound_domains_json, p.outbound_protocols_json,
                       p.fallback_source_ids_json, p.availability_state,
                       p.data_classification, p.origin_characteristics,
                       p.independence_constraints, p.terms_notes,
                       p.owner, p.reviewer, p.review_status, p.paid_provider_approved,
                       p.reviewed_at, p.supersedes_entry_id, p.created_at
                FROM source_portfolio_versions p
                JOIN (
                    SELECT source_id, MAX(portfolio_version) AS version
                    FROM source_portfolio_versions
                    GROUP BY source_id
                ) latest
                  ON latest.source_id = p.source_id
                 AND latest.version = p.portfolio_version
                ORDER BY p.source_id
                """
            ).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    @staticmethod
    def _record_from_row(row) -> SourcePortfolioRecord:
        return SourcePortfolioRecord(
            portfolio_entry_id=row[0],
            source_id=row[1],
            portfolio_version=int(row[2]),
            source_name=row[3],
            publisher_name=row[4],
            source_class=row[5],
            source_role=row[6],
            region_scope=tuple(json.loads(row[7])),
            language_scope=tuple(json.loads(row[8])),
            access_mode=row[9],
            cost_mode=row[10],
            authentication_mode=row[11],
            expected_freshness_minutes=int(row[12]),
            collection_cadence_minutes=int(row[13]),
            adapter_id=row[14],
            adapter_version=row[15],
            outbound_domains=tuple(json.loads(row[16])),
            outbound_protocols=tuple(json.loads(row[17])),
            fallback_source_ids=tuple(json.loads(row[18])),
            availability_state=row[19],
            data_classification=row[20],
            origin_characteristics=row[21],
            independence_constraints=row[22],
            terms_notes=row[23],
            owner=row[24],
            reviewer=row[25],
            review_status=row[26],
            paid_provider_approved=bool(row[27]),
            reviewed_at=datetime.fromisoformat(row[28]),
            supersedes_entry_id=row[29],
            created_at=datetime.fromisoformat(row[30]),
        )
