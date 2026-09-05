"""Phase 17.1 deterministic publication eligibility policy.

Eligibility is a derived, fail-closed publication-readiness decision over the
existing P13.6 live compatibility projection and its current P13.5 semantic
verification decision. This module never recalculates factual verification and
never uses legacy status, scalar confidence or source/origin counts as a
publication promotion path.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime
from .semantic_live_compatibility import (
    SemanticLiveCompatibilityProjection,
    SemanticLiveCompatibilityService,
)


PUBLICATION_ELIGIBILITY_POLICY_VERSION = "KGM_PUBLICATION_ELIGIBILITY_POLICY_V1"
P17_1_GATE = "P17_1_PUBLICATION_ELIGIBILITY_POLICY_VALIDATED"
P17_1_MIGRATION = "NONE"

PUBLIC_SAFETY_STATES = ("ALLOWED", "BLOCKED", "UNKNOWN")
ELIGIBILITY_STATES = ("ELIGIBLE", "BLOCKED")

REASON_ELIGIBLE = "CANONICAL_VERIFIED_PUBLIC_SAFE"
REASON_PUBLIC_SAFETY_BLOCKED = "PUBLIC_SAFETY_BLOCKED"
REASON_PUBLIC_SAFETY_UNKNOWN = "PUBLIC_SAFETY_UNKNOWN"
REASON_UNLINKED = "CANONICAL_REFERENCE_UNLINKED"
REASON_STALE = "CANONICAL_REFERENCE_STALE"
REASON_AMBIGUOUS = "CANONICAL_REFERENCE_AMBIGUOUS"
REASON_DECISION_MISSING = "CANONICAL_DECISION_MISSING"
REASON_CONFIDENCE_REFERENCE_MISSING = "CANONICAL_CONFIDENCE_REFERENCE_MISSING"
REASON_COMPATIBILITY_UNSUPPORTED = "CANONICAL_COMPATIBILITY_UNSUPPORTED"
REASON_VERIFICATION_PREFIX = "CANONICAL_VERIFICATION_"

LIMITATION_COVERAGE_UNKNOWN = "COVERAGE_UNKNOWN"
LIMITATION_COVERAGE_LIMITED = "COVERAGE_LIMITED"
LIMITATION_REPRODUCIBILITY_NOT_INSTRUMENTED = "REPRODUCIBILITY_NOT_INSTRUMENTED"
LIMITATION_REPRODUCIBILITY_FAILED = "REPRODUCIBILITY_INSTRUMENTED_FAILED"


@dataclass(frozen=True)
class PublicationEligibilityDecision:
    publication_candidate_id: str
    policy_version: str
    live_claim_id: str
    semantic_claim_version_id: str | None
    verification_decision_version_id: str | None
    canonical_policy_version_id: str | None
    factual_confidence_version_id: str | None
    compatibility_state: str
    canonical_verification_state: str | None
    coverage_limitation: str | None
    reproducibility_state: str
    public_safety_state: str
    eligibility_state: str
    reason_codes: tuple[str, ...]
    limitation_codes: tuple[str, ...]

    @property
    def promotes_factual_verification(self) -> bool:
        return False

    @property
    def uses_legacy_truth_fallback(self) -> bool:
        return False


@dataclass(frozen=True)
class PublicationEligibilityBoundary:
    runtime_storage: str = "PROJECT_LOCAL_ONLY"
    mixed_shared_canonical_runtime: str = "BLOCKED"
    production_live: str = "NOT_OPERATIONAL"
    public_ingress: str = "NOT_APPROVED_NOT_DEPLOYED"
    public_sharing: str = "NOT_ACTIVE"
    paid_providers: str = "NONE_APPROVED"
    owner_execution: str = "DISABLED"
    activation_gate: str = "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


PUBLICATION_ELIGIBILITY_BOUNDARY = PublicationEligibilityBoundary()


def _normalize_public_safety_state(value: object) -> str:
    state = str(value).strip().upper()
    if state not in PUBLIC_SAFETY_STATES:
        raise ValueError(f"unsupported public_safety_state: {state or '<empty>'}")
    return state


def _candidate_id(
    projection: SemanticLiveCompatibilityProjection,
    public_safety_state: str,
) -> str:
    decision = projection.semantic_decision
    identity = {
        "policy_version": PUBLICATION_ELIGIBILITY_POLICY_VERSION,
        "live_claim_id": projection.legacy.live_claim_id,
        "semantic_claim_version_id": projection.semantic_claim_version_id,
        "verification_decision_version_id": (
            None if decision is None else decision.verification_decision_version_id
        ),
        "public_safety_state": public_safety_state,
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "publication-candidate-" + sha256(encoded.encode("utf-8")).hexdigest()[:24]


def _canonical_reason_codes(
    projection: SemanticLiveCompatibilityProjection,
    *,
    coverage_limitation: str | None,
) -> list[str]:
    state = projection.compatibility_state
    if state == "UNLINKED":
        return [REASON_UNLINKED]
    if state == "STALE_LINK":
        return [REASON_STALE]
    if state == "AMBIGUOUS_CURRENT_LINKS":
        return [REASON_AMBIGUOUS]
    if state == "LINKED_NO_DECISION":
        return [REASON_DECISION_MISSING]
    if state != "LINKED_WITH_DECISION":
        return [REASON_COMPATIBILITY_UNSUPPORTED]

    decision = projection.semantic_decision
    if decision is None:
        return [REASON_DECISION_MISSING]
    if coverage_limitation is None:
        return [REASON_CONFIDENCE_REFERENCE_MISSING]
    if decision.verification_state != "VERIFIED":
        return [REASON_VERIFICATION_PREFIX + decision.verification_state]
    return []


def _limitation_codes(
    *,
    coverage_limitation: str | None,
    reproducibility_state: str,
) -> tuple[str, ...]:
    limitations: list[str] = []
    if coverage_limitation == "UNKNOWN":
        limitations.append(LIMITATION_COVERAGE_UNKNOWN)
    elif coverage_limitation == "LIMITED":
        limitations.append(LIMITATION_COVERAGE_LIMITED)

    if reproducibility_state == "NOT_INSTRUMENTED":
        limitations.append(LIMITATION_REPRODUCIBILITY_NOT_INSTRUMENTED)
    elif reproducibility_state == "INSTRUMENTED_FAILED":
        limitations.append(LIMITATION_REPRODUCIBILITY_FAILED)
    return tuple(limitations)


def evaluate_publication_eligibility(
    projection: SemanticLiveCompatibilityProjection,
    *,
    public_safety_state: str,
    coverage_limitation: str | None,
) -> PublicationEligibilityDecision:
    """Evaluate publication readiness without recalculating semantic truth.

    ``coverage_limitation`` must correspond to the factual-confidence version
    referenced by the current P13.5 decision. Coverage is exposed as a
    limitation label only and never enables factual or publication promotion.
    """

    safety = _normalize_public_safety_state(public_safety_state)
    if coverage_limitation is not None:
        coverage = str(coverage_limitation).strip().upper()
        if coverage not in ("UNKNOWN", "LIMITED", "ADEQUATE"):
            raise ValueError(f"unsupported coverage_limitation: {coverage}")
    else:
        coverage = None

    reasons = _canonical_reason_codes(projection, coverage_limitation=coverage)
    if safety == "BLOCKED":
        reasons.append(REASON_PUBLIC_SAFETY_BLOCKED)
    elif safety == "UNKNOWN":
        reasons.append(REASON_PUBLIC_SAFETY_UNKNOWN)

    eligible = not reasons and safety == "ALLOWED"
    if eligible:
        reasons = [REASON_ELIGIBLE]

    decision = projection.semantic_decision
    return PublicationEligibilityDecision(
        publication_candidate_id=_candidate_id(projection, safety),
        policy_version=PUBLICATION_ELIGIBILITY_POLICY_VERSION,
        live_claim_id=projection.legacy.live_claim_id,
        semantic_claim_version_id=projection.semantic_claim_version_id,
        verification_decision_version_id=(
            None if decision is None else decision.verification_decision_version_id
        ),
        canonical_policy_version_id=(None if decision is None else decision.policy_version_id),
        factual_confidence_version_id=(
            None if decision is None else decision.factual_confidence_version_id
        ),
        compatibility_state=projection.compatibility_state,
        canonical_verification_state=(
            None if decision is None else decision.verification_state
        ),
        coverage_limitation=coverage,
        reproducibility_state=projection.reproducibility_state,
        public_safety_state=safety,
        eligibility_state="ELIGIBLE" if eligible else "BLOCKED",
        reason_codes=tuple(reasons),
        limitation_codes=_limitation_codes(
            coverage_limitation=coverage,
            reproducibility_state=projection.reproducibility_state,
        ),
    )


class PublicationEligibilityService:
    """Read-only P17.1 service over canonical P13.6/P13.5 persisted state."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path
        self._compatibility = SemanticLiveCompatibilityService(runtime)

    def evaluate_live_claim(
        self,
        live_claim_id: str,
        *,
        public_safety_state: str,
    ) -> PublicationEligibilityDecision:
        projection = self._compatibility.project(live_claim_id)
        coverage = self._decision_coverage_limitation(projection)
        return evaluate_publication_eligibility(
            projection,
            public_safety_state=public_safety_state,
            coverage_limitation=coverage,
        )

    def _decision_coverage_limitation(
        self,
        projection: SemanticLiveCompatibilityProjection,
    ) -> str | None:
        decision = projection.semantic_decision
        if decision is None:
            return None
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """SELECT semantic_claim_version_id,coverage_limitation
                   FROM semantic_factual_confidence_versions
                   WHERE factual_confidence_version_id=?""",
                (decision.factual_confidence_version_id,),
            ).fetchone()
        if row is None:
            return None
        if str(row[0]) != decision.semantic_claim_version_id:
            return None
        return str(row[1])


__all__ = [
    "PUBLICATION_ELIGIBILITY_POLICY_VERSION",
    "P17_1_GATE",
    "P17_1_MIGRATION",
    "PUBLIC_SAFETY_STATES",
    "ELIGIBILITY_STATES",
    "PublicationEligibilityDecision",
    "PublicationEligibilityBoundary",
    "PUBLICATION_ELIGIBILITY_BOUNDARY",
    "PublicationEligibilityService",
    "evaluate_publication_eligibility",
]
