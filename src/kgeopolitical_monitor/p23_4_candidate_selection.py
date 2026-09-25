"""P23.4 evidence-yield candidate selection readiness.

Pure, non-activating classifier. It converts governed candidate metadata and
previous remediation outcomes into explicit readiness classes. It never grants
source activation, independence, factual verification, or coverage credit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


P23_4_SELECTION_VERSION = "P23.4-selection-1.0"


@dataclass(frozen=True)
class CandidateReadiness:
    candidate_id: str
    source_id: str
    cell_id: str
    readiness_class: str
    reason_codes: tuple[str, ...]
    expected_dimensions: tuple[str, ...]
    activation_authorized: bool = False
    independence_credit_granted: bool = False


def classify_candidate(
    candidate: Mapping[str, object],
    *,
    repository_active_source_ids: Iterable[str],
    remediation_readiness: Mapping[str, str] | None = None,
) -> CandidateReadiness:
    """Classify a P22.2 candidate for P23.4 preparation.

    The function is deliberately conservative:
    - active paths are excluded from expansion selection;
    - P23.1 readiness may make a source ready only for an owner-gated
      activation *revalidation*, never activation itself;
    - transport and governance blockers remain blockers;
    - no candidate receives factual-independence credit.
    """

    active = {str(x) for x in repository_active_source_ids}
    remediation = {str(k): str(v) for k, v in (remediation_readiness or {}).items()}

    candidate_id = str(candidate["candidate_id"])
    source_id = str(candidate["source_id_proposal"])
    cell_id = str(candidate["cell_id"])
    qualification = str(candidate.get("qualification_decision", "UNKNOWN"))
    rights = str(candidate.get("automated_collection_rights_state", "UNKNOWN"))
    provenance = candidate.get("provenance") or {}
    origin_group = None
    if isinstance(provenance, Mapping):
        origin_group = provenance.get("origin_group_id")

    expected = ["REQUIRED_COVERAGE"]
    if origin_group:
        expected.append("PROVENANCE_ORIGIN_DEPTH")

    if source_id in active:
        status = "ALREADY_REPOSITORY_ACTIVE"
        reasons = ("EXCLUDE_FROM_NEW_EXPANSION",)
    elif remediation.get(source_id) == "READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION":
        status = "READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION"
        reasons = ("P23_1_BOUNDED_REMEDIATION_VALIDATED", "OWNER_ACTIVATION_DECISION_REQUIRED")
    elif remediation.get(source_id) == "BLOCKED_HTTPS_TRANSPORT_TIMEOUT":
        status = "BLOCKED_TRANSPORT"
        reasons = ("HTTPS_TRANSPORT_TIMEOUT", "NO_HTTP_FALLBACK")
    elif qualification == "CONDITIONAL_TAXONOMY_AND_RIGHTS_REVIEW":
        status = "TAXONOMY_AND_RIGHTS_REVIEW_REQUIRED"
        reasons = ("TAXONOMY_GOVERNANCE_PENDING", "AUTOMATED_COLLECTION_RIGHTS_REVIEW_PENDING")
    elif qualification == "QUALIFIED_FOR_FIXTURE_BUILD" and rights == "PENDING_REVIEW":
        status = "RIGHTS_REVIEW_REQUIRED_BEFORE_FIXTURE"
        reasons = ("FIXTURE_BUILD_QUALIFIED", "AUTOMATED_COLLECTION_RIGHTS_REVIEW_PENDING")
    elif qualification == "CONDITIONAL_RIGHTS_REVIEW" or "RIGHTS_REVIEW" in rights:
        status = "RIGHTS_REVIEW_REQUIRED"
        reasons = ("AUTOMATED_COLLECTION_RIGHTS_REVIEW_PENDING",)
    else:
        status = "NOT_READY"
        reasons = ("UNRESOLVED_GOVERNANCE_OR_READINESS_BLOCKERS",)

    return CandidateReadiness(
        candidate_id=candidate_id,
        source_id=source_id,
        cell_id=cell_id,
        readiness_class=status,
        reason_codes=reasons,
        expected_dimensions=tuple(expected),
        activation_authorized=False,
        independence_credit_granted=False,
    )


def select_preparation_cohort(readiness: Iterable[CandidateReadiness]) -> tuple[str, ...]:
    """Return source IDs suitable for governance/rights preparation only.

    This is not an onboarding or activation selection. It intentionally limits
    preparation to exact-taxonomy candidates already qualified for fixture
    build but still blocked on rights review.
    """

    return tuple(
        sorted(
            item.source_id
            for item in readiness
            if item.readiness_class == "RIGHTS_REVIEW_REQUIRED_BEFORE_FIXTURE"
        )
    )
