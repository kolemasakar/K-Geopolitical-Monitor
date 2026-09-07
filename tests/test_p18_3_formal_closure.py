import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED.md"


def _state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _roadmap_minor_version(roadmap: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", roadmap, flags=re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_3_current_state_preserves_validated_gate_after_later_progress():
    state = _state()
    assert int(state["roadmap"]["state_sync_version"].split(".")[1]) >= 28
    assert state["phase18_p18_3"]["state"] == "VALIDATED"
    assert state["phase18_p18_3"]["gate"] == "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED"
    assert "P18_3_VALIDATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_3_exact_engineering_evidence_is_recorded():
    p18_3 = _state()["phase18_p18_3"]
    assert p18_3 == {
        "state": "VALIDATED",
        "gate": "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED",
        "implementation_anchor": "7cf09298ee385a0ed7d5a5797f3a096f4cd04bf7",
        "x64_run_id": 34141047205,
        "x64_job_id": 101802889133,
        "arm64_run_id": 34141047066,
        "arm64_job_id": 101802888555,
        "test_count": 858,
        "next_gate": "P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED",
        "p18_4_state": "READY_TO_BEGIN",
    }


def test_p18_3_roadmap_and_plan_preserve_gate_without_activation_or_migration():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert _roadmap_minor_version(roadmap) >= 28
    assert "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED" in roadmap
    assert "### P18.3 — Shared Datastore Schema and Migration Contract" in roadmap
    assert "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED" in plan
    assert "P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED" in plan
    assert "Shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`" in plan
    assert "MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED" in plan


def test_p18_3_result_and_checkpoint_preserve_safety_boundaries():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")
    for text in (result, checkpoint):
        assert "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED" in text
        assert "7cf09298ee385a0ed7d5a5797f3a096f4cd04bf7" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text


def test_p18_3_historical_next_gate_evidence_remains_and_no_migration_033_exists():
    state = _state()
    assert state["phase18_p18_3"]["p18_4_state"] == "READY_TO_BEGIN"
    assert state["phase18_p18_3"]["next_gate"] == "P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
