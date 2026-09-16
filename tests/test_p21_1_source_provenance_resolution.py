from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "contracts" / "p21_1_source_provenance_resolution.schema.json"
EVIDENCE = ROOT / "docs" / "evidence" / "P21_1_SOURCE_PROVENANCE_RESOLUTION_2026-09-16.json"
P20_BASELINE = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_INDEPENDENCE = ROOT / "docs" / "evidence" / "P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json"
CONTRACT = ROOT / "docs" / "implementation" / "P21_1_SOURCE_PROVENANCE_RESOLUTION_CONTRACT.md"
PLUGIN_DECISION = ROOT / "docs" / "decisions" / "OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p21_1_reviews_exact_current_governed_portfolio_without_mutating_p20_history():
    evidence = _json(EVIDENCE)
    baseline = _json(P20_BASELINE)
    p20 = _json(P20_INDEPENDENCE)

    baseline_ids = {source["source_id"] for source in baseline["sources"]}
    resolved_ids = {record["source_id"] for record in evidence["records"]}

    assert len(baseline_ids) == 10
    assert resolved_ids == baseline_ids
    assert evidence["source_count"] == evidence["reviewed_source_count"] == 10

    # P20 remains historical closure evidence.
    assert p20["known_origin_source_count"] == 0
    assert p20["unknown_origin_source_count"] == 10
    assert p20["known_origin_group_count"] == 0
    assert p20["independent_origin_count"] is None


def test_p21_1_origin_state_distribution_is_explicit_and_fail_closed():
    evidence = _json(EVIDENCE)
    records = evidence["records"]

    assert evidence["publisher_identity_explicit_count"] == 10
    assert evidence["explicit_single_origin_source_count"] == 3
    assert evidence["mixed_origin_source_count"] == 6
    assert evidence["derived_multi_origin_source_count"] == 1
    assert evidence["unknown_origin_state_count"] == 0
    assert evidence["confirmed_source_level_origin_group_count"] == 3
    assert evidence["precise_portfolio_independent_origin_count"] is None

    states = [record["stream_origin_state"] for record in records]
    assert states.count("EXPLICIT_SINGLE_ORIGIN") == 3
    assert states.count("MIXED_ORIGIN") == 6
    assert states.count("DERIVED_MULTI_ORIGIN") == 1


def test_p21_1_single_origin_groups_are_limited_to_supported_direct_institutional_streams():
    evidence = _json(EVIDENCE)
    grouped = {
        record["source_id"]: record["origin_group_id"]
        for record in evidence["records"]
        if record["origin_group_id"] is not None
    }

    assert grouped == {
        "eu-commission-press-corner": "official:european-commission",
        "eu-parliament-press-releases": "official:european-parliament",
        "osce-latest-news": "official:osce",
    }

    for record in evidence["records"]:
        if record["stream_origin_state"] != "EXPLICIT_SINGLE_ORIGIN":
            assert record["origin_group_id"] is None
            assert record["independence_credit_state"] != "SOURCE_LEVEL_ORIGIN_GROUP_CONFIRMED"


def test_p21_1_gdelt_is_derived_and_receives_no_independence_credit():
    evidence = _json(EVIDENCE)
    gdelt = next(record for record in evidence["records"] if record["source_id"] == "gdelt-doc-2")

    assert gdelt["stream_origin_state"] == "DERIVED_MULTI_ORIGIN"
    assert gdelt["syndication_or_copy_relation"] == "DERIVED"
    assert gdelt["origin_group_id"] is None
    assert gdelt["independence_credit_state"] == "NO_INDEPENDENCE_CREDIT"
    assert "gdeltproject.org/about.html" in " ".join(gdelt["evidence_references"])


def test_p21_1_mixed_media_and_platform_streams_require_item_level_provenance():
    evidence = _json(EVIDENCE)
    records = {record["source_id"]: record for record in evidence["records"]}

    for source_id in (
        "consilium-press-releases",
        "haberturk-tr",
        "meduza-ru",
        "rmf24-pl",
        "uk-government-news-communications",
        "ukrainska-pravda-uk",
    ):
        record = records[source_id]
        assert record["stream_origin_state"] == "MIXED_ORIGIN"
        assert record["origin_group_id"] is None
        assert record["independence_credit_state"] == "ITEM_LEVEL_PROVENANCE_REQUIRED"


def test_p21_1_contract_preserves_truth_and_plugin_routing_boundaries():
    evidence = _json(EVIDENCE)
    contract = CONTRACT.read_text(encoding="utf-8")
    plugin_decision = PLUGIN_DECISION.read_text(encoding="utf-8")

    assert evidence["principles"]["publisher_identity_not_underlying_origin"] is True
    assert evidence["principles"]["official_statement_not_underlying_event_truth"] is True
    assert evidence["principles"]["derived_index_gets_no_independence_credit"] is True
    assert evidence["principles"]["plugin_app_connector_mcp_routing_is_provenance_neutral"] is True

    assert "P13.5/P13.6 remain the only canonical factual-verification authority" in contract
    assert "PLUGIN_ROUTE_CREATES_INDEPENDENCE = NO" in contract
    assert "CONNECTOR_ROUTE_CREATES_INDEPENDENCE = NO" in contract
    assert "CUSTOM_MCP_ROUTE_CREATES_INDEPENDENCE = NO" in contract
    assert "PRIMARY_CHATGPT_SURFACE = PLUGIN" in plugin_decision


def test_p21_1_schema_blocks_origin_group_on_mixed_or_derived_streams_by_contract():
    schema = _json(SCHEMA)
    origin_states = schema["properties"]["stream_origin_state"]["enum"]
    credit_states = schema["properties"]["independence_credit_state"]["enum"]

    assert origin_states == [
        "EXPLICIT_SINGLE_ORIGIN",
        "MIXED_ORIGIN",
        "DERIVED_MULTI_ORIGIN",
        "UNKNOWN_ORIGIN",
    ]
    assert "SOURCE_LEVEL_ORIGIN_GROUP_CONFIRMED" in credit_states
    assert "ITEM_LEVEL_PROVENANCE_REQUIRED" in credit_states
    assert "NO_INDEPENDENCE_CREDIT" in credit_states


def test_p21_1_safety_boundary_remains_repository_only():
    safety = _json(EVIDENCE)["safety_boundary"]
    assert safety == {
        "live_source_expansion": False,
        "live_ingest_change": False,
        "runtime_deployment": False,
        "service_restart": False,
        "migration_033": "NOT_CREATED / NOT_PREAUTHORIZED",
        "paid_or_shared_resources_authorized": False,
        "plugin_build": False,
        "plugin_publication": False,
    }
