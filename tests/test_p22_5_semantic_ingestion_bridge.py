from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.semantic_ingestion_bridge import (
    CanonicalSemanticIngestionBridge,
)
from kgeopolitical_monitor.semantic_live_compatibility import (
    SemanticLiveCompatibilityService,
)

NOW = datetime(2026, 9, 19, 16, 30, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path / "project")


def _seed(runtime, *, source_id="ofac-recent-actions-en", legacy_status="VERIFIED"):
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            "INSERT INTO sources(id,name,source_class,reliability) VALUES (?,?,?,?)",
            (source_id, "U.S. Treasury OFAC", "Official sources", "official"),
        )
        connection.execute(
            """
            INSERT INTO raw_items(id,source_id,title,content,collected_at)
            VALUES (?,?,?,?,?)
            """,
            (
                "raw-1",
                source_id,
                "Designation action title",
                "Observed source body",
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_runs(
                analysis_run_id,collection_id,watch_id,status,
                claim_count,finding_count,created_at
            ) VALUES (?,?,?,?,?,?,?)
            """,
            (
                "run-1",
                "collection-1",
                "watch-1",
                "COMPLETED",
                1,
                1,
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id,analysis_run_id,claim_key,title,verification_status,
                confidence,importance,independent_origin_count,source_class_count,
                origins_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                "live-1",
                "run-1",
                "legacy-title-key",
                "Designation action title",
                legacy_status,
                0.99,
                0.9,
                9,
                4,
                '["ofac.treasury.gov"]',
            ),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_evidence(
                claim_id,raw_item_id,original_url,origin_host
            ) VALUES (?,?,?,?)
            """,
            (
                "live-1",
                "raw-1",
                "https://ofac.treasury.gov/recent-actions/example",
                "ofac.treasury.gov",
            ),
        )


def _bridge(runtime, *, allowed=("ofac-recent-actions-en",)):
    return CanonicalSemanticIngestionBridge(
        runtime,
        allowed_source_ids=allowed,
        source_languages={source_id: "en" for source_id in allowed},
    )


def _table_count(runtime, table):
    with sqlite3.connect(runtime.database_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_bridge_creates_p13_publication_attribution_only(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    result = _bridge(runtime).ingest_analysis_run("run-1", created_at=NOW)

    assert result.observed_raw_item_count == 1
    assert result.created_claim_count == 1
    assert result.existing_claim_count == 0
    assert result.semantic_claim_version_count == 1
    assert result.semantic_evidence_relation_count == 1
    assert result.semantic_verification_decision_count == 1
    assert result.verification_state_counts == {"DETECTED": 1}
    assert result.creates_underlying_fact_claims is False
    assert result.imports_legacy_verification is False
    assert result.grants_independence is False

    with sqlite3.connect(runtime.database_path) as connection:
        claim = connection.execute(
            """
            SELECT normalized_proposition,event_action_type,extraction_method
            FROM semantic_claim_versions
            """
        ).fetchone()
        assert claim[0].startswith("U.S. Treasury OFAC published material titled")
        assert claim[1] == "PUBLICATION"
        assert claim[2] == "PUBLICATION_ATTRIBUTION_BRIDGE"

        relation = connection.execute(
            """
            SELECT relation_type
            FROM semantic_evidence_relation_versions
            """
        ).fetchone()
        assert relation[0] == "ATTRIBUTION_ONLY"

        roles = connection.execute(
            """
            SELECT provenance_role,attribution_state
            FROM semantic_claim_provenance_role_versions
            ORDER BY provenance_role
            """
        ).fetchall()
        assert ("UNDERLYING_ORIGIN", "UNRESOLVED") in roles
        assert ("PUBLICATION", "OBSERVED") in roles
        assert ("PUBLISHER", "OBSERVED") in roles

        independence = connection.execute(
            "SELECT COUNT(*) FROM semantic_independence_assessment_versions"
        ).fetchone()[0]
        assert independence == 0
def test_legacy_verified_and_confidence_do_not_promote_canonical_state(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime, legacy_status="VERIFIED")
    _bridge(runtime).ingest_analysis_run("run-1", created_at=NOW)

    projection = SemanticLiveCompatibilityService(runtime).project("live-1")
    assert projection.compatibility_state == "LINKED_WITH_DECISION"
    assert projection.legacy.legacy_verification_status == "VERIFIED"
    assert projection.legacy.legacy_confidence == 0.99
    assert projection.semantic_verification_state == "DETECTED"
    assert projection.legacy_status_promoted is False
    assert projection.legacy_confidence_promoted is False
    assert projection.legacy_origin_count_establishes_independence is False


def test_bridge_is_idempotent_for_already_complete_items(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime)
    bridge = _bridge(runtime)

    first = bridge.ingest_analysis_run("run-1", created_at=NOW)
    second = bridge.ingest_analysis_run("run-1", created_at=NOW)

    assert first.created_claim_count == 1
    assert second.created_claim_count == 0
    assert second.existing_claim_count == 1
    assert _table_count(runtime, "semantic_claim_versions") == 1
    assert _table_count(runtime, "semantic_claim_provenance_role_versions") == 3
    assert _table_count(runtime, "semantic_evidence_relation_versions") == 1
    assert _table_count(runtime, "semantic_factual_confidence_versions") == 1
    assert _table_count(runtime, "semantic_verification_decision_versions") == 1
def test_bridge_rejects_non_authorized_sources_fail_closed(tmp_path):
    runtime = _runtime(tmp_path)
    _seed(runtime, source_id="unexpected-source")
    bridge = _bridge(runtime)

    with pytest.raises(ValueError, match="not authorized"):
        bridge.ingest_analysis_run("run-1", created_at=NOW)

    assert _table_count(runtime, "semantic_claim_versions") == 0
    assert _table_count(runtime, "semantic_verification_decision_versions") == 0


def test_bridge_requires_explicit_language_for_every_authorized_source(tmp_path):
    runtime = _runtime(tmp_path)
    with pytest.raises(ValueError, match="missing source language"):
        CanonicalSemanticIngestionBridge(
            runtime,
            allowed_source_ids=["ofac-recent-actions-en"],
            source_languages={},
        )