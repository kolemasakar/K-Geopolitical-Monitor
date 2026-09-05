from pathlib import Path

import pytest

from kgeopolitical_monitor.public_safe_projection import (
    PublicProvenanceReference,
    PublicSafeProjection,
    PublicSemanticContent,
)
from kgeopolitical_monitor.publication_target import (
    FailingTestPublicationTarget,
    InMemoryPublicationTarget,
    P17_4_GATE,
    P17_4_MIGRATION,
    PUBLICATION_TARGET_BOUNDARY,
    PUBLICATION_TARGET_VERSION,
)
from kgeopolitical_monitor.release_manifest import build_publication_package


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "publication_target.py"


def _projection() -> PublicSafeProjection:
    return PublicSafeProjection(
        public_projection_id="public-projection-abc",
        schema_version="KGM_PUBLIC_SAFE_PROJECTION_V1",
        publication_candidate_id="publication-candidate-1",
        publication_policy_version="KGM_PUBLICATION_ELIGIBILITY_POLICY_V1",
        live_claim_id="live-claim-1",
        semantic_claim_version_id="semantic-claim-version-1",
        verification_decision_version_id="verification-decision-version-1",
        factual_confidence_version_id="confidence-version-1",
        canonical_verification_state="VERIFIED",
        coverage_limitation="LIMITED",
        reproducibility_state="NOT_INSTRUMENTED",
        public_safety_state="ALLOWED",
        limitation_codes=("COVERAGE_LIMITED",),
        content=PublicSemanticContent(
            normalized_proposition="Actor announced a verified event.",
            claimant_actor="Actor",
            subject_text="Subject",
            object_theme="Theme",
            event_action_type="ANNOUNCEMENT",
            polarity="AFFIRMATIVE",
            modality="REPORTED",
            original_language="en",
        ),
        provenance_references=(
            PublicProvenanceReference(
                provenance_entity_version_id="prov-origin-v1",
                provenance_role="UNDERLYING_ORIGIN",
                attribution_state="OBSERVED",
                entity_kind="OFFICIAL_DOCUMENT",
                canonical_name="Origin",
            ),
        ),
        redaction_status="NOT_REQUIRED",
        redaction_count=0,
        omitted_field_classes=("SECRETS",),
    )


def _package():
    return build_publication_package(_projection(), generated_at="2026-09-05T01:40:00Z")


def test_p17_4_identity_gate_and_no_migration_are_exact():
    assert PUBLICATION_TARGET_VERSION == "KGM_PROVIDER_NEUTRAL_PUBLICATION_TARGET_V1"
    assert P17_4_GATE == "P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED"
    assert P17_4_MIGRATION == "NONE"


def test_p17_4_local_sink_accepts_release_without_network_side_effect():
    sink = InMemoryPublicationTarget()
    receipt = sink.publish(_package())
    assert receipt.status == "ACCEPTED_LOCAL_TEST_ONLY"
    assert receipt.duplicate is False
    assert receipt.publication_evidence_only is True
    assert receipt.factual_verification_effect == "NONE"
    assert sink.accepted_count == 1


def test_p17_4_duplicate_release_is_idempotently_suppressed():
    sink = InMemoryPublicationTarget()
    package = _package()
    first = sink.publish(package)
    second = sink.publish(package)
    assert first.receipt_id == second.receipt_id
    assert second.duplicate is True
    assert second.detail == "IDEMPOTENT_DUPLICATE_SUPPRESSED"
    assert sink.accepted_count == 1


def test_p17_4_receipt_is_deterministic_and_bound_to_manifest_digest():
    first = InMemoryPublicationTarget("TEST").publish(_package())
    second = InMemoryPublicationTarget("TEST").publish(_package())
    assert first.receipt_id == second.receipt_id
    assert first.manifest_id == second.manifest_id
    assert first.payload_sha256 == second.payload_sha256


def test_p17_4_failure_target_is_isolated_and_does_not_change_package():
    package = _package()
    before = repr(package)
    with pytest.raises(RuntimeError, match="simulated publication target failure"):
        FailingTestPublicationTarget().publish(package)
    assert repr(package) == before


def test_p17_4_boundary_remains_local_test_only_and_non_operational():
    boundary = PUBLICATION_TARGET_BOUNDARY
    assert boundary.runtime_storage == "PROJECT_LOCAL_ONLY"
    assert boundary.target_mode == "LOCAL_TEST_ONLY"
    assert boundary.external_targets == "NOT_ACTIVATED"
    assert boundary.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary.production_live == "NOT_OPERATIONAL"
    assert boundary.public_sharing == "NOT_ACTIVE"
    assert boundary.paid_providers == "NONE_APPROVED"
    assert boundary.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


def test_p17_4_module_contains_no_network_provider_or_external_credential_dependency():
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "FastAPI",
        "uvicorn",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "GitHub Pages",
        "GPT Store",
        "webhook",
        "access_token",
        "api_key",
        "password",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    ):
        assert forbidden not in source
