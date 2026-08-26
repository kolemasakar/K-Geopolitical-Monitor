"""M12.4 durable outcome resolution and historical forecast evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Iterable

from .database import initialize_database
from .forecast_metrics import calculate_brier_score, calculate_calibration_error
from .forecast_preparation import ForecastHorizon
from .operational_monitoring import _normalize_time, utc_now
from .probabilistic_forecasting import ScenarioType


OBSERVED = "OBSERVED"
NOT_OBSERVED = "NOT_OBSERVED"
PARTIAL = "PARTIAL"
AMBIGUOUS = "AMBIGUOUS"
OUTCOME_STATES = {OBSERVED, NOT_OBSERVED, PARTIAL, AMBIGUOUS}

BINARY_ONE_VS_REST = "BINARY_ONE_VS_REST"
BINARY_ONE_VS_REST_VERSION = "1"


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _scenario_type_value(value: ScenarioType | str | None) -> str | None:
    if value is None:
        return None
    raw = value.value if isinstance(value, ScenarioType) else str(value).strip().lower()
    allowed = {item.value for item in ScenarioType}
    if raw not in allowed:
        raise ValueError(f"unsupported scenario type: {raw}")
    return raw


def _horizon_value(value: ForecastHorizon | str) -> str:
    raw = value.value if isinstance(value, ForecastHorizon) else str(value).strip()
    allowed = {item.value for item in ForecastHorizon}
    if raw not in allowed:
        raise ValueError(f"unsupported forecast horizon: {raw}")
    return raw


def outcome_id(forecast_id: str) -> str:
    return _stable_id("outcome", _nonempty(forecast_id, "forecast_id"))


def evaluation_id(
    outcome_id_value: str,
    scenario_version_id: str,
    method: str,
    method_version: str,
) -> str:
    return _stable_id(
        "feval",
        _nonempty(outcome_id_value, "outcome_id"),
        _nonempty(scenario_version_id, "scenario_version_id"),
        _nonempty(method, "evaluation_method"),
        _nonempty(method_version, "evaluation_method_version"),
    )


@dataclass(frozen=True)
class ForecastOutcome:
    outcome_id: str
    forecast_id: str
    resolved_at: datetime
    outcome_state: str
    observed_scenario_type: str | None
    evidence_refs: tuple[str, ...]
    explanation: str
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        forecast_id_value = _nonempty(self.forecast_id, "forecast_id")
        state = _nonempty(self.outcome_state, "outcome_state").upper()
        if state not in OUTCOME_STATES:
            raise ValueError(f"unsupported outcome state: {state}")
        scenario_type = _scenario_type_value(self.observed_scenario_type)
        if state == OBSERVED and scenario_type is None:
            raise ValueError("OBSERVED outcome requires observed_scenario_type")
        if state == NOT_OBSERVED and scenario_type is not None:
            raise ValueError("NOT_OBSERVED outcome must not set observed_scenario_type")
        refs = tuple(sorted({_nonempty(value, "evidence_ref") for value in self.evidence_refs}))
        if not refs:
            raise ValueError("forecast outcome requires at least one evidence_ref")
        explanation = _nonempty(self.explanation, "explanation")
        resolved = _normalize_time(self.resolved_at)
        created = _normalize_time(self.created_at)
        expected = outcome_id(forecast_id_value)
        if self.outcome_id != expected:
            raise ValueError("outcome_id must match deterministic forecast outcome identity")
        object.__setattr__(self, "forecast_id", forecast_id_value)
        object.__setattr__(self, "outcome_state", state)
        object.__setattr__(self, "observed_scenario_type", scenario_type)
        object.__setattr__(self, "evidence_refs", refs)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "resolved_at", resolved)
        object.__setattr__(self, "created_at", created)

    @classmethod
    def create(
        cls,
        forecast_id: str,
        resolved_at: datetime,
        outcome_state: str,
        *,
        observed_scenario_type: ScenarioType | str | None = None,
        evidence_refs: Iterable[str],
        explanation: str,
        created_at: datetime | None = None,
    ) -> "ForecastOutcome":
        return cls(
            outcome_id=outcome_id(forecast_id),
            forecast_id=forecast_id,
            resolved_at=_normalize_time(resolved_at),
            outcome_state=outcome_state,
            observed_scenario_type=_scenario_type_value(observed_scenario_type),
            evidence_refs=tuple(evidence_refs),
            explanation=explanation,
            created_at=_normalize_time(created_at or utc_now()),
        )


@dataclass(frozen=True)
class ForecastEvaluation:
    evaluation_id: str
    outcome_id: str
    forecast_id: str
    forecast_version_id: str
    scenario_version_id: str
    horizon: str
    scenario_type: str
    scenario_label: str
    raw_probability: float
    calibrated_probability: float
    observed_value: float | None
    brier_score_raw: float | None
    brier_score_calibrated: float | None
    calibration_error_raw: float | None
    calibration_error_calibrated: float | None
    evaluation_method: str
    evaluation_method_version: str
    sample_count: int
    evaluated_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizon", _horizon_value(self.horizon))
        object.__setattr__(self, "scenario_type", _scenario_type_value(self.scenario_type))
        object.__setattr__(self, "scenario_label", _nonempty(self.scenario_label, "scenario_label"))
        for field_name in ("raw_probability", "calibrated_probability"):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        if self.sample_count not in {0, 1}:
            raise ValueError("evaluation sample_count must be 0 or 1")
        if self.sample_count == 0:
            if any(
                value is not None
                for value in (
                    self.observed_value,
                    self.brier_score_raw,
                    self.brier_score_calibrated,
                    self.calibration_error_raw,
                    self.calibration_error_calibrated,
                )
            ):
                raise ValueError("unscorable evaluation must not contain binary metrics")
        else:
            if self.observed_value not in {0.0, 1.0, 0, 1}:
                raise ValueError("scorable evaluation requires observed_value 0 or 1")
            for field_name in (
                "brier_score_raw",
                "brier_score_calibrated",
                "calibration_error_raw",
                "calibration_error_calibrated",
            ):
                value = getattr(self, field_name)
                if value is None or not 0.0 <= float(value) <= 1.0:
                    raise ValueError(f"{field_name} must be between 0 and 1")
                object.__setattr__(self, field_name, float(value))
            object.__setattr__(self, "observed_value", float(self.observed_value))
        object.__setattr__(self, "evaluation_method", _nonempty(self.evaluation_method, "evaluation_method"))
        object.__setattr__(
            self,
            "evaluation_method_version",
            _nonempty(self.evaluation_method_version, "evaluation_method_version"),
        )
        object.__setattr__(self, "evaluated_at", _normalize_time(self.evaluated_at))


@dataclass(frozen=True)
class HorizonEvaluationSummary:
    horizon: str
    evaluation_count: int
    scorable_evaluation_count: int
    unscorable_evaluation_count: int
    forecast_count: int
    mean_brier_score_raw: float | None
    mean_brier_score_calibrated: float | None
    mean_calibration_error_raw: float | None
    mean_calibration_error_calibrated: float | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizon", _horizon_value(self.horizon))


class SQLiteForecastEvaluationRepository:
    """Persist final outcomes and immutable per-scenario historical evaluations."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def save_outcome(self, outcome: ForecastOutcome) -> ForecastOutcome:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            if connection.execute(
                "SELECT 1 FROM forecasts WHERE forecast_id = ?",
                (outcome.forecast_id,),
            ).fetchone() is None:
                raise ValueError("forecast does not exist")
            for evidence_ref in outcome.evidence_refs:
                if connection.execute(
                    "SELECT 1 FROM raw_items WHERE id = ?",
                    (evidence_ref,),
                ).fetchone() is None:
                    raise ValueError(f"unknown outcome evidence reference: {evidence_ref}")

            payload = (
                outcome.forecast_id,
                outcome.resolved_at.isoformat(),
                outcome.outcome_state,
                outcome.observed_scenario_type,
                json.dumps(outcome.evidence_refs),
                outcome.explanation,
                outcome.created_at.isoformat(),
            )
            existing = connection.execute(
                """
                SELECT forecast_id, resolved_at, outcome_state, observed_scenario_type,
                       evidence_refs_json, explanation, created_at
                FROM forecast_outcomes WHERE outcome_id = ?
                """,
                (outcome.outcome_id,),
            ).fetchone()
            if existing is not None:
                if tuple(existing) != payload:
                    raise ValueError("forecast outcome is immutable")
                return outcome
            connection.execute(
                """
                INSERT INTO forecast_outcomes(
                    outcome_id, forecast_id, resolved_at, outcome_state,
                    observed_scenario_type, evidence_refs_json, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (outcome.outcome_id, *payload),
            )
        return outcome

    def get_outcome(self, outcome_id_value: str) -> ForecastOutcome | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT outcome_id, forecast_id, resolved_at, outcome_state,
                       observed_scenario_type, evidence_refs_json, explanation, created_at
                FROM forecast_outcomes WHERE outcome_id = ?
                """,
                (outcome_id_value,),
            ).fetchone()
        if row is None:
            return None
        return ForecastOutcome(
            outcome_id=row[0],
            forecast_id=row[1],
            resolved_at=datetime.fromisoformat(row[2]),
            outcome_state=row[3],
            observed_scenario_type=row[4],
            evidence_refs=tuple(json.loads(row[5])),
            explanation=row[6],
            created_at=datetime.fromisoformat(row[7]),
        )

    def evaluate_version(
        self,
        outcome_id_value: str,
        forecast_version_id_value: str,
        *,
        evaluated_at: datetime,
        method: str = BINARY_ONE_VS_REST,
        method_version: str = BINARY_ONE_VS_REST_VERSION,
    ) -> tuple[ForecastEvaluation, ...]:
        outcome = self.get_outcome(outcome_id_value)
        if outcome is None:
            raise ValueError("forecast outcome does not exist")
        method_value = _nonempty(method, "evaluation_method")
        method_version_value = _nonempty(method_version, "evaluation_method_version")
        evaluated = _normalize_time(evaluated_at)

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            version_row = connection.execute(
                """
                SELECT fv.forecast_id, f.horizon
                FROM forecast_versions fv
                JOIN forecasts f ON f.forecast_id = fv.forecast_id
                WHERE fv.forecast_version_id = ?
                """,
                (forecast_version_id_value,),
            ).fetchone()
            if version_row is None:
                raise ValueError("forecast version does not exist")
            forecast_id_value, horizon = version_row
            if forecast_id_value != outcome.forecast_id:
                raise ValueError("forecast outcome and evaluated version belong to different forecasts")

            scenario_rows = connection.execute(
                """
                SELECT scenario_version_id, scenario_type, label,
                       raw_probability, calibrated_probability
                FROM forecast_scenario_versions
                WHERE forecast_version_id = ?
                ORDER BY scenario_type, label, scenario_version_id
                """,
                (forecast_version_id_value,),
            ).fetchall()
            if not scenario_rows:
                raise ValueError("forecast version has no scenarios")

            if outcome.outcome_state == OBSERVED:
                matches = [row for row in scenario_rows if row[1] == outcome.observed_scenario_type]
                if len(matches) != 1:
                    raise ValueError(
                        "observed_scenario_type must identify exactly one scenario in evaluated version"
                    )

            evaluations: list[ForecastEvaluation] = []
            for row in scenario_rows:
                scenario_version_id_value, scenario_type, label, raw_probability, calibrated_probability = row
                if outcome.outcome_state in {PARTIAL, AMBIGUOUS}:
                    observed_value = None
                    brier_raw = None
                    brier_calibrated = None
                    calibration_raw = None
                    calibration_calibrated = None
                    sample_count = 0
                else:
                    if outcome.outcome_state == NOT_OBSERVED:
                        observed_value = 0.0
                    else:
                        observed_value = 1.0 if scenario_type == outcome.observed_scenario_type else 0.0
                    brier_raw = calculate_brier_score(float(raw_probability), observed_value)
                    brier_calibrated = calculate_brier_score(
                        float(calibrated_probability), observed_value
                    )
                    calibration_raw = calculate_calibration_error(
                        float(raw_probability), observed_value
                    )
                    calibration_calibrated = calculate_calibration_error(
                        float(calibrated_probability), observed_value
                    )
                    sample_count = 1

                eval_id = evaluation_id(
                    outcome.outcome_id,
                    scenario_version_id_value,
                    method_value,
                    method_version_value,
                )
                evaluation = ForecastEvaluation(
                    evaluation_id=eval_id,
                    outcome_id=outcome.outcome_id,
                    forecast_id=outcome.forecast_id,
                    forecast_version_id=forecast_version_id_value,
                    scenario_version_id=scenario_version_id_value,
                    horizon=horizon,
                    scenario_type=scenario_type,
                    scenario_label=label,
                    raw_probability=float(raw_probability),
                    calibrated_probability=float(calibrated_probability),
                    observed_value=observed_value,
                    brier_score_raw=brier_raw,
                    brier_score_calibrated=brier_calibrated,
                    calibration_error_raw=calibration_raw,
                    calibration_error_calibrated=calibration_calibrated,
                    evaluation_method=method_value,
                    evaluation_method_version=method_version_value,
                    sample_count=sample_count,
                    evaluated_at=evaluated,
                )

                existing = connection.execute(
                    """
                    SELECT evaluation_id, outcome_id, forecast_id, forecast_version_id,
                           scenario_version_id, horizon, scenario_type, scenario_label,
                           raw_probability, calibrated_probability, observed_value,
                           brier_score_raw, brier_score_calibrated,
                           calibration_error_raw, calibration_error_calibrated,
                           evaluation_method, evaluation_method_version, sample_count,
                           evaluated_at
                    FROM forecast_evaluations WHERE evaluation_id = ?
                    """,
                    (eval_id,),
                ).fetchone()
                if existing is not None:
                    persisted = self._row_to_evaluation(existing)
                    expected_core = evaluation.__dict__.copy()
                    persisted_core = persisted.__dict__.copy()
                    expected_core.pop("evaluated_at")
                    persisted_core.pop("evaluated_at")
                    if persisted_core != expected_core:
                        raise ValueError("forecast evaluation is immutable")
                    evaluations.append(persisted)
                    continue

                connection.execute(
                    """
                    INSERT INTO forecast_evaluations(
                        evaluation_id, outcome_id, forecast_id, forecast_version_id,
                        scenario_version_id, horizon, scenario_type, scenario_label,
                        raw_probability, calibrated_probability, observed_value,
                        brier_score_raw, brier_score_calibrated,
                        calibration_error_raw, calibration_error_calibrated,
                        evaluation_method, evaluation_method_version, sample_count,
                        evaluated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        evaluation.evaluation_id,
                        evaluation.outcome_id,
                        evaluation.forecast_id,
                        evaluation.forecast_version_id,
                        evaluation.scenario_version_id,
                        evaluation.horizon,
                        evaluation.scenario_type,
                        evaluation.scenario_label,
                        evaluation.raw_probability,
                        evaluation.calibrated_probability,
                        evaluation.observed_value,
                        evaluation.brier_score_raw,
                        evaluation.brier_score_calibrated,
                        evaluation.calibration_error_raw,
                        evaluation.calibration_error_calibrated,
                        evaluation.evaluation_method,
                        evaluation.evaluation_method_version,
                        evaluation.sample_count,
                        evaluation.evaluated_at.isoformat(),
                    ),
                )
                evaluations.append(evaluation)
        return tuple(evaluations)

    @staticmethod
    def _row_to_evaluation(row: tuple[object, ...]) -> ForecastEvaluation:
        return ForecastEvaluation(
            evaluation_id=str(row[0]),
            outcome_id=str(row[1]),
            forecast_id=str(row[2]),
            forecast_version_id=str(row[3]),
            scenario_version_id=str(row[4]),
            horizon=str(row[5]),
            scenario_type=str(row[6]),
            scenario_label=str(row[7]),
            raw_probability=float(row[8]),
            calibrated_probability=float(row[9]),
            observed_value=None if row[10] is None else float(row[10]),
            brier_score_raw=None if row[11] is None else float(row[11]),
            brier_score_calibrated=None if row[12] is None else float(row[12]),
            calibration_error_raw=None if row[13] is None else float(row[13]),
            calibration_error_calibrated=None if row[14] is None else float(row[14]),
            evaluation_method=str(row[15]),
            evaluation_method_version=str(row[16]),
            sample_count=int(row[17]),
            evaluated_at=datetime.fromisoformat(str(row[18])),
        )

    def list_evaluations(self, outcome_id_value: str) -> tuple[ForecastEvaluation, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT evaluation_id, outcome_id, forecast_id, forecast_version_id,
                       scenario_version_id, horizon, scenario_type, scenario_label,
                       raw_probability, calibrated_probability, observed_value,
                       brier_score_raw, brier_score_calibrated,
                       calibration_error_raw, calibration_error_calibrated,
                       evaluation_method, evaluation_method_version, sample_count,
                       evaluated_at
                FROM forecast_evaluations
                WHERE outcome_id = ?
                ORDER BY forecast_version_id, scenario_type, scenario_label, evaluation_id
                """,
                (outcome_id_value,),
            ).fetchall()
        return tuple(self._row_to_evaluation(row) for row in rows)

    def summarize_horizon(self, horizon: ForecastHorizon | str) -> HorizonEvaluationSummary:
        horizon_value = _horizon_value(horizon)
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(sample_count), 0),
                       COUNT(DISTINCT forecast_id),
                       AVG(brier_score_raw), AVG(brier_score_calibrated),
                       AVG(calibration_error_raw), AVG(calibration_error_calibrated)
                FROM forecast_evaluations
                WHERE horizon = ?
                """,
                (horizon_value,),
            ).fetchone()
        evaluation_count = int(row[0])
        scorable_count = int(row[1])
        return HorizonEvaluationSummary(
            horizon=horizon_value,
            evaluation_count=evaluation_count,
            scorable_evaluation_count=scorable_count,
            unscorable_evaluation_count=evaluation_count - scorable_count,
            forecast_count=int(row[2]),
            mean_brier_score_raw=None if row[3] is None else float(row[3]),
            mean_brier_score_calibrated=None if row[4] is None else float(row[4]),
            mean_calibration_error_raw=None if row[5] is None else float(row[5]),
            mean_calibration_error_calibrated=None if row[6] is None else float(row[6]),
        )


__all__ = [
    "OBSERVED",
    "NOT_OBSERVED",
    "PARTIAL",
    "AMBIGUOUS",
    "OUTCOME_STATES",
    "BINARY_ONE_VS_REST",
    "BINARY_ONE_VS_REST_VERSION",
    "ForecastOutcome",
    "ForecastEvaluation",
    "HorizonEvaluationSummary",
    "SQLiteForecastEvaluationRepository",
    "outcome_id",
    "evaluation_id",
]
