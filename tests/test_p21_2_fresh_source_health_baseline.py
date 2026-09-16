import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/P21_2_FRESH_SOURCE_HEALTH_BASELINE_OWNER_LOCAL_2026-09-16.json"
RESULT = ROOT / "docs/implementation/P21_2_FRESH_SOURCE_HEALTH_BASELINE_RESULT.md"
SCRIPT = ROOT / "scripts/p21_2_measure_fresh_health.py"


def test_p21_2_snapshot_is_fresh_complete_and_vantage_bound():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload["measured_source_count"] == 10
    assert payload["unmeasured_source_count"] == 0
    assert payload["collection"]["source_success_count"] == 8
    assert payload["collection"]["source_failure_count"] == 2
    assert payload["collection"]["item_count"] == 260
    assert all(source["measurement_freshness"] == "CURRENT" for source in payload["sources"])
    measurement = payload["phase21_measurement"]
    assert measurement["measurement_vantage"] == "OWNER_LOCAL_KGM_E4_PILOT_ISOLATED_CANONICAL_CHECKOUT"
    assert measurement["canonical_checkout_sha"] == "3ff9df391f31ff8c7d19e6c229e4647e8dc88597"
    assert measurement["production_runtime_mutated"] is False
    assert measurement["runtime_deployment"] is False
    assert measurement["service_restart"] is False
    assert measurement["source_expansion"] is False


def test_p21_2_measured_degradation_is_not_hidden():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    by_source = {source["source_id"]: source for source in payload["sources"]}
    assert by_source["gdelt-doc-2"]["operational_state"] == "UNAVAILABLE"
    assert by_source["gdelt-doc-2"]["error_class"] == "TRANSPORT"
    assert by_source["eu-parliament-press-releases"]["operational_state"] == "UNAVAILABLE"
    assert by_source["eu-parliament-press-releases"]["error_class"] == "PARSER"
    assert by_source["eu-commission-press-corner"]["operational_state"] == "HEALTHY"
    assert by_source["eu-commission-press-corner"]["content_freshness"] == "STALE"
    assert by_source["osce-latest-news"]["operational_state"] == "HEALTHY"
    assert by_source["osce-latest-news"]["content_freshness"] == "STALE"


def test_p21_2_measurement_reuses_ephemeral_health_stack_and_truth_boundary():
    script = SCRIPT.read_text(encoding="utf-8")
    result = RESULT.read_text(encoding="utf-8")
    assert "TemporaryDirectory" in script
    assert "install_phase12_health_probe_governance" in script
    assert "SourceHealthEgressService" in script
    assert "does not claim deployed runtime state" in script
    assert "P13.5/P13.6 remains factual-verification authority" in result
