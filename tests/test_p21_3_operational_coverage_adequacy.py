import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "evidence" / "P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_2026-09-16.json"
POLICY = ROOT / "docs" / "evidence" / "P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json"
PROVENANCE = ROOT / "docs" / "evidence" / "P21_1_SOURCE_PROVENANCE_RESOLUTION_2026-09-16.json"
HEALTH = ROOT / "docs" / "evidence" / "P21_2_FRESH_SOURCE_HEALTH_BASELINE_OWNER_LOCAL_2026-09-16.json"
MIGRATIONS = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p21_3_report_covers_exact_approved_target_set():
    report = _json(REPORT)
    policy = _json(POLICY)
    assert report["schema_version"] == "kgm.p21.3.operational_coverage_adequacy.v1"
    assert report["global_summary"]["target_cell_count"] == 33
    assert {c["cell_id"] for c in report["cells"]} == {c["cell_id"] for c in policy["target_cells"]}
    assert report["global_summary"]["required_cell_count"] == 27
    assert report["global_summary"]["optional_cell_count"] == 6


def test_p21_3_summary_is_explicit_measured_baseline_not_p20_unknown_replay():
    s = _json(REPORT)["global_summary"]
    assert s["status_counts"] == {
        "ADEQUATE": 1,
        "DEGRADED_COLLECTION": 1,
        "MISSING_EXPECTED_COVERAGE": 21,
        "THIN": 10,
    }
    assert s["required_status_counts"] == {
        "ADEQUATE": 1,
        "MISSING_EXPECTED_COVERAGE": 21,
        "THIN": 5,
    }
    assert s["optional_status_counts"] == {"DEGRADED_COLLECTION": 1, "THIN": 5}
    assert s["p20_closure_unknown_cells"] == 17
    assert s["p20_closure_adequate_cells"] == 0
    assert s["p20_closure_confirmed_gap_cells"] == 0


def test_p21_3_eu_cell_is_adequate_only_on_known_lower_bound_and_fresh_policy_thresholds():
    report = {c["cell_id"]: c for c in _json(REPORT)["cells"]}
    eu = report["eu.en.international_organization"]
    assert eu["status"] == "ADEQUATE"
    assert eu["governed_source_count"] == 3
    assert eu["known_independent_origin_lower_bound"] == 2
    assert set(eu["known_origin_groups"]) == {
        "official:european-commission",
        "official:european-parliament",
    }
    assert eu["healthy_source_count"] == 2
    assert eu["stale_or_failed_source_ids"] == ["eu-parliament-press-releases"]
    assert eu["dominant_origin_share_upper_bound"] <= 0.75
    assert eu["reason_codes"] == ["ALL_POLICY_THRESHOLDS_SATISFIED_FAIL_CLOSED"]


def test_p21_3_zero_required_cells_are_confirmed_missing_and_one_source_required_cells_are_thin():
    cells = {c["cell_id"]: c for c in _json(REPORT)["cells"]}
    assert cells["ukraine.uk.official_government"]["status"] == "MISSING_EXPECTED_COVERAGE"
    assert cells["middle_east.ar.national_media"]["status"] == "MISSING_EXPECTED_COVERAGE"
    assert cells["global.en.wire_service"]["status"] == "MISSING_EXPECTED_COVERAGE"
    assert cells["ukraine.uk.national_media"]["status"] == "THIN"
    assert cells["russia.ru.national_media"]["status"] == "THIN"
    assert cells["central_europe.pl.national_media"]["status"] == "THIN"
    assert cells["black_sea.tr.national_media"]["status"] == "THIN"


def test_p21_3_gdelt_degradation_is_preserved_from_fresh_health_evidence():
    report = {c["cell_id"]: c for c in _json(REPORT)["cells"]}
    health = {s["source_id"]: s for s in _json(HEALTH)["sources"]}
    cell = report["global.multi.public_osint"]
    assert cell["status"] == "DEGRADED_COLLECTION"
    assert cell["stale_or_failed_source_ids"] == ["gdelt-doc-2"]
    assert health["gdelt-doc-2"]["operational_state"] == "UNAVAILABLE"
    assert health["gdelt-doc-2"]["error"] == "P12.2 source HTTP error: 429"


def test_p21_3_does_not_invent_independence_for_mixed_or_derived_streams():
    report = _json(REPORT)
    provenance = {r["source_id"]: r for r in _json(PROVENANCE)["records"]}
    assert provenance["ukrainska-pravda-uk"]["independence_credit_state"] == "ITEM_LEVEL_PROVENANCE_REQUIRED"
    assert provenance["gdelt-doc-2"]["independence_credit_state"] == "NO_INDEPENDENCE_CREDIT"
    for cell in report["cells"]:
        assert cell["known_independent_origin_lower_bound"] == len(set(cell["known_origin_groups"]))


def test_p21_3_preserves_truth_runtime_source_expansion_and_migration_boundaries():
    report = _json(REPORT)
    assert report["principles"]["verification_authority"] == "P13.5/P13.6"
    assert report["principles"]["source_count_is_not_independent_origin_count"] is True
    assert report["principles"]["health_and_freshness_are_operational_not_truth"] is True
    safety = report["safety_boundary"]
    assert safety["live_source_expansion"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert safety["plugin_build"] is False
    assert safety["plugin_publication"] is False
    assert not any(path.name.startswith("033_") for path in MIGRATIONS.glob("*.sql"))
