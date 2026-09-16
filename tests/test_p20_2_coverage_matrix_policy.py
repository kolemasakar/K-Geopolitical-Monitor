from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_1_RECONCILIATION_PATH = ROOT / "docs" / "evidence" / "P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json"
P20_1_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_1_source_record.schema.json"
P20_2_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_2_coverage_matrix_policy.schema.json"
MATRIX_PATH = ROOT / "docs" / "evidence" / "P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json"
POLICY_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "p20" / "p20_2_policy_synthetic.json"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _expected_cells() -> list[dict]:
    baseline = _json(BASELINE_PATH)
    reconciliation = _json(P20_1_RECONCILIATION_PATH)
    type_by_source = {
        item["source_id"]: item["source_type"]
        for item in reconciliation["source_type_mapping"]
    }
    aggregates: dict[tuple[str, str, str], dict[str, int]] = defaultdict(
        lambda: {
            "governed_source_count": 0,
            "active_availability_count": 0,
            "degraded_availability_count": 0,
        }
    )

    for source in baseline["sources"]:
        source_type = type_by_source[source["source_id"]]
        for geography_scope in source["region_scope"]:
            for language in source["language_scope"]:
                key = (geography_scope, language, source_type)
                aggregates[key]["governed_source_count"] += 1
                if source["availability_state"] == "ACTIVE":
                    aggregates[key]["active_availability_count"] += 1
                elif source["availability_state"] == "DEGRADED":
                    aggregates[key]["degraded_availability_count"] += 1

    rows = []
    for (geography_scope, language, source_type), counts in sorted(aggregates.items()):
        rows.append(
            {
                "cell_id": f"{geography_scope.lower()}.{language.lower()}.{source_type.lower()}",
                "geography_scope": geography_scope,
                "language": language,
                "source_type": source_type,
                **counts,
                "independent_origin_count": None,
                "coverage_status": "POLICY_UNSET",
            }
        )
    return rows


def test_p20_2_observed_matrix_is_deterministic_from_p20_0_and_p20_1():
    matrix = _json(MATRIX_PATH)
    expected = _expected_cells()

    assert matrix["schema_version"] == "kgm.p20.2.observed_coverage_matrix.v1"
    assert matrix["cell_count"] == 17
    assert len(expected) == 17
    assert matrix["cells"] == expected


def test_p20_2_does_not_treat_source_count_as_independent_origin_count():
    matrix = _json(MATRIX_PATH)

    assert matrix["independent_origin_evaluation"] == "NOT_YET_AVAILABLE_P20_3"
    assert all(cell["independent_origin_count"] is None for cell in matrix["cells"])
    assert any(cell["governed_source_count"] > 1 for cell in matrix["cells"])


def test_p20_2_preserves_policy_unset_as_distinct_from_not_required():
    matrix = _json(MATRIX_PATH)
    policy = _json(POLICY_FIXTURE_PATH)
    schema = _json(P20_2_SCHEMA_PATH)
    allowed = set(schema["properties"]["default_requirement_state"]["enum"])

    assert matrix["policy_state"] == "UNSET"
    assert policy["default_requirement_state"] == "UNSET"
    assert "UNSET" in allowed
    assert "NOT_REQUIRED" in allowed
    assert "UNSET" != "NOT_REQUIRED"


def test_p20_2_target_policy_can_declare_zero_observation_cells_explicitly():
    matrix = _json(MATRIX_PATH)
    policy = _json(POLICY_FIXTURE_PATH)
    observed_ids = {cell["cell_id"] for cell in matrix["cells"]}
    target_ids = {cell["cell_id"] for cell in policy["target_cells"]}

    assert target_ids
    assert target_ids.isdisjoint(observed_ids)
    assert any(cell["requirement_state"] == "REQUIRED" for cell in policy["target_cells"])
    assert any(cell["requirement_state"] == "OPTIONAL" for cell in policy["target_cells"])
    assert "absence from observed cells does not mean NOT_REQUIRED" in matrix["zero_coverage_semantics"]


def test_p20_2_required_synthetic_cell_has_explicit_nonzero_source_target():
    policy = _json(POLICY_FIXTURE_PATH)
    required = next(cell for cell in policy["target_cells"] if cell["requirement_state"] == "REQUIRED")

    assert required["thresholds"]["minimum_source_count"] >= 1
    assert required["thresholds"]["minimum_independent_origin_count"] >= 1
    assert required["policy_reason"]


def test_p20_2_source_type_taxonomy_matches_p20_1_exactly():
    p20_1_schema = _json(P20_1_SCHEMA_PATH)
    p20_2_schema = _json(P20_2_SCHEMA_PATH)
    p20_1_types = p20_1_schema["properties"]["source_type"]["enum"]
    p20_2_types = p20_2_schema["$defs"]["sourceType"]["enum"]

    assert p20_2_types == p20_1_types


def test_p20_2_thresholds_are_configuration_not_global_constants():
    schema = _json(P20_2_SCHEMA_PATH)
    threshold_props = schema["$defs"]["thresholds"]["properties"]

    assert "null" in threshold_props["minimum_source_count"]["type"]
    assert "null" in threshold_props["minimum_independent_origin_count"]["type"]
    assert "null" in threshold_props["minimum_healthy_source_count"]["type"]
    assert "null" in threshold_props["maximum_stale_share"]["type"]
    assert "null" in threshold_props["maximum_dominant_origin_share"]["type"]


def test_p20_2_preserves_runtime_and_resource_boundaries():
    safety = _json(MATRIX_PATH)["safety_boundary"]

    assert safety["live_source_expansion"] is False
    assert safety["live_ingest_change"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
