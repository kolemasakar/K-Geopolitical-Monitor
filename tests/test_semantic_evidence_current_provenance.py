from datetime import datetime, timezone

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_claims import SemanticClaimService
from kgeopolitical_monitor.semantic_evidence import SemanticEvidenceService


NOW = datetime(2026, 9, 2, 1, 30, tzinfo=timezone.utc)


def test_superseded_provenance_edge_does_not_define_current_independence(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    claim = SemanticClaimService(runtime).record_version(
        "claim-current-graph",
        normalized_proposition="A reported event occurred",
        claimant_actor="Actor",
        subject_text="Event",
        object_theme="event",
        event_action_type="REPORT",
        polarity="AFFIRMATIVE",
        modality="REPORTED",
        time_scope={},
        location_scope={},
        quantity={},
        original_language="en",
        extraction_method="HUMAN_REVIEWED",
        extraction_version="1.0",
        extraction_confidence=0.9,
        created_at=NOW,
    )
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)

    a = provenance.record_entity_version(
        "publication-a", entity_kind="PUBLICATION", canonical_name="Publication A", created_at=NOW
    )
    b = provenance.record_entity_version(
        "publication-b", entity_kind="PUBLICATION", canonical_name="Publication B", created_at=NOW
    )
    publisher = provenance.record_entity_version(
        "publisher-a", entity_kind="PUBLISHER", canonical_name="Publisher A", created_at=NOW
    )

    provenance.record_relation_version(
        "correctable-relation",
        subject_entity_version_id=a.provenance_entity_version_id,
        object_entity_version_id=b.provenance_entity_version_id,
        relation_type="SYNDICATED_FROM",
        created_at=NOW,
    )

    ev_a = evidence.record_relation_version(
        "evidence-a",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=a.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )
    ev_b = evidence.record_relation_version(
        "evidence-b",
        semantic_claim_version_id=claim.semantic_claim_version_id,
        evidence_provenance_entity_version_id=b.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="HUMAN_REVIEWED",
        assessment_version="1.0",
        created_at=NOW,
    )

    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=ev_a.evidence_relation_version_id,
        comparison_evidence_relation_version_id=ev_b.evidence_relation_version_id,
    ) == ("NOT_INDEPENDENT", "DERIVATION_PATH")

    # Correct the provenance relation. The old syndication edge remains in history,
    # but current inference must use only the latest version of that relation identity.
    provenance.record_relation_version(
        "correctable-relation",
        subject_entity_version_id=a.provenance_entity_version_id,
        object_entity_version_id=publisher.provenance_entity_version_id,
        relation_type="PUBLISHED_BY",
        note="corrected relationship",
        created_at=NOW,
    )

    assert evidence.infer_pair_fail_closed(
        subject_evidence_relation_version_id=ev_a.evidence_relation_version_id,
        comparison_evidence_relation_version_id=ev_b.evidence_relation_version_id,
    ) == ("UNKNOWN", "INSUFFICIENT_PROVENANCE")
