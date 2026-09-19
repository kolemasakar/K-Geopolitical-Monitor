import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
DECISION = ROOT / "docs/decisions/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_ROADMAP_DECISION_2026-09-19.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"


def test_phase22_owner_approval_opens_only_p22_0():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]

    assert s["roadmap"]["state_sync_version"] == "4.47"
    assert s["roadmap"]["current_position"] == "PHASE_22_APPROVED_P22_0_READY"
    assert s["phases"]["22"] == "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_APPROVED / P22_0_READY"

    assert x["state"] == "APPROVED"
    assert x["decision"] == "OWNER_APPROVED_2026-09-19"
    assert x["gate"] == "P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED"
    assert x["current_position"] == "P22_0_READY"
    assert x["wave_b_candidate_discovery_qualification"] == "AUTHORIZED_AFTER_P22_0"


def test_phase22_approval_preserves_explicit_mutation_gates():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    decision = DECISION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")

    assert DECISION.exists()
    assert PLAN.exists()

    assert x["owner_operational_activation"] == "OWNER_DECISION_REQUIRED"
    assert x["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"
    assert x["plugin_build"] == "NOT_STARTED"
    assert x["plugin_publication"] == "NOT_ACTIVATED"
    assert x["verification_authority"] == "P13.5/P13.6"

    assert "Version: 4.47" in roadmap
    assert "Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion" in roadmap
    assert "PHASE_22_APPROVED / P22_0_READY" in handoff
    assert "does **not itself activate owner-operational monitoring or authorize Wave-B source onboarding**" in decision
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in plan
    assert "WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED" in plan
