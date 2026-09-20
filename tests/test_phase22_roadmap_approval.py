import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
DECISION = ROOT / "docs/decisions/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_ROADMAP_DECISION_2026-09-19.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
PROPOSAL = ROOT / "docs/decisions/POST_PHASE_21_ROADMAP_DECISION_PROPOSAL_2026-09-19.md"


def test_phase22_owner_approval_opens_p22_0_without_activation():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 47
    assert s["roadmap"]["current_position"].startswith("PHASE_22_")
    assert s["phases"]["22"].startswith(("PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_APPROVED", "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"))

    assert x["state"] == "APPROVED"
    assert x["implementation_authorized"] is True
    assert x["current_position"].startswith(("P22_0_", "P22_1_", "P22_2_", "P22_3_", "P22_4_", "P22_5_", "P22_6_", "P22_7_", "P22_8_", "PHASE_22_"))
    assert x["p22_0_state"] in {"READY_TO_BEGIN", "VALIDATED"}

    assert s["post_phase21_strategic_audit"]["decision_state"] == "OWNER_APPROVED_PHASE_22"
    assert s["post_phase21_strategic_audit"]["phase22_created"] is True
    assert s["post_phase21_strategic_audit"]["phase22_authorized"] is True


def test_phase22_approval_preserves_explicit_owner_gates_and_runtime_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]

    assert x["owner_operational_activation"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_BOUNDED_P22_1_PILOT", "BOUNDED_P22_1_PILOT_COMPLETED / PERSISTENT_OWNER_OPERATION_NOT_ACTIVATED"}
    assert x["wave_b_onboarding"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B_OWNER_DECISION_REQUIRED"}
    assert x["public_free_anonymous_first"] is True
    assert x["verification_authority"] == "P13.5/P13.6"

    assert x["runtime_deployment"] is False
    assert x["service_restart"] is False
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"
    assert x["plugin_build_authorized"] is False
    assert x["plugin_publication_authorized"] is False

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert s["activation_gates"]["phase22_owner_operational_pilot"] in {
        "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED",
        "OWNER_ONLY_OPERATIONAL_ACTIVATION = APPROVED_FOR_BOUNDED_P22_1_PILOT",
        "BOUNDED_P22_1_PILOT_COMPLETED / PERSISTENT_OWNER_OPERATION_NOT_ACTIVATED",
    }
    assert s["activation_gates"]["phase22_wave_b_onboarding"] in {"WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED", "WAVE_B_ONBOARDING = APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_INSTITUTIONAL_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B = OWNER_DECISION_REQUIRED"}


def test_phase22_decision_plan_roadmap_handoff_are_converged():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    decision = DECISION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    proposal = PROPOSAL.read_text(encoding="utf-8")

    assert DECISION.exists()
    assert PLAN.exists()
    sync_version = s["roadmap"]["state_sync_version"]
    assert f"Version: {sync_version}" in roadmap
    assert "## Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion" in roadmap
    assert "PHASE_22_" in handoff
    assert "P22_0_ENTRY_CONVERGENCE_OWNER_GATES_VALIDATED" in handoff

    assert "APPROVED / P22_0_READY" in decision
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in decision
    assert "WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED" in decision
    assert ("Status: `APPROVED / P22_0_" in plan or "Status: `PHASE_22_VALIDATED_WITH_KNOWN_LIMITATIONS / P22_0-P22_8_VALIDATED`" in plan)
    assert "APPROVED / SUPERSEDED_BY_PHASE_22_ROADMAP_DECISION" in proposal

    assert s["phase21"]["state"] == "VALIDATED_WITH_KNOWN_LIMITATIONS"
    assert s["phase21"]["gate"] == "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED"


def test_phase22_wave_b_planning_basis_is_exact_and_non_activating():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]

    assert x["wave_b_planning_basis"] == "B_HIGH_REQUIRED"
    assert x["wave_b_gap_cell_count"] == 9
    assert x["wave_b_source_path_deficit"] == 13
    assert x["wave_b_healthy_source_deficit"] == 13
    assert x["wave_b_origin_evidence_deficit"] == 16
    assert x["wave_b_onboarding"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B_OWNER_DECISION_REQUIRED"}
