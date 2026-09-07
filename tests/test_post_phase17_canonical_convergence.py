import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
ROOT_DOCS = (
    "README.md",
    "ARCHITECTURE.md",
    "SECURITY_AND_DATA_POLICY.md",
    "EXTERNAL_INTEGRATIONS.md",
    "SOURCE_POLICY.md",
    "DATA_MODELS.md",
    "PROJECT_HISTORY.md",
)


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_machine_readable_state_matches_roadmap_v4_22_position():
    state = _state()
    roadmap = _text("ROADMAP.md")
    assert state["roadmap"]["strategic_version"] == "v4"
    assert state["roadmap"]["state_sync_version"] == "4.22"
    assert state["roadmap"]["current_position"] == "POST_PHASE_17_PRE_PHASE_18_ARCHITECTURE_GATE"
    assert "Version: 4.22" in roadmap
    assert state["phases"]["17"].split(" / ")[0] in roadmap
    assert state["activation_gates"]["phase18"] in roadmap


def test_root_canonical_docs_share_current_phase_and_runtime_boundaries():
    for path in ROOT_DOCS:
        text = _text(path)
        assert "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "NOT_OPERATIONAL" in text
        assert "PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL" in text or path == "DATA_MODELS.md"

    for path in ("README.md", "ARCHITECTURE.md", "SECURITY_AND_DATA_POLICY.md", "EXTERNAL_INTEGRATIONS.md", "PROJECT_HISTORY.md"):
        assert "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED" in _text(path)


def test_data_models_matches_actual_post_phase14_migration_chain():
    data_models = _text("DATA_MODELS.md")
    state = _state()
    assert state["migrations"]["latest_created"] == 32
    for number, filename in (
        (28, "028_forecast_outcome_assessment_history.sql"),
        (29, "029_forecast_calibration_observations.sql"),
        (30, "030_forecast_performance_intelligence.sql"),
        (31, "031_delivery_intent_audit.sql"),
        (32, "032_operator_quality_feedback.sql"),
    ):
        assert (ROOT / "migrations" / filename).exists(), number
        assert filename in data_models
        assert state["migrations"][f"{number:03d}"] == filename
    assert not (ROOT / "migrations" / "033_controlled_external_publication.sql").exists()
    assert "033" in data_models and "NOT_CREATED / NOT_PREAUTHORIZED" in data_models


def test_activation_and_publication_boundaries_are_synchronized_without_activation():
    state = _state()
    combined = "\n".join(_text(path) for path in ROOT_DOCS)
    assert state["activation_gates"]["phase14_owner_operation"] in combined
    assert state["activation_gates"]["phase17_publication"] in combined
    assert "PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY" in combined
    assert state["activation_gates"]["phase17_current_account_capability"] == "UNAVAILABLE"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert "Phase 18 is not activated" in _text("PROJECT_HISTORY.md")


def test_phase13_historical_no_migration_028_statement_is_not_current_schema_claim():
    data_models = _text("DATA_MODELS.md")
    assert "Historical Phase-13 statement: migration 028 = `NONE` for Phase 13" in data_models
    assert "`028_forecast_outcome_assessment_history.sql`" in data_models
    assert "This later Phase-15 migration `028` does not contradict" in data_models
