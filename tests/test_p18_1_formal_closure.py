import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_p18_1_current_state_converges_to_p18_2_ready_gate():
    state = _state()
    assert state["roadmap"]["state_sync_version"] == "4.26"
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_1_VALIDATED_P18_2_READY_GATE"
    assert state["phases"]["18"] == "ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_1_exact_engineering_evidence_is_recorded():
    p18_1 = _state()["phase18_p18_1"]
    assert p18_1 == {
        "state": "VALIDATED",
        "gate": "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED",
        "implementation_anchor": "01abc4f6be77c856e24497ad77c58ab052bb89e2",
        "x64_run_id": 34124491945,
        "x64_job_id": 101749841571,
        "arm64_run_id": 34124491899,
        "arm64_job_id": 101749841305,
        "test_count": 776,
        "next_gate": "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED",
        "p18_2_state": "READY_TO_BEGIN",
    }


def test_p18_1_roadmap_and_plan_converge_without_activation():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert "Version: 4.26" in roadmap
    assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in roadmap
    assert "P18.1: `VALIDATED`" in roadmap
    assert "P18.2: `READY_TO_BEGIN`" in roadmap
    assert "P18_1_VALIDATED / P18_2_READY / NOT_ACTIVATED" in roadmap
    assert "State: `VALIDATED`" in plan
    assert "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan


def test_p18_1_result_and_checkpoint_preserve_safety_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in text
        assert "01abc4f6be77c856e24497ad77c58ab052bb89e2" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text


def test_p18_1_closure_does_not_create_migration_033():
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
