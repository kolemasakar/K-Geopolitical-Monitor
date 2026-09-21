import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
PLAN = ROOT / "docs/implementation/PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_PLAN.md"
EVIDENCE = ROOT / "docs/evidence/P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_2026-09-20.json"
RESULT = ROOT / "docs/implementation/P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-20_P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED.md"


def test_p23_2_canonical_state_and_evidence_converge():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert state["roadmap"]["current_position"] == "PHASE_23_P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED"
    assert state["phase23"]["current_position"] == "P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED"
    assert state["phase23"]["next_gate"] == "P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED"
    assert state["phase23_p23_2"]["state"] == "VALIDATED_WITH_ZERO_UNDERLYING_ORIGIN_RESOLUTION"
    assert evidence["resolution_observation"]["underlying_origin_resolved_count"] == 0
    assert evidence["resolution_observation"]["underlying_origin_unresolved_count"] == 28
    assert evidence["resolution_observation"]["automatic_factual_independence_credit"] == 0


def test_p23_2_documents_preserve_epistemic_boundary():
    combined = "\n".join([
        ROADMAP.read_text(encoding="utf-8"),
        PLAN.read_text(encoding="utf-8"),
        RESULT.read_text(encoding="utf-8"),
        CHECKPOINT.read_text(encoding="utf-8"),
    ]).lower()
    assert "first-party publication" in combined
    assert "underlying-origin" in combined
    assert "p13.5/p13.6" in ROADMAP.read_text(encoding="utf-8").lower()
