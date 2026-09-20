import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_2026-09-19.json"
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
RESULT = ROOT / "docs/implementation/P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED.md"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_7_records_undefined_feedback_rates_without_invented_owner_feedback():
    x = _json(EVIDENCE)
    assert x["exact_p22_5_cohort"]["canonical_semantic_claim_count"] == 28
    assert x["owner_delivery_read_model"]["projection_row_count"] == 0
    q = x["quality_feedback"]
    assert q["sample_size"] == 0
    assert q["feedback_count"] == 0
    assert q["usefulness_rate"] is None
    assert q["timeliness_rate"] is None
    assert q["noise_feedback_rate"] is None
    assert q["interpretation"] == "NO_OWNER_UTILITY_FEEDBACK_OBSERVED"
    assert x["decision"] == "VALIDATED_WITH_NO_OWNER_UTILITY_FEEDBACK_OBSERVED"
    assert any("No subjective owner feedback" in item for item in x["limitations"])


def test_p22_7_preserves_truth_runtime_and_policy_boundaries():
    x = _json(EVIDENCE)
    b = x["safety_boundary"]
    assert x["verification_authority"] == "P13.5/P13.6"
    assert b["persistent_owner_operation"] == "NOT_ACTIVATED"
    assert b["remaining_wave_b_onboarding_authorized"] is False
    assert b["runtime_deployment"] is False
    assert b["service_restart"] is False
    assert b["paid_or_shared_resources_authorized"] is False
    assert b["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert b["production_live"] == "NOT_OPERATIONAL"
    assert b["plugin_publication"] is False
    assert b["automatic_policy_mutation"] is False
    assert x["validation_policy"]["hp_omen_used"] is False


def test_p22_7_state_opens_only_phase22_acceptance():
    s = _json(STATE)
    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 58
    assert s["roadmap"]["current_position"] in {"PHASE_22_P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED", "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"}
    assert s["phase22"]["p22_7_state"] == "VALIDATED_WITH_NO_OWNER_UTILITY_FEEDBACK_OBSERVED"
    assert s["phase22"]["next_gate"] in {"PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED", "ROADMAP_DECISION_REQUIRED"}
    assert s["phase22"]["persistent_owner_operation"] == "NOT_ACTIVATED"
    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert RESULT.exists() and CHECKPOINT.exists()