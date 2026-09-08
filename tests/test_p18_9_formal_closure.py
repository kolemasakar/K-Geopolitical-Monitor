import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_9_PHASE_18_ACTIVATION_READINESS_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-08_P18_9_PHASE_18_ACTIVATION_READINESS_VALIDATED.md"
MIGRATIONS_PATH = ROOT / "migrations"

IMPLEMENTATION_ANCHOR = "cfb21a5ea92214270161fd5112b103f71b2a1363"
P18_9_GATE = "PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _state() -> dict:
    return json.loads(_text(STATE_PATH))


def _roadmap_minor_version(text: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", text, re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_9_state_converges_to_validated_owner_activation_gate():
    state = _state()
    assert state["roadmap"]["state_sync_version"] == "4.34"
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE"
    assert state["phases"]["18"] == (
        "ARCHITECTURE_APPROVED / IMPLEMENTATION_AUTHORIZED / P18_0_VALIDATED / "
        "P18_1_VALIDATED / P18_2_VALIDATED / P18_3_VALIDATED / P18_4_VALIDATED / "
        "P18_5_VALIDATED / P18_6_VALIDATED / P18_7_VALIDATED / P18_8_VALIDATED / "
        "P18_9_VALIDATED / NOT_ACTIVATED / OWNER_DECISION_REQUIRED"
    )
    assert state["activation_gates"]["phase18_readiness"] == P18_9_GATE
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_9_state_records_exact_implementation_evidence_without_launch_overclaim():
    block = _state()["phase18_p18_9"]
    assert block == {
        "state": "VALIDATED",
        "gate": P18_9_GATE,
        "implementation_anchor": IMPLEMENTATION_ANCHOR,
        "x64_run_id": 34176050235,
        "x64_job_id": 101905532966,
        "arm64_run_id": 34176050242,
        "arm64_job_id": 101905532775,
        "test_count": 1106,
        "real_infrastructure_observation": "NOT_OBSERVED",
        "launch_eligible": False,
        "activation_state": "NOT_AUTHORIZED",
        "next_gate": "EXPLICIT_OWNER_DECISION_PLUS_FRESH_LAUNCH_TIME_VALIDATION_REQUIRED",
    }


def test_p18_9_roadmap_and_plan_close_readiness_without_activation_provider_or_migration():
    roadmap = _text(ROADMAP_PATH)
    plan = _text(PLAN_PATH)
    state = _state()

    assert _roadmap_minor_version(roadmap) == 34
    assert "P18_9_VALIDATED / NOT_ACTIVATED / OWNER_DECISION_REQUIRED" in roadmap
    assert "### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness" in roadmap
    assert "State: `VALIDATED`" in roadmap.split("### P18.9", 1)[1].split("# Current Implementation Checkpoint", 1)[0]
    assert IMPLEMENTATION_ANCHOR in roadmap
    assert P18_9_GATE in roadmap
    assert "real external infrastructure observations remain `NOT_OBSERVED`" in roadmap

    assert "P18_9 = VALIDATED" in plan
    assert P18_9_GATE in plan
    assert "P18_9_LAUNCH_ELIGIBLE = FALSE" in plan
    assert "There is no automatic P18.10 implementation step" in plan
    assert "explicit owner activation/cutover decision" in plan

    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_PATH.glob("*.sql"))


def test_p18_9_result_and_checkpoint_preserve_exact_evidence_and_truth_boundary():
    result = _text(RESULT_PATH)
    checkpoint = _text(CHECKPOINT_PATH)

    for text in (result, checkpoint):
        assert P18_9_GATE in text
        assert IMPLEMENTATION_ANCHOR in text
        assert "1106 passed in 130.05s / SUCCESS" in text
        assert "1106 passed in 98.22s / SUCCESS" in text
        assert "aarch64" in text
        assert "execution_count=0" in text
        assert "recovered_runs=0" in text
        assert "NOT_OBSERVED" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text
        assert "P13.5/P13.6" in text


def test_p18_9_closure_is_readiness_only_and_requires_fresh_owner_launch_gate():
    result = _text(RESULT_PATH)
    checkpoint = _text(CHECKPOINT_PATH)
    roadmap = _text(ROADMAP_PATH)
    plan = _text(PLAN_PATH)
    state = _state()

    assert state["phase18_p18_9"]["launch_eligible"] is False
    assert state["phase18_p18_9"]["activation_state"] == "NOT_AUTHORIZED"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"

    for text in (result, checkpoint, roadmap, plan):
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text

    assert "phase_matrix_validated = True" in result
    assert "launch_eligible = False" in result
    assert "real_infrastructure_observation = NOT_OBSERVED" in result
    assert "real_infrastructure_observation = NOT_OBSERVED" in checkpoint
    assert "Final shared-runtime activation remains a separate owner decision" in result
    assert "fresh launch-time validation" in checkpoint
    assert "Any final activation requires a separate explicit owner decision" in roadmap
