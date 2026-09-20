import json
from pathlib import Path

from kgeopolitical_monitor.p22_3_b1_source_pack import B1_REPOSITORY_ACTIVE_SOURCE_IDS

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
EVIDENCE = ROOT / "docs/evidence/P23_1_B1_BLOCKER_REMEDIATION_READINESS_2026-09-20.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p23_1_state_and_gate_are_canonical():
    state = load(STATE)
    p = state["phase23_p23_1"]
    assert state["roadmap"]["state_sync_version"] == "4.62"
    assert state["roadmap"]["current_position"] == "PHASE_23_P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED"
    assert p["state"] == "VALIDATED_WITH_PARTIAL_REMEDIATION"
    assert p["gate"] == "P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED"
    assert p["next_gate"] == "P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED"


def test_p23_1_readiness_preserves_activation_and_resource_boundaries():
    evidence = load(EVIDENCE)
    assert evidence["uk_sanctions_list"]["exact_branch_live_probe"]["status"] == "SUCCESS"
    assert evidence["uk_sanctions_list"]["exact_branch_live_probe"]["item_count"] == 100
    assert evidence["uk_sanctions_list"]["exact_branch_live_probe"]["transport_limit_relaxed"] is False
    assert evidence["uk_sanctions_list"]["repository_activation"] is False
    assert evidence["russian_government"]["readiness"] == "BLOCKED_HTTPS_TRANSPORT_TIMEOUT"
    assert evidence["russian_government"]["http_fallback_allowed"] is False
    assert evidence["source_activation_delta"] == 0
    assert evidence["acquisition_resource_limit_relaxed"] is False
    assert B1_REPOSITORY_ACTIVE_SOURCE_IDS == (
        "ofac-recent-actions-en",
        "white-house-briefings-en",
    )


def test_p23_1_roadmap_and_handoff_advance_only_to_p23_2_readiness():
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "Version: 4.62" in roadmap
    assert "P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED" in roadmap
    assert "P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED" in roadmap
    assert "PHASE_23_P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED" in handoff
    assert "P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED" in handoff
