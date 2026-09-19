import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_PLAN.md"
RESULT = ROOT / "docs/implementation/P21_6_INTELLIGENCE_QUALITY_IMPACT_RESULT.md"
EVIDENCE = ROOT / "docs/evidence/P21_6_INTELLIGENCE_QUALITY_IMPACT_2026-09-17.json"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED.md"


def test_p21_6_formal_closure_state_is_converged():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase21_p21_6"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 44
    assert "P21.6" in s["phase21"]["validated_sequence"]
    assert s["phase21_p21_6"]["next_gate"] == "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED"

    assert x["state"] == "VALIDATED_WITH_STRUCTURAL_IMPACT_ONLY"
    assert x["gate"] == "P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED"
    assert x["implementation_merge_anchor"] == "c7a29377457b338d8ddc55f7e989dd13557f36b7"
    assert x["implementation_pr"] == 127
    assert x["validation_run_id"] == 35437681811
    assert x["validation_job_id"] == 105883018288
    assert x["test_count"] == 1305
    assert x["exact_cohort_cell_count"] == 2
    assert x["governed_source_path_delta"] == 2
    assert x["healthy_fresh_source_path_delta"] == 1
    assert x["confirmed_independent_origin_lower_bound_delta"] == 1
    assert x["automatic_factual_independence_credit_delta"] == 0
    assert x["adequate_cell_delta"] == 0
    assert x["missing_required_cell_delta"] == -1
    assert x["verification_yield_impact"] == "NOT_OBSERVED"
    assert x["contradiction_workload_impact"] == "NOT_OBSERVED"
    assert x["forecast_input_impact"] == "NOT_OBSERVED"
    assert x["p21_7_state"] == "READY_TO_BEGIN"


def test_p21_6_closure_preserves_truth_runtime_and_future_wave_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    result = RESULT.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")

    assert CHECKPOINT.exists()
    assert evidence["summary"]["adequate_cell_delta"] == 0
    assert evidence["summary"]["missing_required_cell_delta"] == -1
    assert evidence["downstream_intelligence_quality"]["semantic_post_wave_a_corpus_observed"] is False
    assert evidence["downstream_intelligence_quality"]["verification_yield_impact"] == "NOT_OBSERVED"
    assert evidence["principles"]["verification_authority"] == "P13.5/P13.6"
    assert evidence["principles"]["automatic_independence_credit_from_wave_a"] is False

    assert "1305 passed in 89.63s / SUCCESS" in result
    assert "P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED" in roadmap
    assert "P21.6 intelligence quality impact validation" in handoff
    assert "### P21.7 — Phase Acceptance" in plan

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert s["phase21_p21_6"]["runtime_deployment"] is False
    assert s["phase21_p21_6"]["service_restart"] is False
    assert s["phase21_p21_6"]["paid_or_shared_resources_authorized"] is False
    assert s["phase21_p21_6"]["future_source_waves_authorized"] is False
