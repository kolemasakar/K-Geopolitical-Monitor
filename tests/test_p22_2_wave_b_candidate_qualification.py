import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
EVIDENCE = ROOT / "docs/evidence/P22_2_WAVE_B_CANDIDATE_QUALIFICATION_2026-09-19.json"
RESULT = ROOT / "docs/implementation/P22_2_WAVE_B_CANDIDATE_QUALIFICATION_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_2_WAVE_B_CANDIDATE_QUALIFICATION_VALIDATED.md"
P20_BASELINE = ROOT / "docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
WAVE_A = ROOT / "docs/evidence/P21_5_WAVE_A_ONBOARDING_2026-09-17.json"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_2_candidate_universe_exactly_matches_wave_b_deficit():
    e = _json(EVIDENCE)
    assert e["wave"] == "B_HIGH_REQUIRED"
    assert e["planning_basis"] == {
        "gap_cell_count": 9,
        "source_path_deficit": 13,
        "healthy_source_deficit": 13,
        "origin_evidence_deficit_from_confirmed_lower_bound": 16,
    }
    assert len(e["candidates"]) == 13
    assert len({c["candidate_id"] for c in e["candidates"]}) == 13
    assert len({c["source_id_proposal"] for c in e["candidates"]}) == 13
    assert len({c["cell_id"] for c in e["candidates"]}) == 9


def test_p22_2_does_not_collide_with_existing_source_ids():
    e = _json(EVIDENCE)
    existing = {s["source_id"] for s in _json(P20_BASELINE)["sources"]}
    existing |= {s["source_id"] for s in _json(WAVE_A)["sources"]}
    proposed = {c["source_id_proposal"] for c in e["candidates"]}
    assert proposed.isdisjoint(existing)


def test_p22_2_is_public_free_anonymous_but_not_onboarded():
    e = _json(EVIDENCE)
    for c in e["candidates"]:
        assert c["access_mode"] == "PUBLIC_ANONYMOUS"
        assert c["cost_mode"] == "FREE"
        assert c["authentication_mode"] == "NONE"
        assert c["data_classification"] == "PUBLIC"
        assert c["p20_5_readiness"]["eligibility_decision"] == "BLOCKED"
        assert c["p20_5_readiness"]["live_activation_authorized"] is False
        assert c["p20_5_readiness"]["live_activation_state"] == "NOT_ACTIVE"
        assert c["repository_activation"] is False
        assert c["onboarding_authorized"] is False
        assert c["live_activation_authorized"] is False
        assert c["provenance"]["independence_credit_granted"] is False

    assert e["summary"]["p20_5_eligible_not_active_count"] == 0
    assert e["summary"]["p20_5_blocked_count"] == 13
    assert e["summary"]["repository_activation_count"] == 0
    assert e["summary"]["live_activation_count"] == 0
    assert e["summary"]["independence_credit_granted_count"] == 0


def test_p22_2_preserves_specific_rights_and_taxonomy_blockers():
    e = _json(EVIDENCE)
    by_id = {c["source_id_proposal"]: c for c in e["candidates"]}

    people = by_id["people-cn-zh"]
    assert people["automated_collection_rights_state"] == "REQUIRES_WRITTEN_AUTHORIZATION_REVIEW"
    assert "AUTOMATED_COLLECTION_RIGHTS_REVIEW_PENDING" in people["p20_5_readiness"]["reason_codes"]

    for source_id in ("aljazeera-ar", "alarabiya-ar"):
        c = by_id[source_id]
        assert c["taxonomy_fit"] == "GOVERNANCE_CONFIRMATION_REQUIRED"
        assert "TAXONOMY_FIT_GOVERNANCE_CONFIRMATION_REQUIRED" in c["p20_5_readiness"]["reason_codes"]


def test_p22_2_state_preserves_owner_runtime_and_truth_gates():
    s = _json(STATE)
    x = s["phase22"]
    p = s["phase22_p22_2"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 49
    assert s["roadmap"]["current_position"].startswith("PHASE_22_")
    assert x["p22_2_state"] == "VALIDATED_WITH_ONBOARDING_BLOCKERS"
    assert x["p22_1_state"] in {"BLOCKED_ON_OWNER_GATE", "AUTHORIZED_READY_TO_EXECUTE", "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"}
    assert x["p22_3_state"] == "BLOCKED_ON_OWNER_GATE"
    assert x["owner_operational_activation"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_BOUNDED_P22_1_PILOT", "BOUNDED_P22_1_PILOT_COMPLETED / PERSISTENT_OWNER_OPERATION_NOT_ACTIVATED"}
    assert x["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"

    assert p["candidate_count"] == 13
    assert p["p20_5_eligible_not_active_count"] == 0
    assert p["p20_5_blocked_count"] == 13
    assert p["repository_activation_count"] == 0
    assert p["live_activation_count"] == 0
    assert p["independence_credit_granted_count"] == 0
    assert p["verification_authority"] == "P13.5/P13.6"

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"

    assert RESULT.exists()
    assert CHECKPOINT.exists()
