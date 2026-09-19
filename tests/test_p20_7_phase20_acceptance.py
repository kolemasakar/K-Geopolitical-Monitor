from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P20_0 = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_2 = ROOT / "docs" / "evidence" / "P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json"
P20_3 = ROOT / "docs" / "evidence" / "P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json"
P20_4 = ROOT / "docs" / "evidence" / "P20_4_CURRENT_COLLECTION_HEALTH_BASELINE_2026-09-16.json"
P20_6 = ROOT / "docs" / "evidence" / "P20_6_COVERAGE_REPORT_2026-09-16.json"
P20_7_RESULT = ROOT / "docs" / "implementation" / "P20_7_PHASE_20_ACCEPTANCE_RESULT.md"
P20_7_CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-16_PHASE_20_GLOBAL_SOURCE_COVERAGE_VALIDATED.md"
P21_DECISION = ROOT / "docs" / "decisions" / "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_ROADMAP_DECISION_2026-09-16.md"
P21_PLAN = ROOT / "docs" / "implementation" / "PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_PLAN.md"
P21_APPROVAL = ROOT / "docs" / "evidence" / "P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json"
STATE = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
HANDOFF = ROOT / "docs" / "handoff" / "CURRENT_HANDOFF.md"
ROADMAP = ROOT / "ROADMAP.md"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p20_7_acceptance_composes_exact_current_coverage_evidence():
    p20_0 = _json(P20_0)
    p20_2 = _json(P20_2)
    p20_3 = _json(P20_3)
    p20_4 = _json(P20_4)
    p20_6 = _json(P20_6)

    assert len(p20_0["sources"]) == 10
    assert p20_2["cell_count"] == 17
    assert p20_2["policy_state"] == "UNSET"
    assert p20_3["source_count"] == 10
    assert p20_3["known_origin_source_count"] == 0
    assert p20_3["independent_origin_count"] is None
    assert p20_3["monoculture_state"] == "UNKNOWN"
    assert p20_4["source_count"] == 10
    assert p20_4["measured_source_count"] == 0
    assert p20_6["global_summary"]["observed_cell_count"] == 17
    assert p20_6["global_summary"]["unknown_count"] == 17
    assert p20_6["global_summary"]["adequate_count"] == 0
    assert p20_6["global_summary"]["missing_expected_coverage_count"] == 0
    assert {cell["status"] for cell in p20_6["cells"]} == {"UNKNOWN"}


def test_p20_7_required_acceptance_dimensions_are_explicitly_validated():
    result = P20_7_RESULT.read_text(encoding="utf-8")

    for requirement in (
        "Coverage measurable by region, language and source type",
        "Material gaps and limitations explicit",
        "Independent-origin coverage distinguishable from copy amplification",
        "Stale/failed collection cannot masquerade as low geopolitical activity",
        "Current source set evaluated deterministically",
        "No unapproved paid/shared-runtime dependency introduced",
        "Coverage evidence cannot promote factual verification",
    ):
        assert requirement in result

    assert "PASS_WITH_KNOWN_LIMITATIONS" in result
    assert "P20_GLOBAL_SOURCE_COVERAGE_VALIDATED" in result
    assert "does **not** claim exhaustive global coverage" in result


def test_p20_7_unknown_remains_neither_gap_nor_adequacy_at_phase_closure():
    report = _json(P20_6)
    checkpoint = P20_7_CHECKPOINT.read_text(encoding="utf-8")

    assert report["evaluation_basis"] == {
        "coverage_policy_state": "UNSET",
        "independence_evidence_state": "UNKNOWN",
        "health_evidence_state": "UNMEASURED",
    }
    assert report["global_summary"]["unknown_count"] == report["global_summary"]["observed_cell_count"]
    assert report["global_summary"]["adequate_count"] == 0
    assert report["global_summary"]["missing_expected_coverage_count"] == 0
    assert "not silently converted to failure, adequacy, or exhaustive global coverage" in checkpoint


def test_p20_7_required_report_sections_preserve_explicit_unknown_state():
    sections = _json(P20_6)["report_sections"]
    assert all(section["state"] == "UNKNOWN" for section in sections.values())
    assert all(section["reason_codes"] for section in sections.values())


def test_p20_7_preserves_runtime_resource_and_verification_boundaries():
    report = _json(P20_6)
    result = P20_7_RESULT.read_text(encoding="utf-8")

    assert report["safety_boundary"]["runtime_deployment"] is False
    assert report["safety_boundary"]["live_source_expansion"] is False
    assert report["safety_boundary"]["paid_or_shared_resources_authorized"] is False
    assert report["safety_boundary"]["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert "P13.5/P13.6 remain the current factual-verification authority" in result
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))


def test_p20_7_canonical_closure_remains_immutable_after_explicit_phase21_progress():
    state = _json(STATE)
    handoff = HANDOFF.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    result = P20_7_RESULT.read_text(encoding="utf-8")
    decision = P21_DECISION.read_text(encoding="utf-8")
    plan = P21_PLAN.read_text(encoding="utf-8")
    approval = _json(P21_APPROVAL)

    # Historical Phase 20 closure facts remain exact and immutable even after the current state advances.
    assert state["phases"]["20"] == "PHASE_20_GLOBAL_SOURCE_COVERAGE_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS"
    assert state["phase20"]["state"] == "VALIDATED_WITH_KNOWN_LIMITATIONS"
    assert state["phase20"]["gate"] == "P20_GLOBAL_SOURCE_COVERAGE_VALIDATED"
    assert state["phase20"]["decision"] == "PASS_WITH_KNOWN_LIMITATIONS"
    assert state["phase20"]["historical_next_strategic_step"] == "ROADMAP_DECISION_REQUIRED"
    assert state["phase20"]["superseded_by"] == "OWNER_APPROVED_PHASE_21_2026-09-16"
    assert "No subsequent strategic phase is authorized by this result" in result

    # Current state may advance only because a separate owner-approved Phase 21 decision exists.
    major, minor = state["roadmap"]["state_sync_version"].split(".", 1)
    assert major == "4" and int(minor) >= 38
    assert state["roadmap"]["current_position"].startswith("PHASE_21_")
    assert "P21.0" in state["phase21"]["validated_sequence"]
    assert P21_DECISION.exists()
    assert P21_PLAN.exists()
    assert "Authorization basis: owner approval" in decision
    assert "P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED" in decision
    assert "DEPLOYED_RUNTIME_SOURCE_EXPANSION = NO" in plan
    assert "P21_5_BOUNDED_PUBLIC_FREE_ONBOARDING = AUTHORIZED_WAVE_A" in plan
    assert approval["owner_decision"] == "APPROVED_GLOBAL_BASELINE"
    assert "P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json" in handoff
    assert "P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED" in handoff

    assert "Version: 4." in roadmap
    assert "State: `VALIDATED_WITH_KNOWN_LIMITATIONS / CLOSED`" in roadmap
    assert "Gate: `P20_GLOBAL_SOURCE_COVERAGE_VALIDATED`" in roadmap
    assert "Phase 20: `PHASE_20_GLOBAL_SOURCE_COVERAGE_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`" in roadmap
    assert state["phases"]["21"] in roadmap
