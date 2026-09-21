import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
PLAN = ROOT / "docs/implementation/PHASE_23_EVIDENCE_DEPTH_CORROBORATION_OPERATIONAL_YIELD_PLAN.md"
EVIDENCE = ROOT / "docs/evidence/P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_2026-09-21.json"
RESULT = ROOT / "docs/implementation/P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-21_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED.md"


def test_p23_3_canonical_state_and_evidence_converge():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert state["roadmap"]["current_position"] == "PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED"
    assert state["phase23"]["current_position"] == "P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED"
    assert state["phase23"]["next_gate"] == "P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED"
    assert state["phase23_p23_3"]["state"] == "VALIDATED_WITH_ZERO_CORROBORATION_POPULATION"
    obs = evidence["observation"]
    assert obs["relation_distribution"]["ATTRIBUTION_ONLY"] == 28
    assert obs["relation_distribution"]["SUPPORTS"] == 0
    assert obs["independence_distribution"]["INDEPENDENT"] == 0
    assert obs["corroborated_claim_count"] == 0


def test_p23_3_documents_preserve_epistemic_boundary():
    combined = "\n".join([
        ROADMAP.read_text(encoding="utf-8"),
        PLAN.read_text(encoding="utf-8"),
        RESULT.read_text(encoding="utf-8"),
        CHECKPOINT.read_text(encoding="utf-8"),
    ]).lower()
    assert "attribution_only" in combined
    assert "independent" in combined
    assert "p13.5/p13.6" in combined
    assert "zero corroboration" in combined
