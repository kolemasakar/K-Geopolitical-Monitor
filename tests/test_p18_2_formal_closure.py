import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_p18_2_historical_validation_evidence_remains_recorded():
    p18_2 = _state()["phase18_p18_2"]
    assert p18_2 == {
        "state": "VALIDATED",
        "gate": "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED",
        "implementation_anchor": "eb9e51082320858be14aebafafd4746a16674ec7",
        "x64_run_id": 34131110962,
        "x64_job_id": 101771189130,
        "arm64_run_id": 34131110956,
        "arm64_job_id": 101771189222,
        "test_count": 820,
        "next_gate": "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED",
        "p18_3_state": "READY_TO_BEGIN",
    }


def test_p18_2_roadmap_and_plan_preserve_validated_historical_gate():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED" in roadmap
    assert "P18.2" in roadmap
    assert "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan


def test_p18_2_result_and_checkpoint_preserve_safety_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED" in text
        assert "eb9e51082320858be14aebafafd4746a16674ec7" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text


def test_p18_2_history_does_not_authorize_migration_033_or_activation():
    state = _state()
    assert state["phase18_p18_2"]["state"] == "VALIDATED"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
