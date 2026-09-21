from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.semantic_ingestion_bridge import CanonicalSemanticIngestionBridge
from kgeopolitical_monitor.semantic_provenance import SemanticProvenanceService
from kgeopolitical_monitor.p23_2_provenance_resolution import UnderlyingOriginResolutionObserver

NOW = datetime(2026, 9, 20, 5, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _seed(runtime, *, original_url="https://ofac.treasury.gov/recent-actions/example"):
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
            ("live-1", "raw-1", original_url, "ofac.treasury.gov"),
        )
    CanonicalSemanticIngestionBridge(
        runtime,
        allowed_source_ids=["ofac-recent-actions-en"],
        source_languages={"ofac-recent-actions-en": "en"},
    ).ingest_analysis_run("run-1", created_at=NOW)


def _observe(runtime):
    return UnderlyingOriginResolutionObserver(
        runtime,
        trusted_first_party_hosts={"ofac-recent-actions-en": ["ofac.treasury.gov"]},
    ).observe_analysis_run("run-1")


def test_first_party_publication_does_not_resolve_underlying_origin(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    result = _observe(runtime)
    assert result.claim_count == 1
    assert result.first_party_publication_count == 1
    assert result.resolved_underlying_origin_count == 0
    assert result.unresolved_underlying_origin_count == 1
    assert result.semantic_independence_assessment_count == 0
    assert result.first_party_publication_is_origin_credit is False
    assert result.grants_independence_credit is False


def test_untrusted_publication_host_is_not_first_party(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime, original_url="https://mirror.example/recent-actions/example")
    result = _observe(runtime)
    assert result.first_party_publication_count == 0
    assert result.unresolved_underlying_origin_count == 1


def test_explicit_observed_concrete_underlying_origin_is_counted_as_resolved(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    with sqlite3.connect(runtime.database_path) as connection:
        claim_version_id = connection.execute(
            "SELECT semantic_claim_version_id FROM semantic_claim_versions"
        ).fetchone()[0]
        role_id = connection.execute(
            """SELECT claim_provenance_role_id
               FROM semantic_claim_provenance_role_versions
               WHERE provenance_role='UNDERLYING_ORIGIN'"""
        ).fetchone()[0]

    provenance = SemanticProvenanceService(runtime)
    entity = provenance.record_entity_version(
        "explicit-origin-ofac-document",
        entity_kind="OFFICIAL_DOCUMENT",
        canonical_name="Explicit OFAC underlying document",
        source_id="ofac-recent-actions-en",
        canonical_url="https://ofac.treasury.gov/recent-actions/example",
        language="en",
        metadata={"resolution_method": "TEST_EXPLICIT_EVIDENCE"},
        created_at=NOW,
    )
    provenance.record_claim_role_version(
        role_id,
        semantic_claim_version_id=claim_version_id,
        provenance_entity_version_id=entity.provenance_entity_version_id,
        provenance_role="UNDERLYING_ORIGIN",
        attribution_state="OBSERVED",
        note="Explicit provenance evidence, not publisher inference.",
        created_at=NOW,
    )
    result = _observe(runtime)
    assert result.resolved_underlying_origin_count == 1
    assert result.unresolved_underlying_origin_count == 0
    assert result.semantic_independence_assessment_count == 0
    assert result.grants_independence_credit is False


def test_empty_analysis_run_id_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    observer = UnderlyingOriginResolutionObserver(runtime, trusted_first_party_hosts={})
    try:
        observer.observe_analysis_run(" ")
    except ValueError as exc:
        assert "analysis_run_id" in str(exc)
    else:
        raise AssertionError("empty analysis_run_id must fail closed")
