import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
AUDIT = ROOT / "docs/analysis/POST_PHASE_21_STRATEGIC_AUDIT_2026-09-19.md"
PROPOSAL = ROOT / "docs/decisions/POST_PHASE_21_ROADMAP_DECISION_PROPOSAL_2026-09-19.md"


def test_post_phase21_strategic_audit_remains_recorded_after_owner_phase22_decision():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["post_phase21_strategic_audit"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 46
    assert s["phase21"]["next_gate"] == "ROADMAP_DECISION_REQUIRED"

    assert x["state"] == "COMPLETED"
    assert x["decision_state"] in {"ROADMAP_DECISION_REQUIRED", "SUPERSEDED_BY_OWNER_APPROVED_PHASE_22"}
    assert x["primary_constraints"] == [
        "REQUIRED_COVERAGE_GAPS",
        "SEMANTIC_IMPACT_NOT_OBSERVED",
    ]
    assert x["recommended_direction"] == "BOUNDED_OWNER_OPERATIONAL_EVIDENCE_PLUS_HIGH_PRIORITY_SOURCE_EXPANSION"
    if x["decision_state"] == "SUPERSEDED_BY_OWNER_APPROVED_PHASE_22":
        assert x["phase22_created"] is True
        assert x["phase22_authorized"] is True
        assert "22" in s["phases"]


def test_post_phase21_proposal_preserves_owner_runtime_and_resource_gates():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["post_phase21_strategic_audit"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    proposal = PROPOSAL.read_text(encoding="utf-8")

    assert AUDIT.exists()
    assert PROPOSAL.exists()
    sync_version = s["roadmap"]["state_sync_version"]
    assert f"Version: {sync_version}" in roadmap
    assert "Post-Phase-21 Strategic Audit" in roadmap
    assert "POST_PHASE_21" in handoff
    assert "Phase 22 — Operational Evidence Pilot & High-Priority Coverage Expansion" in audit
    assert "PROPOSED / OWNER_DECISION_REQUIRED" in proposal

    assert x["owner_operational_activation_authorized"] is False
    assert x["wave_b_onboarding_authorized"] is False
    assert x["paid_or_shared_resources_authorized"] is False
    assert x["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert x["production_live"] == "NOT_OPERATIONAL"
    assert x["plugin_publication_authorized"] is False

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
