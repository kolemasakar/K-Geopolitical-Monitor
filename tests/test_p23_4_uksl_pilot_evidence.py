"""Historical read-only P23.4 UKSL pilot: do not equate partial range with coverage."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/P23_4_UKSL_CONTROLLED_READONLY_PILOT_2026-09-25.json"
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"


def test_uksl_measured_pilot_captures_distinct_designations_not_csv_rows():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    observed = evidence["identity_regression"]
    assert evidence["acquisition"]["status"] == 206
    assert evidence["acquisition"]["bytes_received"] == 1_500_000
    assert evidence["acquisition"]["existing_transport_max_bytes"] == 2_000_000
    assert observed["captured_fully_terminated_csv_rows"] == 1827
    assert observed["captured_distinct_official_unique_ids"] == 38
    assert observed["original_distinct_item_ids_in_first_100"] == 1
    assert observed["live_bounded_fetch_items_after_fix"] == 38
    assert observed["live_bounded_fetch_distinct_ids"] == 38
    assert observed["duplicate_inflation_after_fix"] == 0


def test_uksl_partial_range_never_claims_full_coverage_or_freshness():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    acceptance = evidence["qualification"]
    assert acceptance["range_is_complete_document"] is False
    assert acceptance["full_designation_coverage_claimed"] is False
    assert acceptance["freshness_credit_granted"] is False
    assert acceptance["full_p20_5_eligibility_pass"] is False
    assert evidence["p23_4_gate_validated"] is False
    assert evidence["safety_boundary"]["repository_source_activation_delta"] == 0


def test_foreign_vpn_route_is_owner_allowed_but_not_silently_configured():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    route = evidence["russian_government_route"]
    assert route["owner_allows_non_ukraine_vpn"] is True
    assert route["tailscale_exit_nodes_available"] == 0
    assert route["vpn_configured"] is False
    assert route["telegram_source_activation"] is False


def test_pilot_state_roadmap_and_handoff_preserve_historical_gate():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    pilot_state = state["phase23_p23_4_uksl_controlled"]
    assert pilot_state["state"] == evidence["qualification"]["decision"]
    assert pilot_state["uk_sanctions_live_distinct_designations"] == 38
    assert pilot_state["p23_4_gate_validated"] is False
    assert pilot_state["source_activation_delta"] == 0
    assert pilot_state["verification_authority"] == "P13.5/P13.6"
    roadmap = ROADMAP.read_text(encoding="utf-8")
    major, minor = state["roadmap"]["state_sync_version"].split(".")
    assert major == "4" and int(minor) >= 66
    assert f"Version: {state['roadmap']['state_sync_version']}" in roadmap
    assert state["roadmap"]["current_position"] in roadmap
    assert "UKSL_CONTROLLED_PILOT_PASS_WITH_MATERIAL_LIMITATIONS" in HANDOFF.read_text(encoding="utf-8")
