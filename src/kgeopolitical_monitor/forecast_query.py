"""M12.6 read-only advanced forecast query and explanation facade."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3

from .advanced_forecasting import (
    ForecastRecord,
    ForecastVersion,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
)
from .forecast_calibration_history import (
    CalibrationBucket,
    CalibrationRun,
    SQLiteForecastCalibrationRepository,
)
from .forecast_evaluation import (
    ForecastEvaluation,
    ForecastOutcome,
    SQLiteForecastEvaluationRepository,
    outcome_id,
)
from .forecast_inputs import (
    ANALYST_ASSUMPTION,
    GRAPH_RELATIONSHIP,
    SOURCE_EVIDENCE,
    ForecastInputRef,
    SQLiteForecastInputRepository,
)


@dataclass(frozen=True)
class ForecastVersionView:
    forecast: ForecastRecord
    version: ForecastVersion
    scenarios: tuple[ScenarioVersion, ...]
    inputs: tuple[ForecastInputRef, ...]


@dataclass(frozen=True)
class ScenarioDelta:
    scenario_type: str
    label: str
    from_raw_probability: float | None
    to_raw_probability: float | None
    from_calibrated_probability: float | None
    to_calibrated_probability: float | None
    from_scenario_confidence: float | None
    to_scenario_confidence: float | None


@dataclass(frozen=True)
class ForecastExplanation:
    forecast_id: str
    forecast_version_id: str
    version_number: int
    change_reason: str
    source_evidence_refs: tuple[str, ...]
    graph_relationship_refs: tuple[str, ...]
    other_provenance_refs: tuple[str, ...]
    analyst_assumptions: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class ForecastOutcomeView:
    outcome: ForecastOutcome
    evaluations: tuple[ForecastEvaluation, ...]


@dataclass(frozen=True)
class ForecastCalibrationView:
    run: CalibrationRun
    buckets: tuple[CalibrationBucket, ...]


class AdvancedForecastQuery:
    """Read-only M12 facade across durable forecast, provenance and evaluation history."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.forecasts = SQLiteAdvancedForecastRepository(self.database_path)
        self.inputs = SQLiteForecastInputRepository(self.database_path)
        self.evaluations = SQLiteForecastEvaluationRepository(self.database_path)
        self.calibration = SQLiteForecastCalibrationRepository(self.database_path)

    def _require_forecast(self, forecast_id_value: str) -> ForecastRecord:
        forecast = self.forecasts.get_forecast(forecast_id_value)
        if forecast is None:
            raise ValueError(f"unknown forecast: {forecast_id_value}")
        return forecast

    def _require_version(self, forecast_version_id_value: str) -> ForecastVersion:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT forecast_id FROM forecast_versions WHERE forecast_version_id = ?",
                (forecast_version_id_value,),
            ).fetchone()
        if row is None:
            raise ValueError(f"unknown forecast version: {forecast_version_id_value}")
        for version in self.forecasts.list_versions(str(row[0])):
            if version.forecast_version_id == forecast_version_id_value:
                return version
        raise ValueError(f"unknown forecast version: {forecast_version_id_value}")

    def _view(self, forecast: ForecastRecord, version: ForecastVersion) -> ForecastVersionView:
        return ForecastVersionView(
            forecast=forecast,
            version=version,
            scenarios=self.forecasts.list_scenarios(version.forecast_version_id),
            inputs=self.inputs.list_inputs(version.forecast_version_id),
        )

    def current_forecast(self, forecast_id_value: str) -> ForecastVersionView:
        forecast = self._require_forecast(forecast_id_value)
        versions = self.forecasts.list_versions(forecast_id_value)
        if not versions:
            raise ValueError("forecast has no persisted versions")
        return self._view(forecast, versions[-1])

    def version_history(self, forecast_id_value: str) -> tuple[ForecastVersionView, ...]:
        forecast = self._require_forecast(forecast_id_value)
        return tuple(self._view(forecast, version) for version in self.forecasts.list_versions(forecast_id_value))

    def compare_scenarios(
        self,
        forecast_id_value: str,
        from_version_number: int,
        to_version_number: int,
    ) -> tuple[ScenarioDelta, ...]:
        versions = {item.version.version_number: item for item in self.version_history(forecast_id_value)}
        if from_version_number not in versions or to_version_number not in versions:
            raise ValueError("requested forecast version number does not exist")
        left = {(item.scenario_type, item.label): item for item in versions[from_version_number].scenarios}
        right = {(item.scenario_type, item.label): item for item in versions[to_version_number].scenarios}
        keys = sorted(set(left) | set(right))
        return tuple(
            ScenarioDelta(
                scenario_type=key[0],
                label=key[1],
                from_raw_probability=None if key not in left else left[key].raw_probability,
                to_raw_probability=None if key not in right else right[key].raw_probability,
                from_calibrated_probability=None if key not in left else left[key].calibrated_probability,
                to_calibrated_probability=None if key not in right else right[key].calibrated_probability,
                from_scenario_confidence=None if key not in left else left[key].scenario_confidence,
                to_scenario_confidence=None if key not in right else right[key].scenario_confidence,
            )
            for key in keys
        )

    def explain_version(self, forecast_version_id_value: str) -> ForecastExplanation:
        version = self._require_version(forecast_version_id_value)
        inputs = self.inputs.list_inputs(forecast_version_id_value)
        scenarios = self.forecasts.list_scenarios(forecast_version_id_value)
        source_refs = tuple(sorted(item.reference_id for item in inputs if item.input_kind == SOURCE_EVIDENCE and item.reference_id))
        graph_refs = tuple(sorted(item.reference_id for item in inputs if item.input_kind == GRAPH_RELATIONSHIP and item.reference_id))
        assumptions = tuple(sorted(item.statement for item in inputs if item.input_kind == ANALYST_ASSUMPTION and item.statement))
        other_refs = tuple(
            sorted(
                f"{item.input_kind}:{item.reference_id}"
                for item in inputs
                if item.reference_id
                and item.input_kind not in {SOURCE_EVIDENCE, GRAPH_RELATIONSHIP}
            )
        )
        text = (
            f"Forecast version {version.version_number} is an analytical output, not a fact. "
            f"It uses {len(source_refs)} source-evidence reference(s), {len(graph_refs)} graph relationship reference(s), "
            f"and {len(assumptions)} explicit analyst assumption(s). Graph relationships remain analytical inputs "
            "and are not independent source evidence. Forecast probability and scenario confidence do not modify "
            "upstream verification confidence or independent-origin counts."
        )
        return ForecastExplanation(
            forecast_id=version.forecast_id,
            forecast_version_id=version.forecast_version_id,
            version_number=version.version_number,
            change_reason=version.change_reason,
            source_evidence_refs=source_refs,
            graph_relationship_refs=graph_refs,
            other_provenance_refs=other_refs,
            analyst_assumptions=assumptions,
            scenario_ids=tuple(item.scenario_version_id for item in scenarios),
            text=text,
        )

    def outcome_history(self, forecast_id_value: str) -> tuple[ForecastOutcomeView, ...]:
        self._require_forecast(forecast_id_value)
        outcome = self.evaluations.get_outcome(outcome_id(forecast_id_value))
        if outcome is None:
            return ()
        return (ForecastOutcomeView(outcome, self.evaluations.list_evaluations(outcome.outcome_id)),)

    def calibration_history(self, forecast_id_value: str | None = None) -> tuple[ForecastCalibrationView, ...]:
        forecast_evaluation_ids: set[str] | None = None
        if forecast_id_value is not None:
            self._require_forecast(forecast_id_value)
            with sqlite3.connect(self.database_path) as connection:
                rows = connection.execute(
                    "SELECT evaluation_id FROM forecast_evaluations WHERE forecast_id = ?",
                    (forecast_id_value,),
                ).fetchall()
            forecast_evaluation_ids = {str(row[0]) for row in rows}

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT calibration_id, evaluation_ids_json FROM forecast_calibration_runs ORDER BY created_at, calibration_id"
            ).fetchall()

        views: list[ForecastCalibrationView] = []
        for calibration_id_value, evaluation_ids_json in rows:
            ids = set(json.loads(str(evaluation_ids_json)))
            if forecast_evaluation_ids is not None and not (ids & forecast_evaluation_ids):
                continue
            run = self.calibration.get_run(str(calibration_id_value))
            if run is not None:
                views.append(ForecastCalibrationView(run, self.calibration.list_buckets(run.calibration_id)))
        return tuple(views)


__all__ = [
    "ForecastVersionView",
    "ScenarioDelta",
    "ForecastExplanation",
    "ForecastOutcomeView",
    "ForecastCalibrationView",
    "AdvancedForecastQuery",
]
