"""M12.3 scenario lifecycle orchestration over the durable forecast baseline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .advanced_forecasting import (
    ForecastVersion,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
    forecast_version_id,
    validate_scenario_distribution,
)
from .forecast_inputs import (
    ForecastInputRef,
    SQLiteForecastInputRepository,
    create_forecast_version_with_inputs,
)
from .operational_monitoring import _normalize_time
from .probabilistic_forecasting import ScenarioType


UNCHANGED = "UNCHANGED"
TRIGGERED = "TRIGGERED"
INHIBITED = "INHIBITED"
INVALIDATED = "INVALIDATED"
SCENARIO_SIGNAL_STATES = {UNCHANGED, TRIGGERED, INHIBITED, INVALIDATED}


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _string_tuple(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    return tuple(_nonempty(value, field_name) for value in values)


def _scenario_type_value(value: ScenarioType | str) -> str:
    raw = value.value if isinstance(value, ScenarioType) else str(value).strip().lower()
    allowed = {item.value for item in ScenarioType}
    if raw not in allowed:
        raise ValueError(f"unsupported scenario type: {raw}")
    return raw


@dataclass(frozen=True)
class ScenarioDraft:
    scenario_type: str
    label: str
    raw_probability: float
    calibrated_probability: float
    scenario_confidence: float
    drivers: tuple[str, ...]
    constraints: tuple[str, ...]
    triggers: tuple[str, ...]
    inhibitors: tuple[str, ...]
    uncertainty_factors: tuple[str, ...]
    invalidation_signals: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "scenario_type", _scenario_type_value(self.scenario_type))
        object.__setattr__(self, "label", _nonempty(self.label, "label"))
        for field_name in ("raw_probability", "calibrated_probability", "scenario_confidence"):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        for field_name in (
            "drivers",
            "constraints",
            "triggers",
            "inhibitors",
            "uncertainty_factors",
            "invalidation_signals",
        ):
            values = _string_tuple(getattr(self, field_name), field_name)
            if not values:
                raise ValueError(f"complete scenario draft requires {field_name}")
            object.__setattr__(self, field_name, values)

    def materialize(self, forecast_version_id_value: str) -> ScenarioVersion:
        return ScenarioVersion.create(
            forecast_version_id_value,
            self.scenario_type,
            self.label,
            self.raw_probability,
            self.calibrated_probability,
            self.scenario_confidence,
            drivers=self.drivers,
            constraints=self.constraints,
            triggers=self.triggers,
            inhibitors=self.inhibitors,
            uncertainty_factors=self.uncertainty_factors,
            invalidation_signals=self.invalidation_signals,
        )


@dataclass(frozen=True)
class ScenarioSignalEvaluation:
    state: str
    triggered_signals: tuple[str, ...]
    inhibitor_signals: tuple[str, ...]
    invalidation_signals: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.state not in SCENARIO_SIGNAL_STATES:
            raise ValueError(f"unsupported scenario signal state: {self.state}")


@dataclass(frozen=True)
class ForecastVersionState:
    version: ForecastVersion
    scenarios: tuple[ScenarioVersion, ...]
    inputs: tuple[ForecastInputRef, ...]


def evaluate_scenario_signals(
    scenario: ScenarioVersion,
    observed_signals: Iterable[str],
) -> ScenarioSignalEvaluation:
    observed = {_nonempty(value, "observed_signal") for value in observed_signals}
    triggered = tuple(value for value in scenario.triggers if value in observed)
    inhibited = tuple(value for value in scenario.inhibitors if value in observed)
    invalidated = tuple(value for value in scenario.invalidation_signals if value in observed)

    if invalidated:
        state = INVALIDATED
    elif inhibited:
        state = INHIBITED
    elif triggered:
        state = TRIGGERED
    else:
        state = UNCHANGED

    return ScenarioSignalEvaluation(
        state=state,
        triggered_signals=triggered,
        inhibitor_signals=inhibited,
        invalidation_signals=invalidated,
    )


class ScenarioLifecycleService:
    """Create immutable forecast versions and preserve complete scenario history."""

    def __init__(self, database_path: str | Path):
        self.forecasts = SQLiteAdvancedForecastRepository(database_path)
        self.inputs = SQLiteForecastInputRepository(database_path)

    def create_next_version(
        self,
        forecast_id_value: str,
        *,
        inputs: Iterable[ForecastInputRef],
        constraints: Iterable[str],
        scenarios: Iterable[ScenarioDraft],
        change_reason: str,
        created_at: datetime,
    ) -> ForecastVersionState:
        reason = _nonempty(change_reason, "change_reason")
        if self.forecasts.get_forecast(forecast_id_value) is None:
            raise ValueError("forecast must exist before creating a scenario version")

        version_number = self.forecasts.next_version_number(forecast_id_value)
        version_id = forecast_version_id(forecast_id_value, version_number)
        input_items = tuple(inputs)
        if not input_items:
            raise ValueError("scenario lifecycle requires provenance-bound forecast inputs")
        if any(item.forecast_version_id != version_id for item in input_items):
            raise ValueError("forecast inputs must target the next deterministic forecast version")

        validated_inputs = self.inputs.validate(input_items)
        draft_items = tuple(scenarios)
        if not draft_items:
            raise ValueError("scenario lifecycle requires at least one scenario draft")
        scenario_items = tuple(draft.materialize(version_id) for draft in draft_items)
        validate_scenario_distribution(scenario_items)

        version = create_forecast_version_with_inputs(
            forecast_id_value,
            version_number,
            inputs=validated_inputs,
            constraints=constraints,
            change_reason=reason,
            created_at=_normalize_time(created_at),
        )
        self.forecasts.save_version(version, scenario_items)
        self.inputs.bind(version, validated_inputs, constraints=constraints)
        return ForecastVersionState(version, scenario_items, validated_inputs)

    def history(self, forecast_id_value: str) -> tuple[ForecastVersionState, ...]:
        return tuple(
            ForecastVersionState(
                version=version,
                scenarios=self.forecasts.list_scenarios(version.forecast_version_id),
                inputs=self.inputs.list_inputs(version.forecast_version_id),
            )
            for version in self.forecasts.list_versions(forecast_id_value)
        )


__all__ = [
    "UNCHANGED",
    "TRIGGERED",
    "INHIBITED",
    "INVALIDATED",
    "SCENARIO_SIGNAL_STATES",
    "ScenarioDraft",
    "ScenarioSignalEvaluation",
    "ForecastVersionState",
    "evaluate_scenario_signals",
    "ScenarioLifecycleService",
]
