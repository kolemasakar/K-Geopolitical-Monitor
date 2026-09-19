import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/"docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP=ROOT/"ROADMAP.md"
HANDOFF=ROOT/"docs/handoff/CURRENT_HANDOFF.md"
PLAN=ROOT/"docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
RESULT=ROOT/"docs/implementation/P22_3_B1_CONTROLLED_ONBOARDING_RESULT.md"
CHECKPOINT=ROOT/"docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED.md"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_3_closure_is_partial_and_opens_only_p22_4():
    s=_json(STATE)
    x=s["phase22"]
    p=s["phase22_p22_3_b1"]
    assert s["roadmap"]["state_sync_version"]=="4.53"
    assert s["roadmap"]["current_position"]=="PHASE_22_P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED"
    assert x["p22_3_state"]=="VALIDATED_WITH_PARTIAL_ONBOARDING"
    assert x["p22_4_state"]=="READY_TO_BEGIN"
    assert x["next_gate"]=="P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED"
    assert p["gate"]=="P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED"
    assert p["implementation_pr"]==140
    assert p["implementation_merge_anchor"]=="9c730ccd4a646aecbd0ada13b972701b65596adf"
    assert p["validation_run_id"]==35451792014
    assert p["validation_job_id"]==105920115982
    assert p["test_count"]==1343


def test_p22_3_closure_preserves_exact_partial_onboarding_counts():
    p=_json(STATE)["phase22_p22_3_b1"]
    assert p["measured_source_count"]==4
    assert p["source_success_count"]==2
    assert p["source_failure_count"]==2
    assert p["collected_item_count"]==28
    assert p["health_behavior_pass_count"]==2
    assert p["content_freshness_credit_count"]==0
    assert p["p20_5_eligible_not_active_count"]==2
    assert p["p20_5_blocked_count"]==2
    assert p["repository_active_count"]==2
    assert p["live_activation_count"]==0
    assert p["independence_credit_granted_count"]==0
    assert p["repository_active_source_ids"]==[
        "ofac-recent-actions-en",
        "white-house-briefings-en",
    ]
    assert p["blocked_sources"]=={
        "uk-sanctions-list-en":"BOUNDED_RESPONSE_LIMIT",
        "russian-government-news-ru":"TRANSPORT_TIMEOUT",
    }


def test_p22_3_closure_converges_docs_and_safety_boundaries():
    s=_json(STATE)
    roadmap=ROADMAP.read_text(encoding="utf-8")
    handoff=HANDOFF.read_text(encoding="utf-8")
    plan=PLAN.read_text(encoding="utf-8")
    result=RESULT.read_text(encoding="utf-8")
    checkpoint=CHECKPOINT.read_text(encoding="utf-8")

    assert "Version: 4.53" in roadmap
    assert "state synchronization: `v4.53`" in roadmap
    assert s["roadmap"]["current_position"] in roadmap
    assert "P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED" in handoff
    assert "State: `VALIDATED_WITH_PARTIAL_ONBOARDING`" in plan
    assert "1343 passed in 107.57s / SUCCESS" in result
    assert "REPOSITORY_ACTIVE = 2" in checkpoint
    assert "LIVE_ACTIVATION = 0" in checkpoint
    assert "INDEPENDENCE_CREDIT = 0" in checkpoint

    assert s["phase22"]["persistent_owner_operation"]=="NOT_ACTIVATED"
    assert s["phase22"]["runtime_deployment"] is False
    assert s["phase22"]["service_restart"] is False
    assert s["phase22"]["paid_or_shared_resources_authorized"] is False
    assert s["phase22"]["migration_033"]=="NOT_CREATED / NOT_PREAUTHORIZED"
    assert s["phase22"]["production_live"]=="NOT_OPERATIONAL"
    assert s["phase22"]["verification_authority"]=="P13.5/P13.6"
