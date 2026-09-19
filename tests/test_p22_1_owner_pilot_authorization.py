import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
AUTH = ROOT / "docs/decisions/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_AUTHORIZATION_2026-09-19.md"


def test_p22_1_bounded_owner_pilot_is_explicitly_authorized_only():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]
    p = s["phase22_p22_1"]

    assert s["roadmap"]["state_sync_version"] == "4.50"
    assert s["roadmap"]["current_position"] == "PHASE_22_P22_1_AUTHORIZED_READY_TO_EXECUTE"

    assert x["p22_1_state"] == "AUTHORIZED_READY_TO_EXECUTE"
    assert x["owner_operational_activation"] == "APPROVED_FOR_BOUNDED_P22_1_PILOT"
    assert x["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"
    assert x["next_gate"] == "P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED"

    assert p["state"] == "AUTHORIZED_READY_TO_EXECUTE"
    assert p["target_node"] == "kgm-e4-owner-pilot"
    assert p["execution_scope"] == "ONE_BOUNDED_OWNER_LOCAL_SESSION"
    assert p["existing_governed_source_set_only"] is True
    assert p["persistent_scheduler_enablement_authorized"] is False
    assert p["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"


def test_p22_1_authorization_preserves_runtime_resource_and_truth_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    p = s["phase22_p22_1"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    auth = AUTH.read_text(encoding="utf-8")

    assert AUTH.exists()
    assert "APPROVED_FOR_BOUNDED_P22_1_PILOT" in auth
    assert "WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED" in auth
    assert "ONE_BOUNDED_OWNER_LOCAL_SESSION" in auth

    assert p["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert p["production_live"] == "NOT_OPERATIONAL"
    assert p["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert p["verification_authority"] == "P13.5/P13.6"
    assert p["shared_runtime_authorized"] is False
    assert p["paid_or_secret_provider_authorized"] is False
    assert p["plugin_publication_authorized"] is False

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"

    assert "Version: 4.50" in roadmap
    assert "PHASE_22_P22_1_AUTHORIZED_READY_TO_EXECUTE" in roadmap
    assert "P22_1_AUTHORIZED_READY_TO_EXECUTE" in handoff
    assert "AUTHORIZED_READY_TO_EXECUTE" in plan
