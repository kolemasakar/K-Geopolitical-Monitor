"""Phase 13 P13.6 read-only compatibility projection for legacy live analysis.

This module bridges historical M8 ``live_analysis_*`` rows to the additive
P13.1-P13.5 semantic stack without rewriting either side. Historical
normalized-title grouping, URL-host counts, ``independent_origin_count`` and
scalar confidence remain compatibility observations only. Canonical semantic
verification is exposed only when an explicit P13.1 ``LIVE_ANALYSIS_CLAIM``
link resolves unambiguously to a current semantic claim version that has a
current P13.5 policy-controlled decision.

No database migration is required for this projection. Reproducibility metadata
is exposed only when E6 instrumentation actually persisted it for the source
collection; missing instrumentation is never reconstructed.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime
from .reproducibility import ReproducibilityStore
from .semantic_verification import SemanticVerificationDecisionVersion, SemanticVerificationService


SEMANTIC_LIVE_COMPATIBILITY_VERSION = "P13.6-1.0"
COMPATIBILITY_STATES = (
    "UNLINKED",
    "STALE_LINK",
    "LINKED_NO_DECISION",
    "LINKED_WITH_DECISION",
    "AMBIGUOUS_CURRENT_LINKS",
)
REPRODUCIBILITY_STATES = (
    "NOT_INSTRUMENTED",
    "INSTRUMENTED_COMPLETED",
    "INSTRUMENTED_FAILED",
)


@dataclass(frozen=True)
class LegacyLiveClaimSnapshot:
    live_claim_id: str
    analysis_run_id: str
    collection_id: str
    watch_id: str
    claim_key: str
    title: str
    legacy_verification_status: str
    legacy_confidence: float
    importance: float
    legacy_independent_origin_count: int
    source_class_count: int
    legacy_origins: tuple[str, ...]
    raw_item_ids: tuple[str, ...]
    origin_hosts: tuple[str, ...]

    @property
    def determines_semantic_verification(self) -> bool:
        return False

    @property
    def establishes_semantic_independence(self) -> bool:
        return False


@dataclass(frozen=True)
class SemanticLiveCompatibilityProjection:
    legacy: LegacyLiveClaimSnapshot
    compatibility_state: str
    historical_semantic_claim_version_ids: tuple[str, ...]
    current_semantic_claim_version_ids: tuple[str, ...]
    semantic_claim_version_id: str | None
    semantic_decision: SemanticVerificationDecisionVersion | None
    reproducibility_state: str
    research_run_id: str | None
    exact_query_snapshot: str | None
    research_cutoff: str | None
    instrumentation_version: str | None

    @property
    def semantic_verification_state(self) -> str | None:
        return None if self.semantic_decision is None else self.semantic_decision.verification_state

    @property
    def has_canonical_semantic_decision(self) -> bool:
        return self.semantic_decision is not None

    @property
    def legacy_status_promoted(self) -> bool:
        return False

    @property
    def legacy_confidence_promoted(self) -> bool:
        return False

    @property
    def legacy_origin_count_establishes_independence(self) -> bool:
        return False


class SemanticLiveCompatibilityService:
    """Read-only P13.6 projection over legacy live and current semantic state."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path
        self._verification = SemanticVerificationService(runtime)
        self._reproducibility = ReproducibilityStore(runtime.database_path)

    def project(self, live_claim_id: str) -> SemanticLiveCompatibilityProjection:
        claim_id = str(live_claim_id).strip()
        if not claim_id:
            raise ValueError("live_claim_id must not be empty")

        legacy = self._legacy_snapshot(claim_id)
        historical_ids, current_ids = self._semantic_links(claim_id)

        semantic_version_id: str | None = None
        decision: SemanticVerificationDecisionVersion | None = None
        if not historical_ids:
            compatibility_state = "UNLINKED"
        elif not current_ids:
            compatibility_state = "STALE_LINK"
        elif len(current_ids) > 1:
            compatibility_state = "AMBIGUOUS_CURRENT_LINKS"
        else:
            semantic_version_id = current_ids[0]
            decision = self._verification.decision_current(semantic_version_id)
            compatibility_state = (
                "LINKED_WITH_DECISION" if decision is not None else "LINKED_NO_DECISION"
            )

        reproducibility_state, research_run_id, exact_query, cutoff, instrumentation = (
            self._reproducibility_snapshot(legacy.collection_id)
        )
        return SemanticLiveCompatibilityProjection(
            legacy=legacy,
            compatibility_state=compatibility_state,
            historical_semantic_claim_version_ids=historical_ids,
            current_semantic_claim_version_ids=current_ids,
            semantic_claim_version_id=semantic_version_id,
            semantic_decision=decision,
            reproducibility_state=reproducibility_state,
            research_run_id=research_run_id,
            exact_query_snapshot=exact_query,
            research_cutoff=cutoff,
            instrumentation_version=instrumentation,
        )

    def project_analysis_run(self, analysis_run_id: str) -> tuple[SemanticLiveCompatibilityProjection, ...]:
        run_id = str(analysis_run_id).strip()
        if not run_id:
            raise ValueError("analysis_run_id must not be empty")
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT claim_id FROM live_analysis_claims WHERE analysis_run_id=? ORDER BY claim_id",
                (run_id,),
            ).fetchall()
        if not rows:
            raise ValueError("live analysis run has no claims or does not exist")
        return tuple(self.project(str(row[0])) for row in rows)

    def project_collection(self, collection_id: str) -> tuple[SemanticLiveCompatibilityProjection, ...]:
        collection = str(collection_id).strip()
        if not collection:
            raise ValueError("collection_id must not be empty")
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT analysis_run_id FROM live_analysis_runs WHERE collection_id=?",
                (collection,),
            ).fetchone()
        if row is None:
            raise ValueError("collection has no live analysis run")
        return self.project_analysis_run(str(row[0]))

    def semantic_state(self, live_claim_id: str) -> str | None:
        """Return only canonical P13.5 semantic state; never fall back to legacy status."""
        return self.project(live_claim_id).semantic_verification_state

    def _legacy_snapshot(self, live_claim_id: str) -> LegacyLiveClaimSnapshot:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT c.claim_id,c.analysis_run_id,r.collection_id,r.watch_id,
                       c.claim_key,c.title,c.verification_status,c.confidence,
                       c.importance,c.independent_origin_count,c.source_class_count,
                       c.origins_json
                FROM live_analysis_claims c
                JOIN live_analysis_runs r ON r.analysis_run_id=c.analysis_run_id
                WHERE c.claim_id=?
                """,
                (live_claim_id,),
            ).fetchone()
            if row is None:
                raise ValueError("live analysis claim does not exist")
            evidence_rows = connection.execute(
                """
                SELECT raw_item_id,origin_host
                FROM live_analysis_evidence
                WHERE claim_id=? ORDER BY raw_item_id,origin_host
                """,
                (live_claim_id,),
            ).fetchall()

        try:
            origins_value = json.loads(row[11])
        except (TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("legacy live claim origins_json is invalid") from exc
        if not isinstance(origins_value, list) or any(not isinstance(item, str) for item in origins_value):
            raise RuntimeError("legacy live claim origins_json must be a string array")

        raw_ids = tuple(sorted({str(item[0]) for item in evidence_rows}))
        hosts = tuple(sorted({str(item[1]) for item in evidence_rows if str(item[1]).strip()}))
        return LegacyLiveClaimSnapshot(
            live_claim_id=str(row[0]),
            analysis_run_id=str(row[1]),
            collection_id=str(row[2]),
            watch_id=str(row[3]),
            claim_key=str(row[4]),
            title=str(row[5]),
            legacy_verification_status=str(row[6]),
            legacy_confidence=float(row[7]),
            importance=float(row[8]),
            legacy_independent_origin_count=int(row[9]),
            source_class_count=int(row[10]),
            legacy_origins=tuple(str(item) for item in origins_value),
            raw_item_ids=raw_ids,
            origin_hosts=hosts,
        )

    def _semantic_links(self, live_claim_id: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT v.semantic_claim_version_id,v.semantic_claim_id,v.semantic_version,
                       latest.latest_version
                FROM semantic_claim_links l
                JOIN semantic_claim_versions v
                  ON v.semantic_claim_version_id=l.semantic_claim_version_id
                JOIN (
                    SELECT semantic_claim_id,MAX(semantic_version) AS latest_version
                    FROM semantic_claim_versions GROUP BY semantic_claim_id
                ) latest ON latest.semantic_claim_id=v.semantic_claim_id
                WHERE l.target_type='LIVE_ANALYSIS_CLAIM' AND l.target_id=?
                ORDER BY v.semantic_claim_id,v.semantic_version,v.semantic_claim_version_id
                """,
                (live_claim_id,),
            ).fetchall()
        historical = tuple(str(row[0]) for row in rows)
        current = tuple(str(row[0]) for row in rows if int(row[2]) == int(row[3]))
        return historical, current

    def _reproducibility_snapshot(
        self,
        collection_id: str,
    ) -> tuple[str, str | None, str | None, str | None, str | None]:
        bundle = self._reproducibility.bundle_for_collection(collection_id)
        if bundle is None:
            return "NOT_INSTRUMENTED", None, None, None, None
        run = bundle["research_run"]
        status = str(run["status"])
        if status == "COMPLETED":
            state = "INSTRUMENTED_COMPLETED"
        elif status == "FAILED":
            state = "INSTRUMENTED_FAILED"
        else:
            raise RuntimeError("instrumented collection audit is not terminal")
        return (
            state,
            str(run["research_run_id"]),
            str(run["exact_query_snapshot"]),
            str(run["research_cutoff"]),
            str(run["instrumentation_version"]),
        )
