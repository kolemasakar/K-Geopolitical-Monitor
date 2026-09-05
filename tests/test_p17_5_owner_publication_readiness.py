from pathlib import Path

import pytest

from kgeopolitical_monitor.owner_publication_readiness import (
    OWNER_PUBLICATION_READINESS_BOUNDARY,
    OWNER_PUBLICATION_READINESS_VERSION,
    P17_5_GATE,
    P17_5_MIGRATION,
    UNRESOLVED_ACTIVATION_PREREQUISITES,
    project_owner_publication_readiness,
)
from kgeopolitical_monitor.public_safe_projection import (
    PublicProvenanceReference,
    PublicSafeProjection,
    PublicSemanticContent,
)
from kgeopolitical_monitor.publication_eligibility import PublicationEligibilityDecision
from kgeopolitical_monitor.publication_target import InMemoryPublicationTarget
from kgeopolitical_monitor.release_manifest import build_publication_package


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "owner_publication_readiness.py"
BACKEND_API_PATH = ROOT / "src" / "kgeopolitical_monitor" / "backend_action_api.py"


def _eligibility(**overrides):
    values = {
        "publication_candidate_id": "publication-candidate-1",
        "policy_version": "KGM_PUBLICATION_ELIGIBILITY_POLICY_V1",
        "live_claim_id": "live-claim-1",
        "semantic_claim_version_id": "semantic-v1",
        "verification_decision_version_id": "decision-v1",
        "canonical_policy_version_id": "policy-v1",
        "factual_confidence_version_id": "confidence-v1",
        "compatibility_state": "LINKED_WITH_DECISION",
        "canonical_verification_state": "VERIFIED",
        "coverage_limitation": "LIMITED",
        "reproducibility_state": "NOT_INSTRUMENTED",
        "public_safety_state": "ALLOWED",
        "eligibility_state": "ELIGIBLE",
        "reason_codes": ("CANONICAL_VERIFIED_PUBLIC_SAFE",),
        "limitation_codes": ("COVERAGE_LIMITED",),
    }
    values.update(overrides)
    return PublicationEligibilityDecision(**values)


def _projection(candidate_id="publication-candidate-1"):
    return PublicSafeProjection(
        public_projection_id="public-projection-1",
        schema_version="KGM_PUBLIC_SAFE_PROJECTION_V1",
        publication_candidate_id=candidate_id,
        publication_policy_version="KGM_PUBLICATION_ELIGIBILITY_POLICY_V1",
        live_claim_id="live-claim-1",
        semantic_claim_version_id="semantic-v1",
        verification_decision_version_id="decision-v1",
        factual_confidence_version_id="confidence-v1",
        canonical_verification_state="VERIFIED",
        coverage_limitation="LIMITED",
        reproducibility_state="NOT_INSTRUMENTED",
        public_safety_state="ALLOWED",
        limitation_codes=("COVERAGE_LIMITED",),
        content=PublicSemanticContent(
            normalized_proposition="Verified event.", claimant_actor=None, subject_text=None,
            object_theme=None, event_action_type=None, polarity="AFFIRMATIVE",
            modality="REPORTED", original_language="en",
        ),
        provenance_references=(PublicProvenanceReference(
            provenance_entity_version_id="origin-v1", provenance_role="UNDERLYING_ORIGIN",
            attribution_state="OBSERVED", entity_kind="OFFICIAL_DOCUMENT", canonical_name="Origin",
        ),),
        redaction_status="NOT_REQUIRED",
        redaction_count=0,
        omitted_field_classes=("SECRETS",),
    )


def test_p17_5_identity_gate_and_no_migration_are_exact():
    assert OWNER_PUBLICATION_READINESS_VERSION == "KGM_OWNER_PUBLICATION_READINESS_V1"
    assert P17_5_GATE == "P17_5_OWNER_PUBLICATION_READINESS_PROJECTION_VALIDATED"
    assert P17_5_MIGRATION == "NONE"


def test_p17_5_complete_local_test_pipeline_is_engineering_ready_not_activated():
    eligibility = _eligibility()
    projection = _projection()
    package = build_publication_package(projection, generated_at="2026-09-05T02:00:00Z")
    receipt = InMemoryPublicationTarget().publish(package)
    result = project_owner_publication_readiness(
        eligibility, projection=projection, package=package, receipt=receipt
    )
    assert result.readiness_state == "ENGINEERING_READY_NOT_ACTIVATED"
    assert result.local_test_target_status == "ACCEPTED_LOCAL_TEST_ONLY"
    assert result.approval_effect == "NONE"
    assert result.publication_effect == "NONE"
    assert result.unresolved_activation_prerequisites == UNRESOLVED_ACTIVATION_PREREQUISITES


def test_p17_5_incomplete_or_blocked_candidate_stays_blocked():
    result = project_owner_publication_readiness(_eligibility(eligibility_state="BLOCKED"))
    assert result.readiness_state == "BLOCKED_OR_INCOMPLETE"
    assert result.public_projection_id is None
    assert result.release_id is None


def test_p17_5_cross_object_mismatch_fails_closed():
    with pytest.raises(ValueError, match="publication candidate"):
        project_owner_publication_readiness(_eligibility(), projection=_projection("other"))
    projection = _projection()
    package = build_publication_package(projection, generated_at="2026-09-05T02:00:00Z")
    with pytest.raises(ValueError, match="requires public-safe projection"):
        project_owner_publication_readiness(_eligibility(), package=package)
    receipt = InMemoryPublicationTarget().publish(package)
    with pytest.raises(ValueError, match="requires publication package"):
        project_owner_publication_readiness(_eligibility(), projection=projection, receipt=receipt)


def test_p17_5_boundaries_remain_owner_read_only_and_not_activated():
    boundary = OWNER_PUBLICATION_READINESS_BOUNDARY
    assert boundary.visibility == "PROJECT_LOCAL_OWNER_READ_ONLY"
    assert boundary.publication_activation == "NOT_AUTHORIZED"
    assert boundary.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary.backend_https == "NOT_DEPLOYED"
    assert boundary.public_gpt_action == "NOT_CONNECTED_NOT_APPROVED"
    assert boundary.owner_execution == "DISABLED"
    assert boundary.production_live == "NOT_OPERATIONAL"
    assert boundary.public_sharing == "NOT_ACTIVE"
    assert boundary.paid_providers == "NONE_APPROVED"


def test_p17_5_module_has_no_io_write_or_public_route_and_is_not_exposed_by_owner_api():
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "INSERT INTO", "UPDATE ", "DELETE FROM", "FastAPI", "uvicorn",
        "requests", "httpx", "socket", "subprocess",
    ):
        assert forbidden not in source
    if BACKEND_API_PATH.exists():
        backend_source = BACKEND_API_PATH.read_text(encoding="utf-8")
        assert "owner_publication_readiness" not in backend_source
