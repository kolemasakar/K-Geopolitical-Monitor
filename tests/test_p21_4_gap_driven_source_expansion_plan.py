import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/evidence/P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_2026-09-16.json"
POLICY = ROOT / "docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json"
BASELINE = ROOT / "docs/evidence/P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_2026-09-16.json"
RESULT = ROOT / "docs/implementation/P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_RESULT.md"
MIGRATIONS = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p21_4_plan_is_exactly_gap_driven_from_p21_3():
    plan = _json(PLAN)
    baseline = _json(BASELINE)
    gaps = {c["cell_id"] for c in baseline["cells"] if c["status"] != "ADEQUATE"}
    assert plan["authority_state"] == "PLANNING_ONLY"
    assert plan["summary"]["gap_cell_count"] == 32
    assert plan["summary"]["adequate_excluded_count"] == 1
    assert {c["cell_id"] for c in plan["gap_cells"]} == gaps
    assert "eu.en.international_organization" not in gaps


def test_p21_4_deficits_are_deterministic_against_approved_policy_thresholds():
    plan = _json(PLAN)
    policy = {c["cell_id"]: c for c in _json(POLICY)["target_cells"]}
    baseline = {c["cell_id"]: c for c in _json(BASELINE)["cells"]}
    for row in plan["gap_cells"]:
        p = policy[row["cell_id"]]["thresholds"]
        b = baseline[row["cell_id"]]
        assert row["source_path_deficit"] == max((p["minimum_source_count"] or 0) - b["governed_source_count"], 0)
        assert row["healthy_source_deficit"] == max((p["minimum_healthy_source_count"] or 0) - b["healthy_source_count"], 0)
        if p["minimum_independent_origin_count"] is None:
            assert row["origin_evidence_deficit_from_confirmed_lower_bound"] is None
        else:
            assert row["origin_evidence_deficit_from_confirmed_lower_bound"] == max(
                p["minimum_independent_origin_count"] - b["known_independent_origin_lower_bound"], 0
            )


def test_p21_4_global_deficit_totals_and_waves_are_locked():
    plan = _json(PLAN)
    assert plan["summary"]["minimum_new_source_path_deficit"] == 49
    assert plan["summary"]["minimum_healthy_source_deficit"] == 49
    assert plan["summary"]["origin_evidence_deficit_from_confirmed_lower_bound"] == 54
    waves = {w["wave"]: w for w in plan["waves"]}
    assert [(k, waves[k]["gap_cell_count"], waves[k]["source_path_deficit"]) for k in waves] == [
        ("A_CRITICAL_REQUIRED", 2, 2),
        ("B_HIGH_REQUIRED", 9, 13),
        ("C_STANDARD_REQUIRED", 14, 27),
        ("D_WATCH_REQUIRED", 1, 1),
        ("E_OPTIONAL_STANDARD", 4, 4),
        ("F_OPTIONAL_WATCH", 2, 2),
    ]


def test_p21_4_priority_is_policy_criticality_not_editorial_judgment():
    rows = _json(PLAN)["gap_cells"]
    rank = {"A_CRITICAL_REQUIRED": 1, "B_HIGH_REQUIRED": 2, "C_STANDARD_REQUIRED": 3,
            "D_WATCH_REQUIRED": 4, "E_OPTIONAL_STANDARD": 5, "F_OPTIONAL_WATCH": 6}
    assert all(r["priority_rank"] == rank[r["wave"]] for r in rows)
    assert rows == sorted(rows, key=lambda r: (r["priority_rank"], {"MISSING_EXPECTED_COVERAGE": 0, "THIN": 1, "DEGRADED_COLLECTION": 2}.get(r["current_status"], 9), r["cell_id"]))


def test_p21_4_degraded_osint_is_repair_or_alternate_first_not_forced_expansion():
    rows = {r["cell_id"]: r for r in _json(PLAN)["gap_cells"]}
    gdelt = rows["global.multi.public_osint"]
    assert gdelt["current_status"] == "DEGRADED_COLLECTION"
    assert gdelt["source_path_deficit"] == 0
    assert gdelt["healthy_source_deficit"] == 1
    assert gdelt["recommended_action"] == "REPAIR_EXISTING_OR_ADD_ALTERNATE_PUBLIC_FREE_PATH"


def test_p21_4_candidate_qualification_preserves_independence_and_truth_boundaries():
    q = set(_json(PLAN)["candidate_qualification"])
    assert "PUBLIC_OR_FREE_ACCESS_FIRST" in q
    assert "PROVENANCE_MUST_BE_RESOLVABLE_OR_REMAIN_UNKNOWN" in q
    assert "DOMAIN_SOURCE_LANGUAGE_COUNTS_DO_NOT_CREATE_INDEPENDENCE" in q
    assert "P13_5_P13_6_REMAIN_FACTUAL_VERIFICATION_AUTHORITY" in q


def test_p21_4_is_planning_only_and_p21_5_remains_owner_gated():
    plan = _json(PLAN)
    assert plan["live_onboarding_authorized"] is False
    assert plan["paid_provider_authorized"] is False
    b = plan["execution_boundary"]
    assert b["p21_4"] == "PLAN_AND_CANDIDATE_DISCOVERY_ONLY"
    assert b["p21_5"] == "SEPARATE_EXPLICIT_OWNER_DECISION_REQUIRED_BEFORE_ANY_LIVE_SOURCE_ONBOARDING"
    assert b["runtime_deployment"] is False
    assert b["service_restart"] is False
    assert b["registry_activation"] is False
    assert b["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS.glob("*.sql"))


def test_p21_4_result_does_not_claim_activation_or_verification_promotion():
    text = RESULT.read_text(encoding="utf-8")
    assert "planning only" in text.lower()
    assert "separate explicit owner gate" in text.lower()
    assert "P13.5/P13.6 remain factual-verification authority" in text
