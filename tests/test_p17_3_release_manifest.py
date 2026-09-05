from dataclasses import replace
from pathlib import Path

import pytest

from kgeopolitical_monitor.public_safe_projection import (
    PublicProvenanceReference,
    PublicSafeProjection,
    PublicSemanticContent,
)
from kgeopolitical_monitor.release_manifest import (
    P17_3_GATE,
    P17_3_MIGRATION,
    RELEASE_MANIFEST_BOUNDARY,
    RELEASE_MANIFEST_VERSION,
    build_publication_package,
    build_release_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "release_manifest.py"


def _projection(**overrides) -> PublicSafeProjection:
    values = {
        "public_projection_id": "public-projection-abc",
        "schema_version": "KGM_PUBLIC_SAFE_PROJECTION_V1",
        "publication_candidate_id": "publication-candidate-1",
        "publication_policy_version": "KGM_PUBLICATION_ELIGIBILITY_POLICY_V1",
        "live_claim_id": "live-claim-1",
        "semantic_claim_version_id": "semantic-claim-version-1",
        "verification_decision_version_id": "verification-decision-version-1",
        "factual_confidence_version_id": "confidence-version-1",
        "canonical_verification_state": "VERIFIED",
        "coverage_limitation": "LIMITED",
        "reproducibility_state": "NOT_INSTRUMENTED",
        "public_safety_state": "ALLOWED",
        "limitation_codes": ("COVERAGE_LIMITED", "REPRODUCIBILITY_NOT_INSTRUMENTED"),
        "content": PublicSemanticContent(
            normalized_proposition="Actor announced a verified event.",
            claimant_actor="Actor",
            subject_text="Subject",
            object_theme="Theme",
            event_action_type="ANNOUNCEMENT",
            polarity="AFFIRMATIVE",
            modality="REPORTED",
            original_language="en",
        ),
        "provenance_references": (
            PublicProvenanceReference(
                provenance_entity_version_id="prov-publication-v1",
                provenance_role="PUBLICATION",
                attribution_state="OBSERVED",
                entity_kind="PUBLICATION",
                canonical_name="Publication",
            ),
            PublicProvenanceReference(
                provenance_entity_version_id="prov-origin-v1",
                provenance_role="UNDERLYING_ORIGIN",
                attribution_state="OBSERVED",
                entity_kind="OFFICIAL_DOCUMENT",
                canonical_name="Origin",
            ),
        ),
        "redaction_status": "NOT_REQUIRED",
        "redaction_count": 0,
        "omitted_field_classes": ("SECRETS", "RAW_ITEM_CONTENT"),
    }
    values.update(overrides)
    return PublicSafeProjection(**values)


def test_p17_3_identity_gate_and_no_migration_are_exact():
    assert RELEASE_MANIFEST_VERSION == "KGM_RELEASE_MANIFEST_V1"
    assert P17_3_GATE == "P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED"
    assert P17_3_MIGRATION == "NONE"


def test_p17_3_manifest_is_deterministic_and_hashes_exact_public_payload():
    projection = _projection()
    first = build_release_manifest(projection, generated_at="2026-09-05T01:30:00Z")
    second = build_release_manifest(projection, generated_at="2026-09-05T01:30:00Z")
    assert first == second
    assert first.release_manifest_id.startswith("release-manifest-")
    assert len(first.payload_sha256) == 64
    changed = build_release_manifest(
        replace(projection, content=replace(projection.content, normalized_proposition="Changed")),
        generated_at="2026-09-05T01:30:00Z",
    )
    assert changed.payload_sha256 != first.payload_sha256
    assert changed.release_manifest_id != first.release_manifest_id


def test_p17_3_package_identity_binds_manifest_and_public_payload():
    package = build_publication_package(_projection(), generated_at="2026-09-05T01:30:00Z")
    assert package.release_id.startswith("release-")
    assert package.manifest.public_projection_id == "public-projection-abc"
    assert package.public_payload["public_projection_id"] == "public-projection-abc"
    assert package.manifest.payload_sha256


def test_p17_3_reproducibility_is_not_reconstructed_when_not_instrumented():
    manifest = build_release_manifest(_projection(), generated_at="2026-09-05T01:30:00Z")
    assert manifest.reproducibility_references == ()
    assert manifest.reproducibility_limitation == "EXACT_HISTORY_NOT_INSTRUMENTED_OR_UNAVAILABLE"
    assert manifest.reconstructed_exact_history is False
    with pytest.raises(ValueError, match="persisted instrumentation"):
        build_release_manifest(
            _projection(),
            generated_at="2026-09-05T01:30:00Z",
            reproducibility_references=("invented-query-history",),
        )


def test_p17_3_instrumented_reproducibility_accepts_only_explicit_refs():
    projection = _projection(reproducibility_state="PERSISTED_INSTRUMENTED")
    manifest = build_release_manifest(
        projection,
        generated_at="2026-09-05T01:30:00Z",
        reproducibility_references=("rr-2", "rr-1", "rr-2"),
    )
    assert manifest.reproducibility_references == ("rr-1", "rr-2")
    assert manifest.reproducibility_limitation is None
    missing = build_release_manifest(projection, generated_at="2026-09-05T01:30:00Z")
    assert missing.reproducibility_references == ()
    assert missing.reproducibility_limitation == "PERSISTED_REPRODUCIBILITY_REFERENCE_NOT_SUPPLIED"


def test_p17_3_provenance_roles_remain_distinct_and_are_not_truth_operators():
    manifest = build_release_manifest(_projection(), generated_at="2026-09-05T01:30:00Z")
    assert manifest.provenance_roles == ("PUBLICATION", "UNDERLYING_ORIGIN")
    assert manifest.proves_underlying_origin is False
    assert manifest.promotes_factual_verification is False


def test_p17_3_invalid_projection_states_fail_closed():
    cases = (
        (_projection(schema_version="legacy"), "projection version"),
        (_projection(canonical_verification_state="PARTLY_VERIFIED"), "VERIFIED"),
        (_projection(public_safety_state="BLOCKED"), "ALLOWED"),
        (_projection(redaction_status="UNKNOWN"), "redaction"),
    )
    for projection, expected in cases:
        with pytest.raises(ValueError, match=expected):
            build_release_manifest(projection, generated_at="2026-09-05T01:30:00Z")
    with pytest.raises(ValueError, match="generated_at"):
        build_release_manifest(_projection(), generated_at="")


def test_p17_3_boundaries_remain_non_operational():
    boundary = RELEASE_MANIFEST_BOUNDARY
    assert boundary.runtime_storage == "PROJECT_LOCAL_ONLY"
    assert boundary.mixed_shared_canonical_runtime == "BLOCKED"
    assert boundary.production_live == "NOT_OPERATIONAL"
    assert boundary.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary.public_sharing == "NOT_ACTIVE"
    assert boundary.paid_providers == "NONE_APPROVED"
    assert boundary.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


def test_p17_3_module_has_no_persistence_network_or_reconstructed_history_side_effects():
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        "FastAPI",
        "uvicorn",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "datetime.now",
        "utcnow",
    ):
        assert forbidden not in source
