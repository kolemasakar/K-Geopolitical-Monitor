from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.publication_eligibility import (
    P17_1_GATE,
    P17_1_MIGRATION,
    PUBLICATION_ELIGIBILITY_BOUNDARY,
    PUBLICATION_ELIGIBILITY_POLICY_VERSION,
    PublicationEligibilityDecision,
    evaluate_publication_eligibility,
)
from kgeopolitical_monitor.semantic_live_compatibility import (
    LegacyLiveClaimSnapshot,
    SemanticLiveCompatibilityProjection,
)
from kgeopolitical_monitor.semantic_verification import SemanticVerificationDecisionVersion


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "publication_eligibility.py"


def _legacy(**overrides) -> LegacyLiveClaimSnapshot:
    values = {
        "live_claim_id": "live-claim-1",
        "analysis_run_id": "analysis-run-1",
        "collection_id": "collection-1",
        "watch_id": "watch-1",
        "claim_key": "claim-key-1",
        "title": "Legacy title",
        "legacy_verification_status": "VERIFIED",
        "legacy_confidence": 1.0,
        "importance": 1.0,
        "legacy_independent_origin_count": 99,
        "source_class_count": 99,
        "legacy_origins": ("legacy-a", "legacy-b"),
        "raw_item_ids": ("raw-1", "raw-2"),
        "origin_hosts": ("a.example", "b.example"),
    }
    values.update(overrides)
    return LegacyLiveClaimSnapshot(**values)


def _decision(state: str = "VERIFIED", **overrides) -> SemanticVerificationDecisionVersion:
    values = {
        "verification_decision_version_id": "verification-decision-version-1",
        "verification_decision_id": "verification-decision-1",
        "decision_version": 1,
        "semantic_claim_version_id": "semantic-claim-version-1",
        "policy_version_id": "semantic-policy-version-1",
        "factual_confidence_version_id": "confidence-version-1",
        "verification_state": state,
        "decision_code": "INITIAL",
        "evidence_snapshot": (),
        "independence_snapshot": (),
        "contradiction_snapshot": (),
        "rationale": "canonical P13.5 decision",
        "supersedes_decision_version_id": None,
        "created_at": datetime(2026, 9, 5, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return SemanticVerificationDecisionVersion(**values)


def _projection(
    *,
    compatibility_state: str = "LINKED_WITH_DECISION",
    decision: SemanticVerificationDecisionVersion | None = None,
    semantic_claim_version_id: str | None = "semantic-claim-version-1",
    reproducibility_state: str = "INSTRUMENTED_COMPLETED",
) -> SemanticLiveCompatibilityProjection:
    if decision is None and compatibility_state == "LINKED_WITH_DECISION":
        decision = _decision()
    current_ids = () if semantic_claim_version_id is None else (semantic_claim_version_id,)
    historical_ids = current_ids if compatibility_state != "UNLINKED" else ()
    return SemanticLiveCompatibilityProjection(
        legacy=_legacy(),
        compatibility_state=compatibility_state,
        historical_semantic_claim_version_ids=historical_ids,
        current_semantic_claim_version_ids=current_ids,
        semantic_claim_version_id=semantic_claim_version_id,
        semantic_decision=decision,
        reproducibility_state=reproducibility_state,
        research_run_id="research-run-1" if reproducibility_state != "NOT_INSTRUMENTED" else None,
        exact_query_snapshot="exact-query" if reproducibility_state != "NOT_INSTRUMENTED" else None,
        research_cutoff="2026-09-05T00:00:00+00:00" if reproducibility_state != "NOT_INSTRUMENTED" else None,
        instrumentation_version="E6-1.0" if reproducibility_state != "NOT_INSTRUMENTED" else None,
    )


def test_p17_1_policy_identity_gate_and_migration_boundary_are_exact():
    assert PUBLICATION_ELIGIBILITY_POLICY_VERSION == "KGM_PUBLICATION_ELIGIBILITY_POLICY_V1"
    assert P17_1_GATE == "P17_1_PUBLICATION_ELIGIBILITY_POLICY_VALIDATED"
    assert P17_1_MIGRATION == "NONE"


def test_p17_1_verified_public_safe_claim_is_eligible():
    result = evaluate_publication_eligibility(
        _projection(),
        public_safety_state="ALLOWED",
        coverage_limitation="ADEQUATE",
    )
    assert isinstance(result, PublicationEligibilityDecision)
    assert result.eligibility_state == "ELIGIBLE"
    assert result.reason_codes == ("CANONICAL_VERIFIED_PUBLIC_SAFE",)
    assert result.canonical_verification_state == "VERIFIED"
    assert result.compatibility_state == "LINKED_WITH_DECISION"
    assert result.public_safety_state == "ALLOWED"
    assert result.limitation_codes == ()
    assert result.promotes_factual_verification is False
    assert result.uses_legacy_truth_fallback is False


def test_p17_1_coverage_limitations_are_labels_not_promotion_or_automatic_blockers():
    limited = evaluate_publication_eligibility(
        _projection(reproducibility_state="NOT_INSTRUMENTED"),
        public_safety_state="ALLOWED",
        coverage_limitation="LIMITED",
    )
    unknown = evaluate_publication_eligibility(
        _projection(),
        public_safety_state="ALLOWED",
        coverage_limitation="UNKNOWN",
    )

    assert limited.eligibility_state == "ELIGIBLE"
    assert limited.limitation_codes == (
        "COVERAGE_LIMITED",
        "REPRODUCIBILITY_NOT_INSTRUMENTED",
    )
    assert unknown.eligibility_state == "ELIGIBLE"
    assert unknown.limitation_codes == ("COVERAGE_UNKNOWN",)


def test_p17_1_public_safety_must_explicitly_allow_publication():
    for safety, reason in (
        ("BLOCKED", "PUBLIC_SAFETY_BLOCKED"),
        ("UNKNOWN", "PUBLIC_SAFETY_UNKNOWN"),
    ):
        result = evaluate_publication_eligibility(
            _projection(),
            public_safety_state=safety,
            coverage_limitation="ADEQUATE",
        )
        assert result.eligibility_state == "BLOCKED"
        assert reason in result.reason_codes


def test_p17_1_legacy_verified_high_confidence_and_large_counts_never_bypass_semantic_linkage():
    cases = (
        ("UNLINKED", None, "CANONICAL_REFERENCE_UNLINKED"),
        ("STALE_LINK", None, "CANONICAL_REFERENCE_STALE"),
        ("AMBIGUOUS_CURRENT_LINKS", None, "CANONICAL_REFERENCE_AMBIGUOUS"),
        ("LINKED_NO_DECISION", None, "CANONICAL_DECISION_MISSING"),
    )
    for compatibility_state, decision, reason in cases:
        projection = _projection(
            compatibility_state=compatibility_state,
            decision=decision,
            semantic_claim_version_id=(
                None if compatibility_state == "UNLINKED" else "semantic-claim-version-1"
            ),
        )
        result = evaluate_publication_eligibility(
            projection,
            public_safety_state="ALLOWED",
            coverage_limitation=None,
        )
        assert projection.legacy.legacy_verification_status == "VERIFIED"
        assert projection.legacy.legacy_confidence == 1.0
        assert projection.legacy.legacy_independent_origin_count == 99
        assert result.eligibility_state == "BLOCKED"
        assert reason in result.reason_codes


@pytest.mark.parametrize("state", ["DETECTED", "PARTLY_VERIFIED", "DISPUTED", "UNVERIFIABLE"])
def test_p17_1_only_current_p13_5_verified_state_can_be_eligible(state: str):
    result = evaluate_publication_eligibility(
        _projection(decision=_decision(state)),
        public_safety_state="ALLOWED",
        coverage_limitation="ADEQUATE",
    )
    assert result.eligibility_state == "BLOCKED"
    assert result.reason_codes == (f"CANONICAL_VERIFICATION_{state}",)


def test_p17_1_missing_referenced_confidence_fails_closed_even_for_verified():
    result = evaluate_publication_eligibility(
        _projection(),
        public_safety_state="ALLOWED",
        coverage_limitation=None,
    )
    assert result.eligibility_state == "BLOCKED"
    assert result.reason_codes == ("CANONICAL_CONFIDENCE_REFERENCE_MISSING",)


def test_p17_1_candidate_identity_is_deterministic_and_safety_sensitive():
    projection = _projection()
    first = evaluate_publication_eligibility(
        projection,
        public_safety_state="ALLOWED",
        coverage_limitation="ADEQUATE",
    )
    second = evaluate_publication_eligibility(
        projection,
        public_safety_state="ALLOWED",
        coverage_limitation="LIMITED",
    )
    blocked = evaluate_publication_eligibility(
        projection,
        public_safety_state="BLOCKED",
        coverage_limitation="ADEQUATE",
    )
    assert first.publication_candidate_id == second.publication_candidate_id
    assert first.publication_candidate_id.startswith("publication-candidate-")
    assert first.publication_candidate_id != blocked.publication_candidate_id


def test_p17_1_reproducibility_failure_is_a_limitation_not_exact_history_reconstruction():
    result = evaluate_publication_eligibility(
        _projection(reproducibility_state="INSTRUMENTED_FAILED"),
        public_safety_state="ALLOWED",
        coverage_limitation="ADEQUATE",
    )
    assert result.eligibility_state == "ELIGIBLE"
    assert result.limitation_codes == ("REPRODUCIBILITY_INSTRUMENTED_FAILED",)


def test_p17_1_runtime_and_activation_boundary_stays_closed():
    boundary = PUBLICATION_ELIGIBILITY_BOUNDARY
    assert boundary.runtime_storage == "PROJECT_LOCAL_ONLY"
    assert boundary.mixed_shared_canonical_runtime == "BLOCKED"
    assert boundary.production_live == "NOT_OPERATIONAL"
    assert boundary.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary.public_sharing == "NOT_ACTIVE"
    assert boundary.paid_providers == "NONE_APPROVED"
    assert boundary.owner_execution == "DISABLED"
    assert boundary.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


def test_p17_1_invalid_public_safety_or_coverage_values_fail_closed():
    with pytest.raises(ValueError):
        evaluate_publication_eligibility(
            _projection(), public_safety_state="", coverage_limitation="ADEQUATE"
        )
    with pytest.raises(ValueError):
        evaluate_publication_eligibility(
            _projection(), public_safety_state="ALLOWED", coverage_limitation="GLOBAL"
        )


def test_p17_1_module_is_read_only_and_has_no_public_transport_dependencies():
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden_sql in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
        assert forbidden_sql not in source
    for forbidden_dependency in ("FastAPI", "uvicorn", "requests", "httpx", "socket"):
        assert forbidden_dependency not in source
