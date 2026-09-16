from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_health_egress import install_phase12_health_probe_governance


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
REUSE_MAP_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_REUSE_MAP_2026-09-16.json"
P12_5_MATRIX_PATH = ROOT / "docs" / "implementation" / "P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _runtime_records(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    return install_phase12_health_probe_governance(
        runtime,
        reviewed_at=datetime(2026, 9, 16, tzinfo=timezone.utc),
    )


def _record_payload(record) -> dict:
    return {
        "source_id": record.source_id,
        "source_name": record.source_name,
        "source_class": record.source_class,
        "source_role": record.source_role,
        "region_scope": list(record.region_scope),
        "language_scope": list(record.language_scope),
        "expected_freshness_minutes": record.expected_freshness_minutes,
        "collection_cadence_minutes": record.collection_cadence_minutes,
        "adapter_id": record.adapter_id,
        "outbound_domains": list(record.outbound_domains),
        "availability_state": record.availability_state,
    }


def test_p20_0_machine_baseline_matches_existing_governed_source_network(tmp_path):
    baseline = _json(BASELINE_PATH)
    records = sorted(_runtime_records(tmp_path), key=lambda item: item.source_id)
    expected = sorted(baseline["sources"], key=lambda item: item["source_id"])

    assert baseline["schema_version"] == "kgm.p20.0.existing_coverage_baseline.v1"
    assert baseline["source_count"] == 10
    assert len(records) == 10
    assert [_record_payload(record) for record in records] == expected


def test_p20_0_preserves_public_free_nonpaid_governance_boundaries(tmp_path):
    records = _runtime_records(tmp_path)

    assert sum(record.availability_state == "ACTIVE" for record in records) == 9
    assert sum(record.availability_state == "DEGRADED" for record in records) == 1
    assert all(record.access_mode == "PUBLIC_ANONYMOUS" for record in records)
    assert all(record.cost_mode == "FREE" for record in records)
    assert all(record.data_classification == "PUBLIC" for record in records)
    assert all(record.review_status == "APPROVED" for record in records)
    assert all(record.paid_provider_approved is False for record in records)


def test_p20_0_does_not_infer_independent_origins_or_coverage_eligibility():
    baseline = _json(BASELINE_PATH)
    reuse_map = _json(REUSE_MAP_PATH)
    field_status = {item["p20_field"]: item["status"] for item in reuse_map["field_reuse"]}

    assert baseline["independent_origin_count"] is None
    assert field_status["origin_group_id"] == "MISSING_CANONICAL"
    assert field_status["syndication_or_copy_relation"] == "MISSING_CANONICAL"
    assert field_status["active_for_coverage"] == "NEW_P20_POLICY_FIELD"
    assert field_status["source_type"] == "P20_1_MAPPING_REQUIRED"


def test_p20_0_reuses_existing_coverage_health_and_recovery_components():
    reuse_map = _json(REUSE_MAP_PATH)
    component_status = {
        item["component"]: item["status"] for item in reuse_map["component_reuse"]
    }

    assert component_status["source_portfolio"] == "REUSE_PRIMARY"
    assert component_status["adapter_framework"] == "REUSE_PRIMARY"
    assert component_status["source_health_egress"] == "REUSE_PRIMARY"
    assert component_status["operational_coverage"] == "REUSE_PRIMARY"
    assert component_status["region_language_coverage"] == "REUSE_PARTIAL"
    assert component_status["recovery_coverage"] == "REUSE_PRIMARY"
    assert component_status["semantic_provenance"] == "REUSE_FOR_ORIGIN_EVIDENCE_ONLY"
    assert component_status["draft_pr_78"] == "REFERENCE_ONLY_STALE"


def test_p20_0_keeps_haberturk_historical_domain_drift_explicit():
    baseline = _json(BASELINE_PATH)
    historical_matrix = P12_5_MATRIX_PATH.read_text(encoding="utf-8")
    current = next(item for item in baseline["sources"] if item["source_id"] == "haberturk-tr")
    reconciliation = baseline["historical_reconciliation_items"]

    assert current["outbound_domains"] == ["www.haberturk.com"]
    assert "rss.haberturk.com" in historical_matrix
    assert reconciliation == [
        {
            "source_id": "haberturk-tr",
            "kind": "DOMAIN_MEASUREMENT_DRIFT",
            "current_governed_domain": "www.haberturk.com",
            "historical_p12_5_matrix_domain": "rss.haberturk.com",
            "disposition": "KEEP_EXPLICIT_FOR_P20_1_METADATA_RECONCILIATION",
        }
    ]


def test_p20_0_does_not_allocate_migration_033_or_live_expansion():
    baseline = _json(BASELINE_PATH)
    conclusions = _json(REUSE_MAP_PATH)["p20_0_conclusions"]

    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
    assert baseline["safety_boundary"]["live_source_expansion"] is False
    assert baseline["safety_boundary"]["live_ingest_change"] is False
    assert baseline["safety_boundary"]["runtime_deployment"] is False
    assert baseline["safety_boundary"]["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert conclusions["new_live_collection_required"] is False
    assert conclusions["new_database_migration_required"] is False
    assert conclusions["new_paid_resource_required"] is False
    assert conclusions["source_level_independence_currently_measurable"] is False
    assert conclusions["next_gate"] == "P20_1_SOURCE_TAXONOMY_METADATA_CONTRACT_VALIDATED"
