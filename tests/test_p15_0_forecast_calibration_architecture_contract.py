from kgeopolitical_monitor.forecast_calibration_contract import (
    FORECAST_CALIBRATION_ARCHITECTURE_VERSION,
    OUTCOME_AMBIGUOUS,
    OUTCOME_PARTIAL,
    OUTCOME_RESOLVED,
    OUTCOME_STATES,
    OUTCOME_UNRESOLVED,
    P15_0_GATE,
    SCOREABLE_OUTCOME_STATES,
    forecast_calibration_architecture_contract,
)
from kgeopolitical_monitor.forecast_semantics import (
    FORECAST_SEMANTIC_FIELDS,
    FORECAST_SEMANTICS_VERSION,
)


def test_p15_0_contract_identity_and_gate_are_explicit():
    contract = forecast_calibration_architecture_contract()

    assert FORECAST_CALIBRATION_ARCHITECTURE_VERSION == (
        "KGM_FORECAST_CALIBRATION_PERFORMANCE_ARCHITECTURE_V1"
    )
    assert P15_0_GATE == "P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED"
    assert contract["version"] == FORECAST_CALIBRATION_ARCHITECTURE_VERSION
    assert contract["gate"] == P15_0_GATE
    assert contract["phase"] == "P15.0"


def test_p15_0_preserves_e7_probability_semantics_without_generic_aliases():
    contract = forecast_calibration_architecture_contract()
    scenario = contract["entities"]["scenario_version"]

    assert contract["compatibility"]["forecast_semantics_version"] == FORECAST_SEMANTICS_VERSION
    assert tuple(scenario["probability_fields"]) == FORECAST_SEMANTIC_FIELDS
    assert tuple(contract["compatibility"]["existing_probability_fields"]) == FORECAST_SEMANTIC_FIELDS
    assert "probability" not in scenario["probability_fields"]
    assert "confidence" not in scenario["probability_fields"]


def test_p15_0_outcome_states_fail_closed_for_automatic_scoring():
    contract = forecast_calibration_architecture_contract()

    assert OUTCOME_STATES == (
        OUTCOME_RESOLVED,
        OUTCOME_UNRESOLVED,
        OUTCOME_PARTIAL,
        OUTCOME_AMBIGUOUS,
    )
    assert SCOREABLE_OUTCOME_STATES == (OUTCOME_RESOLVED,)
    assert tuple(contract["outcome_contract"]["scoreable_states"]) == (OUTCOME_RESOLVED,)

    rules = " ".join(contract["outcome_contract"]["rules"])
    assert "UNRESOLVED is not equivalent to a negative outcome" in rules
    assert "PARTIAL is not automatically coerced to a binary outcome" in rules
    assert "AMBIGUOUS fails closed for automatic scoring" in rules


def test_p15_0_entities_keep_forecast_outcome_and_performance_roles_distinct():
    entities = forecast_calibration_architecture_contract()["entities"]

    assert set(entities) == {
        "forecast",
        "forecast_version",
        "scenario_version",
        "outcome_assessment",
        "calibration_observation",
        "performance_aggregate",
    }
    assert entities["forecast_version"]["parent"] == "forecast_id"
    assert entities["scenario_version"]["parent"] == "forecast_version_id"
    assert tuple(entities["calibration_observation"]["parents"]) == (
        "forecast_version_id",
        "scenario_version_id",
        "outcome_assessment_id",
    )


def test_p15_0_calibration_is_performance_evidence_not_truth_promotion():
    contract = forecast_calibration_architecture_contract()
    calibration = contract["calibration_contract"]
    invariants = " ".join(contract["epistemic_invariants"])

    assert tuple(calibration["initial_metric_family"]) == (
        "BRIER_SCORE",
        "RELIABILITY_BUCKETS",
    )
    assert "Calibration score cannot promote factual verification" in invariants
    assert "Performance rank cannot promote factual verification" in invariants
    assert "Coverage metrics cannot promote factual verification confidence" in invariants
    assert "Legacy scalar confidence cannot promote factual verification" in invariants
    assert "counts cannot promote factual verification" in invariants
    assert "P13.5" in invariants and "P13.6" in invariants


def test_p15_0_runtime_and_phase14_activation_boundaries_are_unchanged():
    contract = forecast_calibration_architecture_contract()
    boundary = contract["runtime_security_boundary"]
    compatibility = contract["compatibility"]

    assert boundary == {
        "runtime_storage": "PROJECT_LOCAL_ONLY",
        "mixed_shared_canonical_runtime": "BLOCKED",
        "production_live": "NOT_OPERATIONAL",
        "public_ingress": "NOT_APPROVED_NOT_DEPLOYED",
        "paid_providers": "NONE_APPROVED",
        "owner_execution": "DISABLED",
    }
    assert compatibility["phase_14_owner_activation"] == "UNCHANGED_OWNER_DECISION_REQUIRED"
    assert compatibility["migration_028"] == "NONE_FOR_P15_0"


def test_p15_0_contract_returns_detached_copy():
    first = forecast_calibration_architecture_contract()
    first["entities"]["forecast"]["meaning"] = "mutated"

    second = forecast_calibration_architecture_contract()
    assert second["entities"]["forecast"]["meaning"] != "mutated"
