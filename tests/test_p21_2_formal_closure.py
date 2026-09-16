import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
RESULT = ROOT / "docs/implementation/P21_2_FRESH_SOURCE_HEALTH_BASELINE_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED.md"
EVIDENCE = ROOT / "docs/evidence/P21_2_FRESH_SOURCE_HEALTH_BASELINE_OWNER_LOCAL_2026-09-16.json"


def test_p21_2_formal_closure_and_p21_3_ready_state():
    state = json.loads(STATE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    roadmap = ROADMAP.read_text()
    handoff = HANDOFF.read_text()
    result = RESULT.read_text()

    assert state["roadmap"]["state_sync_version"] == "4.39"
    assert state["roadmap"]["current_position"] == "PHASE_21_P21_2_VALIDATED_P21_3_READY"
    assert state["phase21"]["validated_sequence"] == ["P21.0", "P21.1", "P21.2"]
    assert state["phase21"]["next_gate"] == "P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED"
    p = state["phase21_p21_2"]
    assert p["state"] == "VALIDATED_WITH_MEASURED_DEGRADATION"
    assert p["gate"] == "P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED"
    assert p["measured_source_count"] == 10 and p["unmeasured_source_count"] == 0
    assert p["source_success_count"] == 8 and p["source_failure_count"] == 2
    assert p["healthy_fresh_count"] == 6 and p["healthy_stale_content_count"] == 2
    assert p["production_runtime_mutated"] is False
    assert evidence["measured_source_count"] == 10
    assert evidence["measurement_scope"]["production_runtime_mutated"] is False
    assert evidence["phase21_measurement"]["source_expansion"] is False
    assert "1263 passed in 122.61s" in result
    assert CHECKPOINT.exists()
    assert "P21_3_READY" in handoff
    assert "State: `READY_TO_BEGIN`" in roadmap
    assert state["activation_gates"]["phase21_live_source_expansion"] == "P21_5_EXPLICIT_OWNER_DECISION_REQUIRED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
