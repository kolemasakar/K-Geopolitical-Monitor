import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
RESULT = ROOT / "docs/implementation/P22_0_ENTRY_CONVERGENCE_OWNER_GATES_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED.md"


def test_p22_0_entry_convergence_is_validated_and_p22_2_is_ready():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]

    assert s["roadmap"]["state_sync_version"] == "4.48"
    assert s["roadmap"]["current_position"] == "PHASE_22_P22_0_VALIDATED_P22_2_READY"
    assert x["p22_0_state"] == "VALIDATED"
    assert x["p22_0_gate"] == "P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED"
    assert x["p22_1_state"] == "BLOCKED_ON_OWNER_GATE"
    assert x["p22_2_state"] == "READY_TO_BEGIN"
    assert x["p22_3_state"] == "BLOCKED_ON_OWNER_GATE"
    assert x["next_gate"] == "P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED"


def test_p22_0_preserves_owner_wave_runtime_and_truth_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")

    assert RESULT.exists()
    assert CHECKPOINT.exists()

    assert x["owner_operational_activation"] == "OWNER_DECISION_REQUIRED"
    assert x["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"
    assert x["verification_authority"] == "P13.5/P13.6"

    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in result
    assert "WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED" in result
    assert "P22_2_STATE = READY_TO_BEGIN" in result
    assert "P22_1 = BLOCKED_ON_OWNER_GATE" in checkpoint

    assert "Version: 4.48" in roadmap
    assert "### P22.2 — Wave-B Candidate Discovery & Qualification" in roadmap
    assert "State: `READY_TO_BEGIN`" in roadmap
    assert "P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED" in handoff
    assert "State: `READY_TO_BEGIN`" in plan

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
