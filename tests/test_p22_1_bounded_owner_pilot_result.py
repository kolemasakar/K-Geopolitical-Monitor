import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"
EVIDENCE = ROOT / "docs/evidence/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_2026-09-19.json"
RESULT = ROOT / "docs/implementation/P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_RESULT.md"
CHECKPOINT = ROOT / "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_1_BOUNDED_OWNER_OPERATIONAL_PILOT_VALIDATED.md"


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_p22_1_real_owner_local_pilot_evidence_is_bounded_and_exact_main():
    e = _json(EVIDENCE)
    assert e["canonical_sha"] == "ec71242cc3cb8f793a7dcf0b70c884e085db5b26"
    assert e["host"]["device_name"] == "kgm-e4-owner-pilot"
    assert e["host"]["architecture"] == "aarch64"
    assert e["isolated_execution"]["exact_main_sha"] == e["canonical_sha"]
    assert e["isolated_execution"]["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert e["isolated_execution"]["database_integrity"] == "ok"
    assert e["supervisor_tick"]["execution_count"] == 1
    assert e["supervisor_tick"]["status"] == "COMPLETED"
    assert e["supervisor_tick"]["recovered_runs"] == 0


def test_p22_1_preserves_measured_collection_degradation_without_semantic_promotion():
    e = _json(EVIDENCE)
    collection = e["source_collection"]
    attempts = {x["source_id"]: x for x in collection["attempts"]}

    assert collection["status"] == "PARTIAL"
    assert collection["item_count"] == 0
    assert collection["source_success_count"] == 1
    assert collection["source_failure_count"] == 1
    assert attempts["consilium-press-releases"]["status"] == "SUCCESS"
    assert attempts["gdelt-doc-2"]["status"] == "FAILED"
    assert "429" in attempts["gdelt-doc-2"]["error"]

    semantic = e["semantic_observation"]
    assert semantic["semantic_corpus_observed"] is False
    assert semantic["canonical_semantic_decisions_observed"] == 0
    assert semantic["verification_yield_impact"] == "NOT_OBSERVED"
    assert semantic["contradiction_workload_impact"] == "NOT_OBSERVED"
    assert semantic["forecast_input_impact"] == "NOT_OBSERVED"
    assert semantic["verification_authority"] == "P13.5/P13.6"


def test_p22_1_did_not_mutate_deployed_runtime_or_open_later_gates():
    e = _json(EVIDENCE)
    d = e["deployed_runtime_containment"]
    safety = e["safety_boundary"]

    assert d["deployed_sha_before"] == d["deployed_sha_after"]
    assert d["deployed_runtime_mutated_by_p22_1"] is False
    assert d["service_before"] == d["service_after"] == "active"
    assert d["service_restart"] is False
    assert d["deployed_runtime_db_readable_by_kgmops"] is False

    assert safety["wave_b_onboarding"] == "OWNER_DECISION_REQUIRED"
    assert safety["persistent_scheduler_enablement"] is False
    assert safety["paid_or_shared_resources_authorized"] is False
    assert safety["migration_033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert safety["production_live"] == "NOT_OPERATIONAL"
    assert safety["plugin_publication"] is False


def test_p22_1_canonical_state_moves_only_to_p22_3_owner_gate():
    s = _json(STATE)
    x = s["phase22"]
    p = s["phase22_p22_1"]

    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 51
    assert s["roadmap"]["current_position"].startswith("PHASE_22_")
    assert x["p22_1_state"] == "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"
    assert x["p22_2_state"] == "VALIDATED_WITH_ONBOARDING_BLOCKERS"
    assert x["p22_3_state"] in {"BLOCKED_ON_OWNER_GATE", "AUTHORIZED_B1_IMPLEMENTATION_READY", "VALIDATED_WITH_PARTIAL_ONBOARDING"}
    assert x["wave_b_onboarding"] in {"OWNER_DECISION_REQUIRED", "APPROVED_FOR_B1_INSTITUTIONAL_COHORT", "B1_PARTIAL_ONBOARDING_VALIDATED / REMAINING_WAVE_B_OWNER_DECISION_REQUIRED"}
    assert x["next_gate"] in {"P22_3_WAVE_B_ONBOARDING_OWNER_DECISION_REQUIRED", "P22_3_B1_P20_5_READINESS_AND_ONBOARDING_VALIDATION", "P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED", "P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED"}

    assert p["state"] == "VALIDATED_WITH_MEASURED_COLLECTION_DEGRADATION"
    assert p["semantic_corpus_observed"] is False
    assert p["persistent_owner_operation_activated"] is False
    assert p["deployed_runtime_mutated"] is False

    assert RESULT.exists()
    assert CHECKPOINT.exists()
