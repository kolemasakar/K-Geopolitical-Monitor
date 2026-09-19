import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_PLAN.md"
RESULT = ROOT / "docs/implementation/P21_7_PHASE_21_ACCEPTANCE_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED.md"


def test_p21_7_phase_acceptance_state_is_converged():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase21_p21_7"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 45
    assert s["roadmap"]["current_position"].startswith(("PHASE_21_", "PHASE_22_"))
    assert s["phases"]["21"] == "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS"

    assert s["phase21"]["state"] == "VALIDATED_WITH_KNOWN_LIMITATIONS"
    assert s["phase21"]["decision"] == "PASS_WITH_KNOWN_LIMITATIONS"
    assert s["phase21"]["gate"] == "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED"
    assert s["phase21"]["validated_sequence"][-1] == "P21.7"
    assert s["phase21"]["next_gate"] == "ROADMAP_DECISION_REQUIRED"

    assert x["state"] == "PASS_WITH_KNOWN_LIMITATIONS"
    assert x["gate"] == "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED"
    assert x["decision"] == "PASS_WITH_KNOWN_LIMITATIONS"
    assert x["acceptance_criteria_count"] == 8
    assert x["next_gate"] == "ROADMAP_DECISION_REQUIRED"


def test_p21_7_acceptance_preserves_material_coverage_limitations():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase21_p21_7"]
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    assert x["target_cell_count"] == 33
    assert x["required_cell_count"] == 27
    assert x["post_wave_a_structural_projection"] == {
        "adequate": 1,
        "degraded_collection": 2,
        "missing_expected_coverage": 20,
        "thin": 10,
    }
    assert x["required_post_wave_a_structural_projection"] == {
        "adequate": 1,
        "degraded_collection": 1,
        "missing_expected_coverage": 20,
        "thin": 5,
    }
    assert x["automatic_factual_independence_credit_delta"] == 0
    assert x["adequate_cell_delta"] == 0
    assert x["missing_required_cell_delta"] == -1
    assert x["verification_yield_impact"] == "NOT_OBSERVED"
    assert x["contradiction_workload_impact"] == "NOT_OBSERVED"
    assert x["forecast_input_impact"] == "NOT_OBSERVED"

    assert "20 required target cells remain `MISSING_EXPECTED_COVERAGE`" in result
    assert "PASS_WITH_KNOWN_LIMITATIONS" in checkpoint
    assert "does **not** claim" in result.lower()
    assert "broadly adequate" in result.lower()


def test_p21_7_acceptance_preserves_truth_runtime_and_activation_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase21_p21_7"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")

    assert x["verification_authority"] == "P13.5/P13.6"
    assert x["future_source_waves_authorized"] is False
    assert x["runtime_deployment"] is False
    assert x["service_restart"] is False
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["plugin_build_authorized"] is False
    assert x["plugin_publication_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    sync_version = s["roadmap"]["state_sync_version"]
    assert f"Version: {sync_version}" in roadmap
    assert "P21.7: `PASS_WITH_KNOWN_LIMITATIONS`" in roadmap
    assert "ROADMAP_DECISION_REQUIRED" in handoff
    assert "ROADMAP_DECISION_REQUIRED" in plan
