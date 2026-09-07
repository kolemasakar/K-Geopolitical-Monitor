import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _roadmap_minor_version(roadmap: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", roadmap, flags=re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_6_current_state_converges_to_p18_7_ready_gate():
    state = _state()
    assert state["roadmap"]["state_sync_version"] == "4.31"
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_6_VALIDATED_P18_7_READY_GATE"
    assert state["phases"]["18"] == (
        "ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / "
        "P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / "
        "P18_5_VALIDATED / P18_6_VALIDATED / P18_7_READY / NOT_ACTIVATED"
    )
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_6_exact_engineering_evidence_is_recorded():
    assert _state()["phase18_p18_6"] == {
        "state": "VALIDATED",
        "gate": "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED",
        "implementation_anchor": "8d3e8679db3e722186f04dc0fff32fdb8e13e703",
        "x64_run_id": 34154397826,
        "x64_job_id": 101843094272,
        "arm64_run_id": 34154397829,
        "arm64_job_id": 101843094702,
        "test_count": 963,
        "next_gate": "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED",
        "p18_7_state": "READY_TO_BEGIN",
    }


def test_p18_6_roadmap_and_plan_converge_without_activation_or_migration():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert _roadmap_minor_version(roadmap) == 31
    assert "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED" in roadmap
    assert "P18_6_VALIDATED / P18_7_READY / NOT_ACTIVATED" in roadmap
    assert "### P18.7 — Backup, Disaster Recovery and Rollback" in roadmap
    assert "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED" in plan
    assert "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED" in plan
    assert "P18_6 = VALIDATED" in plan
    assert "P18_7 = READY_TO_BEGIN" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan
    assert "MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED" in plan


def test_p18_6_result_and_checkpoint_preserve_security_safety_and_truth_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED" in text
        assert "8d3e8679db3e722186f04dc0fff32fdb8e13e703" in text
        assert "963 passed" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text
        assert "P13.5/P13.6" in text


def test_p18_6_closure_keeps_p18_7_ready_only_and_no_migration_033():
    state = _state()
    assert state["phase18_p18_6"]["p18_7_state"] == "READY_TO_BEGIN"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["public_sharing"] == "NOT_ACTIVE"
    assert state["verification_authority"] == "P13.5/P13.6"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
