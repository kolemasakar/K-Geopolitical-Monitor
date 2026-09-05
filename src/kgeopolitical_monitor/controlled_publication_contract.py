"""Phase 17.0 controlled external publication readiness architecture contract.

This module is deliberately non-operational. It defines machine-readable boundaries
for publication eligibility, public-safe projection, release manifests/packages and
provider-neutral target evidence without activating publication, public ingress,
credentials, a GPT Action, shared runtime or production/live operation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Final


CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION: Final[str] = (
    "KGM_CONTROLLED_PUBLICATION_ARCHITECTURE_V1"
)
P17_0_GATE: Final[str] = "P17_0_CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT_VALIDATED"

PUBLICATION_ELIGIBILITY_PENDING: Final[str] = "PENDING"
PUBLICATION_ELIGIBILITY_ELIGIBLE: Final[str] = "ELIGIBLE"
PUBLICATION_ELIGIBILITY_BLOCKED: Final[str] = "BLOCKED"
PUBLICATION_ELIGIBILITY_STATES: Final[tuple[str, ...]] = (
    PUBLICATION_ELIGIBILITY_PENDING,
    PUBLICATION_ELIGIBILITY_ELIGIBLE,
    PUBLICATION_ELIGIBILITY_BLOCKED,
)

PUBLICATION_TARGET_PREPARED: Final[str] = "PREPARED"
PUBLICATION_TARGET_ACCEPTED: Final[str] = "ACCEPTED"
PUBLICATION_TARGET_FAILED: Final[str] = "FAILED"
PUBLICATION_TARGET_STATES: Final[tuple[str, ...]] = (
    PUBLICATION_TARGET_PREPARED,
    PUBLICATION_TARGET_ACCEPTED,
    PUBLICATION_TARGET_FAILED,
)

CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT: Final[dict[str, object]] = {
    "version": CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION,
    "gate": P17_0_GATE,
    "phase": "P17.0",
    "status": "ARCHITECTURE_BASELINE",
    "entities": {
        "canonical_intelligence_state": {
            "ownership": "EXISTING_CANONICAL_STORES",
            "meaning": "Existing persisted KGM intelligence referenced by publication; never duplicated as a Phase 17 truth store.",
        },
        "publication_eligibility": {
            "identity": "publication_candidate_id",
            "states": PUBLICATION_ELIGIBILITY_STATES,
            "meaning": "Derived publishability decision under a versioned policy; not factual-verification status.",
        },
        "public_safe_projection": {
            "identity": "public_projection_id",
            "parent": "publication_candidate_id",
            "meaning": "Allowlist-based, data-minimized derived representation produced before any export or target boundary.",
        },
        "release_manifest": {
            "identity": "release_manifest_id",
            "parent": "public_projection_id",
            "meaning": "Deterministic provenance/version/digest record for a publication package.",
        },
        "publication_package": {
            "identity": "publication_package_id",
            "parent": "release_manifest_id",
            "meaning": "Public-safe package assembled from the projection and manifest without rewriting canonical intelligence meaning.",
        },
        "publication_target_attempt": {
            "identity": "publication_target_attempt_id",
            "parent": "publication_package_id",
            "states": PUBLICATION_TARGET_STATES,
            "meaning": "Provider-neutral local/test target evidence; no real public target is activated by P17.0.",
        },
        "release_receipt": {
            "identity": "release_receipt_id",
            "parent": "publication_target_attempt_id",
            "meaning": "Evidence that a target accepted/recorded a package; never event evidence or factual corroboration.",
        },
    },
    "separation_chain": (
        "CANONICAL_INTELLIGENCE_STATE",
        "PUBLICATION_ELIGIBILITY",
        "PUBLIC_SAFE_PROJECTION",
        "RELEASE_MANIFEST",
        "PUBLICATION_PACKAGE",
        "LOCAL_TEST_PUBLICATION_TARGET",
        "RELEASE_RECEIPT",
    ),
    "publication_truth_contract": {
        "rules": (
            "Publication is a derived presentation layer, not canonical truth state.",
            "Publisher or publication identity is not automatically the underlying origin.",
            "Publication lifecycle state is not factual-verification state.",
            "Publication eligibility cannot promote factual verification or silently upgrade an unverified or disputed claim.",
            "A release receipt proves only that a target accepted or recorded a package.",
            "Release receipt, view, click, download, reaction and engagement counts are not event evidence, independent corroboration or truth operators.",
            "Canonical factual verification remains owned by the current P13.5 decision through the P13.6 bridge.",
        ),
    },
    "public_safe_projection_boundary": {
        "mode": "STRICT_ALLOWLIST_FAIL_CLOSED",
        "rules": (
            "Public-safe redaction and data minimization occur before any export or publication-target boundary.",
            "Missing, stale, ambiguous or non-public-safe canonical references fail closed.",
            "Canonical provenance, verification state, uncertainty, contradiction state and coverage limitations cannot be silently strengthened or removed.",
            "Owner/admin API responses are not public payload pass-throughs.",
            "Third-party source material is not republished wholesale; bounded KGM-derived summaries, metadata and provenance/source references are used as appropriate.",
        ),
        "forbidden_public_payload_classes": (
            "SECRETS",
            "AUTHENTICATION_MATERIAL",
            "OWNER_ADMIN_TOKENS",
            "PRIVATE_DATABASE_PATHS",
            "RAW_OPERATOR_FEEDBACK",
            "UNNECESSARY_RUNTIME_METADATA",
            "NON_PUBLIC_OPERATIONAL_DIAGNOSTICS",
        ),
    },
    "reproducibility_contract": {
        "rules": (
            "Exact reproducibility or execution-history claims are emitted only from persisted instrumentation.",
            "Uninstrumented or unavailable exact history remains explicitly NOT_INSTRUMENTED or unavailable.",
            "Reconstructed or inferred query/tool execution history is never labeled exact.",
            "Release manifests may reference persisted reproducibility identifiers but cannot invent missing instrumentation.",
        ),
    },
    "publication_target_contract": {
        "mode": "LOCAL_TEST_ONLY",
        "rules": (
            "Canonical automated validation performs no real network publication.",
            "No GitHub Pages, public object bucket, CMS, social account, email list, webhook, public website or GPT Store target is enabled by P17.0.",
            "Publication-target failure is isolated from monitoring and canonical analytical persistence.",
            "Target receipts are publication evidence only.",
            "Public/external credentials are absent from canonical publication records.",
            "Any real publication target requires a later explicit owner activation decision and fresh security/platform validation.",
        ),
    },
    "historical_e8_boundary": {
        "owner_only_publication_readiness": "APPROVED",
        "external_sharing": "NOT_ACTIVE",
        "public_action": "NOT_APPROVED",
        "public_backend": "NOT_DEPLOYED",
        "public_gpt": "NOT_PUBLISHED",
        "owner_api_public_reuse": "FORBIDDEN",
        "admin_dashboard_public_reuse": "FORBIDDEN",
        "platform_requirements": "REVALIDATE_AT_ACTUAL_LAUNCH_GATE",
    },
    "compatibility": {
        "canonical_verification": "P13_5_THROUGH_P13_6_UNCHANGED",
        "phase_14_owner_activation": "UNCHANGED_OWNER_DECISION_REQUIRED",
        "phase_15_forecast_performance": "DESCRIPTIVE_NON_PROMOTIONAL",
        "phase_16_delivery_quality": "VALIDATED_NON_TRUTH_OPERATOR",
        "migration_033": "NONE_FOR_P17_0",
        "phase_18_shared_runtime": "NOT_ACTIVATED_NEW_ARCHITECTURE_APPROVAL_REQUIRED",
    },
    "activation_contract": {
        "readiness_gate": "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED",
        "activation_gate": "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION",
        "readiness_may_reach": "VALIDATED_READY / NOT_ACTIVATED",
        "actual_publication": "NOT_AUTHORIZED_BY_P17_0",
    },
    "runtime_security_boundary": {
        "runtime_storage": "PROJECT_LOCAL_ONLY",
        "mixed_shared_canonical_runtime": "BLOCKED",
        "production_live": "NOT_OPERATIONAL",
        "public_ingress": "NOT_APPROVED_NOT_DEPLOYED",
        "private_gpt_action": "NOT_CONNECTED",
        "backend_https": "NOT_DEPLOYED",
        "admin_dashboard": "NOT_DEPLOYED",
        "public_sharing": "NOT_ACTIVE",
        "paid_providers": "NONE_APPROVED",
        "owner_execution": "DISABLED",
        "external_publication_activation": "NOT_AUTHORIZED_BY_P17_0",
    },
    "epistemic_invariants": (
        "Publication and publication eligibility are not factual-verification states.",
        "Publisher/publication identity is not underlying-origin proof.",
        "Publication receipts and engagement counts cannot create independent corroboration or promote factual verification.",
        "Public projection cannot silently strengthen provenance, verification, uncertainty or coverage meaning.",
        "No self-modifying verification, alert, source, forecast, delivery or publication policy is authorized in Phase 17.",
    ),
}


def controlled_publication_architecture_contract() -> dict[str, object]:
    """Return a detached copy of the P17.0 architecture contract."""

    return deepcopy(CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT)


__all__ = [
    "CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION",
    "P17_0_GATE",
    "PUBLICATION_ELIGIBILITY_PENDING",
    "PUBLICATION_ELIGIBILITY_ELIGIBLE",
    "PUBLICATION_ELIGIBILITY_BLOCKED",
    "PUBLICATION_ELIGIBILITY_STATES",
    "PUBLICATION_TARGET_PREPARED",
    "PUBLICATION_TARGET_ACCEPTED",
    "PUBLICATION_TARGET_FAILED",
    "PUBLICATION_TARGET_STATES",
    "CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT",
    "controlled_publication_architecture_contract",
]
