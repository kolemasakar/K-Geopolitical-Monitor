import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _roadmap_minor_version(roadmap: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", roadmap, flags=re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_7_historical_closure_remains_recorded_after_later_phase_advances():
    state = _state()
    assert float(state["roadmap"]["state_sync_version"]) >= 4.32
    assert state["phase18_p18_7"]["state"] == "VALIDATED"
    assert state["phase18_p18_7"]["gate"] == "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED"
    assert "P18_7_VALIDATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_7_exact_engineering_evidence_is_recorded():
    assert _state()["phase18_p18_7"] == {
        "state": "VALIDATED",
        "gate": "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED",
        "implementation_anchor": "cdd23c945cccdc27a43fa14d18ebeb6309b991f1",
        "x64_run_id": 34159594021,
        "x64_job_id": 101858434798,
        "arm64_run_id": 34159594044,
        "arm64_job_id": 101858434830,
        "test_count": 1034,
        "next_gate": "P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED",
        "p18_8_state": "READY_TO_BEGIN",
    }


def test_p18_7_roadmap_and_plan_preserve_validated_gate_without_pinning_current_phase():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert _roadmap_minor_version(roadmap) >= 32
    assert "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED" in roadmap
    assert "P18_7_VALIDATED" in roadmap
    assert "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness" in roadmap
    assert "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED" in plan
    assert "P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED" in plan
    assert "P18_7 = VALIDATED" in plan
    assert "P18_8 = VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan
    assert "MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED" in plan
    assert "PAID_PROVIDERS = NONE_APPROVED" in plan


def test_p18_7_result_and_checkpoint_preserve_recovery_safety_and_truth_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED" in text
        assert "cdd23c945cccdc27a43fa14d18ebeb6309b991f1" in text
        assert "1034 passed" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text
        assert "P13.5/P13.6" in text


def test_p18_7_closure_keeps_p18_8_ready_only_and_infrastructure_unobserved():
    state = _state()
    result = RESULT_PATH.read_text(encoding="utf-8")
    assert state["phase18_p18_7"]["p18_8_state"] == "READY_TO_BEGIN"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["public_sharing"] == "NOT_ACTIVE"
    assert state["verification_authority"] == "P13.5/P13.6"
    assert "off_host_storage_observed = False" in result
    assert "provider_pitr_observed = False" in result
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
