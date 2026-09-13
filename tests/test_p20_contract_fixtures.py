from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "p20"
CONTRACT_ROOT = ROOT / "docs" / "contracts"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_machine_contracts_and_fixtures_are_valid_json():
    paths = [
        CONTRACT_ROOT / "p20_source_record.schema.json",
        CONTRACT_ROOT / "p20_coverage_policy.schema.json",
        CONTRACT_ROOT / "p20_coverage_report.schema.json",
        FIXTURE_ROOT / "source_registry_valid.json",
        FIXTURE_ROOT / "coverage_policy_valid.json",
        FIXTURE_ROOT / "coverage_report_synthetic.json",
    ]

    for path in paths:
        assert isinstance(load_json(path), dict), path


def test_fixture_endpoints_are_synthetic_and_non_routable():
    registry = load_json(FIXTURE_ROOT / "source_registry_valid.json")
    endpoints = [source["primary_domain_or_endpoint"] for source in registry["sources"]]

    assert endpoints
    assert all(".invalid/" in endpoint for endpoint in endpoints)


def test_source_count_is_not_independent_origin_count():
    registry = load_json(FIXTURE_ROOT / "source_registry_valid.json")
    active = [source for source in registry["sources"] if source["active_for_coverage"]]
    origin_groups = {source["origin_group_id"] for source in active}

    assert len(active) == 3
    assert len(origin_groups) == 2
    assert len(active) != len(origin_groups)


def test_syndicated_copy_shares_origin_group_with_original():
    registry = load_json(FIXTURE_ROOT / "source_registry_valid.json")
    by_id = {source["source_id"]: source for source in registry["sources"]}

    original = by_id["synthetic-wire-alpha"]
    copy = by_id["synthetic-copy-alpha"]

    assert original["syndication_or_copy_relation"] == "ORIGINAL"
    assert copy["syndication_or_copy_relation"] == "SYNDICATED_COPY"
    assert original["origin_group_id"] == copy["origin_group_id"]


def test_inactive_historical_source_is_retained_but_excluded_from_active_coverage():
    registry = load_json(FIXTURE_ROOT / "source_registry_valid.json")
    historical = next(source for source in registry["sources"] if source["source_id"] == "synthetic-history-gamma")

    assert historical["collection_status"] == "RETIRED"
    assert historical["health_status"] == "DISABLED_EXPECTED"
    assert historical["active_for_coverage"] is False


def test_policy_requires_independent_origins_separately_from_source_count():
    policy = load_json(FIXTURE_ROOT / "coverage_policy_valid.json")
    required = next(cell for cell in policy["cells"] if cell["required"])

    assert required["minimum_source_count"] == 3
    assert required["minimum_independent_origin_count"] == 2


def test_synthetic_report_exposes_explainable_monoculture_and_collection_degradation():
    report = load_json(FIXTURE_ROOT / "coverage_report_synthetic.json")
    by_status = {cell["status"]: cell for cell in report["cells"]}

    monoculture = by_status["MONOCULTURE_RISK"]
    degraded = by_status["DEGRADED_COLLECTION"]

    assert monoculture["source_count"] == 3
    assert monoculture["independent_origin_count"] == 1
    assert "INDEPENDENT_ORIGIN_REQUIREMENT_NOT_MET" in monoculture["reason_codes"]
    assert degraded["stale_source_count"] > 0
    assert "STALE_SHARE_EXCEEDED" in degraded["reason_codes"]
