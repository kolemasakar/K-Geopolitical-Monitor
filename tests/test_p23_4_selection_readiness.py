import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
EVIDENCE = ROOT / "docs/evidence/P23_4_EVIDENCE_YIELD_SELECTION_READINESS_2026-09-21.json"
ROADMAP = ROOT / "ROADMAP.md"


def test_p23_4_preselection_does_not_close_expansion_gate():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert state["roadmap"]["current_position"] == "PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED"
    assert state["phase23"]["next_gate"] == "P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED"
    assert evidence["p23_4_gate_validated"] is False
    assert evidence["decision"] == "PRESELECTION_COMPLETE_OWNER_DECISION_REQUIRED"


def test_p23_4_preselection_preserves_zero_activation_delta():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    safety = evidence["safety_boundary"]
    assert safety["source_activation_delta"] == 0
    assert safety["repository_activation_delta"] == 0
    assert safety["acquisition_resource_limit_relaxed"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["production_live"] == "NOT_OPERATIONAL"
    assert safety["hp_omen_used"] is False


def test_p23_4_owner_gate_candidate_and_preparation_cohort_are_explicit():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    owner = evidence["owner_gate_candidate"]
    assert owner["source_id"] == "uk-sanctions-list-en"
    assert owner["activation_authorized"] is False
    assert owner["independence_credit_granted"] is False
    assert {x["source_id"] for x in evidence["preparation_cohort"]} == {
        "cctv-news-zh", "anadolu-en", "trt-haber-tr"
    }


def test_p23_4_roadmap_records_owner_gate_without_claiming_validation():
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED" in roadmap
    assert "PRESELECTION_COMPLETE / OWNER_DECISION_REQUIRED_FOR_EXPANSION" in roadmap
