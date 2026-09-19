import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"docs/evidence/P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_2026-09-19.json"
STATE=ROOT/"docs/state/CURRENT_PROJECT_STATE.json"
RESULT=ROOT/"docs/implementation/P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_RESULT.md"

def _json(p): return json.loads(p.read_text(encoding="utf-8"))

def test_p22_6_measures_zero_downstream_uplift_without_positive_promotion():
    x=_json(E)
    assert x["exact_p22_5_cohort"]["canonical_semantic_claim_count"]==28
    assert x["contradiction_observation"]["semantic_contradiction_version_count"]==0
    assert x["contradiction_observation"]["positive_consistency_claim"] is False
    assert x["analytical_coverage_observation"]["underlying_event_analytical_claim_count"]==0
    assert x["forecast_input_observation"]["forecast_version_input_count"]==0
    assert x["impact_summary"]["downstream_intelligence_uplift"]=="NOT_OBSERVED"
    assert x["independence"]["automatic_factual_independence_credit"]==0
    assert x["verification_authority"]=="P13.5/P13.6"

def test_p22_6_state_opens_only_p22_7_and_preserves_runtime_boundaries():
    s=_json(STATE)
    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 57
    assert s["roadmap"]["current_position"].startswith("PHASE_22_")
    assert s["phase22"]["p22_6_state"]=="VALIDATED_WITH_NO_DOWNSTREAM_UPLIFT_OBSERVED"
    assert s["phase22"]["next_gate"] in {"P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED", "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"}
    assert s["phase22"]["persistent_owner_operation"]=="NOT_ACTIVATED"
    assert s["runtime"]["production_live"]=="NOT_OPERATIONAL"
    assert RESULT.exists()