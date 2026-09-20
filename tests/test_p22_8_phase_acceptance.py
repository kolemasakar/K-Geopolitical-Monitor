import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
EVIDENCE = ROOT / "docs/evidence/P22_8_PHASE_ACCEPTANCE_2026-09-20.json"
RESULT = ROOT / "docs/implementation/P22_8_PHASE_22_ACCEPTANCE_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-20_PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED.md"


def test_p22_8_acceptance_state_is_converged():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22_p22_8"]
    e = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert s["roadmap"]["state_sync_version"] == "4.59"
    assert s["roadmap"]["current_position"] == "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"
    assert s["phases"]["22"] == "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS"
    assert s["phase22"]["state"] == "VALIDATED_WITH_KNOWN_LIMITATIONS"
    assert s["phase22"]["current_position"] == "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"
    assert s["phase22"]["next_gate"] == "ROADMAP_DECISION_REQUIRED"
    assert x["decision"] == "PASS_WITH_KNOWN_LIMITATIONS"
    assert x["gate"] == "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"
    assert x["acceptance_criteria_count"] == 8
    assert x["next_gate"] == "ROADMAP_DECISION_REQUIRED"
    assert e["decision"] == "PASS_WITH_KNOWN_LIMITATIONS"


def test_p22_8_acceptance_preserves_measured_limitations():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22_p22_8"]
    result = RESULT.read_text(encoding="utf-8")

    assert x["required_post_b1"] == {
        "adequate": 1,
        "degraded_collection": 3,
        "missing_expected_coverage": 18,
        "thin": 5,
    }
    assert x["missing_required_cell_delta"] == -2
    assert x["adequate_cell_delta"] == 0
    assert x["healthy_fresh_path_delta"] == 0
    assert x["canonical_semantic_claim_count"] == 28
    assert x["automatic_factual_independence_credit_delta"] == 0
    assert x["downstream_intelligence_uplift"] == "NOT_OBSERVED"
    assert x["owner_utility_uplift"] == "NOT_OBSERVED"
    assert "18 required cells remain" in result
    assert "positive owner utility is not demonstrated" in result.lower()
    assert "does **not** claim" in result.lower()


def test_p22_8_acceptance_preserves_authority_and_activation_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22_p22_8"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    assert x["verification_authority"] == "P13.5/P13.6"
    assert x["persistent_owner_operation"] == "NOT_ACTIVATED"
    assert x["remaining_wave_b_onboarding_authorized"] is False
    assert x["runtime_deployment"] is False
    assert x["service_restart"] is False
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"
    assert x["plugin_publication"] is False
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert "Version: 4.59" in roadmap
    assert "P22.8" in roadmap and "PASS_WITH_KNOWN_LIMITATIONS" in roadmap
    assert "ROADMAP_DECISION_REQUIRED" in handoff
    assert "ROADMAP_DECISION_REQUIRED" in plan
    assert "HP-OMEN is not used" in checkpoint
