"""Phase 23 P23.2 underlying-origin/provenance resolution observation.

This layer is intentionally read-only. It distinguishes confirmed first-party
publication provenance from resolved underlying origin, so a publisher/host
match cannot silently create origin or independence credit.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Iterable, Mapping
from urllib.parse import urlsplit

from .operational_monitoring import OperationalMonitoringRuntime


P23_2_PROVENANCE_RESOLUTION_VERSION = "P23.2-1.0"


def _host(url: str | None) -> str | None:
    if not url:
        return None
    try:
        value = (urlsplit(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return None
    return value or None


def _normalized_hosts(values: Iterable[str]) -> frozenset[str]:
    result = set()
    for value in values:
        host = str(value).strip().lower().rstrip(".")
        if host:
            result.add(host)
    return frozenset(result)


@dataclass(frozen=True)
class OriginResolutionObservation:
    analysis_run_id: str
    claim_count: int
    first_party_publication_count: int
    resolved_underlying_origin_count: int
    asserted_underlying_origin_count: int
    unresolved_underlying_origin_count: int
    mixed_underlying_origin_count: int
    other_underlying_origin_state_count: int
    semantic_independence_assessment_count: int

    @property
    def underlying_origin_resolution_rate(self) -> float | None:
        if self.claim_count == 0:
            return None
        return self.resolved_underlying_origin_count / self.claim_count

    @property
    def first_party_publication_is_origin_credit(self) -> bool:
        return False

    @property
    def grants_independence_credit(self) -> bool:
        return False


class UnderlyingOriginResolutionObserver:
    """Read-only exact-cohort provenance observer.

    First-party publication confirmation is contextual provenance only.
    Resolved origin requires a current concrete UNDERLYING_ORIGIN role with
    attribution_state=OBSERVED. ASSERTED, UNRESOLVED and MIXED do not count.
    """

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        *,
        trusted_first_party_hosts: Mapping[str, Iterable[str]],
    ):
        self.database_path = runtime.database_path
        self.trusted_first_party_hosts = {
            str(source_id): _normalized_hosts(hosts)
            for source_id, hosts in trusted_first_party_hosts.items()
        }

    def observe_analysis_run(self, analysis_run_id: str) -> OriginResolutionObservation:
        run_id = str(analysis_run_id).strip()
        if not run_id:
            raise ValueError("analysis_run_id must not be empty")

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT
                    c.semantic_claim_version_id,
                    ri.source_id,
                    le.original_url,
                    role.attribution_state,
                    origin.entity_kind
                FROM semantic_claim_versions c
                JOIN semantic_claim_links live_link
                  ON live_link.semantic_claim_version_id=c.semantic_claim_version_id
                 AND live_link.target_type='LIVE_ANALYSIS_CLAIM'
                JOIN live_analysis_claims lc
                  ON lc.claim_id=live_link.target_id
                 AND lc.analysis_run_id=?
                JOIN semantic_claim_links raw_link
                  ON raw_link.semantic_claim_version_id=c.semantic_claim_version_id
                 AND raw_link.target_type='RAW_ITEM'
                JOIN raw_items ri
                  ON ri.id=raw_link.target_id
                LEFT JOIN live_analysis_evidence le
                  ON le.claim_id=lc.claim_id
                 AND le.raw_item_id=ri.id
                LEFT JOIN semantic_claim_provenance_role_versions role
                  ON role.semantic_claim_version_id=c.semantic_claim_version_id
                 AND role.provenance_role='UNDERLYING_ORIGIN'
                 AND role.role_version=(
                    SELECT MAX(role2.role_version)
                    FROM semantic_claim_provenance_role_versions role2
                    WHERE role2.claim_provenance_role_id=role.claim_provenance_role_id
                 )
                LEFT JOIN semantic_provenance_entity_versions origin
                  ON origin.provenance_entity_version_id=role.provenance_entity_version_id
                WHERE c.extraction_method='PUBLICATION_ATTRIBUTION_BRIDGE'
                ORDER BY c.semantic_claim_version_id
                """,
                (run_id,),
            ).fetchall()

            independence_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM semantic_independence_assessment_versions ia
                WHERE ia.semantic_claim_version_id IN (
                    SELECT DISTINCT c.semantic_claim_version_id
                    FROM semantic_claim_versions c
                    JOIN semantic_claim_links l
                      ON l.semantic_claim_version_id=c.semantic_claim_version_id
                     AND l.target_type='LIVE_ANALYSIS_CLAIM'
                    JOIN live_analysis_claims lc
                      ON lc.claim_id=l.target_id
                    WHERE lc.analysis_run_id=?
                      AND c.extraction_method='PUBLICATION_ATTRIBUTION_BRIDGE'
                )
                """,
                (run_id,),
            ).fetchone()[0]

        first_party = 0
        resolved = 0
        asserted = 0
        unresolved = 0
        mixed = 0
        other = 0

        for _claim_id, source_id, original_url, state, entity_kind in rows:
            host = _host(original_url)
            if host is not None and host in self.trusted_first_party_hosts.get(source_id, frozenset()):
                first_party += 1

            normalized_state = (state or "").upper()
            normalized_kind = (entity_kind or "").upper()
            concrete = normalized_kind not in {"", "UNKNOWN", "MIXED"}

            if normalized_state == "OBSERVED" and concrete:
                resolved += 1
            elif normalized_state == "ASSERTED":
                asserted += 1
            elif normalized_state == "UNRESOLVED" and normalized_kind == "UNKNOWN":
                unresolved += 1
            elif normalized_state == "MIXED" and normalized_kind == "MIXED":
                mixed += 1
            else:
                other += 1

        return OriginResolutionObservation(
            analysis_run_id=run_id,
            claim_count=len(rows),
            first_party_publication_count=first_party,
            resolved_underlying_origin_count=resolved,
            asserted_underlying_origin_count=asserted,
            unresolved_underlying_origin_count=unresolved,
            mixed_underlying_origin_count=mixed,
            other_underlying_origin_state_count=other,
            semantic_independence_assessment_count=int(independence_count),
        )
