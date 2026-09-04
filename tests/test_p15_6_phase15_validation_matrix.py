from pathlib import Path

from kgeopolitical_monitor.forecast_calibration_contract import (
    P15_0_GATE,
    forecast_calibration_architecture_contract,
)
from kgeopolitical_monitor.forecast_outcome_persistence import P15_1_GATE
from kgeopolitical_monitor.forecast_outcome_resolution import P15_2_GATE
from kgeopolitical_monitor.forecast_calibration_engine import P15_3_GATE
from kgeopolitical_monitor.forecast_performance_intelligence import P15_4_GATE
from kgeopolitical_monitor.forecast_performance_projection import P15_5_GATE


ROOT = Path(__file__).resolve().parents[1]
STRATEGIC_GATE = "PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED"
CLOSURE_ANCHOR = "77b444e2c89f763e56acc22183c74634ea993573"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p15_6_all_sequential_subphase_gates_are_present_and_exact():
    assert P15_0_GATE == "P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED"
    assert P15_1_GATE == "P15_1_FORECAST_OUTCOME_PERSISTENCE_MODEL_VALIDATED"
    assert P15_2_GATE == "P15_2_PROVENANCE_BOUND_OUTCOME_RESOLUTION_VALIDATED"
    assert P15_3_GATE == "P15_3_CALIBRATION_ENGINE_VALIDATED"
    assert P15_4_GATE == "P15_4_PERFORMANCE_INTELLIGENCE_DRIFT_BIAS_VALIDATED"
    assert P15_5_GATE == "P15_5_OWNER_READ_ONLY_PERFORMANCE_PROJECTION_VALIDATED"


def test_p15_6_validation_matrix_covers_entire_phase_and_strategic_gate():
    matrix = _text("docs/implementation/P15_6_VALIDATION_MATRIX.md")
    for token in (
        STRATEGIC_GATE,
        P15_0_GATE,
        P15_1_GATE,
        P15_2_GATE,
        P15_3_GATE,
        P15_4_GATE,
        P15_5_GATE,
        "PROJECT_LOCAL_ONLY",
        "PRODUCTION_LIVE = NOT_OPERATIONAL",
        "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED",
    ):
        assert token in matrix


def test_p15_6_migration_scope_is_additive_and_stops_at_030():
    migrations = {path.name for path in (ROOT / "migrations").glob("*.sql")}
    assert "028_forecast_outcome_assessment_history.sql" in migrations
    assert "029_forecast_calibration_observations.sql" in migrations
    assert "030_forecast_performance_intelligence.sql" in migrations
    assert not any(name.startswith("031_") for name in migrations)


def test_p15_6_new_phase15_schema_does_not_create_factual_verification_fields():
    phase15_sql = "\n".join(
        _text(path)
        for path in (
            "migrations/028_forecast_outcome_assessment_history.sql",
            "migrations/029_forecast_calibration_observations.sql",
            "migrations/030_forecast_performance_intelligence.sql",
        )
    ).lower()
    for forbidden in (
        "verification_status",
        "factual_confidence",
        "verification_score",
        "independent_origin_count",
        "coverage_confidence real",
    ):
        assert forbidden not in phase15_sql


def test_p15_6_architecture_preserves_truth_and_runtime_boundaries():
    contract = forecast_calibration_architecture_contract()
    boundary = contract["runtime_security_boundary"]
    invariants = " ".join(contract["epistemic_invariants"])

    assert boundary["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert boundary["mixed_shared_canonical_runtime"] == "BLOCKED"
    assert boundary["production_live"] == "NOT_OPERATIONAL"
    assert boundary["paid_providers"] == "NONE_APPROVED"
    assert boundary["owner_execution"] == "DISABLED"
    assert "Calibration score cannot promote factual verification" in invariants
    assert "Performance rank cannot promote factual verification" in invariants
    assert "P13.5" in invariants and "P13.6" in invariants


def test_p15_6_phase14_activation_boundary_remains_unchanged():
    documents = "\n".join(
        [
            _text("ROADMAP.md"),
            _text("README.md"),
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_RESULT.md"),
            _text("docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_PLAN.md"),
            _text("docs/implementation/P15_6_VALIDATION_MATRIX.md"),
        ]
    )
    assert "PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY" in documents
    assert "VALIDATED_READY / NOT_ACTIVATED" in documents
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in documents
    assert "PRODUCTION_LIVE = NOT_OPERATIONAL" in documents


def test_p15_6_phase16_remains_sequential_and_unactivated():
    roadmap = _text("ROADMAP.md")
    assert "Phase 16 — Delivery, Operator Experience and Quality Feedback" in roadmap
    assert "PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED" in roadmap
    assert "APPROVED_SEQUENTIAL / NOT_STARTED" in roadmap


def test_p15_6_does_not_add_owner_projection_to_public_backend_routes():
    backend = _text("src/kgeopolitical_monitor/backend_action_api.py")
    assert "forecast_performance_projection" not in backend
    assert "OwnerForecastPerformanceProjection" not in backend


def test_phase15_canonical_closure_state_is_synchronized_to_v4_19():
    roadmap = _text("ROADMAP.md")
    readme = _text("README.md")
    plan = _text("docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_PLAN.md")
    matrix = _text("docs/implementation/P15_6_VALIDATION_MATRIX.md")
    result = _text("docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_RESULT.md")
    checkpoint = _text(
        "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED.md"
    )

    assert "Version: 4.19" in roadmap
    assert "state synchronization: `v4.19`" in roadmap
    assert "Version: 4.19" in readme
    assert "PHASE_15_VALIDATED" in readme

    for document in (roadmap, readme, plan, matrix, result, checkpoint):
        assert STRATEGIC_GATE in document
        assert CLOSURE_ANCHOR in document

    assert "Status: `VALIDATED`" in plan
    assert "Status: `VALIDATED`" in matrix
    assert "Status: `VALIDATED`" in result
    assert f"State: `{STRATEGIC_GATE}`" in checkpoint
    assert "P15.0–P15.6: `VALIDATED`" in roadmap
    assert "P15.0–P15.6: `VALIDATED`" in readme


def test_phase15_saved_closure_evidence_matches_exact_candidate_runs():
    documents = "\n".join(
        [
            _text("ROADMAP.md"),
            _text("README.md"),
            _text("docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_PLAN.md"),
            _text("docs/implementation/P15_6_VALIDATION_MATRIX.md"),
            _text("docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_RESULT.md"),
            _text(
                "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED.md"
            ),
        ]
    )
    for token in (
        CLOSURE_ANCHOR,
        "33906546408",
        "101132699703",
        "33906546431",
        "101132700003",
        "576 passed, 2 warnings / SUCCESS",
        "native `aarch64`",
    ):
        assert token in documents
