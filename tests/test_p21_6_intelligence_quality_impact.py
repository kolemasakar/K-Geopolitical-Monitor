from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "p21_6_intelligence_quality_impact.py"
REPORT = ROOT / "docs" / "evidence" / "P21_6_INTELLIGENCE_QUALITY_IMPACT_2026-09-17.json"

SPEC = importlib.util.spec_from_file_location("p21_6_intelligence_quality_impact", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
p21_6 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p21_6)


def _report() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def _cells() -> dict[str, dict]:
    return {cell["cell_id"]: cell for cell in _report()["cells"]}


def test_p21_6_checked_in_evidence_is_exact_deterministic_builder_output():
    assert p21_6.build_report(ROOT) == _report()


def test_p21_6_cohort_is_exactly_wave_a_two_cells_and_two_sources():
    cohort = _report()["cohort"]
    assert cohort["basis"] == "EXACT_P21_5_WAVE_A_REPOSITORY_ACTIVE_POLICY_CELLS"
    assert cohort["cell_count"] == 2
    assert cohort["source_count"] == 2
    assert cohort["cell_ids"] == [
        "ukraine.uk.national_media",
        "ukraine.uk.official_government",
    ]
    assert cohort["source_ids"] == ["suspilne-uk", "ukraine-government-kmu-uk"]


def test_p21_6_structural_source_and_health_deltas_are_measured_not_inferred():
    summary = _report()["summary"]
    assert summary["governed_source_path_delta"] == 2
    assert summary["healthy_fresh_source_path_delta"] == 1
    assert summary["confirmed_independent_origin_lower_bound_delta"] == 1


def test_p21_6_exact_cohort_status_counts_match_pre_post_overlay():
    summary = _report()["summary"]
    assert summary["pre_status_counts"] == {
        "MISSING_EXPECTED_COVERAGE": 1,
        "THIN": 1,
    }
    assert summary["post_status_counts"] == {
        "DEGRADED_COLLECTION": 1,
        "THIN": 1,
    }
    assert summary["adequate_cell_delta"] == 0
    assert summary["missing_required_cell_delta"] == -1


def test_p21_6_national_media_reaches_source_and_health_thresholds_but_stays_thin():
    cell = _cells()["ukraine.uk.national_media"]
    assert cell["pre"]["status"] == "THIN"
    assert cell["post"]["status"] == "THIN"
    assert cell["post"]["governed_source_count"] == 2
    assert cell["post"]["healthy_fresh_source_count"] == 2
    assert cell["post"]["confirmed_independent_origin_lower_bound"] == 0
    assert "INDEPENDENT_ORIGIN_LOWER_BOUND_BELOW_MINIMUM" in cell["post"]["reason_codes"]


def test_p21_6_official_government_moves_missing_to_degraded_due_stale_content():
    cell = _cells()["ukraine.uk.official_government"]
    assert cell["pre"]["status"] == "MISSING_EXPECTED_COVERAGE"
    assert cell["post"]["status"] == "DEGRADED_COLLECTION"
    assert cell["post"]["governed_source_count"] == 1
    assert cell["post"]["healthy_fresh_source_count"] == 0
    assert cell["post"]["stale_or_failed_source_ids"] == ["ukraine-government-kmu-uk"]
    assert cell["post"]["reason_codes"] == ["HEALTH_OR_FRESHNESS_THRESHOLD_NOT_MET"]


def test_p21_6_kmu_adds_source_topology_origin_lower_bound_not_claim_independence_credit():
    report = _report()
    official = _cells()["ukraine.uk.official_government"]
    assert official["post"]["known_origin_groups"] == [
        "official:cabinet-of-ministers-ukraine"
    ]
    assert official["post"]["confirmed_independent_origin_lower_bound"] == 1
    assert report["summary"]["automatic_factual_independence_credit_delta"] == 0
    assert report["principles"]["source_level_origin_group_is_topology_evidence_not_claim_truth"] is True
    assert report["principles"]["automatic_independence_credit_from_wave_a"] is False


def test_p21_6_portfolio_projection_changes_missing_to_degraded_without_adequacy_gain():
    summary = _report()["summary"]
    assert summary["portfolio_pre_status_counts"] == {
        "ADEQUATE": 1,
        "DEGRADED_COLLECTION": 1,
        "MISSING_EXPECTED_COVERAGE": 21,
        "THIN": 10,
    }
    assert summary["portfolio_post_structural_status_counts"] == {
        "ADEQUATE": 1,
        "DEGRADED_COLLECTION": 2,
        "MISSING_EXPECTED_COVERAGE": 20,
        "THIN": 10,
    }


def test_p21_6_downstream_semantic_quality_impacts_remain_not_observed():
    impact = _report()["downstream_intelligence_quality"]
    assert impact["semantic_post_wave_a_corpus_observed"] is False
    assert impact["verification_yield_impact"] == "NOT_OBSERVED"
    assert impact["contradiction_workload_impact"] == "NOT_OBSERVED"
    assert impact["forecast_input_impact"] == "NOT_OBSERVED"


def test_p21_6_preserves_p13_verification_authority_and_fail_closed_semantics():
    principles = _report()["principles"]
    assert principles["verification_authority"] == "P13.5/P13.6"
    assert principles["coverage_health_is_not_truth"] is True
    assert principles["exact_cohort_only"] is True
    assert principles["no_counterfactual_semantic_quality_claim"] is True


def test_p21_6_preserves_runtime_resource_migration_plugin_and_future_wave_boundaries():
    safety = _report()["safety_boundary"]
    assert safety["deployed_runtime_mutated"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["production_live"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert safety["plugin_build"] is False
    assert safety["plugin_publication"] is False
    assert safety["future_source_waves_authorized"] is False
    assert not any(path.name.startswith("033_") for path in (ROOT / "migrations").glob("*.sql"))
