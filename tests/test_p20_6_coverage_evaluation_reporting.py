from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P20_2_MATRIX = ROOT / "docs" / "evidence" / "P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json"
P20_3_BASELINE = ROOT / "docs" / "evidence" / "P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json"
P20_4_BASELINE = ROOT / "docs" / "evidence" / "P20_4_CURRENT_COLLECTION_HEALTH_BASELINE_2026-09-16.json"
P20_6_SCHEMA = ROOT / "docs" / "contracts" / "p20_6_coverage_report.schema.json"
P20_6_REPORT = ROOT / "docs" / "evidence" / "P20_6_COVERAGE_REPORT_2026-09-16.json"
P20_6_OPERATOR = ROOT / "docs" / "evidence" / "P20_6_COVERAGE_REPORT_2026-09-16.md"
P20_6_MODEL = ROOT / "docs" / "implementation" / "P20_6_COVERAGE_EVALUATION_REPORTING.md"
P20_6_FIXTURE = ROOT / "tests" / "fixtures" / "p20" / "p20_6_reporting_synthetic.json"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate(case: dict) -> str:
    if case["policy_state"] != "DECLARED":
        return "UNKNOWN"
    if case["requirement"] == "NOT_REQUIRED":
        return "NOT_REQUIRED_BY_POLICY"
    if case["requirement"] == "REQUIRED" and case["source_count"] == 0:
        return "MISSING_EXPECTED_COVERAGE"
    if case["health_state"] == "CURRENT_DEGRADED":
        return "DEGRADED_COLLECTION"
    if case["health_state"] != "CURRENT_HEALTHY":
        return "UNKNOWN"
    if case["independent_origin_count"] is None or case["monoculture_risk"] is None:
        return "UNKNOWN"
    if case["monoculture_risk"]:
        return "MONOCULTURE_RISK"
    if case["minimum_source_count"] is None or case["minimum_independent_origin_count"] is None:
        return "UNKNOWN"
    if (
        case["source_count"] >= case["minimum_source_count"]
        and case["independent_origin_count"] >= case["minimum_independent_origin_count"]
    ):
        return "ADEQUATE"
    return "THIN"


def test_p20_6_current_report_reproduces_all_p20_2_observed_cells_without_reclassification():
    matrix = _json(P20_2_MATRIX)
    report = _json(P20_6_REPORT)

    matrix_by_id = {cell["cell_id"]: cell for cell in matrix["cells"]}
    report_by_id = {cell["cell_id"]: cell for cell in report["cells"]}

    assert matrix["cell_count"] == 17
    assert report["global_summary"]["observed_cell_count"] == 17
    assert set(report_by_id) == set(matrix_by_id)
    for cell_id, cell in report_by_id.items():
        source = matrix_by_id[cell_id]
        assert cell["geography_scope"] == source["geography_scope"]
        assert cell["language"] == source["language"]
        assert cell["source_type"] == source["source_type"]
        assert cell["governed_source_count"] == source["governed_source_count"]
        assert cell["status"] == "UNKNOWN"
        assert cell["independent_origin_count"] is None
        assert cell["healthy_source_count"] is None
        assert cell["stale_or_failed_source_count"] is None
        assert set(cell["reason_codes"]) == {
            "POLICY_UNSET",
            "INDEPENDENCE_UNKNOWN",
            "HEALTH_UNMEASURED",
        }


def test_p20_6_current_summary_is_fail_closed_and_composes_p20_3_p20_4_inputs():
    independence = _json(P20_3_BASELINE)
    health = _json(P20_4_BASELINE)
    report = _json(P20_6_REPORT)
    summary = report["global_summary"]

    assert independence["source_count"] == 10
    assert independence["known_origin_source_count"] == 0
    assert health["source_count"] == 10
    assert health["measured_source_count"] == 0
    assert summary["governed_source_count"] == 10
    assert summary["known_origin_source_count"] == 0
    assert summary["measured_source_count"] == 0
    assert summary["adequate_count"] == 0
    assert summary["thin_count"] == 0
    assert summary["monoculture_risk_count"] == 0
    assert summary["degraded_collection_count"] == 0
    assert summary["missing_expected_coverage_count"] == 0
    assert summary["not_required_count"] == 0
    assert summary["unknown_count"] == 17


def test_p20_6_required_report_sections_are_explicit_not_empty_array_inference():
    sections = _json(P20_6_REPORT)["report_sections"]
    assert set(sections) == {
        "region_gaps",
        "language_gaps",
        "source_type_gaps",
        "monoculture_warnings",
        "stale_or_failed_sources",
        "latency_outliers",
        "missing_expected_sources",
    }
    assert sections["region_gaps"]["state"] == "UNKNOWN"
    assert sections["language_gaps"]["state"] == "UNKNOWN"
    assert sections["source_type_gaps"]["state"] == "UNKNOWN"
    assert sections["monoculture_warnings"]["state"] == "UNKNOWN"
    assert sections["stale_or_failed_sources"]["state"] == "UNKNOWN"
    assert sections["latency_outliers"]["state"] == "UNKNOWN"
    assert sections["missing_expected_sources"]["state"] == "UNKNOWN"
    assert all(section["items"] == [] for section in sections.values())


def test_p20_6_synthetic_status_precedence_is_deterministic():
    fixture = _json(P20_6_FIXTURE)
    assert fixture["schema_version"] == "kgm.p20.6.reporting.synthetic.v1"
    assert len(fixture["cases"]) == 9
    for case in fixture["cases"]:
        assert _evaluate(case) == case["expected_status"], case["case_id"]


def test_p20_6_unknown_is_not_gap_and_not_adequate():
    cases = {case["case_id"]: case for case in _json(P20_6_FIXTURE)["cases"]}
    for case_id in ("policy-unset", "unknown-origin", "unmeasured-health"):
        status = _evaluate(cases[case_id])
        assert status == "UNKNOWN"
        assert status not in {"ADEQUATE", "MISSING_EXPECTED_COVERAGE"}


def test_p20_6_schema_preserves_nullable_evidence_and_explainable_statuses():
    schema = _json(P20_6_SCHEMA)
    cell = schema["$defs"]["coverageCell"]["properties"]
    statuses = set(cell["status"]["enum"])

    assert "null" in cell["independent_origin_count"]["type"]
    assert "null" in cell["healthy_source_count"]["type"]
    assert "null" in cell["stale_or_failed_source_count"]["type"]
    assert statuses == {
        "ADEQUATE",
        "THIN",
        "MONOCULTURE_RISK",
        "DEGRADED_COLLECTION",
        "MISSING_EXPECTED_COVERAGE",
        "NOT_REQUIRED_BY_POLICY",
        "UNKNOWN",
    }
    assert cell["reason_codes"]["minItems"] == 1


def test_p20_6_first_report_does_not_reconstruct_uninstrumented_change_history():
    report = _json(P20_6_REPORT)
    assert report["input_refs"]["previous_report"] is None
    assert report["changes_since_previous_report"] == {
        "state": "NO_PREVIOUS_REPORT",
        "changes": [],
    }


def test_p20_6_operator_and_machine_reports_expose_same_current_control_facts():
    operator = P20_6_OPERATOR.read_text(encoding="utf-8")
    model = P20_6_MODEL.read_text(encoding="utf-8")

    assert "Observed coverage cells | 17" in operator
    assert "Governed sources | 10" in operator
    assert "Unknown cells | 17" in operator
    assert "target policy: `UNSET`" in operator
    assert "source-origin evidence: `UNKNOWN`" in operator
    assert "fresh collection-health evidence persisted in canonical repository: `UNMEASURED`" in operator
    assert "UNKNOWN is distinct from both a confirmed gap and adequate coverage" in model
    assert "P13.5/P13.6 remain the current factual-verification authority" in model


def test_p20_6_preserves_runtime_resource_and_migration_boundaries():
    safety = _json(P20_6_REPORT)["safety_boundary"]
    assert safety["runtime_deployment"] is False
    assert safety["live_source_expansion"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
