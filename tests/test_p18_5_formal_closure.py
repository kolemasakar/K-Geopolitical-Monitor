import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _roadmap_minor_version(roadmap: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", roadmap, flags=re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_5_current_state_preserves_validated_gate_after_later_progress():
    state = _state()
    assert int(state["roadmap"]["state_sync_version"].split(".")[1]) >= 30
    assert state["phase18_p18_5"]["state"] == "VALIDATED"
    assert state["phase18_p18_5"]["gate"] == "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED"
    assert "P18_5_VALIDATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_5_exact_engineering_evidence_is_recorded():
    assert _state()["phase18_p18_5"] == {
        "state": "VALIDATED",
        "gate": "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED",
        "implementation_anchor": "8effa120d76d2a0511dc1cf6a4cbb1b4b22b7f30",
        "x64_run_id": 34149258098,
        "x64_job_id": 101827861321,
        "arm64_run_id": 34149258084,
        "arm64_job_id": 101827861052,
        "test_count": 921,
        "next_gate": "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED",
        "p18_6_state": "READY_TO_BEGIN",
    }


def test_p18_5_roadmap_and_plan_preserve_gate_without_activation_or_migration():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert _roadmap_minor_version(roadmap) >= 30
    assert "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED" in roadmap
    assert "### P18.5 — Audit, Transactional Outbox and Side-Effect Isolation" in roadmap
    assert "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED" in plan
    assert "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan
    assert "MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED" in plan


def test_p18_5_result_and_checkpoint_preserve_safety_and_truth_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED" in text
        assert "8effa120d76d2a0511dc1cf6a4cbb1b4b22b7f30" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text
        assert "P13.5/P13.6" in text


def test_p18_5_historical_next_gate_evidence_remains_and_no_migration_033_exists():
    state = _state()
    assert state["phase18_p18_5"]["p18_6_state"] == "READY_TO_BEGIN"
    assert state["phase18_p18_5"]["next_gate"] == "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["verification_authority"] == "P13.5/P13.6"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
