"""Phase 15.0 forecast calibration and performance architecture contract.

This module defines the machine-readable epistemic and lifecycle boundaries for
forecast evaluation.  It is deliberately non-operational: no calibration score is
computed here, no outcome is resolved here, and no factual verification state is
modified here.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Final


FORECAST_CALIBRATION_ARCHITECTURE_VERSION: Final[str] = (
    "KGM_FORECAST_CALIBRATION_PERFORMANCE_ARCHITECTURE_V1"
)
P15_0_GATE: Final[str] = "P15_0_FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT_VALIDATED"

OUTCOME_RESOLVED: Final[str] = "RESOLVED"
OUTCOME_UNRESOLVED: Final[str] = "UNRESOLVED"
OUTCOME_PARTIAL: Final[str] = "PARTIAL"
OUTCOME_AMBIGUOUS: Final[str] = "AMBIGUOUS"
OUTCOME_STATES: Final[tuple[str, ...]] = (
    OUTCOME_RESOLVED,
    OUTCOME_UNRESOLVED,
    OUTCOME_PARTIAL,
    OUTCOME_AMBIGUOUS,
)

SCOREABLE_OUTCOME_STATES: Final[tuple[str, ...]] = (OUTCOME_RESOLVED,)

FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT: Final[dict[str, object]] = {
    "version": FORECAST_CALIBRATION_ARCHITECTURE_VERSION,
    "gate": P15_0_GATE,
    "phase": "P15.0",
    "status": "ARCHITECTURE_BASELINE",
    "entities": {
        "forecast": {
            "identity": "forecast_id",
            "meaning": "Stable forecast question/target and evaluation horizon.",
        },
        "forecast_version": {
            "identity": "forecast_version_id",
            "parent": "forecast_id",
            "meaning": "Immutable analytical forecast snapshot and provenance-bound assumptions.",
        },
        "scenario_version": {
            "identity": "scenario_version_id",
            "parent": "forecast_version_id",
            "probability_fields": (
                "raw_probability",
                "calibrated_probability",
                "scenario_confidence",
            ),
            "meaning": "Immutable scenario probability assessment under the E7 semantic contract.",
        },
        "outcome_assessment": {
            "identity": "outcome_assessment_id",
            "parent": "forecast_id",
            "states": OUTCOME_STATES,
            "meaning": "Provenance-bound assessment of what can be concluded at evaluation time.",
        },
        "calibration_observation": {
            "identity": "calibration_observation_id",
            "parents": ("forecast_version_id", "scenario_version_id", "outcome_assessment_id"),
            "meaning": "Immutable scoring observation produced only when the outcome is scoreable.",
        },
        "performance_aggregate": {
            "identity": "performance_aggregate_id",
            "meaning": "Derived forecast-performance evidence over an explicitly defined cohort.",
        },
    },
    "outcome_contract": {
        "states": OUTCOME_STATES,
        "scoreable_states": SCOREABLE_OUTCOME_STATES,
        "rules": (
            "RESOLVED requires explicit outcome evidence and provenance.",
            "UNRESOLVED is not equivalent to a negative outcome.",
            "PARTIAL is not automatically coerced to a binary outcome.",
            "AMBIGUOUS fails closed for automatic scoring.",
            "Outcome assessment does not rewrite historical forecast versions.",
        ),
    },
    "calibration_contract": {
        "initial_metric_family": ("BRIER_SCORE", "RELIABILITY_BUCKETS"),
        "rules": (
            "Calibration evaluates forecast probability performance, not factual verification quality.",
            "A score requires an explicitly scoreable outcome assessment.",
            "Raw and calibrated probabilities remain separate evaluation inputs.",
            "Scenario confidence is never substituted for probability.",
            "Aggregate performance must expose cohort definition and sample size.",
            "Small-sample performance must remain explicitly qualified.",
        ),
    },
    "epistemic_invariants": (
        "Forecast probability or confidence cannot promote factual verification.",
        "Calibration score cannot promote factual verification.",
        "Performance rank cannot promote factual verification.",
        "Coverage metrics cannot promote factual verification confidence.",
        "Legacy scalar confidence cannot promote factual verification.",
        "Source, host, domain, language, adapter or item counts cannot promote factual verification.",
        "Outcome evidence and forecast input evidence remain distinct provenance roles.",
        "Outcome resolution does not retroactively convert forecast context into independent evidence.",
        "Canonical factual verification remains owned by the current P13.5 decision through the P13.6 bridge.",
    ),
    "compatibility": {
        "forecast_semantics_version": "KGM_FORECAST_SEMANTICS_V1",
        "existing_probability_fields": (
            "raw_probability",
            "calibrated_probability",
            "scenario_confidence",
        ),
        "migration_028": "NONE_FOR_P15_0",
        "legacy_forecast_state": "READABLE_UNCHANGED",
        "phase_14_owner_activation": "UNCHANGED_OWNER_DECISION_REQUIRED",
    },
    "runtime_security_boundary": {
        "runtime_storage": "PROJECT_LOCAL_ONLY",
        "mixed_shared_canonical_runtime": "BLOCKED",
        "production_live": "NOT_OPERATIONAL",
        "public_ingress": "NOT_APPROVED_NOT_DEPLOYED",
        "paid_providers": "NONE_APPROVED",
        "owner_execution": "DISABLED",
    },
}


def forecast_calibration_architecture_contract() -> dict[str, object]:
    """Return a detached copy of the P15.0 architecture contract."""

    return deepcopy(FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT)


__all__ = [
    "FORECAST_CALIBRATION_ARCHITECTURE_VERSION",
    "P15_0_GATE",
    "OUTCOME_RESOLVED",
    "OUTCOME_UNRESOLVED",
    "OUTCOME_PARTIAL",
    "OUTCOME_AMBIGUOUS",
    "OUTCOME_STATES",
    "SCOREABLE_OUTCOME_STATES",
    "FORECAST_CALIBRATION_ARCHITECTURE_CONTRACT",
    "forecast_calibration_architecture_contract",
]
