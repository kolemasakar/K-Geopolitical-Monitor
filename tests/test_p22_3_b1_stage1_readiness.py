import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"docs/evidence/P22_3_B1_STAGE1_READINESS_2026-09-19.json"

def test_b1_stage1_stays_fail_closed_before_live_health():
    x=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert x["cohort_id"]=="B1_INSTITUTIONAL"
    assert x["source_count"]==4
    assert x["summary"]["fixture_pass_count"]==4
    assert x["summary"]["rollback_pass_count"]==4
    assert x["summary"]["live_health_pass_count"]==0
    assert x["summary"]["p20_5_eligible_count"]==0
    assert x["summary"]["repository_active_count"]==0
    assert all(s["eligibility_decision"]=="BLOCKED" for s in x["sources"])
    assert all(s["repository_activation"]=="NOT_ACTIVE" for s in x["sources"])
    assert x["summary"]["independence_credit_granted_count"]==0
    assert x["safety_boundary"]["persistent_owner_operation"]=="NOT_ACTIVATED"
