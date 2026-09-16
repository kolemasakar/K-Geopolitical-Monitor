from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P20_0_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json"
P20_4_SCHEMA_PATH = ROOT / "docs" / "contracts" / "p20_4_collection_health_latency.schema.json"
P20_4_BASELINE_PATH = ROOT / "docs" / "evidence" / "P20_4_CURRENT_COLLECTION_HEALTH_BASELINE_2026-09-16.json"
P20_4_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "p20" / "p20_4_collection_health_synthetic.json"
P12_5_SOURCE_PATH = ROOT / "src" / "kgeopolitical_monitor" / "source_health_egress.py"
P19_CLOSURE_PATH = ROOT / "docs" / "evidence" / "PHASE_19_TARGETED_CATCHUP_FRESHNESS_CLOSURE_VALIDATION_2026-09-15.md"
MIGRATIONS_DIR = ROOT / "migrations"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate(case: dict) -> dict:
    item = case["input"]
    registration = item["registration_state"]

    if registration == "EXPECTED_NOT_REGISTERED":
        return {
            "collection_latency_state": "NOT_APPLICABLE",
            "content_latency_state": "NOT_APPLICABLE",
            "missing_source_state": "EXPECTED_NOT_REGISTERED",
            "health_state": "UNKNOWN",
            "evaluation_completeness": "UNKNOWN",
        }

    if registration == "REGISTERED_DISABLED":
        expected = item["disable_expected"] is True
        state = "DISABLED_EXPECTED" if expected else "DISABLED_UNEXPECTED"
        return {
            "collection_latency_state": "NOT_APPLICABLE",
            "content_latency_state": "NOT_APPLICABLE",
            "missing_source_state": state,
            "health_state": state,
            "evaluation_completeness": "COMPLETE",
        }

    if registration != "REGISTERED_ENABLED":
        return {
            "collection_latency_state": "UNKNOWN",
            "content_latency_state": "UNKNOWN",
            "missing_source_state": "UNKNOWN",
            "health_state": "UNKNOWN",
            "evaluation_completeness": "UNKNOWN",
        }

    if item["last_attempt_status"] is None or item["attempt_age_minutes"] is None:
        return {
            "collection_latency_state": "UNKNOWN",
            "content_latency_state": "UNKNOWN",
            "missing_source_state": "PRESENT_UNMEASURED",
            "health_state": "UNKNOWN",
            "evaluation_completeness": "UNKNOWN",
        }

    measurement_limit = max(
        item["collection_cadence_minutes"] * 2,
        item["expected_freshness_minutes"],
    )
    collection_latency = (
        "WITHIN_EXPECTATION"
        if item["attempt_age_minutes"] <= measurement_limit
        else "EXCEEDED_EXPECTATION"
    )

    if item["last_attempt_status"] == "FAILED":
        content_latency = "UNKNOWN"
    elif item["content_age_minutes"] is None:
        content_latency = "NO_CONTENT_OBSERVED"
    elif item["content_age_minutes"] <= item["expected_freshness_minutes"]:
        content_latency = "WITHIN_EXPECTATION"
    else:
        content_latency = "EXCEEDED_EXPECTATION"

    if collection_latency == "EXCEEDED_EXPECTATION":
        health = "STALE"
    elif item["last_attempt_status"] == "FAILED":
        health = "UNREACHABLE" if item["error_class"] == "TRANSPORT" else "DEGRADED"
    elif item["portfolio_availability_state"] == "DEGRADED":
        health = "DEGRADED"
    elif content_latency in {"NO_CONTENT_OBSERVED", "EXCEEDED_EXPECTATION"}:
        health = "NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY"
    else:
        health = "HEALTHY"

    return {
        "collection_latency_state": collection_latency,
        "content_latency_state": content_latency,
        "missing_source_state": "PRESENT_MEASURED",
        "health_state": health,
        "evaluation_completeness": "COMPLETE",
    }


def test_p20_4_current_repository_baseline_is_explicitly_unmeasured_not_inferred():
    p20_0 = _json(P20_0_BASELINE_PATH)
    p20_4 = _json(P20_4_BASELINE_PATH)

    assert p20_4["source_count"] == 10
    assert p20_4["measured_source_count"] == 0
    assert p20_4["unmeasured_source_count"] == 10
    assert p20_4["health_summary"] == {"UNKNOWN": 10}
    assert {item["source_id"] for item in p20_4["sources"]} == {
        item["source_id"] for item in p20_0["sources"]
    }
    assert {item["health_state"] for item in p20_4["sources"]} == {"UNKNOWN"}
    assert {item["missing_source_state"] for item in p20_4["sources"]} == {"PRESENT_UNMEASURED"}
    assert next(
        item for item in p20_4["sources"] if item["source_id"] == "eu-parliament-press-releases"
    )["portfolio_availability_state"] == "DEGRADED"


def test_p20_4_synthetic_cases_classify_deterministically():
    fixture = _json(P20_4_FIXTURE_PATH)

    assert fixture["schema_version"] == "kgm.p20.4.collection_health.synthetic.v1"
    assert len(fixture["cases"]) == 12
    for case in fixture["cases"]:
        assert _evaluate(case) == case["expected"]


def test_p20_4_quiet_content_is_not_collector_failure_or_event_silence():
    cases = {item["case_id"]: item for item in _json(P20_4_FIXTURE_PATH)["cases"]}

    no_content = _evaluate(cases["collector-healthy-no-content"])
    stale_content = _evaluate(cases["collector-healthy-stale-content"])

    assert no_content["collection_latency_state"] == "WITHIN_EXPECTATION"
    assert no_content["health_state"] == "NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY"
    assert stale_content["collection_latency_state"] == "WITHIN_EXPECTATION"
    assert stale_content["content_latency_state"] == "EXCEEDED_EXPECTATION"
    assert stale_content["health_state"] == "NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY"


def test_p20_4_recovery_gap_does_not_reclassify_current_collector_health():
    cases = {item["case_id"]: item for item in _json(P20_4_FIXTURE_PATH)["cases"]}

    complete = _evaluate(cases["healthy-current"])
    gap = _evaluate(cases["healthy-current-recovery-gap"])
    assert complete == gap
    assert complete["health_state"] == "HEALTHY"


def test_p20_4_preserves_p12_5_measurement_limit_and_error_dimensions():
    source = P12_5_SOURCE_PATH.read_text(encoding="utf-8")

    assert "record.collection_cadence_minutes * 2" in source
    assert "record.expected_freshness_minutes" in source
    assert 'operational_state = "UNAVAILABLE"' in source
    assert 'error_class = classify_attempt_error(error)' in source
    assert 'content_freshness = "UNKNOWN"' in source


def test_p20_4_preserves_p19_recovery_coverage_as_separate_dimension():
    evidence = P19_CLOSURE_PATH.read_text(encoding="utf-8")

    assert "explicit `UNKNOWN` and exact uncovered interval" in evidence
    assert "`GAP`, exact covered and uncovered intervals" in evidence
    assert "propagate coverage state into analysis evidence" in evidence


def test_p20_4_contract_contains_required_explainable_states():
    schema = _json(P20_4_SCHEMA_PATH)
    props = schema["properties"]

    assert set(props["health_state"]["enum"]) == {
        "HEALTHY",
        "DEGRADED",
        "STALE",
        "UNREACHABLE",
        "DISABLED_EXPECTED",
        "DISABLED_UNEXPECTED",
        "NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY",
        "UNKNOWN",
    }
    assert "EXPECTED_NOT_REGISTERED" in props["missing_source_state"]["enum"]
    assert "NO_CONTENT_OBSERVED" in props["content_latency_state"]["enum"]
    assert set(props["recovery_coverage_state"]["enum"]) == {
        "COMPLETE", "GAP", "UNKNOWN", "NOT_APPLICABLE"
    }


def test_p20_4_preserves_runtime_and_resource_boundaries():
    baseline = _json(P20_4_BASELINE_PATH)
    safety = baseline["safety_boundary"]
    principles = baseline["principles"]

    assert principles["portfolio_availability_is_not_current_operational_health"] is True
    assert principles["collector_health_is_not_content_credibility"] is True
    assert principles["content_silence_is_not_geopolitical_silence"] is True
    assert principles["recovery_gap_is_coverage_evidence_not_collector_failure"] is True
    assert safety["live_source_expansion"] is False
    assert safety["live_ingest_change"] is False
    assert safety["runtime_deployment"] is False
    assert safety["service_restart"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))
