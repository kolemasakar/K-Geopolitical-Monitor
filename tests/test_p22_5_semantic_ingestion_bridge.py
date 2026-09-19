from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.p22_5_semantic_ingestion_bridge import (
    P225SemanticIngestionBridge,
    P22_5_POLICY_ID,
)
from kgeopolitical_monitor.semantic_live_compatibility import SemanticLiveCompatibilityService


NOW = datetime(2026, 9, 19, 16, 30, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _seed(runtime, *, unsupported=False, duplicate_title=False):
    rows = [
        ("raw-ofac", "ofac-recent-actions-en", "Sanctions action announced", "https://ofac.treasury.gov/recent-actions/x"),
        (
            "raw-wh",
            "white-house-briefings-en" if not unsupported else "other-source",
            "Sanctions action announced" if duplicate_title else "White House statement issued",
            "https://www.whitehouse.gov/briefings-statements/x",
        ),
    ]
    with sqlite3.connect(runtime.database_path) as connection:
        for _, source_id, _, _ in rows:
            connection.execute(
                "INSERT OR IGNORE INTO sources(id,name,source_class,reliability) VALUES (?,?,?,?)",
                (source_id, source_id, "Official sources", "official"),
            )
        for raw_id, source_id, title, _ in rows:
            connection.execute(
                "INSERT INTO raw_items(id,source_id,title,content,collected_at) VALUES (?,?,?,?,?)",
                (raw_id, source_id, title, title, NOW.isoformat()),
            )
        connection.execute(
            """INSERT INTO live_analysis_runs(
                analysis_run_id,collection_id,watch_id,status,claim_count,finding_count,created_at
            ) VALUES ('analysis-1','collection-1','watch-1','COMPLETED',2,2,?)""",
            (NOW.isoformat(),),
        )
        for index, (raw_id, _, title, url) in enumerate(rows, start=1):
            claim_id = f"legacy-live-{index}"
            connection.execute(
                """INSERT INTO live_analysis_claims(
                    claim_id,analysis_run_id,claim_key,title,verification_status,
                    confidence,importance,independent_origin_count,source_class_count,origins_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    claim_id,
                    "analysis-1",
                    f"key-{index}",
                    title,
                    "DETECTED",
                    0.5,
                    0.5,
                    1,
                    1,
                    "[]",
                ),
            )
            connection.execute(
                """INSERT INTO live_analysis_evidence(
                    claim_id,raw_item_id,original_url,origin_host
                ) VALUES (?,?,?,?)""",
                (claim_id, raw_id, url, url.split("/")[2]),
            )
    return "analysis-1"
def _counts(runtime):
    names = (
        "semantic_claim_versions",
        "semantic_claim_links",
        "semantic_provenance_entity_versions",
        "semantic_claim_provenance_role_versions",
        "semantic_evidence_relation_versions",
        "semantic_independence_assessment_versions",
        "semantic_factual_confidence_versions",
        "semantic_verification_decision_versions",
    )
    with sqlite3.connect(runtime.database_path) as connection:
        return {
            name: int(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
            for name in names
        }


def test_bridge_creates_canonical_detected_corpus_without_truth_promotion(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime)
    result = P225SemanticIngestionBridge(runtime).bridge_analysis_run(
        run_id,
        created_at=NOW,
    )

    assert result.claim_count == 2
    assert result.created_count == 2
    assert result.skipped_count == 0
    assert result.evidence_relation_count == 2
    assert result.verification_states == ("DETECTED",)

    counts = _counts(runtime)
    assert counts["semantic_claim_versions"] == 2
    assert counts["semantic_evidence_relation_versions"] == 2
    assert counts["semantic_independence_assessment_versions"] == 0
    assert counts["semantic_factual_confidence_versions"] == 2
    assert counts["semantic_verification_decision_versions"] == 2
    with sqlite3.connect(runtime.database_path) as connection:
        relation_types = {
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT relation_type FROM semantic_evidence_relation_versions"
            )
        }
        states = {
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT verification_state FROM semantic_verification_decision_versions"
            )
        }
        origins = connection.execute(
            """SELECT provenance_role,attribution_state,e.entity_kind
               FROM semantic_claim_provenance_role_versions r
               JOIN semantic_provenance_entity_versions e
                 ON e.provenance_entity_version_id=r.provenance_entity_version_id
               WHERE provenance_role='UNDERLYING_ORIGIN'"""
        ).fetchall()

    assert relation_types == {"ATTRIBUTION_ONLY"}
    assert states == {"DETECTED"}
    assert origins and all(row == ("UNDERLYING_ORIGIN", "UNRESOLVED", "UNKNOWN") for row in origins)


def test_bridge_is_idempotent_after_complete_canonical_decision(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime)
    bridge = P225SemanticIngestionBridge(runtime)

    first = bridge.bridge_analysis_run(run_id, created_at=NOW)
    before = _counts(runtime)
    second = bridge.bridge_analysis_run(run_id, created_at=NOW)
    after = _counts(runtime)

    assert first.created_count == 2
    assert second.created_count == 0
    assert second.skipped_count == 2
    assert before == after
def test_semantic_identity_is_not_headline_identity(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime, duplicate_title=True)
    P225SemanticIngestionBridge(runtime).bridge_analysis_run(run_id, created_at=NOW)

    with sqlite3.connect(runtime.database_path) as connection:
        rows = connection.execute(
            "SELECT semantic_claim_id,normalized_proposition FROM semantic_claim_versions ORDER BY semantic_claim_id"
        ).fetchall()

    assert len(rows) == 2
    assert len({row[0] for row in rows}) == 2
    assert {row[1] for row in rows} == {"Sanctions action announced"}


def test_bridge_rejects_sources_outside_authorized_b1_cohort_before_semantic_write(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime, unsupported=True)

    with pytest.raises(ValueError, match="outside authorized B1 semantic cohort"):
        P225SemanticIngestionBridge(runtime).bridge_analysis_run(run_id, created_at=NOW)

    counts = _counts(runtime)
    assert counts["semantic_claim_versions"] == 0
    assert counts["semantic_verification_decision_versions"] == 0


def test_compatibility_projection_sees_only_canonical_p13_decisions(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime)
    P225SemanticIngestionBridge(runtime).bridge_analysis_run(run_id, created_at=NOW)

    service = SemanticLiveCompatibilityService(runtime)
    projections = service.project_analysis_run(run_id)

    assert len(projections) == 2
    assert all(p.compatibility_state == "LINKED_WITH_DECISION" for p in projections)
    assert all(p.semantic_verification_state == "DETECTED" for p in projections)
    assert all(p.legacy_status_promoted is False for p in projections)
def test_bridge_policy_preserves_default_permanent_invariants(tmp_path):
    runtime = _runtime(tmp_path)
    run_id = _seed(runtime)
    bridge = P225SemanticIngestionBridge(runtime)
    bridge.bridge_analysis_run(run_id, created_at=NOW)

    policy = bridge.verification.policy_current(P22_5_POLICY_ID)
    assert policy is not None
    assert policy.review_status == "APPROVED"
    assert policy.rules["count_only_promotion_forbidden"] is True
    assert policy.rules["official_status_only_promotion_forbidden"] is True
    assert policy.rules["verified_requires_explicit_independent_support_pair"] is True
