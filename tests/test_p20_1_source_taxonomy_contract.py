from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
RECONCILIATION_PATH = ROOT / "docs" / "evidence" / "P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json"
SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_1_source_record.schema.json"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p20_1_all_p20_0_sources_have_exactly_one_type_mapping():
    baseline = _json(BASELINE_PATH)
    reconciliation = _json(RECONCILIATION_PATH)
    baseline_ids = {item["source_id"] for item in baseline["sources"]}
    mapping = reconciliation["source_type_mapping"]
    mapped_ids = [item["source_id"] for item in mapping]

    assert len(baseline_ids) == 10
    assert len(mapping) == 10
    assert len(mapped_ids) == len(set(mapped_ids))
    assert set(mapped_ids) == baseline_ids


def test_p20_1_source_types_are_allowed_by_contract():
    reconciliation = _json(RECONCILIATION_PATH)
    schema = _json(SCHEMA_PATH)
    allowed = set(schema["properties"]["source_type"]["enum"])

    assert {item["source_type"] for item in reconciliation["source_type_mapping"]} <= allowed


def test_p20_1_all_current_adapters_have_explicit_collection_method_mapping():
    baseline = _json(BASELINE_PATH)
    reconciliation = _json(RECONCILIATION_PATH)
    adapter_ids = {item["adapter_id"] for item in baseline["sources"]}
    method_mapping = reconciliation["collection_method_mapping"]
    schema = _json(SCHEMA_PATH)
    allowed_methods = set(schema["properties"]["collection_method"]["enum"])

    assert set(method_mapping) == adapter_ids
    assert set(method_mapping.values()) <= allowed_methods


def test_p20_1_preserves_multi_value_region_and_language_semantics():
    baseline = _json(BASELINE_PATH)
    schema = _json(SCHEMA_PATH)
    rules = {
        item["p20_field"]: item["rule"]
        for item in _json(RECONCILIATION_PATH)["field_reconciliation"]
    }

    assert any(len(item["region_scope"]) > 1 for item in baseline["sources"])
    assert schema["properties"]["languages"]["type"] == "array"
    assert schema["properties"]["geography"]["properties"]["legacy_region_scope"]["type"] == "array"
    assert rules["geography.legacy_region_scope"] == "PRESERVE_MULTI_VALUE_NO_GEOPOLITICAL_INFERENCE"
    assert rules["languages"] == "PRESERVE_MULTI_VALUE"


def test_p20_1_unknown_semantic_fields_are_nullable_and_not_inferred():
    schema = _json(SCHEMA_PATH)
    reconciliation = _json(RECONCILIATION_PATH)
    rules = {
        item["p20_field"]: item["rule"]
        for item in reconciliation["field_reconciliation"]
    }

    assert "null" in schema["properties"]["reliability_class"]["type"]
    assert "null" in schema["properties"]["origin_group_id"]["type"]
    assert "null" in schema["properties"]["syndication_or_copy_relation"]["type"]
    assert "null" in schema["properties"]["active_for_coverage"]["type"]
    assert rules["reliability_class"] == "NULL_UNTIL_EXPLICITLY_GOVERNED"
    assert rules["origin_group_id"] == "NULL_UNLESS_EXPLICIT_ORIGIN_EVIDENCE_EXISTS"
    assert rules["syndication_or_copy_relation"] == "NULL_UNLESS_EXPLICIT_PROVENANCE_EVIDENCE_EXISTS"
    assert rules["active_for_coverage"] == "NULL_UNTIL_P20_2_COVERAGE_POLICY"


def test_p20_1_does_not_equate_active_governance_with_health_or_coverage_policy():
    reconciliation = _json(RECONCILIATION_PATH)
    rules = {
        item["p20_field"]: item["rule"]
        for item in reconciliation["field_reconciliation"]
    }

    assert rules["health_status"] == "ACTIVE_TO_UNKNOWN_HEALTH_DEGRADED_TO_DEGRADED"
    assert rules["collection_status"] == "UNKNOWN_UNTIL_EXPLICIT_COLLECTION_LIFECYCLE_METADATA"
    assert rules["active_for_coverage"] == "NULL_UNTIL_P20_2_COVERAGE_POLICY"


def test_p20_1_preserves_haberturk_historical_endpoint_drift():
    baseline = _json(BASELINE_PATH)
    reconciliation = _json(RECONCILIATION_PATH)
    haberturk = next(item for item in baseline["sources"] if item["source_id"] == "haberturk-tr")
    historical = reconciliation["historical_reconciliation"]

    assert haberturk["outbound_domains"] == ["www.haberturk.com"]
    assert historical == [
        {
            "source_id": "haberturk-tr",
            "canonical_current_endpoint": "www.haberturk.com",
            "historical_endpoint_aliases": ["rss.haberturk.com"],
            "rule": "PRESERVE_HISTORICAL_MEASUREMENT_AS_ALIAS_DO_NOT_REWRITE_P12_5",
        }
    ]


def test_p20_1_preserves_epistemic_boundaries_and_runtime_safety():
    reconciliation = _json(RECONCILIATION_PATH)
    principles = reconciliation["principles"]
    safety = reconciliation["safety_boundary"]

    assert all(principles.values())
    assert safety["live_source_expansion"] is False
    assert safety["live_ingest_change"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
