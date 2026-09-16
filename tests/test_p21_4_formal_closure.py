import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED.md"
RESULT = ROOT / "docs/implementation/P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_RESULT.md"


def test_p21_4_formal_closure_remains_historical_after_forward_progress():
    s = json.loads(STATE.read_text())
    roadmap = ROADMAP.read_text()
    result = RESULT.read_text()
    checkpoint = CHECKPOINT.read_text()
    major, minor = s["roadmap"]["state_sync_version"].split(".", 1)
    assert major == "4" and int(minor) >= 41
    assert "P21.4" in s["phase21"]["validated_sequence"]
    assert s["phase21_p21_4"]["state"] == "VALIDATED"
    assert s["phase21_p21_4"]["test_count"] == 1281
    assert s["phase21_p21_4"]["gap_cell_count"] == 32
    assert s["phase21_p21_4"]["minimum_new_source_path_deficit"] == 49
    assert "P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED" in roadmap
    assert "1281 passed in 115.53s / SUCCESS" in result
    # Historical closure evidence remains immutable: at P21.4 close, P21.5 still required a separate owner decision.
    assert "P21_5_OWNER_DECISION_REQUIRED" in checkpoint
    assert "P21.5 is not started by this checkpoint" in checkpoint


def test_p21_4_historical_non_authorization_does_not_block_later_owner_decision():
    s = json.loads(STATE.read_text())
    checkpoint = CHECKPOINT.read_text()
    assert "does not authorize live onboarding" in checkpoint
    # Current state may remain owner-gated or advance only through an explicit recorded owner authorization.
    gate = s["activation_gates"]["phase21_live_source_expansion"]
    assert gate in {
        "P21_5_EXPLICIT_OWNER_DECISION_REQUIRED",
        "P21_5_AUTHORIZED_BY_OWNER_2026-09-16 / BOUNDED_PUBLIC_FREE_ONLY",
    }
    if gate.startswith("P21_5_AUTHORIZED_BY_OWNER"):
        assert s["phase21_p21_5"]["owner_authorization"] == "docs/evidence/P21_5_CONTROLLED_SOURCE_ONBOARDING_OWNER_AUTHORIZATION_2026-09-16.json"
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
