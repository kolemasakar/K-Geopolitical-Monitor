import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
ROADMAP = ROOT / "ROADMAP.md"
HANDOFF = ROOT / "docs/handoff/CURRENT_HANDOFF.md"
PLAN = ROOT / "docs/implementation/PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_PLAN.md"
AUTH = ROOT / "docs/decisions/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_AUTHORIZATION_2026-09-19.md"


def test_p22_1_bounded_owner_pilot_is_explicitly_authorized_only():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    x = s["phase22"]
    p = s["phase22_p22_1"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 50
    assert s["roadmap"]["current_position"].startswith(("PHASE_22_", "PHASE_23_"))

    assert x["p22_1_state"] in {"AUTHORIZED_READY_TO_EXECUTE", "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"}
    assert x["owner_operational_activation"] in {"APPROVED_FOR_BOUNDED_P22_1_PILOT", "BOUNDED_P22_1_PILOT_COMPLETED / PERSISTENT_OWNER_OPERATION_NOT_ACTIVATED"}
    assert x["wave_b_onboarding"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B_OWNER_DECISION_REQUIRED"}
    assert x["next_gate"] in {"P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED", "P22_3_WAVE_B_ONBOARDING_OWNER_DECISION_REQUIRED", "P22_3_B1_P20_5_READINESS_AND_ONBOARDING_VALIDATION", "P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED", "P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED", "P22_5_CANONICAL_SEMANTIC_INGESTION_BRIDGE_IMPLEMENTATION", "P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED", "P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED", "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED", "ROADMAP_DECISION_REQUIRED"}

    assert p["state"] in {"AUTHORIZED_READY_TO_EXECUTE", "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"}
    assert p["target_node"] == "kgm-e4-owner-pilot"
    assert p["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"
    if p["state"] == "AUTHORIZED_READY_TO_EXECUTE":
        assert p["execution_scope"] == "ONE_BOUNDED_OWNER_LOCAL_SESSION"
        assert p["existing_governed_source_set_only"] is True
        assert p["persistent_scheduler_enablement_authorized"] is False
    else:
        assert p["state"] == "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"
        assert p["persistent_owner_operation_activated"] is False
        assert p["deployed_runtime_mutated"] is False


def test_p22_1_authorization_preserves_runtime_resource_and_truth_boundaries():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    p = s["phase22_p22_1"]
    roadmap = ROADMAP.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    auth = AUTH.read_text(encoding="utf-8")

    assert AUTH.exists()
    assert "APPROVED_FOR_BOUNDED_P22_1_PILOT" in auth
    assert "WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED" in auth
    assert "ONE_BOUNDED_OWNER_LOCAL_SESSION" in auth

    assert p["production_live"] == "NOT_OPERATIONAL"
    assert p["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert p["verification_authority"] == "P13.5/P13.6"
    if p["state"] == "AUTHORIZED_READY_TO_EXECUTE":
        assert p["runtime_storage"] == "PROJECT_LOCAL_ONLY"
        assert p["shared_runtime_authorized"] is False
        assert p["paid_or_secret_provider_authorized"] is False
        assert p["plugin_publication_authorized"] is False
    else:
        assert p["paid_or_shared_resources_authorized"] is False
        assert p["plugin_publication_authorized"] is False
        assert p["deployed_service_restart"] is False

    assert s["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert s["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert s["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"

    sync_version = s["roadmap"]["state_sync_version"]
    assert f"Version: {sync_version}" in roadmap
    assert s["roadmap"]["current_position"] in roadmap
    assert "P22_1" in handoff
    assert "P22.1" in plan
