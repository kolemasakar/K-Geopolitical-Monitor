"""E7 canonical semantics for forecast probability presentation.

This module is presentation-only. It names already-persisted M12 forecast fields and
makes their epistemic boundaries machine-readable without changing forecasting,
verification, confidence, graph, provenance, or storage state.
"""

from __future__ import annotations

from typing import Final


FORECAST_SEMANTICS_VERSION: Final[str] = "KGM_FORECAST_SEMANTICS_V1"

RAW_PROBABILITY: Final[str] = "raw_probability"
CALIBRATED_PROBABILITY: Final[str] = "calibrated_probability"
SCENARIO_CONFIDENCE: Final[str] = "scenario_confidence"

FORECAST_SEMANTIC_FIELDS: Final[tuple[str, ...]] = (
    RAW_PROBABILITY,
    CALIBRATED_PROBABILITY,
    SCENARIO_CONFIDENCE,
)

FORECAST_SEMANTIC_CONTRACT: Final[dict[str, object]] = {
    "version": FORECAST_SEMANTICS_VERSION,
    "fields": {
        RAW_PROBABILITY: {
            "class": "FORECAST_PROBABILITY",
            "meaning": "Analytical scenario probability before calibration.",
            "is_factual_confidence": False,
            "is_verification_confidence": False,
        },
        CALIBRATED_PROBABILITY: {
            "class": "CALIBRATED_FORECAST_PROBABILITY",
            "meaning": "Calibrated analytical scenario probability.",
            "is_factual_confidence": False,
            "is_verification_confidence": False,
        },
        SCENARIO_CONFIDENCE: {
            "class": "SCENARIO_ANALYTICAL_CONFIDENCE",
            "meaning": (
                "Confidence in the quality or stability of the scenario assessment; "
                "not the probability that the scenario occurs."
            ),
            "is_probability": False,
            "is_factual_confidence": False,
            "is_verification_confidence": False,
        },
    },
    "invariants": (
        "Forecast probabilities are analytical outputs, not facts.",
        "Scenario confidence is not forecast probability.",
        "Forecast metrics do not modify claim verification state.",
        "Forecast metrics do not modify factual or evidence confidence.",
        "Forecast metrics do not modify independent-origin counts.",
        "Graph relationships used as forecast context are not independent evidence.",
    ),
}


def forecast_semantic_contract() -> dict[str, object]:
    """Return a fresh JSON-safe copy of the canonical E7 semantic contract."""

    fields = FORECAST_SEMANTIC_CONTRACT["fields"]
    assert isinstance(fields, dict)
    invariants = FORECAST_SEMANTIC_CONTRACT["invariants"]
    assert isinstance(invariants, tuple)
    return {
        "version": FORECAST_SEMANTICS_VERSION,
        "fields": {
            str(name): dict(value)
            for name, value in fields.items()
            if isinstance(value, dict)
        },
        "invariants": list(invariants),
    }


__all__ = [
    "FORECAST_SEMANTICS_VERSION",
    "RAW_PROBABILITY",
    "CALIBRATED_PROBABILITY",
    "SCENARIO_CONFIDENCE",
    "FORECAST_SEMANTIC_FIELDS",
    "FORECAST_SEMANTIC_CONTRACT",
    "forecast_semantic_contract",
]
