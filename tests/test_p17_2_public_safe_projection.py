from dataclasses import replace
from pathlib import Path

import pytest

from kgeopolitical_monitor.public_safe_projection import (
    MAX_PROPOSITION_CHARS,
    OMITTED_FIELD_CLASSES,
    P17_2_GATE,
    P17_2_MIGRATION,
    PUBLIC_SAFE_PROJECTION_BOUNDARY,
    PUBLIC_SAFE_PROJECTION_VERSION,
    PublicProvenanceReference,
    project_public_safe,
)
from kgeopolitical_monitor.publication_eligibility import PublicationEligibilityDecision


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "public_safe_projection.py"


def _eligibility(**overrides) -> PublicationEligibilityDecision:
    values = {
        "publication_candidate_id": "publication-candidate-1",
        "policy_version": "KGM_PUBLICATION_ELIGIBILITY_POLICY_V1",
        "live_claim_id": "live-claim-1",
        "semantic_claim_version_id": "semantic-claim-version-1",
        "verification_decision_version_id": "verification-decision-version-1",
        "canonical_policy_version_id": "semantic-policy-version-1",
        "factual_confidence_version_id": "confidence-version-1",
        "compatibility_state": "LINKED_WITH_DECISION",
        "canonical_verification_state": "VERIFIED",
        "coverage_limitation": "LIMITED",
        "reproducibility_state": "NOT_INSTRUMENTED",
        "public_safety_state": "ALLOWED",
        "eligibility_state": "ELIGIBLE",
        "reason_codes": ("CANONICAL_VERIFIED_PUBLIC_SAFE",),
        "limitation_codes": ("COVERAGE_LIMITED", "REPRODUCIBILITY_NOT_INSTRUMENTED"),
    }
    values.update(overrides)
    return PublicationEligibilityDecision(**values)


def _provenance() -> tuple[PublicProvenanceReference, ...]:
    return (
        PublicProvenanceReference(
            provenance_entity_version_id="prov-origin-v1",
            provenance_role="UNDERLYING_ORIGIN",
            attribution_state="OBSERVED",
            entity_kind="OFFICIAL_DOCUMENT",
            canonical_name="Underlying origin",
        ),
        PublicProvenanceReference(
            provenance_entity_version_id="prov-publisher-v1",
            provenance_role="PUBLISHER",
            attribution_state="OBSERVED",
            entity_kind="PUBLISHER",
            canonical_name="Publisher name",
        ),
        PublicProvenanceReference(
            provenance_entity_version_id="prov-publication-v1",
            provenance_role="PUBLICATION",
            attribution_state="OBSERVED",
            entity_kind="PUBLICATION",
            canonical_name="Publication name",
        ),
    )


def _project(eligibility: PublicationEligibilityDecision | None = None, **overrides):
    values = {
        "normalized_proposition": "Actor announced a verified event.",
        "claimant_actor": "Actor",
        "subject_text": "Subject",
        "object_theme": "Theme",
        "event_action_type": "ANNOUNCEMENT",
        "polarity": "AFFIRMATIVE",
        "modality": "REPORTED",
        "original_language": "en",
        "provenance_references": _provenance(),
    }
    values.update(overrides)
    return project_public_safe(eligibility or _eligibility(), **values)


def test_p17_2_identity_gate_and_no_migration_are_exact():
    assert PUBLIC_SAFE_PROJECTION_VERSION == "KGM_PUBLIC_SAFE_PROJECTION_V1"
    assert P17_2_GATE == "P17_2_PUBLIC_SAFE_PROJECTION_REDACTION_VALIDATED"
    assert P17_2_MIGRATION == "NONE"


def test_p17_2_projection_requires_exact_p17_1_eligible_and_allowed_state():
    with pytest.raises(ValueError, match="ELIGIBLE"):
        _project(_eligibility(eligibility_state="BLOCKED"))
    with pytest.raises(ValueError, match="ALLOWED"):
        _project(_eligibility(public_safety_state="BLOCKED"))
    with pytest.raises(ValueError, match="canonical VERIFIED"):
        _project(_eligibility(canonical_verification_state="PARTLY_VERIFIED"))


def test_p17_2_projection_preserves_canonical_ids_and_limitations_without_truth_promotion():
    result = _project()
    assert result.semantic_claim_version_id == "semantic-claim-version-1"
    assert result.verification_decision_version_id == "verification-decision-version-1"
    assert result.factual_confidence_version_id == "confidence-version-1"
    assert result.canonical_verification_state == "VERIFIED"
    assert result.coverage_limitation == "LIMITED"
    assert result.reproducibility_state == "NOT_INSTRUMENTED"
    assert result.limitation_codes == (
        "COVERAGE_LIMITED",
        "REPRODUCIBILITY_NOT_INSTRUMENTED",
    )
    assert result.promotes_factual_verification is False
    assert result.creates_independent_corroboration is False


def test_p17_2_publication_publisher_and_underlying_origin_remain_distinct_roles():
    result = _project()
    by_role = {item.provenance_role: item for item in result.provenance_references}
    assert by_role["PUBLICATION"].provenance_entity_version_id == "prov-publication-v1"
    assert by_role["PUBLISHER"].provenance_entity_version_id == "prov-publisher-v1"
    assert by_role["UNDERLYING_ORIGIN"].provenance_entity_version_id == "prov-origin-v1"
    assert len({item.provenance_entity_version_id for item in by_role.values()}) == 3


def test_p17_2_sensitive_authentication_and_private_paths_are_redacted_and_bounded():
    proposition = (
        "Bearer abcdefghijklmnop api_key=supersecret "
        "C:\\Users\\Owner\\private\\kgm.db /opt/kgm/private/state.db "
        + ("x" * (MAX_PROPOSITION_CHARS + 100))
    )
    result = _project(normalized_proposition=proposition)
    public_text = result.content.normalized_proposition
    assert "abcdefghijklmnop" not in public_text
    assert "supersecret" not in public_text
    assert "C:\\Users\\Owner" not in public_text
    assert "/opt/kgm/private/state.db" not in public_text
    assert "[REDACTED_AUTH]" in public_text
    assert "[REDACTED_SECRET]" in public_text
    assert "[REDACTED_PATH]" in public_text
    assert len(public_text) <= MAX_PROPOSITION_CHARS
    assert result.redaction_status == "APPLIED"
    assert result.redaction_count >= 5


def test_p17_2_public_dict_is_strict_allowlist_without_raw_or_internal_fields():
    result = _project()
    public = result.as_public_dict()
    serialized = repr(public)
    forbidden = (
        "raw_item_id",
        "raw_item_ids",
        "source_id",
        "metadata_json",
        "watch_id",
        "exact_query_snapshot",
        "delivery_retry",
        "operator_feedback",
        "database_path",
        "authorization",
        "access_token",
        "password",
    )
    for field in forbidden:
        assert field not in serialized
    assert set(OMITTED_FIELD_CLASSES).issuperset(
        {"RAW_ITEM_CONTENT", "RAW_ITEM_IDENTIFIERS", "SOURCE_INTERNAL_IDENTIFIERS"}
    )


def test_p17_2_projection_identity_is_deterministic_and_content_sensitive():
    first = _project()
    second = _project()
    changed = _project(normalized_proposition="Actor announced a different verified event.")
    assert first.public_projection_id == second.public_projection_id
    assert first.public_projection_id.startswith("public-projection-")
    assert first.public_projection_id != changed.public_projection_id


def test_p17_2_provenance_order_is_deterministic_and_not_count_based_corroboration():
    first = _project(provenance_references=tuple(reversed(_provenance())))
    second = _project(provenance_references=_provenance())
    assert first.provenance_references == second.provenance_references
    assert first.public_projection_id == second.public_projection_id
    assert first.creates_independent_corroboration is False


def test_p17_2_invalid_provenance_taxonomy_fails_closed():
    bad_role = replace(_provenance()[0], provenance_role="HOST_COUNT")
    bad_state = replace(_provenance()[0], attribution_state="VERIFIED")
    bad_kind = replace(_provenance()[0], entity_kind="INDEPENDENT_ORIGIN_COUNT")
    for reference, expected in (
        (bad_role, "provenance_role"),
        (bad_state, "attribution_state"),
        (bad_kind, "entity_kind"),
    ):
        with pytest.raises(ValueError, match=expected):
            _project(provenance_references=(reference,))


def test_p17_2_invalid_semantic_taxonomy_and_missing_canonical_ids_fail_closed():
    with pytest.raises(ValueError, match="polarity"):
        _project(polarity="CERTAIN")
    with pytest.raises(ValueError, match="modality"):
        _project(modality="CONFIRMED_BY_COUNT")
    with pytest.raises(ValueError, match="canonical identifiers"):
        _project(_eligibility(factual_confidence_version_id=None))
    with pytest.raises(ValueError, match="coverage limitation"):
        _project(_eligibility(coverage_limitation=None))


def test_p17_2_runtime_activation_boundary_stays_closed():
    boundary = PUBLIC_SAFE_PROJECTION_BOUNDARY
    assert boundary.runtime_storage == "PROJECT_LOCAL_ONLY"
    assert boundary.mixed_shared_canonical_runtime == "BLOCKED"
    assert boundary.production_live == "NOT_OPERATIONAL"
    assert boundary.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary.public_sharing == "NOT_ACTIVE"
    assert boundary.paid_providers == "NONE_APPROVED"
    assert boundary.owner_execution == "DISABLED"
    assert boundary.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


def test_p17_2_module_is_read_only_and_has_no_public_transport_dependencies():
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden_sql in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
        assert forbidden_sql not in source
    for forbidden_dependency in (
        "FastAPI",
        "uvicorn",
        "requests",
        "httpx",
        "socket",
        "subprocess",
    ):
        assert forbidden_dependency not in source
