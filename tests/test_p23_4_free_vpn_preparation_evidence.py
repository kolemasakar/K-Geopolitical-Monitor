"""Free foreign VPN preparation is repository-only and does not close P23.4."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / "ops/p23_4_govru_free_vpn"
EVIDENCE = ROOT / "docs/evidence/P23_4_FREE_NON_UA_VPN_NODE_PREPARATION_2026-09-25.json"
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"


def test_free_vpn_preparation_has_no_external_side_effects_or_paid_resources():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    section = state["phase23_p23_4_govru_free_vpn"]
    assert evidence["state"] == section["state"]
    assert evidence["cloud_account_mutated"] is False
    assert evidence["new_vm_provisioned"] is False
    assert evidence["existing_vm_wireguard_changed"] is False
    assert evidence["production_deployment"] is False
    assert evidence["source_activation_delta"] == 0
    assert section["owner_kgm_runtime_network_modified"] is False
    assert section["vpn_configured"] is False
    assert section["paid_resources_used"] is False


def test_preparation_does_not_falsely_close_expansion_gate():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert state["roadmap"]["current_position"] == (
        "PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED"
    )
    assert state["phase23"]["next_gate"] == "P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED"
    assert state["phase23"]["p23_4_gate_validated"] is False
    assert evidence["p23_4_gate_validated"] is False
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "Version: " + state["roadmap"]["state_sync_version"] in roadmap
    assert state["roadmap"]["current_position"] in roadmap


def test_runbook_requires_tenancy_and_existing_owner_network_gates():
    runbook = (OPS / "README.md").read_text(encoding="utf-8")
    for expected in [
        "Home Region", "50 GB", "Always Free", "source-specific",
        "wg-kgm-govru", "not a host-wide", "separate explicit existing-host network-change gate"
    ]:
        assert expected.lower() in runbook.lower()
    for file in [
        "official_connect_proxy.py",
        "oci_free_guard.py",
        "inventory.template.json",
        "wireguard-node.example.conf",
        "wireguard-kgm-owner.example.conf",
        "kgm-govru-egress.service.example",
    ]:
        assert (OPS / file).is_file()
    assert "REPOSITORY_PREPARED_TENANCY_PREFLIGHT_REQUIRED" in (
        HANDOFF.read_text(encoding="utf-8")
    )
