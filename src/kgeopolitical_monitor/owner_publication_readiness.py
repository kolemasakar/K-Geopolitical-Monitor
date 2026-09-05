"""Phase 17.5 owner publication readiness projection.

Read-only project-local preview of publication readiness. It never publishes,
approves activation, exposes a route, deploys HTTPS, or connects a GPT Action.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .publication_eligibility import PublicationEligibilityDecision
from .public_safe_projection import PublicSafeProjection
from .publication_target import PublicationTargetReceipt
from .release_manifest import PublicationPackage


OWNER_PUBLICATION_READINESS_VERSION: Final[str] = "KGM_OWNER_PUBLICATION_READINESS_V1"
P17_5_GATE: Final[str] = "P17_5_OWNER_PUBLICATION_READINESS_PROJECTION_VALIDATED"
P17_5_MIGRATION: Final[str] = "NONE"


@dataclass(frozen=True)
class OwnerPublicationReadiness:
    schema_version: str
    publication_candidate_id: str
    eligibility_state: str
    reason_codes: tuple[str, ...]
    limitation_codes: tuple[str, ...]
    public_safety_state: str
    canonical_verification_state: str | None
    coverage_limitation: str | None
    reproducibility_state: str
    public_projection_id: str | None
    redaction_status: str | None
    release_id: str | None
    release_manifest_id: str | None
    payload_sha256: str | None
    local_test_target_status: str | None
    unresolved_activation_prerequisites: tuple[str, ...]
    readiness_state: str

    @property
    def approval_effect(self) -> str:
        return "NONE"

    @property
    def publication_effect(self) -> str:
        return "NONE"


UNRESOLVED_ACTIVATION_PREREQUISITES: Final[tuple[str, ...]] = (
    "EXPLICIT_OWNER_ACTIVATION_DECISION_REQUIRED",
    "REAL_PUBLICATION_TARGET_NOT_APPROVED",
    "PUBLIC_INGRESS_NOT_APPROVED_NOT_DEPLOYED",
    "BACKEND_HTTPS_NOT_DEPLOYED",
    "PUBLIC_GPT_ACTION_NOT_CONNECTED_OR_APPROVED",
    "PUBLIC_SHARING_NOT_ACTIVE",
    "PAID_PROVIDERS_NONE_APPROVED",
    "THEN_CURRENT_PLATFORM_SECURITY_PRIVACY_ROLLBACK_VALIDATION_REQUIRED",
)


def project_owner_publication_readiness(
    eligibility: PublicationEligibilityDecision,
    *,
    projection: PublicSafeProjection | None = None,
    package: PublicationPackage | None = None,
    receipt: PublicationTargetReceipt | None = None,
) -> OwnerPublicationReadiness:
    if projection is not None and projection.publication_candidate_id != eligibility.publication_candidate_id:
        raise ValueError("projection does not belong to publication candidate")
    if package is not None:
        if projection is None:
            raise ValueError("package requires public-safe projection")
        if package.manifest.public_projection_id != projection.public_projection_id:
            raise ValueError("package does not belong to public-safe projection")
    if receipt is not None:
        if package is None:
            raise ValueError("target receipt requires publication package")
        if receipt.release_id != package.release_id:
            raise ValueError("target receipt does not belong to publication package")

    pipeline_ready = (
        eligibility.eligibility_state == "ELIGIBLE"
        and eligibility.public_safety_state == "ALLOWED"
        and eligibility.canonical_verification_state == "VERIFIED"
        and projection is not None
        and package is not None
    )
    readiness = "ENGINEERING_READY_NOT_ACTIVATED" if pipeline_ready else "BLOCKED_OR_INCOMPLETE"

    return OwnerPublicationReadiness(
        schema_version=OWNER_PUBLICATION_READINESS_VERSION,
        publication_candidate_id=eligibility.publication_candidate_id,
        eligibility_state=eligibility.eligibility_state,
        reason_codes=eligibility.reason_codes,
        limitation_codes=eligibility.limitation_codes,
        public_safety_state=eligibility.public_safety_state,
        canonical_verification_state=eligibility.canonical_verification_state,
        coverage_limitation=eligibility.coverage_limitation,
        reproducibility_state=eligibility.reproducibility_state,
        public_projection_id=None if projection is None else projection.public_projection_id,
        redaction_status=None if projection is None else projection.redaction_status,
        release_id=None if package is None else package.release_id,
        release_manifest_id=None if package is None else package.manifest.release_manifest_id,
        payload_sha256=None if package is None else package.manifest.payload_sha256,
        local_test_target_status=None if receipt is None else receipt.status,
        unresolved_activation_prerequisites=UNRESOLVED_ACTIVATION_PREREQUISITES,
        readiness_state=readiness,
    )


@dataclass(frozen=True)
class OwnerPublicationReadinessBoundary:
    visibility: str = "PROJECT_LOCAL_OWNER_READ_ONLY"
    publication_activation: str = "NOT_AUTHORIZED"
    public_ingress: str = "NOT_APPROVED_NOT_DEPLOYED"
    backend_https: str = "NOT_DEPLOYED"
    public_gpt_action: str = "NOT_CONNECTED_NOT_APPROVED"
    owner_execution: str = "DISABLED"
    production_live: str = "NOT_OPERATIONAL"
    public_sharing: str = "NOT_ACTIVE"
    paid_providers: str = "NONE_APPROVED"
    activation_gate: str = "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


OWNER_PUBLICATION_READINESS_BOUNDARY = OwnerPublicationReadinessBoundary()


__all__ = [
    "OWNER_PUBLICATION_READINESS_VERSION",
    "P17_5_GATE",
    "P17_5_MIGRATION",
    "OwnerPublicationReadiness",
    "UNRESOLVED_ACTIVATION_PREREQUISITES",
    "project_owner_publication_readiness",
    "OwnerPublicationReadinessBoundary",
    "OWNER_PUBLICATION_READINESS_BOUNDARY",
]
