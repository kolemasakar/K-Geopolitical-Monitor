from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_evidence import (
    EVIDENCE_RELATION_TYPES,
    INDEPENDENCE_STATES,
    SemanticEvidenceService,
)


NOW = datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _claim(runtime, claim_id="claim-evidence-1"):
    return SemanticClaimService(runtime).record_version(
        claim_id,
        normalized_proposition="The government announced a new measure",
        claimant_actor="Government",
        subject_text="Government",
        object_theme="new measure",
        event_action_type="ANNOUNCEMENT",
        polarity="AFFIRMATIVE",
        modality="REPORTED",
        time_scope={"date": "2026-09-02"},
        location_scope={"country": "Example"},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.95,
        created_at=NOW,
    )


def _entity(service, entity_id, *, kind="PUBLICATION", url=None, language="en"):
    return service.record_entity_version(
        entity_id,
        entity_kind=kind,
        canonical_name=entity_id,
        canonical_url=url,
        language=language,
        created_at=NOW,
    )


def _evidence(service, relation_id, claim, entity, *, relation_type="SUPPORTS"):
    return service.record_relation_version(
        relation_id,
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=entity.provenance_entity_version_id,
        relation_type=relation_type,
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )


def test_all_typed_evidence_relations_persist_without_truth_promotion(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    service = SemanticEvidenceService(runtime)

    stored = []
    for index, relation_type in enumerate(EVIDENCE_RELATION_TYPES):
        entity = _entity(provenance, f"publication-{index}")
        relation = _evidence(
            service,
            f"evidence-{index}",
            claim,
            entity,
            relation_type=relation_type,
        )
        stored.append(relation)
        assert relation.changes_verification_state is False
        assert relation.resolves_contradiction is False

    assert {item.relation_type for item in service.relations_for_claim(claim.semantic_claim_version_id)} == set(
        EVIDENCE_RELATION_TYPES
    )
    assert len(stored) == 6


def test_syndicated_and_translated_publications_are_not_independent(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)

    original = _entity(provenance, "wire-original", kind="WIRE_REPORT", url="https://wire.example/r/1")
    syndication = _entity(provenance, "publisher-a", url="https://a.example/article", language="en")
    translation = _entity(provenance, "publisher-b", url="https://b.example/uk/article", language="uk")
    provenance.record_relation_version(
        "syndicated-from",
        subject_entity_version_id=syndication.provenance_entity_version_id,
        object_entity_version_id=original.provenance_entity_version_id,
        relation_type="SYNDICATED_FROM",
        created_at=NOW,
    )
    provenance.record_relation_version(
        "translated-from",
        subject_entity_version_id=translation.provenance_entity_version_id,
        object_entity_version_id=syndication.provenance_entity_version_id,
        relation_type="TRANSLATED_FROM",
        created_at=NOW,
    )
    left = _evidence(evidence, "evidence-a", claim, syndication)
    right = _evidence(evidence, "evidence-b", claim, translation)

    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
    ) == ("NOT_INDEPENDENT", "DERIVATION_PATH")


def test_two_publications_citing_same_official_statement_are_not_independent(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)

    statement = _entity(
        provenance,
        "official-statement",
        kind="OFFICIAL_STATEMENT",
        url="https://gov.example/statement/1",
    )
    publication_a = _entity(provenance, "publication-a", url="https://a.example/report")
    publication_b = _entity(provenance, "publication-b", url="https://b.example/report")
    for relation_id, publication in (("cite-a", publication_a), ("cite-b", publication_b)):
        provenance.record_relation_version(
            relation_id,
            subject_entity_version_id=publication.provenance_entity_version_id,
            object_entity_version_id=statement.provenance_entity_version_id,
            relation_type="CITES",
            created_at=NOW,
        )
    left = _evidence(evidence, "evidence-a", claim, publication_a)
    right = _evidence(evidence, "evidence-b", claim, publication_b)

    state, rationale = evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
    )
    assert state == "NOT_INDEPENDENT"
    assert rationale == "DERIVATION_PATH"


def test_different_publishers_without_origin_proof_remain_unknown(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)

    left_entity = _entity(provenance, "publisher-a", url="https://a.example/report", language="en")
    right_entity = _entity(provenance, "publisher-b", url="https://b.example/report", language="pl")
    left = _evidence(evidence, "evidence-a", claim, left_entity)
    right = _evidence(evidence, "evidence-b", claim, right_entity)

    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
    ) == ("UNKNOWN", "INSUFFICIENT_PROVENANCE")


def test_unknown_and_mixed_provenance_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)

    concrete = _entity(provenance, "concrete-publication")
    unknown = _entity(provenance, "unknown-origin", kind="UNKNOWN", language=None)
    mixed = _entity(provenance, "mixed-origin", kind="MIXED", language=None)
    concrete_evidence = _evidence(evidence, "evidence-concrete", claim, concrete)
    unknown_evidence = _evidence(evidence, "evidence-unknown", claim, unknown)
    mixed_evidence = _evidence(evidence, "evidence-mixed", claim, mixed)

    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=concrete_evidence.evidence_relation_version_id,
        comparison_evidence_relation_version_id=unknown_evidence.evidence_relation_version_id,
    ) == ("UNKNOWN", "UNRESOLVED_ORIGIN")
    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=concrete_evidence.evidence_relation_version_id,
        comparison_evidence_relation_version_id=mixed_evidence.evidence_relation_version_id,
    ) == ("MIXED", "MIXED_ORIGIN")


def test_independent_state_requires_explicit_compatible_rationale(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)
    left = _evidence(evidence, "evidence-a", claim, _entity(provenance, "origin-a", kind="OFFICIAL_DOCUMENT"))
    right = _evidence(evidence, "evidence-b", claim, _entity(provenance, "origin-b", kind="DATASET"))

    with pytest.raises(ValueError, match="incompatible"):
        evidence.record_independence_version(
            "assessment-1",
            semantic_claim_version_id=claim.semantic_claim_version_id,
            subject_evidence_relation_version_id=left.evidence_relation_version_id,
            comparison_evidence_relation_version_id=right.evidence_relation_version_id,
            independence_state="INDEPENDENT",
            rationale_code="INSUFFICIENT_PROVENANCE",
            assessment_method="HUMAN_REVIEWED",
            assessment_version="1.0",
            created_at=NOW,
        )

    recorded = evidence.record_independence_version(
        "assessment-1",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
        independence_state="INDEPENDENT",
        rationale_code="EXPLICIT_DISTINCT_UNDERLYING_ORIGINS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        note="Distinct underlying origin records explicitly reviewed",
        created_at=NOW,
    )
    assert recorded.independence_state == "INDEPENDENT"
    assert recorded.changes_verification_state is False
    assert recorded.factual_confidence is None


def test_evidence_and_independence_versions_are_append_only(tmp_path):
    runtime = _runtime(tmp_path)
    claim = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)
    left_entity = _entity(provenance, "origin-a")
    right_entity = _entity(provenance, "origin-b")
    first = _evidence(evidence, "evidence-versioned", claim, left_entity, relation_type="CONTEXT_ONLY")
    second = evidence.record_relation_version(
        "evidence-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=left_entity.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.1",
        created_at=NOW,
    )
    right = _evidence(evidence, "evidence-right", claim, right_entity)
    a1 = evidence.record_independence_version(
        "assessment-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        subject_evidence_relation_version_id=second.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
        independence_state="UNKNOWN",
        rationale_code="INSUFFICIENT_PROVENANCE",
        assessment_method="RULE_BASED",
        assessment_version="1.0",
        created_at=NOW,
    )
    a2 = evidence.record_independence_version(
        "assessment-versioned",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        subject_evidence_relation_version_id=second.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
        independence_state="INDEPENDENT",
        rationale_code="MANUAL_REVIEW",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.1",
        created_at=NOW,
    )

    assert first.relation_version == 1 and second.relation_version == 2
    assert second.supersedes_relation_version_id == first.evidence_relation_version_id
    assert [item.relation_version for item in evidence.relation_history("evidence-versioned")] == [1, 2]
    assert a1.assessment_version_number == 1 and a2.assessment_version_number == 2
    assert a2.supersedes_assessment_version_id == a1.independence_assessment_version_id
    assert [item.assessment_version_number for item in evidence.assessment_history("assessment-versioned")] == [1, 2]

    with sqlite3.connect(runtime.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE semantic_evidence_relation_versions SET note='mutated' WHERE evidence_relation_version_id=?",
                (first.evidence_relation_version_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM semantic_independence_assessment_versions WHERE independence_assessment_version_id=?",
                (a1.independence_assessment_version_id,),
            )


def test_claim_scope_and_reference_identity_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    claim_a = _claim(runtime, "claim-a")
    claim_b = _claim(runtime, "claim-b")
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)
    left = _evidence(evidence, "evidence-a", claim_a, _entity(provenance, "entity-a"))
    right = _evidence(evidence, "evidence-b", claim_b, _entity(provenance, "entity-b"))

    with pytest.raises(ValueError, match="belong to the semantic claim"):
        evidence.record_independence_version(
            "assessment-cross-claim",
            semantic_claim_version_id=claim_a.semantic_claim_version_id,
            subject_evidence_relation_version_id=left.evidence_relation_version_id,
            comparison_evidence_relation_version_id=right.evidence_relation_version_id,
            independence_state="UNKNOWN",
            rationale_code="INSUFFICIENT_PROVENANCE",
            assessment_method="RULE_BASED",
            assessment_version="1.0",
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="provenance entity version does not exist"):
        evidence.record_relation_version(
            "missing-entity",
            semantic_claim_version_id=claim_a.semantic_claim_version_id,
            evidence_provenance_entity_version_id="missing",
            relation_type="SUPPORTS",
            assessment_method="HUMAN_REVIEWED",
            assessment_version="1.0",
            created_at=NOW,
        )


def test_p13_3_schema_stops_before_contradiction_verification_and_confidence(tmp_path):
    runtime = _runtime(tmp_path)
    forbidden = {
        "contradiction_state",
        "verification_state",
        "verification_status",
        "factual_confidence",
        "coverage_confidence",
        "verification_policy",
    }
    with sqlite3.connect(runtime.database_path) as connection:
        for table in (
            "semantic_evidence_relation_versions",
            "semantic_independence_assessment_versions",
        ):
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
            assert forbidden.isdisjoint(columns)
    assert set(INDEPENDENCE_STATES) == {"INDEPENDENT", "NOT_INDEPENDENT", "UNKNOWN", "MIXED"}
