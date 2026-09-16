from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P20_0_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_1_RECONCILIATION_PATH = ROOT / "docs" / "evidence" / "P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json"
P20_3_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_3_source_independence.schema.json"
P20_3_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json"
P20_3_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "p20" / "p20_3_independence_synthetic.json"
P13_3_IMPLEMENTATION_PATH = ROOT / "src" / "kgeopolitical_monitor" / "semantic_evidence.py"
MIGRATIONS_DIR = ROOT / "migrations"


KNOWN_RELATIONS = {"ORIGINAL", "SYNDICATED_COPY", "AGGREGATOR_COPY", "DERIVED"}
COPY_RELATIONS = {"SYNDICATED_COPY", "AGGREGATOR_COPY", "DERIVED"}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate(case: dict) -> dict:
    observations = case["source_observations"]
    source_count = len(observations)
    known_origin = [
        item
        for item in observations
        if item["origin_identity_state"] == "EXPLICIT_SINGLE_ORIGIN"
        and item["origin_group_id"] is not None
    ]
    known_origin_source_count = len(known_origin)
    unknown_origin_source_count = source_count - known_origin_source_count
    known_origin_group_count = len({item["origin_group_id"] for item in known_origin})
    complete = all(
        item["origin_identity_state"] == "EXPLICIT_SINGLE_ORIGIN"
        and item["origin_group_id"] is not None
        and item["syndication_or_copy_relation"] in KNOWN_RELATIONS
        for item in observations
    )

    if complete:
        origin_counts = Counter(item["origin_group_id"] for item in observations)
        independent_origin_count = len(origin_counts)
        copy_chain_count = sum(
            item["syndication_or_copy_relation"] in COPY_RELATIONS for item in observations
        )
        dominant_origin_share = round(max(origin_counts.values()) / source_count, 10)
        redundancy_score = round(source_count / independent_origin_count, 10)
        evaluation_completeness = "COMPLETE"
        if source_count == 1:
            monoculture_state = "NO_REDUNDANCY"
        elif independent_origin_count == 1:
            monoculture_state = "CONFIRMED_MONOCULTURE"
        else:
            monoculture_state = "CONFIRMED_DIVERSE"

        thresholds = case["policy_thresholds"]
        minimum_origins = thresholds["minimum_independent_origin_count"]
        maximum_share = thresholds["maximum_dominant_origin_share"]
        monoculture_risk = (
            None
            if minimum_origins is None or maximum_share is None
            else independent_origin_count < minimum_origins
            or dominant_origin_share > maximum_share
        )
    else:
        independent_origin_count = None
        copy_chain_count = None
        dominant_origin_share = None
        redundancy_score = None
        evaluation_completeness = "PARTIAL" if known_origin_source_count else "UNKNOWN"
        monoculture_state = "UNKNOWN"
        monoculture_risk = None

    return {
        "source_count": source_count,
        "known_origin_source_count": known_origin_source_count,
        "unknown_origin_source_count": unknown_origin_source_count,
        "known_origin_group_count": known_origin_group_count,
        "independent_origin_count": independent_origin_count,
        "copy_chain_count": copy_chain_count,
        "dominant_origin_share": dominant_origin_share,
        "redundancy_score": redundancy_score,
        "evaluation_completeness": evaluation_completeness,
        "monoculture_state": monoculture_state,
        "monoculture_risk": monoculture_risk,
    }


def test_p20_3_current_ten_source_portfolio_remains_unknown_not_inferred_independent():
    p20_0 = _json(P20_0_BASELINE_PATH)
    p20_3 = _json(P20_3_BASELINE_PATH)
    baseline_ids = {item["source_id"] for item in p20_0["sources"]}
    p20_3_ids = {item["source_id"] for item in p20_3["sources"]}

    assert p20_3["source_count"] == 10
    assert baseline_ids == p20_3_ids
    assert p20_3["known_origin_source_count"] == 0
    assert p20_3["unknown_origin_source_count"] == 10
    assert p20_3["independent_origin_count"] is None
    assert p20_3["copy_chain_count"] is None
    assert p20_3["dominant_origin_share"] is None
    assert p20_3["redundancy_score"] is None
    assert p20_3["monoculture_state"] == "UNKNOWN"
    assert all(item["origin_group_id"] is None for item in p20_3["sources"])
    assert all(item["syndication_or_copy_relation"] is None for item in p20_3["sources"])


def test_p20_3_synthetic_cases_evaluate_deterministically():
    fixture = _json(P20_3_FIXTURE_PATH)

    assert fixture["schema_version"] == "kgm.p20.3.independence.synthetic.v1"
    assert len(fixture["cases"]) == 5
    for case in fixture["cases"]:
        assert _evaluate(case) == case["expected_evaluation"]


def test_p20_3_syndication_derivation_and_aggregation_do_not_create_origins():
    cases = {item["cell_id"]: item for item in _json(P20_3_FIXTURE_PATH)["cases"]}
    monoculture = _evaluate(cases["synthetic.monoculture"])

    assert monoculture["source_count"] == 3
    assert monoculture["independent_origin_count"] == 1
    assert monoculture["copy_chain_count"] == 2
    assert monoculture["dominant_origin_share"] == 1.0
    assert monoculture["redundancy_score"] == 3.0
    assert monoculture["monoculture_state"] == "CONFIRMED_MONOCULTURE"
    assert monoculture["monoculture_risk"] is True


def test_p20_3_unknown_or_mixed_origin_blocks_precise_metrics():
    cases = {item["cell_id"]: item for item in _json(P20_3_FIXTURE_PATH)["cases"]}

    for cell_id in ("synthetic.unknown-origin", "synthetic.mixed-origin"):
        result = _evaluate(cases[cell_id])
        assert result["evaluation_completeness"] == "PARTIAL"
        assert result["independent_origin_count"] is None
        assert result["copy_chain_count"] is None
        assert result["dominant_origin_share"] is None
        assert result["redundancy_score"] is None
        assert result["monoculture_state"] == "UNKNOWN"
        assert result["monoculture_risk"] is None


def test_p20_3_contract_keeps_unknown_metrics_nullable_and_policy_thresholds_configurable():
    schema = _json(P20_3_SCHEMA_PATH)
    props = schema["properties"]
    thresholds = schema["$defs"]["policyThresholds"]["properties"]

    assert "null" in props["independent_origin_count"]["type"]
    assert "null" in props["copy_chain_count"]["type"]
    assert "null" in props["dominant_origin_share"]["type"]
    assert "null" in props["redundancy_score"]["type"]
    assert "null" in props["monoculture_risk"]["type"]
    assert "null" in thresholds["minimum_independent_origin_count"]["type"]
    assert "null" in thresholds["maximum_dominant_origin_share"]["type"]


def test_p20_3_remains_aligned_with_p13_fail_closed_independence_semantics():
    p13_3 = P13_3_IMPLEMENTATION_PATH.read_text(encoding="utf-8")
    p20_1_rules = {
        item["p20_field"]: item["rule"]
        for item in _json(P20_1_RECONCILIATION_PATH)["field_reconciliation"]
    }
    principles = _json(P20_3_BASELINE_PATH)["principles"]

    assert 'INDEPENDENCE_STATES = ("INDEPENDENT", "NOT_INDEPENDENT", "UNKNOWN", "MIXED")' in p13_3
    assert "EXPLICIT_DISTINCT_UNDERLYING_ORIGINS" in p13_3
    assert "INSUFFICIENT_PROVENANCE" in p13_3
    assert p20_1_rules["origin_group_id"] == "NULL_UNLESS_EXPLICIT_ORIGIN_EVIDENCE_EXISTS"
    assert p20_1_rules["syndication_or_copy_relation"] == "NULL_UNLESS_EXPLICIT_PROVENANCE_EVIDENCE_EXISTS"
    assert principles["absence_of_known_derivation_does_not_prove_independence"] is True
    assert principles["p13_claim_independence_remains_separate_from_p20_portfolio_topology"] is True


def test_p20_3_preserves_runtime_and_resource_boundaries():
    safety = _json(P20_3_BASELINE_PATH)["safety_boundary"]

    assert safety["live_source_expansion"] is False
    assert safety["live_ingest_change"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
