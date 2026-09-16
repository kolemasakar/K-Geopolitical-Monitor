import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
REPORT = ROOT / "docs/evidence/P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_2026-09-16.json"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-16_P21_3_OPERATIONAL_COVERAGE_ADEQUACY_VALIDATED.md"


def test_p21_3_formal_closure_and_p21_4_readiness_are_synchronized():
    s = json.loads(STATE.read_text())
    r = json.loads(REPORT.read_text())
    roadmap = ROADMAP.read_text()
    handoff = HANDOFF.read_text()
    assert s["roadmap"]["state_sync_version"] == "4.40"
    assert s["roadmap"]["current_position"] == "PHASE_21_P21_3_VALIDATED_P21_4_READY"
    assert s["phase21"]["validated_sequence"] == ["P21.0", "P21.1", "P21.2", "P21.3"]
    assert s["phase21"]["next_gate"] == "P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED"
    assert s["phase21_p21_3"]["state"] == "VALIDATED"
    assert s["phase21_p21_3"]["test_count"] == 1271
    assert r["global_summary"]["status_counts"] == {"ADEQUATE": 1, "DEGRADED_COLLECTION": 1, "MISSING_EXPECTED_COVERAGE": 21, "THIN": 10}
    assert "P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED" in roadmap
    assert "State: `READY_TO_BEGIN`" in roadmap.split("### P21.4", 1)[1].split("### P21.5", 1)[0]
    assert "P21_3_VALIDATED / P21_4_READY" in handoff
    assert CHECKPOINT.exists()


def test_p21_3_closure_does_not_activate_p21_5_or_runtime():
    s = json.loads(STATE.read_text())
    assert s["activation_gates"]["phase21_live_source_expansion"] == "P21_5_EXPLICIT_OWNER_DECISION_REQUIRED"
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
