from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
P20_0_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_1_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_1_source_record.schema.json"
P20_4_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_4_collection_health_latency.schema.json"
P20_5_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_5_source_onboarding.schema.json"
P20_5_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_5_SOURCE_ONBOARDING_BASELINE_2026-09-16.json"
P20_5_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "p20" / "p20_5_onboarding_synthetic.json"
MIGRATIONS_DIR = ROOT / "migrations"


SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate(case: dict) -> dict:
    item = case["input"]
    allowed_types = set(_json(P20_1_SCHEMA_PATH)["properties"]["source_type"]["enum"])
    reasons: list[str] = []

    if not SOURCE_ID_RE.fullmatch(str(item.get("source_id") or "")):
        reasons.append("SOURCE_ID_INVALID")
    if not str(item.get("display_name") or "").strip():
        reasons.append("DISPLAY_NAME_MISSING")
    if item.get("source_type") not in allowed_types:
        reasons.append("SOURCE_TYPE_INVALID")
    if not item.get("geography_scope"):
        reasons.append("GEOGRAPHY_SCOPE_MISSING")
    if not item.get("language_scope"):
        reasons.append("LANGUAGE_SCOPE_MISSING")
    if not str(item.get("primary_domain_or_endpoint") or "").strip():
        reasons.append("ENDPOINT_MISSING")
    if item.get("expected_freshness_minutes", 0) <= 0:
        reasons.append("EXPECTED_FRESHNESS_INVALID")
    if item.get("collection_cadence_minutes", 0) <= 0:
        reasons.append("COLLECTION_CADENCE_INVALID")
    if item.get("health_behavior_status") != "PASS":
        reasons.append("HEALTH_BEHAVIOR_NOT_PASS")
    if item.get("fixture_validation_status") != "PASS":
        reasons.append("FIXTURE_VALIDATION_NOT_PASS")
    if item.get("rollback_disable_status") != "PASS":
        reasons.append("ROLLBACK_DISABLE_NOT_PASS")

    governance = item.get("governance_review_status")
    if governance == "REJECTED":
        reasons.append("GOVERNANCE_REJECTED")
    elif governance != "APPROVED":
        reasons.append("GOVERNANCE_NOT_APPROVED")

    resource_authorization_required = (
        item.get("cost_mode") == "PAID"
        or item.get("authentication_mode") != "NONE"
        or item.get("access_mode") == "RESTRICTED"
        or item.get("data_classification") != "PUBLIC"
    )
    if resource_authorization_required:
        if item.get("resource_authorization_state") != "APPROVED":
            reasons.append("RESOURCE_AUTHORIZATION_REQUIRED")
    elif item.get("resource_authorization_state") not in {"NOT_REQUIRED", "APPROVED"}:
        reasons.append("RESOURCE_AUTHORIZATION_STATE_INVALID")

    if item.get("activation_requested") is True:
        reasons.append("LIVE_ACTIVATION_OUT_OF_SCOPE")

    if governance == "REJECTED":
        decision = "REJECTED"
        reasons = [reason for reason in reasons if reason == "GOVERNANCE_REJECTED"]
    elif reasons:
        decision = "BLOCKED"
    else:
        decision = "ELIGIBLE_NOT_ACTIVE"

    return {
        "eligibility_decision": decision,
        "reason_codes": reasons,
        "independence_credit_granted": False,
        "live_activation_authorized": False,
        "live_activation_state": "NOT_ACTIVE",
    }


def test_p20_5_synthetic_onboarding_cases_are_deterministic():
    fixture = _json(P20_5_FIXTURE_PATH)

    assert fixture["schema_version"] == "kgm.p20.5.onboarding.synthetic.v1"
    assert len(fixture["cases"]) == 12
    for case in fixture["cases"]:
        assert _evaluate(case) == case["expected"]


def test_p20_5_unknown_provenance_can_be_ready_but_never_gets_independence_credit():
    cases = {item["case_id"]: item for item in _json(P20_5_FIXTURE_PATH)["cases"]}
    unknown = _evaluate(cases["valid-public-unknown-provenance"])
    known = _evaluate(cases["valid-public-known-provenance"])

    assert unknown["eligibility_decision"] == "ELIGIBLE_NOT_ACTIVE"
    assert known["eligibility_decision"] == "ELIGIBLE_NOT_ACTIVE"
    assert unknown["independence_credit_granted"] is False
    assert known["independence_credit_granted"] is False


def test_p20_5_paid_or_secret_resource_is_blocked_without_separate_authorization():
    cases = {item["case_id"]: item for item in _json(P20_5_FIXTURE_PATH)["cases"]}

    for case_id in ("paid-resource-not-approved", "secret-auth-not-approved"):
        result = _evaluate(cases[case_id])
        assert result["eligibility_decision"] == "BLOCKED"
        assert result["reason_codes"] == ["RESOURCE_AUTHORIZATION_REQUIRED"]


def test_p20_5_live_activation_is_explicitly_out_of_scope():
    cases = {item["case_id"]: item for item in _json(P20_5_FIXTURE_PATH)["cases"]}
    result = _evaluate(cases["activation-requested-inside-p20-5"])
    schema = _json(P20_5_SCHEMA_PATH)["properties"]

    assert result["eligibility_decision"] == "BLOCKED"
    assert result["reason_codes"] == ["LIVE_ACTIVATION_OUT_OF_SCOPE"]
    assert schema["live_activation_authorized"]["const"] is False
    assert schema["live_activation_state"]["const"] == "NOT_ACTIVE"
    assert schema["independence_credit_granted"]["const"] is False


def test_p20_5_taxonomy_is_exactly_reused_from_p20_1():
    p20_1_types = set(_json(P20_1_SCHEMA_PATH)["properties"]["source_type"]["enum"])
    p20_5_types = set(_json(P20_5_SCHEMA_PATH)["properties"]["source_type"]["enum"])

    assert p20_5_types == p20_1_types


def test_p20_5_requires_health_fixture_and_rollback_readiness():
    schema = _json(P20_5_SCHEMA_PATH)
    required = set(schema["required"])
    p20_4_health_states = set(_json(P20_4_SCHEMA_PATH)["properties"]["health_state"]["enum"])

    assert "health_behavior_status" in required
    assert "fixture_validation_status" in required
    assert "rollback_disable_status" in required
    assert "NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY" in p20_4_health_states
    assert "DISABLED_EXPECTED" in p20_4_health_states
    assert "DISABLED_UNEXPECTED" in p20_4_health_states


def test_p20_5_baseline_does_not_mutate_current_source_network():
    p20_0 = _json(P20_0_BASELINE_PATH)
    p20_5 = _json(P20_5_BASELINE_PATH)

    assert p20_5["current_governed_source_count"] == p20_0["source_count"] == 10
    assert p20_5["new_source_candidate_count"] == 0
    assert p20_5["new_coverage_eligible_source_count"] == 0
    assert p20_5["live_activation_authorized_count"] == 0
    assert p20_5["paid_provider_approved_count"] == 0
    assert p20_5["secret_backed_source_approved_count"] == 0


def test_p20_5_preserves_epistemic_and_runtime_boundaries():
    baseline = _json(P20_5_BASELINE_PATH)
    principles = baseline["principles"]
    safety = baseline["safety_boundary"]

    assert principles["unknown_provenance_may_remain_unknown"] is True
    assert principles["unknown_provenance_grants_no_independence_credit"] is True
    assert principles["coverage_eligibility_does_not_activate_source"] is True
    assert principles["source_onboarding_does_not_change_claim_verification"] is True
    assert safety["live_source_expansion"] is False
    assert safety["live_ingest_change"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["control_plane_change"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
