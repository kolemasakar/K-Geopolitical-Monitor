from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.semantic_ingestion_bridge import CanonicalSemanticIngestionBridge
from kgeopolitical_monitor.semantic_provenance import SemanticProvenanceService
from kgeopolitical_monitor.semantic_evidence import SemanticEvidenceService
from kgeopolitical_monitor.p23_3_corroboration_observation import CorroborationEvidenceObserver

NOW = datetime(2026, 9, 21, 17, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _seed(runtime):
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id,name,source_class,reliability) VALUES (?,?,?,?)",
            ("ofac-recent-actions-en", "U.S. Treasury OFAC", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES (?,?,?,?,?)",
            ("raw-1", "ofac-recent-actions-en", "Designation action title", "Observed source body", NOW.isoformat()),
        )
        connection.execute(
            """INSERT INTO live_analysis_runs(
                analysis_run_id,collection_id,watch_id,status,claim_count,finding_count,created_at
            ) VALUES (?,?,?,?,?,?,?)""",
            ("run-1", "collection-1", "watch-1", "COMPLETED", 1, 1, NOW.isoformat()),
        )
        connection.execute(
            """INSERT INTO live_analysis_claims(
                claim_id,analysis_run_id,claim_key,title,verification_status,
                confidence,importance,independent_origin_count,source_class_count,origins_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("live-1", "run-1", "legacy-title-key", "Designation action title", "DETECTED", 0.9, 0.8, 1, 1, '["ofac.treasury.gov"]'),
        )
        connection.execute(
            "INSERT INTO live_analysis_evidence(claim_id,raw_item_id,original_url,origin_host) VALUES (?,?,?,?)",
            ("live-1", "raw-1", "https://ofac.treasury.gov/recent-actions/example", "ofac.treasury.gov"),
        )
    CanonicalSemanticIngestionBridge(
        runtime,
        allowed_source_ids=["ofac-recent-actions-en"],
        source_languages={"ofac-recent-actions-en": "en"},
    ).ingest_analysis_run("run-1", created_at=NOW)


def _claim(runtime):
    with sqlite3.connect(runtime.database_path) as connection:
        return connection.execute(
            "SELECT semantic_claim_version_id FROM semantic_claim_versions"
        ).fetchone()[0]


def _add_support_pair(runtime, independence_state="INDEPENDENT", rationale="EXPLICIT_DISTINCT_UNDERLYING_ORIGINS"):
    claim_id = _claim(runtime)
    provenance = SemanticProvenanceService(runtime)
    evidence = SemanticEvidenceService(runtime)
    left_entity = provenance.record_entity_version(
        "origin-left",
        entity_kind="OFFICIAL_DOCUMENT",
        canonical_name="Left explicit origin",
        source_id="ofac-recent-actions-en",
        canonical_url="https://example.test/left",
        language="en",
        metadata={"test": True},
        created_at=NOW,
    )
    right_entity = provenance.record_entity_version(
        "origin-right",
        entity_kind="OFFICIAL_DOCUMENT",
        canonical_name="Right explicit origin",
        source_id="ofac-recent-actions-en",
        canonical_url="https://example.test/right",
        language="en",
        metadata={"test": True},
        created_at=NOW,
    )
    left = evidence.record_relation_version(
        "support-left",
        semantic_claim_version_id=claim_id,
        evidence_provenance_entity_version_id=left_entity.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="TEST",
        assessment_version="1",
        created_at=NOW,
    )
    right = evidence.record_relation_version(
        "support-right",
        semantic_claim_version_id=claim_id,
        evidence_provenance_entity_version_id=right_entity.provenance_entity_version_id,
        relation_type="SUPPORTS",
        assessment_method="TEST",
        assessment_version="1",
        created_at=NOW,
    )
    evidence.record_independence_version(
        "pair-1",
        semantic_claim_version_id=claim_id,
        subject_evidence_relation_version_id=left.evidence_relation_version_id,
        comparison_evidence_relation_version_id=right.evidence_relation_version_id,
        independence_state=independence_state,
        rationale_code=rationale,
        assessment_method="TEST",
        assessment_version="1",
        created_at=NOW,
    )


def test_attribution_only_cohort_does_not_create_corroboration(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    result = CorroborationEvidenceObserver(runtime).observe_analysis_run("run-1")
    assert result.claim_count == 1
    assert result.relation_distribution["ATTRIBUTION_ONLY"] == 1
    assert result.relation_distribution["SUPPORTS"] == 0
    assert result.independence_distribution["INDEPENDENT"] == 0
    assert result.corroborated_claim_count == 0
    assert result.changes_verification_state is False
    assert result.grants_factual_independence_credit is False


def test_explicit_current_independent_support_pair_counts_as_corroborated(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    _add_support_pair(runtime)
    result = CorroborationEvidenceObserver(runtime).observe_analysis_run("run-1")
    assert result.relation_distribution["SUPPORTS"] == 2
    assert result.independence_distribution["INDEPENDENT"] == 1
    assert result.claims_with_support == 1
    assert result.corroborated_claim_count == 1
    assert result.changes_verification_state is False


def test_unknown_support_pair_is_not_corroborated(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    _add_support_pair(runtime, independence_state="UNKNOWN", rationale="INSUFFICIENT_PROVENANCE")
    result = CorroborationEvidenceObserver(runtime).observe_analysis_run("run-1")
    assert result.relation_distribution["SUPPORTS"] == 2
    assert result.independence_distribution["UNKNOWN"] == 1
    assert result.corroborated_claim_count == 0


def test_empty_analysis_run_id_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    observer = CorroborationEvidenceObserver(runtime)
    try:
        observer.observe_analysis_run(" ")
    except ValueError as exc:
        assert "analysis_run_id" in str(exc)
    else:
        raise AssertionError("empty analysis_run_id must fail closed")
