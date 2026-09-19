import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HEALTH=ROOT/"docs/evidence/P22_3_B1_FRESH_HEALTH_2026-09-19.json"
ONBOARD=ROOT/"docs/evidence/P22_3_B1_ONBOARDING_2026-09-19.json"
RESULT=ROOT/"docs/implementation/P22_3_B1_CONTROLLED_ONBOARDING_RESULT.md"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_b1_fresh_health_is_exact_main_and_contained():
    h=_json(HEALTH)
    assert h["exact_main_sha"]=="445699eb8b60fec3a70cbbfb5d831ffb35aa26a3"
    assert h["host_label"]=="kgm-e4-owner-pilot" and h["architecture"]=="aarch64"
    assert h["summary"]=={
        "measured_source_count":4,
        "success_count":2,
        "failure_count":2,
        "item_count":28,
        "health_behavior_pass_count":2,
        "content_freshness_credit_count":0,
    }
    assert h["deployed_sha_before"]==h["deployed_sha_after"]=="b31b2136b5fe982d0b63b0135479b1549041906c"
    assert h["service_before"]==h["service_after"]=="active"
    assert h["runtime_deployment"] is False and h["service_restart"] is False
    assert h["production_runtime_mutated"] is False


def test_b1_onboarding_activates_only_p20_5_pass_sources():
    x=_json(ONBOARD)
    by={s["source_id"]:s for s in x["sources"]}
    assert x["summary"]["p20_5_eligible_not_active_count"]==2
    assert x["summary"]["p20_5_blocked_count"]==2
    assert x["summary"]["repository_active_count"]==2
    assert x["summary"]["live_activation_count"]==0
    assert by["ofac-recent-actions-en"]["p22_3_repository_activation"]=="ACTIVE"
    assert by["white-house-briefings-en"]["p22_3_repository_activation"]=="ACTIVE"
    assert by["uk-sanctions-list-en"]["eligibility_decision"]=="BLOCKED"
    assert "BOUNDED_RESPONSE_LIMIT" in by["uk-sanctions-list-en"]["reason_codes"]
    assert by["russian-government-news-ru"]["eligibility_decision"]=="BLOCKED"
    assert "TRANSPORT_TIMEOUT" in by["russian-government-news-ru"]["reason_codes"]
    assert all(s["live_activation_authorized"] is False and s["live_activation_state"]=="NOT_ACTIVE" for s in x["sources"])
    assert all(s["independence_credit_granted"] is False for s in x["sources"])


def test_b1_result_preserves_truth_and_runtime_boundaries():
    t=RESULT.read_text(encoding="utf-8")
    assert "IMPLEMENTED / VALIDATION_CANDIDATE / PARTIAL_ONBOARDING" in t
    assert "P13.5/P13.6 remain factual-verification authority" in t
    assert "Repository activation is not deployed-runtime activation" in t
