"""P22.5 bounded canonical semantic-ingestion bridge.

This bridge converts an already-created legacy live-analysis claim into the
additive P13 semantic stack without treating headline grouping, publisher
identity, source count, or official status as factual verification.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .semantic_claims import SemanticClaimService
from .semantic_evidence import SemanticEvidenceService
from .semantic_live_compatibility import SemanticLiveCompatibilityService
from .semantic_provenance import SemanticProvenanceService
from .semantic_verification import SemanticVerificationService


P22_5_SEMANTIC_BRIDGE_VERSION = "P22.5-BRIDGE-1.0"
P22_5_POLICY_ID = "p22-5-bounded-semantic-bridge-policy"
SUPPORTED_SOURCE_IDS = frozenset({
    "ofac-recent-actions-en",
    "white-house-briefings-en",
})
def _stable(prefix: str, *parts: str) -> str:
    payload = "\n".join(str(part) for part in parts)
    return f"{prefix}-" + sha256(payload.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class BridgedClaim:
    live_claim_id: str
    semantic_claim_version_id: str
    verification_state: str
    evidence_relation_count: int
    created: bool


@dataclass(frozen=True)
class BridgeRunResult:
    analysis_run_id: str
    claim_count: int
    created_count: int
    skipped_count: int
    evidence_relation_count: int
    verification_states: tuple[str, ...]


class P225SemanticIngestionBridge:
    """Fail-closed bridge for the owner-authorized B1 semantic observation."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.claims = SemanticClaimService(runtime)
        self.provenance = SemanticProvenanceService(runtime)
        self.evidence = SemanticEvidenceService(runtime)
        self.verification = SemanticVerificationService(runtime)
        self.compatibility = SemanticLiveCompatibilityService(runtime)
    def bridge_analysis_run(
        self,
        analysis_run_id: str,
        *,
        created_at: datetime,
    ) -> BridgeRunResult:
        run_id = str(analysis_run_id).strip()
        if not run_id:
            raise ValueError("analysis_run_id must not be empty")
        timestamp = _normalize_time(created_at)
        grouped = self._load_claim_evidence(run_id)
        if not grouped:
            raise ValueError("live analysis run has no evidence-backed claims")

        source_ids = {
            item["source_id"]
            for claim in grouped.values()
            for item in claim["evidence"]
        }
        unsupported = source_ids - SUPPORTED_SOURCE_IDS
        if unsupported:
            raise ValueError(
                "P22.5 bridge source is outside authorized B1 semantic cohort: "
                + ", ".join(sorted(unsupported))
            )

        self._ensure_policy(timestamp)
        results = [
            self._bridge_claim(live_claim_id, payload, timestamp)
            for live_claim_id, payload in sorted(grouped.items())
        ]
        states = tuple(sorted({item.verification_state for item in results}))
        return BridgeRunResult(
            analysis_run_id=run_id,
            claim_count=len(results),
            created_count=sum(1 for item in results if item.created),
            skipped_count=sum(1 for item in results if not item.created),
            evidence_relation_count=sum(item.evidence_relation_count for item in results),
            verification_states=states,
        )
    def _bridge_claim(
        self,
        live_claim_id: str,
        payload: dict[str, object],
        created_at: datetime,
    ) -> BridgedClaim:
        projection = self.compatibility.project(live_claim_id)
        if projection.compatibility_state == "LINKED_WITH_DECISION":
            decision = projection.semantic_decision
            assert decision is not None
            with sqlite3.connect(self.database_path) as connection:
                count = int(connection.execute(
                    """SELECT COUNT(*) FROM semantic_evidence_relation_versions
                       WHERE semantic_claim_version_id=?""",
                    (projection.semantic_claim_version_id,),
                ).fetchone()[0])
            return BridgedClaim(
                live_claim_id,
                str(projection.semantic_claim_version_id),
                decision.verification_state,
                count,
                False,
            )
        if projection.compatibility_state != "UNLINKED":
            raise RuntimeError(
                f"live claim {live_claim_id} has partial/ambiguous semantic state: "
                f"{projection.compatibility_state}"
            )

        title = str(payload["title"]).strip()
        semantic_id = _stable("p225-semantic-claim", live_claim_id)
        claim = self.claims.record_version(
            semantic_id,
            normalized_proposition=title,
            polarity="UNKNOWN",
            modality="REPORTED",
            original_language="en",
            extraction_method="BOUNDED_LIVE_TITLE_PROPOSITION_BRIDGE",
            extraction_version=P22_5_SEMANTIC_BRIDGE_VERSION,
            extraction_confidence=0.25,
            created_at=created_at,
        )
        self.claims.link(
            claim.semantic_claim_version_id,
            target_type="LIVE_ANALYSIS_CLAIM",
            target_id=live_claim_id,
            created_at=created_at,
        )

        unknown = self.provenance.record_entity_version(
            _stable("p225-unresolved-origin", live_claim_id),
            entity_kind="UNKNOWN",
            canonical_name="Unresolved underlying origin",
            metadata={"bridge_version": P22_5_SEMANTIC_BRIDGE_VERSION},
            created_at=created_at,
        )
        self.provenance.record_claim_role_version(
            _stable("p225-origin-role", live_claim_id),
            semantic_claim_version_id=claim.semantic_claim_version_id,
            provenance_entity_version_id=unknown.provenance_entity_version_id,
            provenance_role="UNDERLYING_ORIGIN",
            attribution_state="UNRESOLVED",
            note="Publisher/source identity does not establish underlying origin.",
            created_at=created_at,
        )

        relation_count = 0
        for item in payload["evidence"]:
            raw_id = str(item["raw_item_id"])
            source_id = str(item["source_id"])
            url = str(item["original_url"])
            publication = self.provenance.record_entity_version(
                _stable("p225-publication", raw_id),
                entity_kind="PUBLICATION",
                canonical_name=title,
                source_id=source_id,
                raw_item_id=raw_id,
                canonical_url=url,
                language="en",
                metadata={"bridge_version": P22_5_SEMANTIC_BRIDGE_VERSION},
                created_at=created_at,
            )
            self.provenance.record_claim_role_version(
                _stable("p225-publication-role", live_claim_id, raw_id),
                semantic_claim_version_id=claim.semantic_claim_version_id,
                provenance_entity_version_id=publication.provenance_entity_version_id,
                provenance_role="PUBLICATION",
                attribution_state="OBSERVED",
                created_at=created_at,
            )
            self.claims.link(
                claim.semantic_claim_version_id,
                target_type="RAW_ITEM",
                target_id=raw_id,
                created_at=created_at,
            )
            self.evidence.record_relation_version(
                _stable("p225-evidence", live_claim_id, raw_id),
                semantic_claim_version_id=claim.semantic_claim_version_id,
                evidence_provenance_entity_version_id=publication.provenance_entity_version_id,
                raw_item_id=raw_id,
                relation_type="ATTRIBUTION_ONLY",
                assessment_method="P22_5_BOUNDED_BRIDGE",
                assessment_version=P22_5_SEMANTIC_BRIDGE_VERSION,
                note="Publication/title evidence only; no automatic support or independence.",
                created_at=created_at,
            )
            relation_count += 1

        self.verification.record_confidence_version(
            claim.semantic_claim_version_id,
            evidence_sufficiency="LOW",
            provenance_independence="UNKNOWN",
            authority_proximity="LOW",
            contradiction_resolution="UNKNOWN",
            temporal_freshness="UNKNOWN",
            extraction_certainty="LOW",
            translation_certainty="UNKNOWN",
            claim_specific_certainty="LOW",
            coverage_limitation="LIMITED",
            assessment_method="P22_5_BOUNDED_BRIDGE",
            assessment_version=P22_5_SEMANTIC_BRIDGE_VERSION,
            note="Fail-closed title-derived proposition with unresolved underlying origin.",
            created_at=created_at,
        )
        decision = self.verification.record_decision(
            claim.semantic_claim_version_id,
            policy_id=P22_5_POLICY_ID,
            verification_state="DETECTED",
            decision_code="INITIAL",
            rationale=(
                "Canonical claim is linked to observed publication evidence, but "
                "claim specificity, freshness and underlying-origin independence "
                "remain insufficient for factual promotion."
            ),
            created_at=created_at,
        )
        return BridgedClaim(
            live_claim_id,
            claim.semantic_claim_version_id,
            decision.verification_state,
            relation_count,
            True,
        )

    def _ensure_policy(self, created_at: datetime) -> None:
        current = self.verification.policy_current(P22_5_POLICY_ID)
        if current is None:
            self.verification.record_policy_version(
                P22_5_POLICY_ID,
                policy_name="P22.5 bounded semantic-ingestion verification policy",
                created_at=created_at,
            )
            return
        if current.review_status != "APPROVED":
            raise RuntimeError("P22.5 bridge policy is not approved")
    def _load_claim_evidence(
        self,
        analysis_run_id: str,
    ) -> dict[str, dict[str, object]]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """SELECT c.claim_id,c.title,e.raw_item_id,e.original_url,r.source_id
                   FROM live_analysis_claims c
                   JOIN live_analysis_evidence e ON e.claim_id=c.claim_id
                   JOIN raw_items r ON r.id=e.raw_item_id
                   WHERE c.analysis_run_id=?
                   ORDER BY c.claim_id,e.raw_item_id""",
                (analysis_run_id,),
            ).fetchall()
        grouped: dict[str, dict[str, object]] = {}
        for live_id, title, raw_id, url, source_id in rows:
            item = grouped.setdefault(
                str(live_id),
                {"title": str(title), "evidence": []},
            )
            item["evidence"].append({
                "raw_item_id": str(raw_id),
                "original_url": str(url),
                "source_id": str(source_id),
            })
        return grouped
