import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED.md"
RESULT = ROOT / "docs/implementation/P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_RESULT.md"

def test_p21_4_formal_closure_and_p21_5_owner_gate_are_synchronized():
    s = json.loads(STATE.read_text())
    roadmap = ROADMAP.read_text()
    result = RESULT.read_text()
    assert s["roadmap"]["state_sync_version"] == "4.41"
    assert s["roadmap"]["current_position"] == "PHASE_21_P21_4_VALIDATED_P21_5_OWNER_DECISION_REQUIRED"
    assert s["phase21"]["validated_sequence"] == ["P21.0", "P21.1", "P21.2", "P21.3", "P21.4"]
    assert s["phase21_p21_4"]["state"] == "VALIDATED"
    assert s["phase21_p21_4"]["test_count"] == 1281
    assert s["phase21_p21_4"]["gap_cell_count"] == 32
    assert s["phase21_p21_4"]["minimum_new_source_path_deficit"] == 49
    assert "P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED" in roadmap
    assert "P21_5_OWNER_DECISION_REQUIRED" in roadmap
    assert "1281 passed in 115.53s / SUCCESS" in result
    assert CHECKPOINT.exists()

def test_p21_4_closure_does_not_start_or_authorize_p21_5():
    s = json.loads(STATE.read_text())
    assert s["activation_gates"]["phase21_live_source_expansion"] == "P21_5_EXPLICIT_OWNER_DECISION_REQUIRED"
    assert s["phase21_p21_4"]["live_source_onboarding"] is False
    assert s["phase21_p21_4"]["runtime_deployment"] is False
    assert s["phase21_p21_4"]["paid_provider_authorized"] is False
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
