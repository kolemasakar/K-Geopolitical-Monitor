from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_contradictions import SemanticContradictionService
from kgeopolitical_monitor.semantic_evidence import SemanticEvidenceService
from kgeopolitical_monitor.semantic_provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_verification import SemanticVerificationService


NOW = datetime(2026, 9, 4, 7, 30, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _claim(runtime, claim_id="verification-claim", proposition="The event occurred"):
    return SemanticClaimService(runtime).record_version(
        claim_id,
        normalized_proposition=proposition,
        claimant_actor="Actor",
        subject_text="Actor",
        object_theme="event",
        event_action_type="OCCURRENCE",
        polarity="AFFIRMATIVE",
        modality="ASSERTED",
        time_scope={"date": "2026-09-04"},
        location_scope={"country": "Example"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.95,
        created_at=NOW,
    )


def _entity(runtime, entity_id, *, kind="OFFICIAL_DOCUMENT"):
    return SemanticProvenanceService(runtime).record_entity_version(
        entity_id,
        entity_kind=kind,
        canonical_name=entity_id,
        created_at=NOW,
    )


def _evidence(runtime, claim, relation_id, entity_id, relation_type="SUPPORTS"):
    entity = _entity(runtime, entity_id)
    return SemanticEvidenceService(runtime).record_relation_version(
        relation_id,
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity.provenance_entity_version_id,
        relation_type=relation_type,
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )


def _independent_pair(runtime, claim, left, right, assessment_id="independent-pair"):
    return SemanticEvidenceService(runtime).record_independence_version(
        assessment_id,
        semantic_claim_version_id=claim.semantic_claim_version_id,
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
        independence_state="INDEPENDENT",
        rationale_code="EXPLICIT_DISTINCT_UNDERLYING_ORIGINS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        note="Distinct underlying origins reviewed",
        created_at=NOW,
    )


def _policy(service, **kwargs):
    return service.record_policy_version(
        "canonical-policy",
        policy_name="Canonical semantic verification policy",
        created_at=NOW,
        **kwargs,
    )


def _confidence(service, claim, **overrides):
    values = {
        "evidence_sufficiency": "HIGH",
        "provenance_independence": "HIGH",
        "authority_proximity": "HIGH",
        "contradiction_resolution": "HIGH",
        "temporal_freshness": "HIGH",
        "extraction_certainty": "HIGH",
        "translation_certainty": "HIGH",
        "claim_specific_certainty": "HIGH",
        "coverage_limitation": "ADEQUATE",
        "assessment_method": "HUMAN_REVIEWED",
        "assessment_version": "1.0",
        "note": "Multidimensional assessment",
    }
    values.update(overrides)
    return service.record_confidence_version(
        claim.semantic_claim_version_id,
        created_at=NOW,
        **values,
    )


def test_policy_versions_are_append_only_and_cannot_weaken_permanent_invariants(tmp_path):
    runtime = _runtime(tmp_path)
    service = SemanticVerificationService(runtime)
    first = _policy(service)
    second = _policy(
        service,
        rules={"verified_minimum_confidence": {"authority_proximity": "HIGH"}},
    )

    assert first.policy_version == 1 and second.policy_version == 2
    assert second.supersedes_policy_version_id == first.policy_version_id
    assert second.rules["count_only_promotion_forbidden"] is True
    assert second.rules["verified_minimum_confidence"]["authority_proximity"] == "HIGH"
    assert service.policy_current("canonical-policy") == second

    with pytest.raises(ValueError, match="cannot weaken permanent invariant"):
        service.record_policy_version(
            "unsafe-policy",
            policy_name="Unsafe",
            rules={"count_only_promotion_forbidden": False},
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="cannot weaken canonical minimum"):
        service.record_policy_version(
            "unsafe-threshold-policy",
            policy_name="Unsafe threshold",
            rules={"verified_minimum_confidence": {"evidence_sufficiency": "MEDIUM"}},
            created_at=NOW,
        )

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_verification_policy_versions SET policy_name='mutated' WHERE policy_version_id=?",
                (first.policy_version_id,),
            )


def test_confidence_is_multidimensional_versioned_and_has_no_promotional_scalar(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    service = SemanticVerificationService(runtime)
    first = _confidence(service, claim, evidence_sufficiency="MEDIUM", coverage_limitation="LIMITED")
    second = _confidence(service, claim)

    assert first.confidence_version == 1 and second.confidence_version == 2
    assert second.supersedes_confidence_version_id == first.factual_confidence_version_id
    assert second.presentation_scalar is None
    assert second.coverage_confidence is None
    assert second.changes_verification_state is False
    assert service.confidence_current(claim.semantic_claim_version_id) == second

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM semantic_factual_confidence_versions WHERE factual_confidence_version_id=?",
                (first.factual_confidence_version_id,),
            )


def test_two_supporting_items_do_not_verify_without_explicit_independence(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    _evidence(runtime, claim, "support-a", "origin-a")
    _evidence(runtime, claim, "support-b", "origin-b")
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="explicit current independent supporting evidence pair"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="VERIFIED",
            decision_code="INITIAL",
            rationale="Two items alone are insufficient",
            created_at=NOW,
        )


def test_explicit_independent_support_pair_and_strong_profile_can_verify(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    left = _evidence(runtime, claim, "support-a", "origin-a")
    right = _evidence(runtime, claim, "support-b", "origin-b",)
    independence = _independent_pair(runtime, claim, left, right)
    service = SemanticVerificationService(runtime)
    policy = _policy(service)
    confidence = _confidence(service, claim)

    decision = service.record_decision(
        claim.semantic_claim_version_id,
        policy_id=policy.policy_id,
        verification_state="VERIFIED",
        decision_code="INITIAL",
        rationale="Explicit independent support pair and policy confidence gates satisfied",
        created_at=NOW,
    )

    assert decision.verification_state == "VERIFIED"
    assert decision.policy_version_id == policy.policy_version_id
    assert decision.factual_confidence_version_id == confidence.factual_confidence_version_id
    assert {item["evidence_relation_version_id"] for item in decision.evidence_snapshot} == {
        left.evidence_relation_version_id,
        right.evidence_relation_version_id,
    }
    assert {item["independence_assessment_version_id"] for item in decision.independence_snapshot} == {
        independence.independence_assessment_version_id
    }
    assert decision.contradiction_snapshot == ()
    assert decision.is_policy_controlled is True
    assert decision.coverage_confidence is None


def test_verified_is_blocked_by_current_unresolved_contradiction(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime, "claim-left")
    other = _claim(runtime, "claim-right", "The event did not occur")
    left = _evidence(runtime, claim, "support-a", "origin-a")
    right = _evidence(runtime, claim, "support-b", "origin-b")
    _independent_pair(runtime, claim, left, right)
    SemanticContradictionService(runtime).record_version(
        "contradiction-1",
        left_semantic_claim_version_id=claim.semantic_claim_version_id,
        right_semantic_claim_version_id=other.semantic_claim_version_id,
        contradiction_dimension="OCCURRENCE_EXISTENCE",
        lifecycle_state="UNRESOLVED",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        note="Material occurrence contradiction",
        created_at=NOW,
    )
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="unresolved current contradiction"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="VERIFIED",
            decision_code="INITIAL",
            rationale="Must fail closed",
            created_at=NOW,
        )


def test_resolved_contradiction_does_not_itself_create_verified_truth(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime, "claim-left")
    other = _claim(runtime, "claim-right", "The event did not occur")
    contradictions = SemanticContradictionService(runtime)
    contradictions.record_version(
        "contradiction-1",
        left_semantic_claim_version_id=claim.semantic_claim_version_id,
        right_semantic_claim_version_id=other.semantic_claim_version_id,
        contradiction_dimension="OCCURRENCE_EXISTENCE",
        lifecycle_state="UNRESOLVED",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    contradictions.record_version(
        "contradiction-1",
        left_semantic_claim_version_id=claim.semantic_claim_version_id,
        right_semantic_claim_version_id=other.semantic_claim_version_id,
        contradiction_dimension="OCCURRENCE_EXISTENCE",
        lifecycle_state="RESOLVED",
        reconciliation_code="NEW_EVIDENCE",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.1",
        note="Analytical contradiction reconciled; no factual winner selected",
        created_at=NOW,
    )
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="explicit current independent supporting evidence pair"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="VERIFIED",
            decision_code="INITIAL",
            rationale="Resolved contradiction alone cannot verify",
            created_at=NOW,
        )


def test_current_contradicting_evidence_blocks_verified_even_with_independent_support(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    left = _evidence(runtime, claim, "support-a", "origin-a")
    right = _evidence(runtime, claim, "support-b", "origin-b")
    _independent_pair(runtime, claim, left, right)
    _evidence(runtime, claim, "contradiction-evidence", "origin-c", relation_type="CONTRADICTS")
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="current contradicting evidence"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="VERIFIED",
            decision_code="INITIAL",
            rationale="Conflict remains current",
            created_at=NOW,
        )


def test_decision_snapshot_uses_global_latest_evidence_identity_versions(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)
    entity_a = _entity(runtime, "origin-a")
    entity_b = _entity(runtime, "origin-b")
    old = evidence.record_relation_version(
        "evidence-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity_a.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    right = evidence.record_relation_version(
        "support-b",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity_b.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    _independent_pair(runtime, claim, old, right, "old-independent-pair")
    newest = evidence.record_relation_version(
        "evidence-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity_a.provenance_entity_version_id,
        relation_type="QUALIFIES",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.1",
        created_at=NOW,
    )
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="explicit current independent supporting evidence pair"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="VERIFIED",
            decision_code="INITIAL",
            rationale="Superseded support must not remain current",
            created_at=NOW,
        )
    detected = service.record_decision(
        claim.semantic_claim_version_id,
        policy_id="canonical-policy",
        verification_state="DETECTED",
        decision_code="INITIAL",
        rationale="Current snapshot retained without promotion",
        created_at=NOW,
    )
    ids = {item["evidence_relation_version_id"] for item in detected.evidence_snapshot}
    assert newest.evidence_relation_version_id in ids
    assert old.evidence_relation_version_id not in ids
    assert provenance is not None


def test_disputed_and_unverifiable_states_require_explicit_current_conditions(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim)

    with pytest.raises(ValueError, match="DISPUTED requires"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="DISPUTED",
            decision_code="INITIAL",
            rationale="No current dispute exists",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="LIMITED coverage limitation"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="UNVERIFIABLE",
            decision_code="INITIAL",
            rationale="Coverage is not limited",
            created_at=NOW,
        )


def test_decision_history_is_append_only_and_transition_code_is_audited(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    _evidence(runtime, claim, "support-a", "origin-a")
    service = SemanticVerificationService(runtime)
    _policy(service)
    _confidence(service, claim, evidence_sufficiency="MEDIUM")
    first = service.record_decision(
        claim.semantic_claim_version_id,
        policy_id="canonical-policy",
        verification_state="DETECTED",
        decision_code="INITIAL",
        rationale="Initial detection",
        created_at=NOW,
    )
    second = service.record_decision(
        claim.semantic_claim_version_id,
        policy_id="canonical-policy",
        verification_state="PARTLY_VERIFIED",
        decision_code="PROMOTE",
        rationale="Supporting evidence and minimum multidimensional confidence present",
        created_at=NOW,
    )

    assert first.decision_version == 1 and second.decision_version == 2
    assert second.supersedes_decision_version_id == first.verification_decision_version_id
    assert [item.verification_state for item in service.decision_history(claim.semantic_claim_version_id)] == [
        "DETECTED",
        "PARTLY_VERIFIED",
    ]
    with pytest.raises(ValueError, match="decision_code must be HOLD"):
        service.record_decision(
            claim.semantic_claim_version_id,
            policy_id="canonical-policy",
            verification_state="PARTLY_VERIFIED",
            decision_code="PROMOTE",
            rationale="Wrong transition code",
            created_at=NOW,
        )
    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_verification_decision_versions SET rationale='mutated' WHERE verification_decision_version_id=?",
                (first.verification_decision_version_id,),
            )
