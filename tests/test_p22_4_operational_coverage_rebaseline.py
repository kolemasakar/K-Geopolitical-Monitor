import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/evidence/P22_4_OPERATIONAL_COVERAGE_REBASELINE_2026-09-19.json"
RESULT=ROOT/"docs/implementation/P22_4_OPERATIONAL_COVERAGE_REBASELINE_RESULT.md"
CHECKPOINT=ROOT/"docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED.md"
STATE=ROOT/"docs/state/CURRENT_PROJECT_STATE.json"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_4_rebaseline_has_exact_fail_closed_structural_delta():
    x=_json(REPORT)
    assert x["pre_b1_post_wave_a"]["status_counts"] == {
        "ADEQUATE":1,
        "DEGRADED_COLLECTION":2,
        "MISSING_EXPECTED_COVERAGE":20,
        "THIN":10,
    }
    assert x["post_b1"]["status_counts"] == {
        "ADEQUATE":1,
        "DEGRADED_COLLECTION":4,
        "MISSING_EXPECTED_COVERAGE":18,
        "THIN":10,
    }
    assert x["post_b1"]["required_status_counts"] == {
        "ADEQUATE":1,
        "DEGRADED_COLLECTION":3,
        "MISSING_EXPECTED_COVERAGE":18,
        "THIN":5,
    }
    assert x["structural_impact"]["required_missing_cell_delta"] == -2
    assert x["structural_impact"]["adequate_cell_delta"] == 0


def test_p22_4_changed_cells_do_not_receive_unobserved_freshness_or_truth_credit():
    x=_json(REPORT)
    by={c["cell_id"]:c for c in x["changed_cells"]}
    assert set(by)=={"global.en.sanctions_regulatory","united_states.en.official_government"}
    assert all(c["status"]=="DEGRADED_COLLECTION" for c in by.values())
    assert all(c["content_freshness_credited_source_ids"]==[] for c in by.values())
    assert x["structural_impact"]["healthy_fresh_path_delta"] == 0
    assert x["structural_impact"]["automatic_factual_independence_credit_delta"] == 0
    assert x["verification_authority"] == "P13.5/P13.6"


def test_p22_4_keeps_blockers_and_runtime_boundaries_explicit():
    x=_json(REPORT)
    assert x["unchanged_blocker_cells"] == [{
        "cell_id":"russia.ru.official_government",
        "status":"MISSING_EXPECTED_COVERAGE",
        "blocked_candidate":"russian-government-news-ru",
        "blocker":"TRANSPORT_TIMEOUT",
    }]
    b=x["safety_boundary"]
    assert b["persistent_owner_operation"]=="NOT_ACTIVATED"
    assert b["runtime_deployment"] is False
    assert b["service_restart"] is False
    assert b["production_live"]=="NOT_OPERATIONAL"
    assert b["migration_033"]=="NOT_CREATED / NOT_PREAUTHORIZED"


def test_p22_4_canonical_state_opens_only_p22_5():
    s=_json(STATE)
    x=s["phase22"]
    p=s["phase22_p22_4"]
    assert s["roadmap"]["state_sync_version"]=="4.54"
    assert s["roadmap"]["current_position"]=="PHASE_22_P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED"
    assert x["p22_4_state"]=="VALIDATED_WITH_MEASURED_DEGRADATION"
    assert x["next_gate"]=="P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED"
    assert p["required_missing_expected_coverage_count"]==18
    assert p["required_degraded_collection_count"]==3
    assert p["adequate_count"]==1
    assert RESULT.exists() and CHECKPOINT.exists()
