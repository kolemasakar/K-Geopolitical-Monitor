import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
RESULT = ROOT / "docs/implementation/P21_2_FRESH_SOURCE_HEALTH_BASELINE_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED.md"
EVIDENCE = ROOT / "docs/evidence/P21_2_FRESH_SOURCE_HEALTH_BASELINE_OWNER_LOCAL_2026-09-16.json"


def test_p21_2_formal_closure_remains_immutable_after_later_phase21_progress():
    state = json.loads(STATE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    roadmap = ROADMAP.read_text()
    handoff = HANDOFF.read_text()
    result = RESULT.read_text()

    major, minor = state["roadmap"]["state_sync_version"].split(".", 1)
    assert major == "4" and int(minor) >= 39
    assert state["roadmap"]["current_position"].startswith("PHASE_21_")
    assert state["phase21"]["validated_sequence"][:3] == ["P21.0", "P21.1", "P21.2"]
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
    assert "P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED" in handoff
    assert "### P21.2 — Fresh Operational Health Baseline" in roadmap
    assert "State: `VALIDATED_WITH_MEASURED_DEGRADATION`" in roadmap.split("### P21.2", 1)[1].split("### P21.3", 1)[0]
    # P21.2 historical closure remains immutable, while current activation state may lawfully advance
    # through the separately recorded owner authorization for P21.5.
    gate = state["activation_gates"]["phase21_live_source_expansion"]
    assert gate in {
        "P21_5_EXPLICIT_OWNER_DECISION_REQUIRED",
        "P21_5_AUTHORIZED_BY_OWNER_2026-09-16 / BOUNDED_PUBLIC_FREE_ONLY",
        "P21_5_WAVE_A_VALIDATED / FUTURE_WAVES_OWNER_DECISION_REQUIRED",
    }
    if gate.startswith("P21_5_AUTHORIZED_BY_OWNER"):
        assert state["phase21_p21_5"]["owner_authorization"] == "docs/evidence/P21_5_CONTROLLED_SOURCE_ONBOARDING_OWNER_AUTHORIZATION_2026-09-16.json"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
