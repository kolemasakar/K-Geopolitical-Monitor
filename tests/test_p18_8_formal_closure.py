import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_8_NONPROD_SHADOW_CANARY_READINESS_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-08_P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED.md"
MIGRATIONS_PATH = ROOT / "migrations"

IMPLEMENTATION_ANCHOR = "5cb0c4075c709c2f32c62857de7b577d04a90da6"
P18_8_GATE = "P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED"
P18_9_GATE = "PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _state() -> dict:
    return json.loads(_text(STATE_PATH))


def _roadmap_minor_version(text: str) -> int:
    match = re.search(r"^Version: 4\.(\d+)$", text, re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def test_p18_8_historical_closure_remains_valid_after_later_phase_progress():
    state = _state()
    assert int(state["roadmap"]["state_sync_version"].split(".")[-1]) >= 33
    assert "P18_8_VALIDATED" in state["phases"]["18"]
    assert "NOT_ACTIVATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"


def test_p18_8_state_preserves_exact_implementation_evidence_without_infra_overclaim():
    block = _state()["phase18_p18_8"]
    assert block["state"] == "VALIDATED"
    assert block["gate"] == P18_8_GATE
    assert block["implementation_anchor"] == IMPLEMENTATION_ANCHOR
    assert block["x64_run_id"] == 34172531605
    assert block["x64_job_id"] == 101895457213
    assert block["arm64_run_id"] == 34172531604
    assert block["arm64_job_id"] == 101895457340
    assert block["test_count"] == 1077
    assert block["next_gate"] == P18_9_GATE
    assert block["p18_9_state"] in {"READY_TO_BEGIN", "VALIDATED"}
    assert block["real_infrastructure_observation"] == "NOT_OBSERVED"


def test_p18_8_roadmap_and_plan_preserve_closure_boundaries_during_later_progress():
    roadmap = _text(ROADMAP_PATH)
    plan = _text(PLAN_PATH)
    state = _state()

    assert _roadmap_minor_version(roadmap) >= 33
    assert "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness" in roadmap
    assert "State: `VALIDATED`" in roadmap.split("### P18.8", 1)[1].split("### P18.9", 1)[0]
    assert "### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness" in roadmap
    p18_9_roadmap = roadmap.split("### P18.9", 1)[1].split("# Current Implementation Checkpoint", 1)[0]
    assert any(state_marker in p18_9_roadmap for state_marker in ("State: `READY_TO_BEGIN`", "State: `VALIDATED`"))
    assert P18_9_GATE in roadmap
    assert "NOT_OBSERVED" in roadmap

    assert "P18_8 = VALIDATED" in plan
    assert any(marker in plan for marker in ("P18_9 = READY_TO_BEGIN", "P18_9 = VALIDATED"))
    assert "P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness" in plan
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in plan

    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_PATH.glob("*.sql"))


def test_p18_8_result_and_checkpoint_preserve_exact_evidence_and_truth_boundary():
    result = _text(RESULT_PATH)
    checkpoint = _text(CHECKPOINT_PATH)

    for text in (result, checkpoint):
        assert P18_8_GATE in text
        assert IMPLEMENTATION_ANCHOR in text
        assert "1077 passed in 141.19s / SUCCESS" in text
        assert "1077 passed in 102.82s / SUCCESS" in text
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


def test_p18_8_historical_transition_to_p18_9_did_not_authorize_activation():
    result = _text(RESULT_PATH)
    checkpoint = _text(CHECKPOINT_PATH)
    roadmap = _text(ROADMAP_PATH)
    plan = _text(PLAN_PATH)

    assert P18_9_GATE in result
    assert P18_9_GATE in checkpoint

    for text in (result, checkpoint, roadmap, plan):
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text

    assert "real_infrastructure_observation = NOT_OBSERVED" in result
    assert "real_infrastructure_observation = NOT_OBSERVED" in checkpoint
    normalized_result = " ".join(result.split()).lower()
    assert (
        "final shared-runtime activation still requires a separate explicit owner "
        "decision plus fresh launch-time validation"
    ) in normalized_result

    # Current canonical planning may have legally progressed beyond P18.8, but
    # that progression must still remain readiness-only and non-activated.
    assert any(marker in roadmap for marker in ("P18.9: `READY_TO_BEGIN`", "P18.9: `VALIDATED`", "P18.9: `VALIDATED`;")) or "P18.9: `VALIDATED`" in roadmap
    assert any(marker in plan for marker in ("P18_9 = READY_TO_BEGIN", "P18_9 = VALIDATED"))
