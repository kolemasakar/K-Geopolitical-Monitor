import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
AUTH = ROOT / "docs/evidence/P22_3_B1_OWNER_AUTHORIZATION_2026-09-19.json"
DECISION = ROOT / "docs/decisions/P22_3_B1_CONTROLLED_ONBOARDING_OWNER_AUTHORIZATION_2026-09-19.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_3_b1_authorization_is_exact_and_bounded():
    a = _json(AUTH)
    assert a["status"] == "AUTHORIZED"
    assert a["cohort_id"] == "B1_INSTITUTIONAL"
    assert a["source_ids"] == [
        "ofac-recent-actions-en",
        "uk-sanctions-list-en",
        "russian-government-news-ru",
        "white-house-briefings-en",
    ]
    assert len(a["source_ids"]) == 4
    assert a["repository_activation_rule"] == "CONDITIONAL_ON_PER_SOURCE_P20_5_PASS"
    assert a["remaining_p22_2_candidates_authorized"] is False


def test_p22_3_b1_requires_full_p20_5_pass_before_repository_activation():
    a = _json(AUTH)
    assert a["required_states"] == {
        "health_behavior_status": "PASS",
        "fixture_validation_status": "PASS",
        "rollback_disable_status": "PASS",
        "governance_review_status": "APPROVED",
        "eligibility_decision": "ELIGIBLE_NOT_ACTIVE",
    }


def test_p22_3_b1_preserves_runtime_and_truth_boundaries():
    a = _json(AUTH)
    s = _json(STATE)
    x = s["phase22"]

    assert a["persistent_owner_operation_authorized"] is False
    assert a["runtime_deployment_authorized"] is False
    assert a["service_restart_authorized"] is False
    assert a["paid_or_shared_resources_authorized"] is False
    assert a["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert a["production_live"] == "NOT_OPERATIONAL"
    assert a["verification_authority"] == "P13.5/P13.6"

    assert x["p22_3_state"] in {"AUTHORIZED_B1_IMPLEMENTATION_READY", "VALIDATED_WITH_PARTIAL_ONBOARDING"}
    assert x["wave_b_onboarding"] in {"APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B_OWNER_DECISION_REQUIRED"}
    assert x["persistent_owner_operation"] == "NOT_ACTIVATED"
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"

    assert DECISION.exists()
    assert "B1_REPOSITORY_ACTIVATION = CONDITIONAL_ON_P20_5_PASS" in DECISION.read_text(encoding="utf-8")
    assert any(marker in PLAN.read_text(encoding="utf-8") for marker in ("State: `AUTHORIZED_B1_IMPLEMENTATION_READY`", "State: `VALIDATED_WITH_PARTIAL_ONBOARDING`"))
