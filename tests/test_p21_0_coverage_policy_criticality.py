from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "contracts" / "p21_0_coverage_policy_criticality.schema.json"
PROPOSAL = ROOT / "docs" / "evidence" / "P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json"
P20_SCHEMA = ROOT / "docs" / "contracts" / "p20_2_coverage_matrix_policy.schema.json"
P20_MATRIX = ROOT / "docs" / "evidence" / "P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json"
AUDIT = ROOT / "docs" / "evidence" / "P21_0_EXISTING_POLICY_REUSE_AUDIT_2026-09-16.md"
CONTRACT = ROOT / "docs" / "implementation" / "P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT.md"
MATRIX = ROOT / "docs" / "implementation" / "P21_0_VALIDATION_MATRIX.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p21_0_extension_reuses_p20_policy_semantics():
    p20 = _json(P20_SCHEMA)
    p21 = _json(SCHEMA)

    p20_states = p20["properties"]["default_requirement_state"]["enum"]
    p21_states = p21["properties"]["default_requirement_state"]["enum"]
    assert p21_states == p20_states == ["REQUIRED", "OPTIONAL", "NOT_REQUIRED", "UNSET"]

    p20_source_types = p20["$defs"]["sourceType"]["enum"]
    p21_source_types = p21["$defs"]["sourceType"]["enum"]
    assert p21_source_types == p20_source_types

    for field in (
        "minimum_source_count",
        "minimum_independent_origin_count",
        "minimum_healthy_source_count",
        "maximum_stale_share",
        "maximum_dominant_origin_share",
    ):
        assert field in p20["$defs"]["thresholds"]["properties"]
        assert field in p21["$defs"]["thresholds"]["properties"]


def test_p21_0_adds_authority_criticality_and_freshness_without_rewriting_p20():
    p21 = _json(SCHEMA)
    p20_matrix = _json(P20_MATRIX)

    assert p21["properties"]["authority_state"]["enum"] == ["DRAFT", "APPROVED", "RETIRED"]
    assert p21["$defs"]["criticality"]["enum"] == ["CRITICAL", "HIGH", "STANDARD", "WATCH", "NONE"]
    thresholds = p21["$defs"]["thresholds"]["properties"]
    assert "maximum_collection_latency_minutes" in thresholds
    assert "maximum_content_freshness_minutes" in thresholds

    assert p20_matrix["policy_state"] == "UNSET"
    assert p20_matrix["cell_count"] == 17
    assert {cell["coverage_status"] for cell in p20_matrix["cells"]} == {"POLICY_UNSET"}


def test_p21_0_draft_policy_is_explicitly_non_authoritative():
    policy = _json(PROPOSAL)

    assert policy["authority_state"] == "DRAFT"
    assert policy["effective_from"] is None
    assert policy["default_requirement_state"] == "UNSET"
    assert policy["target_cells"]
    assert any(cell["cell_id"] == "middle_east.ar.national_media" for cell in policy["target_cells"])
    assert any(cell["cell_id"] == "ukraine.uk.official_government" for cell in policy["target_cells"])


def test_p21_0_draft_policy_cells_satisfy_contract_invariants():
    policy = _json(PROPOSAL)
    allowed_states = {"REQUIRED", "OPTIONAL", "NOT_REQUIRED", "UNSET"}
    allowed_criticality = {"CRITICAL", "HIGH", "STANDARD", "WATCH", "NONE"}
    seen = set()

    for cell in policy["target_cells"]:
        assert cell["cell_id"] not in seen
        seen.add(cell["cell_id"])
        assert cell["requirement_state"] in allowed_states
        assert cell["criticality"] in allowed_criticality
        assert cell["policy_reason"].strip()
        assert cell["policy_basis"]
        thresholds = cell["thresholds"]
        assert "maximum_collection_latency_minutes" in thresholds
        assert "maximum_content_freshness_minutes" in thresholds
        if cell["requirement_state"] == "REQUIRED":
            assert cell["criticality"] != "NONE"
            assert thresholds["minimum_source_count"] is not None
            assert thresholds["minimum_healthy_source_count"] is not None
        if cell["requirement_state"] == "NOT_REQUIRED":
            assert cell["criticality"] == "NONE"


def test_p21_0_global_draft_has_explicit_macroregional_baseline():
    policy = _json(PROPOSAL)
    scopes = {cell["geography_scope"] for cell in policy["target_cells"]}
    languages = {cell["language"] for cell in policy["target_cells"]}
    source_types = {cell["source_type"] for cell in policy["target_cells"]}

    assert policy["version"] == "0.2-draft-global-baseline"
    assert len(policy["target_cells"]) == 33
    assert {
        "UKRAINE",
        "RUSSIA",
        "EUROPE",
        "MIDDLE_EAST",
        "EAST_ASIA",
        "SOUTHEAST_ASIA",
        "SOUTH_ASIA",
        "CENTRAL_ASIA",
        "CAUCASUS",
        "NORTH_AFRICA",
        "SUB_SAHARAN_AFRICA",
        "NORTH_AMERICA",
        "LATIN_AMERICA",
        "BRAZIL",
        "OCEANIA",
        "GLOBAL",
    }.issubset(scopes)
    assert {"uk", "ru", "ar", "zh", "ja", "ko", "hi", "id", "es", "pt", "fr", "en"}.issubset(languages)
    assert {"WIRE_SERVICE", "SANCTIONS_REGULATORY", "ECONOMIC_ENERGY", "THINK_TANK_RESEARCH"}.issubset(source_types)


def test_p21_0_global_draft_does_not_claim_exhaustive_world_coverage():
    policy = _json(PROPOSAL)
    assert policy["default_requirement_state"] == "UNSET"

    caucasus = next(cell for cell in policy["target_cells"] if cell["cell_id"] == "caucasus.multi.regional_local_media")
    assert "transitional" in " ".join(caucasus["policy_basis"]).lower()

    osint = next(cell for cell in policy["target_cells"] if cell["cell_id"] == "global.multi.public_osint")
    assert "not exhaustive-global-coverage proof" in " ".join(osint["policy_basis"])


def test_p21_0_unobserved_target_cells_are_policy_not_invented_evidence():
    observed_ids = {cell["cell_id"] for cell in _json(P20_MATRIX)["cells"]}
    proposal_ids = {cell["cell_id"] for cell in _json(PROPOSAL)["target_cells"]}

    unobserved_targets = proposal_ids - observed_ids
    assert "ukraine.uk.official_government" in unobserved_targets
    assert "russia.ru.official_government" in unobserved_targets
    assert "middle_east.ar.national_media" in unobserved_targets
    assert "east_asia.zh.national_media" in unobserved_targets
    assert "latin_america.es.national_media" in unobserved_targets

    contract = CONTRACT.read_text(encoding="utf-8")
    assert "Policy never creates evidence automatically" in contract
    assert "A `DRAFT` policy" in contract


def test_p21_0_validation_matrix_keeps_gate_pending_until_policy_approval():
    audit = AUDIT.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")

    assert "REUSE_P20_2_POLICY_CONTRACT = YES" in audit
    assert "MUTATE_P20_HISTORICAL_EVIDENCE = NO" in audit
    assert "P21_0_GATE = NOT_YET_GRANTED" in contract
    assert "Target policy approved" in matrix
    assert "PENDING" in matrix
    assert "must not be treated as canonical gaps until separately approved" in matrix
