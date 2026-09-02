from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.contradictions import Contradiction
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_contradictions import (
    CONTRADICTION_DIMENSIONS,
    CONTRADICTION_LIFECYCLE_STATES,
    SemanticContradictionService,
)
from kgeopolitical_monitor.semantic_evidence import SemanticEvidenceService


NOW = datetime(2026, 9, 2, 6, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _claim(runtime, claim_id, proposition, *, polarity="AFFIRMATIVE", modality="ASSERTED"):
    return SemanticClaimService(runtime).record_version(
        claim_id,
        normalized_proposition=proposition,
        claimant_actor="Actor",
        subject_text="Subject",
        object_theme="Theme",
        event_action_type="REPORT",
        polarity=polarity,
        modality=modality,
        time_scope={"date": "2026-09-02"},
        location_scope={"country": "Example"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.9,
        created_at=NOW,
    )


def _pair(runtime):
    left = _claim(runtime, "claim-left", "The event occurred", polarity="AFFIRMATIVE")
    right = _claim(
        runtime,
        "claim-right",
        "The event did not occur",
        polarity="NEGATED",
        modality="DENIED",
    )
    return left, right


def _record(
    service,
    contradiction_id,
    left,
    right,
    *,
    dimension="OCCURRENCE_EXISTENCE",
    state="DETECTED",
    code="NONE",
    note=None,
):
    return service.record_version(
        contradiction_id,
        left_semantic_claim_version_id=left.semantic_claim_version_id,
        right_semantic_claim_version_id=right.semantic_claim_version_id,
        contradiction_dimension=dimension,
        lifecycle_state=state,
        reconciliation_code=code,
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        note=note,
        created_at=NOW,
    )


def test_all_contradiction_dimensions_persist_without_truth_promotion(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    service = SemanticContradictionService(runtime)

    stored = []
    for index, dimension in enumerate(CONTRADICTION_DIMENSIONS):
        contradiction = _record(
            service,
            f"contradiction-{index}",
            left,
            right,
            dimension=dimension,
        )
        stored.append(contradiction)
        assert contradiction.lifecycle_state == "DETECTED"
        assert contradiction.changes_verification_state is False
        assert contradiction.determines_factual_truth is False
        assert contradiction.factual_confidence is None

    assert {item.contradiction_dimension for item in stored} == set(CONTRADICTION_DIMENSIONS)
    assert set(CONTRADICTION_LIFECYCLE_STATES) == {
        "DETECTED",
        "UNRESOLVED",
        "EVOLVING",
        "RESOLVED",
    }


def test_lifecycle_is_versioned_and_resolution_preserves_disagreement_history(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    service = SemanticContradictionService(runtime)

    detected = _record(service, "contradiction-lifecycle", left, right, state="DETECTED")
    evolving = _record(service, "contradiction-lifecycle", left, right, state="EVOLVING")
    resolved = _record(
        service,
        "contradiction-lifecycle",
        left,
        right,
        state="RESOLVED",
        code="NEW_EVIDENCE",
        note="Later primary evidence reconciled the occurrence discrepancy; historical disagreement retained.",
    )

    assert [item.lifecycle_state for item in service.history("contradiction-lifecycle")] == [
        "DETECTED",
        "EVOLVING",
        "RESOLVED",
    ]
    assert detected.contradiction_version == 1
    assert evolving.contradiction_version == 2
    assert resolved.contradiction_version == 3
    assert evolving.supersedes_contradiction_version_id == detected.contradiction_version_id
    assert resolved.supersedes_contradiction_version_id == evolving.contradiction_version_id
    assert service.current("contradiction-lifecycle") == resolved
    assert service.contradictions_for_claim(left.semantic_claim_version_id) == (resolved,)


def test_resolution_state_requires_explicit_reconciliation_and_explanation(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    service = SemanticContradictionService(runtime)

    with pytest.raises(ValueError, match="requires a reconciliation code"):
        _record(
            service,
            "bad-resolved-none",
            left,
            right,
            state="RESOLVED",
            code="NONE",
            note="reviewed",
        )
    with pytest.raises(ValueError, match="requires an explanatory note"):
        _record(
            service,
            "bad-resolved-note",
            left,
            right,
            state="RESOLVED",
            code="MANUAL_REVIEW",
        )
    with pytest.raises(ValueError, match="non-RESOLVED"):
        _record(
            service,
            "bad-open-code",
            left,
            right,
            state="UNRESOLVED",
            code="NEW_EVIDENCE",
        )


def test_contradiction_identity_cannot_drift_to_other_claims_or_dimension(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    other = _claim(runtime, "claim-other", "A different proposition")
    service = SemanticContradictionService(runtime)
    _record(service, "stable-identity", left, right, dimension="TIME")

    with pytest.raises(ValueError, match="cannot change claim versions or contradiction dimension"):
        _record(service, "stable-identity", left, right, dimension="LOCATION")
    with pytest.raises(ValueError, match="cannot change claim versions or contradiction dimension"):
        _record(service, "stable-identity", left, other, dimension="TIME")
    with pytest.raises(ValueError, match="two different semantic claim versions"):
        _record(service, "same-claim", left, left)


def test_evidence_links_enforce_current_relation_and_claim_side(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    contradictions = SemanticContradictionService(runtime)
    evidence_service = SemanticEvidenceService(runtime)
    provenance = SemanticProvenanceService(runtime)
    contradiction = _record(contradictions, "contradiction-evidence", left, right)

    left_entity = provenance.record_entity_version(
        "left-publication",
        entity_kind="PUBLICATION",
        canonical_name="Left publication",
        canonical_url="https://left.example/report",
        created_at=NOW,
    )
    right_entity = provenance.record_entity_version(
        "right-publication",
        entity_kind="PUBLICATION",
        canonical_name="Right publication",
        canonical_url="https://right.example/report",
        created_at=NOW,
    )
    left_v1 = evidence_service.record_relation_version(
        "left-evidence",
        semantic_claim_version_id=left.semantic_claim_version_id,
        evidence_provenance_entity_version_id=left_entity.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    left_v2 = evidence_service.record_relation_version(
        "left-evidence",
        semantic_claim_version_id=left.semantic_claim_version_id,
        evidence_provenance_entity_version_id=left_entity.provenance_entity_version_id,
        relation_type="QUALIFIES",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.1",
        created_at=NOW,
    )
    right_current = evidence_service.record_relation_version(
        "right-evidence",
        semantic_claim_version_id=right.semantic_claim_version_id,
        evidence_provenance_entity_version_id=right_entity.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )

    with pytest.raises(ValueError, match="current evidence relation version"):
        contradictions.record_evidence_link(
            contradiction_version_id=contradiction.contradiction_version_id,
            evidence_relation_version_id=left_v1.evidence_relation_version_id,
            claim_side="LEFT",
            link_role="CLAIM_EVIDENCE",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="does not match contradiction claim side"):
        contradictions.record_evidence_link(
            contradiction_version_id=contradiction.contradiction_version_id,
            evidence_relation_version_id=right_current.evidence_relation_version_id,
            claim_side="LEFT",
            link_role="CLAIM_EVIDENCE",
            created_at=NOW,
        )

    left_link = contradictions.record_evidence_link(
        contradiction_version_id=contradiction.contradiction_version_id,
        evidence_relation_version_id=left_v2.evidence_relation_version_id,
        claim_side="LEFT",
        link_role="QUALIFIER",
        note="Current left-side evidence",
        created_at=NOW,
    )
    right_link = contradictions.record_evidence_link(
        contradiction_version_id=contradiction.contradiction_version_id,
        evidence_relation_version_id=right_current.evidence_relation_version_id,
        claim_side="RIGHT",
        link_role="CLAIM_EVIDENCE",
        created_at=NOW,
    )
    assert left_link.changes_verification_state is False
    assert {
        item.contradiction_evidence_link_id
        for item in contradictions.evidence_links(contradiction.contradiction_version_id)
    } == {
        left_link.contradiction_evidence_link_id,
        right_link.contradiction_evidence_link_id,
    }

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_contradiction_evidence_links SET note='mutated' WHERE contradiction_evidence_link_id=?",
                (left_link.contradiction_evidence_link_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM semantic_contradiction_evidence_links WHERE contradiction_evidence_link_id=?",
                (right_link.contradiction_evidence_link_id,),
            )


def test_p13_3_contradicts_relation_does_not_auto_create_or_resolve_contradiction(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    provenance = SemanticProvenanceService(runtime)
    entity = provenance.record_entity_version(
        "contradicting-publication",
        entity_kind="PUBLICATION",
        canonical_name="Contradicting publication",
        canonical_url="https://example.com/contradiction",
        created_at=NOW,
    )
    relation = SemanticEvidenceService(runtime).record_relation_version(
        "p13-3-contradicts",
        semantic_claim_version_id=left.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity.provenance_entity_version_id,
        relation_type="CONTRADICTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    assert relation.resolves_contradiction is False
    with sqlite3.connect(runtime.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM semantic_contradiction_versions"
        ).fetchone()[0] == 0

    contradiction = _record(
        SemanticContradictionService(runtime),
        "explicit-only",
        left,
        right,
        state="UNRESOLVED",
    )
    assert contradiction.lifecycle_state == "UNRESOLVED"
    assert contradiction.changes_verification_state is False


def test_contradiction_versions_are_append_only(tmp_path):
    runtime = _runtime(tmp_path)
    left, right = _pair(runtime)
    service = SemanticContradictionService(runtime)
    contradiction = _record(service, "append-only", left, right)

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_contradiction_versions SET lifecycle_state='RESOLVED' WHERE contradiction_version_id=?",
                (contradiction.contradiction_version_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM semantic_contradiction_versions WHERE contradiction_version_id=?",
                (contradiction.contradiction_version_id,),
            )


def test_p13_4_schema_stops_before_verification_policy_and_confidence(tmp_path):
    runtime = _runtime(tmp_path)
    forbidden = {
        "verification_state",
        "verification_status",
        "factual_confidence",
        "coverage_confidence",
        "verification_policy",
        "truth_state",
        "source_reputation_score",
        "independent_origin_count",
    }
    with sqlite3.connect(runtime.database_path) as connection:
        for table in (
            "semantic_contradiction_versions",
            "semantic_contradiction_evidence_links",
        ):
            columns = {
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            assert forbidden.isdisjoint(columns)


def test_legacy_contradiction_container_remains_compatible(tmp_path):
    legacy = Contradiction("legacy-a", "legacy-b")
    assert legacy.claim_a == "legacy-a"
    assert legacy.claim_b == "legacy-b"
    assert legacy.status == "DETECTED"
    legacy_custom = Contradiction("a", "b", status="DISPUTED")
    assert legacy_custom.status == "DISPUTED"
