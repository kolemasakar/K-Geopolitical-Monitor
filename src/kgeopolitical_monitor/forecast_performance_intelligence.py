"""Phase 15.4 provenance-bound forecast performance intelligence.

This module aggregates immutable Phase 15.3 calibration observations over an
explicit cohort and compares compatible, non-overlapping temporal cohorts for
descriptive drift. It measures forecast performance only: no metric produced
here can create, alter, rank or promote factual-verification state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Iterable

from .database import initialize_database
from .forecast_calibration_engine import (
    DEFAULT_RELIABILITY_BUCKET_COUNT,
    SCORING_METHOD,
    SCORING_METHOD_VERSION,
)
from .operational_monitoring import _normalize_time, utc_now


P15_4_GATE = "P15_4_PERFORMANCE_INTELLIGENCE_DRIFT_BIAS_VALIDATED"
AGGREGATE_METHOD = "PROVENANCE_BOUND_PERFORMANCE_AGGREGATE"
AGGREGATE_METHOD_VERSION = "1"
DRIFT_COMPARISON_METHOD = "DISJOINT_TEMPORAL_COHORT_DELTA"
DRIFT_COMPARISON_METHOD_VERSION = "1"

FORECAST_HORIZONS = {
    "short_term",
    "medium_term",
    "long_term",
    "global_evolutionary",
}
SCENARIO_TYPES = {"baseline", "positive", "negative", "alternative"}

BIAS_OVER_PREDICTION = "OVER_PREDICTION"
BIAS_UNDER_PREDICTION = "UNDER_PREDICTION"
BIAS_WITHIN_TOLERANCE = "WITHIN_TOLERANCE"


class PerformanceIntelligenceError(ValueError):
    """Raised when a requested performance aggregate/comparison is unsafe."""


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise PerformanceIntelligenceError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _sample_qualification(sample_count: int) -> str:
    count = int(sample_count)
    if count < 1:
        raise PerformanceIntelligenceError("sample_count must be positive")
    if count < 5:
        return "N_LT_5"
    if count < 20:
        return "N_5_TO_19"
    return "N_GE_20"


def classify_bias(bias: float, *, tolerance: float = 0.05) -> str:
    """Classify signed probability bias using an explicit descriptive tolerance.

    Positive bias means mean predicted probability exceeds observed frequency.
    This is a descriptive label only; ``tolerance`` is not a confidence bound or
    statistical-significance threshold.
    """

    bias_value = float(bias)
    tolerance_value = float(tolerance)
    if not -1.0 <= bias_value <= 1.0:
        raise PerformanceIntelligenceError("bias must be between -1 and 1")
    if not 0.0 <= tolerance_value <= 1.0:
        raise PerformanceIntelligenceError("bias tolerance must be between 0 and 1")
    if bias_value > tolerance_value:
        return BIAS_OVER_PREDICTION
    if bias_value < -tolerance_value:
        return BIAS_UNDER_PREDICTION
    return BIAS_WITHIN_TOLERANCE


def _expected_calibration_error(
    rows: Iterable[tuple[int, float, float]],
) -> float:
    grouped: dict[int, list[float]] = {}
    total = 0
    for bucket, predicted, observed in rows:
        bucket_value = int(bucket)
        data = grouped.setdefault(bucket_value, [0.0, 0.0, 0.0])
        data[0] += 1.0
        data[1] += float(predicted)
        data[2] += float(observed)
        total += 1
    if total == 0:
        raise PerformanceIntelligenceError("cannot compute calibration error for empty cohort")

    error = 0.0
    for count, predicted_sum, observed_sum in grouped.values():
        mean_predicted = predicted_sum / count
        mean_observed = observed_sum / count
        error += (count / total) * abs(mean_predicted - mean_observed)
    return error


@dataclass(frozen=True)
class PerformanceCohortDefinition:
    """Explicit query contract for a P15.4 performance cohort.

    Time windows use a half-open interval: ``evaluated_from <= t < evaluated_to``.
    Omitting both time bounds is valid for a cumulative snapshot, but drift
    comparisons require both bounds on both cohorts.
    """

    forecast_id: str | None = None
    horizon: str | None = None
    scenario_type: str | None = None
    evaluated_from: datetime | None = None
    evaluated_to: datetime | None = None
    scoring_method: str = SCORING_METHOD
    scoring_method_version: str = SCORING_METHOD_VERSION
    reliability_bucket_count: int = DEFAULT_RELIABILITY_BUCKET_COUNT

    def __post_init__(self) -> None:
        forecast_id = None if self.forecast_id is None else _nonempty(self.forecast_id, "forecast_id")
        horizon = None if self.horizon is None else str(self.horizon).strip()
        scenario_type = None if self.scenario_type is None else str(self.scenario_type).strip().lower()
        if horizon is not None and horizon not in FORECAST_HORIZONS:
            raise PerformanceIntelligenceError(f"unsupported forecast horizon: {horizon}")
        if scenario_type is not None and scenario_type not in SCENARIO_TYPES:
            raise PerformanceIntelligenceError(f"unsupported scenario type: {scenario_type}")
        bucket_count = int(self.reliability_bucket_count)
        if bucket_count < 2:
            raise PerformanceIntelligenceError("reliability bucket_count must be at least 2")
        evaluated_from = None if self.evaluated_from is None else _normalize_time(self.evaluated_from)
        evaluated_to = None if self.evaluated_to is None else _normalize_time(self.evaluated_to)
        if evaluated_from is not None and evaluated_to is not None and evaluated_from >= evaluated_to:
            raise PerformanceIntelligenceError("evaluated_from must be earlier than evaluated_to")

        object.__setattr__(self, "forecast_id", forecast_id)
        object.__setattr__(self, "horizon", horizon)
        object.__setattr__(self, "scenario_type", scenario_type)
        object.__setattr__(self, "evaluated_from", evaluated_from)
        object.__setattr__(self, "evaluated_to", evaluated_to)
        object.__setattr__(self, "scoring_method", _nonempty(self.scoring_method, "scoring_method"))
        object.__setattr__(self, "scoring_method_version", _nonempty(self.scoring_method_version, "scoring_method_version"))
        object.__setattr__(self, "reliability_bucket_count", bucket_count)

    def payload(self) -> dict[str, object]:
        return {
            "forecast_id": self.forecast_id,
            "horizon": self.horizon,
            "scenario_type": self.scenario_type,
            "evaluated_from": None if self.evaluated_from is None else self.evaluated_from.isoformat(),
            "evaluated_to": None if self.evaluated_to is None else self.evaluated_to.isoformat(),
            "scoring_method": self.scoring_method,
            "scoring_method_version": self.scoring_method_version,
            "reliability_bucket_count": self.reliability_bucket_count,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))

    def dimension_signature(self) -> tuple[object, ...]:
        """Dimensions that must match before temporal drift comparison."""

        return (
            self.forecast_id,
            self.horizon,
            self.scenario_type,
            self.scoring_method,
            self.scoring_method_version,
            self.reliability_bucket_count,
        )


@dataclass(frozen=True)
class PerformanceAggregate:
    aggregate_id: str
    cohort_definition_json: str
    observation_set_hash: str
    forecast_id: str | None
    horizon: str | None
    scenario_type: str | None
    scoring_method: str
    scoring_method_version: str
    reliability_bucket_count: int
    evaluated_from: datetime | None
    evaluated_to: datetime | None
    sample_count: int
    forecast_count: int
    sample_qualification: str
    mean_raw_probability: float
    mean_calibrated_probability: float
    observed_rate: float
    mean_brier_raw: float
    mean_brier_calibrated: float
    expected_calibration_error_raw: float
    expected_calibration_error_calibrated: float
    bias_raw: float
    bias_calibrated: float
    brier_improvement: float
    calibration_error_improvement: float
    aggregate_method: str
    aggregate_method_version: str
    generated_at: datetime
    observation_ids: tuple[str, ...]


@dataclass(frozen=True)
class PerformanceDriftComparison:
    comparison_id: str
    baseline_aggregate_id: str
    recent_aggregate_id: str
    baseline_sample_count: int
    recent_sample_count: int
    mean_raw_probability_delta: float
    mean_calibrated_probability_delta: float
    observed_rate_delta: float
    mean_brier_raw_delta: float
    mean_brier_calibrated_delta: float
    calibration_error_raw_delta: float
    calibration_error_calibrated_delta: float
    bias_raw_shift: float
    bias_calibrated_shift: float
    comparison_method: str
    comparison_method_version: str
    created_at: datetime


class ForecastPerformanceIntelligenceEngine:
    """Build immutable performance snapshots and descriptive drift comparisons."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    @staticmethod
    def _aggregate_from_row(
        connection: sqlite3.Connection,
        row: tuple[object, ...],
    ) -> PerformanceAggregate:
        aggregate_id = str(row[0])
        observation_ids = tuple(
            str(item[0])
            for item in connection.execute(
                """SELECT observation_id
                   FROM forecast_performance_aggregate_observations
                   WHERE aggregate_id = ? ORDER BY observation_order""",
                (aggregate_id,),
            ).fetchall()
        )
        return PerformanceAggregate(
            aggregate_id=aggregate_id,
            cohort_definition_json=str(row[1]),
            observation_set_hash=str(row[2]),
            forecast_id=None if row[3] is None else str(row[3]),
            horizon=None if row[4] is None else str(row[4]),
            scenario_type=None if row[5] is None else str(row[5]),
            scoring_method=str(row[6]),
            scoring_method_version=str(row[7]),
            reliability_bucket_count=int(row[8]),
            evaluated_from=None if row[9] is None else datetime.fromisoformat(str(row[9])),
            evaluated_to=None if row[10] is None else datetime.fromisoformat(str(row[10])),
            sample_count=int(row[11]),
            forecast_count=int(row[12]),
            sample_qualification=str(row[13]),
            mean_raw_probability=float(row[14]),
            mean_calibrated_probability=float(row[15]),
            observed_rate=float(row[16]),
            mean_brier_raw=float(row[17]),
            mean_brier_calibrated=float(row[18]),
            expected_calibration_error_raw=float(row[19]),
            expected_calibration_error_calibrated=float(row[20]),
            bias_raw=float(row[21]),
            bias_calibrated=float(row[22]),
            brier_improvement=float(row[23]),
            calibration_error_improvement=float(row[24]),
            aggregate_method=str(row[25]),
            aggregate_method_version=str(row[26]),
            generated_at=datetime.fromisoformat(str(row[27])),
            observation_ids=observation_ids,
        )

    @staticmethod
    def _select_aggregate(
        connection: sqlite3.Connection,
        aggregate_id: str,
    ) -> PerformanceAggregate | None:
        row = connection.execute(
            """SELECT aggregate_id, cohort_definition_json, observation_set_hash,
                      forecast_id, horizon, scenario_type, scoring_method,
                      scoring_method_version, reliability_bucket_count,
                      evaluated_from, evaluated_to, sample_count, forecast_count,
                      sample_qualification, mean_raw_probability,
                      mean_calibrated_probability, observed_rate, mean_brier_raw,
                      mean_brier_calibrated, expected_calibration_error_raw,
                      expected_calibration_error_calibrated, bias_raw,
                      bias_calibrated, brier_improvement,
                      calibration_error_improvement, aggregate_method,
                      aggregate_method_version, generated_at
               FROM forecast_performance_aggregates WHERE aggregate_id = ?""",
            (aggregate_id,),
        ).fetchone()
        if row is None:
            return None
        return ForecastPerformanceIntelligenceEngine._aggregate_from_row(connection, row)

    def aggregate(
        self,
        cohort: PerformanceCohortDefinition,
        *,
        generated_at: datetime | None = None,
    ) -> PerformanceAggregate:
        if not isinstance(cohort, PerformanceCohortDefinition):
            raise PerformanceIntelligenceError("cohort must be a PerformanceCohortDefinition")
        generated_time = _normalize_time(generated_at or utc_now())

        conditions = [
            "scoring_method = ?",
            "scoring_method_version = ?",
            "reliability_bucket_count = ?",
        ]
        parameters: list[object] = [
            cohort.scoring_method,
            cohort.scoring_method_version,
            cohort.reliability_bucket_count,
        ]
        if cohort.forecast_id is not None:
            conditions.append("forecast_id = ?")
            parameters.append(cohort.forecast_id)
        if cohort.horizon is not None:
            conditions.append("horizon = ?")
            parameters.append(cohort.horizon)
        if cohort.scenario_type is not None:
            conditions.append("scenario_type = ?")
            parameters.append(cohort.scenario_type)
        if cohort.evaluated_from is not None:
            conditions.append("evaluated_at >= ?")
            parameters.append(cohort.evaluated_from.isoformat())
        if cohort.evaluated_to is not None:
            conditions.append("evaluated_at < ?")
            parameters.append(cohort.evaluated_to.isoformat())

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            rows = connection.execute(
                f"""SELECT observation_id, forecast_id, raw_probability,
                           calibrated_probability, observed_value, brier_score_raw,
                           brier_score_calibrated, raw_reliability_bucket,
                           calibrated_reliability_bucket
                    FROM forecast_calibration_observations
                    WHERE {' AND '.join(conditions)}
                    ORDER BY evaluated_at, observation_id""",
                tuple(parameters),
            ).fetchall()
            if not rows:
                raise PerformanceIntelligenceError("cohort contains no calibration observations")

            observation_ids = tuple(str(row[0]) for row in rows)
            observation_set_hash = sha256("\x1f".join(observation_ids).encode("utf-8")).hexdigest()
            sample_count = len(rows)
            forecast_count = len({str(row[1]) for row in rows})
            mean_raw_probability = sum(float(row[2]) for row in rows) / sample_count
            mean_calibrated_probability = sum(float(row[3]) for row in rows) / sample_count
            observed_rate = sum(float(row[4]) for row in rows) / sample_count
            mean_brier_raw = sum(float(row[5]) for row in rows) / sample_count
            mean_brier_calibrated = sum(float(row[6]) for row in rows) / sample_count
            ece_raw = _expected_calibration_error(
                (int(row[7]), float(row[2]), float(row[4])) for row in rows
            )
            ece_calibrated = _expected_calibration_error(
                (int(row[8]), float(row[3]), float(row[4])) for row in rows
            )
            bias_raw = mean_raw_probability - observed_rate
            bias_calibrated = mean_calibrated_probability - observed_rate
            cohort_json = cohort.canonical_json()
            aggregate_id = _stable_id(
                "fperf",
                cohort_json,
                observation_set_hash,
                AGGREGATE_METHOD,
                AGGREGATE_METHOD_VERSION,
            )

            existing = self._select_aggregate(connection, aggregate_id)
            if existing is not None:
                if existing.observation_ids != observation_ids:
                    raise PerformanceIntelligenceError(
                        "existing performance aggregate conflicts with immutable observation membership"
                    )
                return existing

            candidate = PerformanceAggregate(
                aggregate_id=aggregate_id,
                cohort_definition_json=cohort_json,
                observation_set_hash=observation_set_hash,
                forecast_id=cohort.forecast_id,
                horizon=cohort.horizon,
                scenario_type=cohort.scenario_type,
                scoring_method=cohort.scoring_method,
                scoring_method_version=cohort.scoring_method_version,
                reliability_bucket_count=cohort.reliability_bucket_count,
                evaluated_from=cohort.evaluated_from,
                evaluated_to=cohort.evaluated_to,
                sample_count=sample_count,
                forecast_count=forecast_count,
                sample_qualification=_sample_qualification(sample_count),
                mean_raw_probability=mean_raw_probability,
                mean_calibrated_probability=mean_calibrated_probability,
                observed_rate=observed_rate,
                mean_brier_raw=mean_brier_raw,
                mean_brier_calibrated=mean_brier_calibrated,
                expected_calibration_error_raw=ece_raw,
                expected_calibration_error_calibrated=ece_calibrated,
                bias_raw=bias_raw,
                bias_calibrated=bias_calibrated,
                brier_improvement=mean_brier_raw - mean_brier_calibrated,
                calibration_error_improvement=ece_raw - ece_calibrated,
                aggregate_method=AGGREGATE_METHOD,
                aggregate_method_version=AGGREGATE_METHOD_VERSION,
                generated_at=generated_time,
                observation_ids=observation_ids,
            )

            connection.execute(
                """INSERT INTO forecast_performance_aggregates(
                       aggregate_id, cohort_definition_json, observation_set_hash,
                       forecast_id, horizon, scenario_type, scoring_method,
                       scoring_method_version, reliability_bucket_count,
                       evaluated_from, evaluated_to, sample_count, forecast_count,
                       sample_qualification, mean_raw_probability,
                       mean_calibrated_probability, observed_rate, mean_brier_raw,
                       mean_brier_calibrated, expected_calibration_error_raw,
                       expected_calibration_error_calibrated, bias_raw,
                       bias_calibrated, brier_improvement,
                       calibration_error_improvement, aggregate_method,
                       aggregate_method_version, generated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    candidate.aggregate_id,
                    candidate.cohort_definition_json,
                    candidate.observation_set_hash,
                    candidate.forecast_id,
                    candidate.horizon,
                    candidate.scenario_type,
                    candidate.scoring_method,
                    candidate.scoring_method_version,
                    candidate.reliability_bucket_count,
                    None if candidate.evaluated_from is None else candidate.evaluated_from.isoformat(),
                    None if candidate.evaluated_to is None else candidate.evaluated_to.isoformat(),
                    candidate.sample_count,
                    candidate.forecast_count,
                    candidate.sample_qualification,
                    candidate.mean_raw_probability,
                    candidate.mean_calibrated_probability,
                    candidate.observed_rate,
                    candidate.mean_brier_raw,
                    candidate.mean_brier_calibrated,
                    candidate.expected_calibration_error_raw,
                    candidate.expected_calibration_error_calibrated,
                    candidate.bias_raw,
                    candidate.bias_calibrated,
                    candidate.brier_improvement,
                    candidate.calibration_error_improvement,
                    candidate.aggregate_method,
                    candidate.aggregate_method_version,
                    candidate.generated_at.isoformat(),
                ),
            )
            connection.executemany(
                """INSERT INTO forecast_performance_aggregate_observations(
                       aggregate_id, observation_order, observation_id
                   ) VALUES (?, ?, ?)""",
                [
                    (candidate.aggregate_id, index, observation_id)
                    for index, observation_id in enumerate(candidate.observation_ids, start=1)
                ],
            )
            return candidate

    @staticmethod
    def _cohort_from_aggregate(aggregate: PerformanceAggregate) -> PerformanceCohortDefinition:
        payload = json.loads(aggregate.cohort_definition_json)
        return PerformanceCohortDefinition(
            forecast_id=payload.get("forecast_id"),
            horizon=payload.get("horizon"),
            scenario_type=payload.get("scenario_type"),
            evaluated_from=(
                None
                if payload.get("evaluated_from") is None
                else datetime.fromisoformat(str(payload["evaluated_from"]))
            ),
            evaluated_to=(
                None
                if payload.get("evaluated_to") is None
                else datetime.fromisoformat(str(payload["evaluated_to"]))
            ),
            scoring_method=str(payload["scoring_method"]),
            scoring_method_version=str(payload["scoring_method_version"]),
            reliability_bucket_count=int(payload["reliability_bucket_count"]),
        )

    @staticmethod
    def _comparison_from_row(row: tuple[object, ...]) -> PerformanceDriftComparison:
        return PerformanceDriftComparison(
            comparison_id=str(row[0]),
            baseline_aggregate_id=str(row[1]),
            recent_aggregate_id=str(row[2]),
            baseline_sample_count=int(row[3]),
            recent_sample_count=int(row[4]),
            mean_raw_probability_delta=float(row[5]),
            mean_calibrated_probability_delta=float(row[6]),
            observed_rate_delta=float(row[7]),
            mean_brier_raw_delta=float(row[8]),
            mean_brier_calibrated_delta=float(row[9]),
            calibration_error_raw_delta=float(row[10]),
            calibration_error_calibrated_delta=float(row[11]),
            bias_raw_shift=float(row[12]),
            bias_calibrated_shift=float(row[13]),
            comparison_method=str(row[14]),
            comparison_method_version=str(row[15]),
            created_at=datetime.fromisoformat(str(row[16])),
        )

    def compare_drift(
        self,
        baseline_aggregate_id: str,
        recent_aggregate_id: str,
        *,
        created_at: datetime | None = None,
    ) -> PerformanceDriftComparison:
        baseline_id = _nonempty(baseline_aggregate_id, "baseline_aggregate_id")
        recent_id = _nonempty(recent_aggregate_id, "recent_aggregate_id")
        if baseline_id == recent_id:
            raise PerformanceIntelligenceError("drift comparison requires two different aggregates")
        created_time = _normalize_time(created_at or utc_now())

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            baseline = self._select_aggregate(connection, baseline_id)
            recent = self._select_aggregate(connection, recent_id)
            if baseline is None or recent is None:
                raise PerformanceIntelligenceError("performance aggregate does not exist")

            baseline_cohort = self._cohort_from_aggregate(baseline)
            recent_cohort = self._cohort_from_aggregate(recent)
            if baseline_cohort.dimension_signature() != recent_cohort.dimension_signature():
                raise PerformanceIntelligenceError(
                    "drift comparison requires identical non-temporal cohort dimensions"
                )
            if (
                baseline_cohort.evaluated_from is None
                or baseline_cohort.evaluated_to is None
                or recent_cohort.evaluated_from is None
                or recent_cohort.evaluated_to is None
            ):
                raise PerformanceIntelligenceError(
                    "drift comparison requires explicit bounded time windows"
                )
            if baseline_cohort.evaluated_to > recent_cohort.evaluated_from:
                raise PerformanceIntelligenceError(
                    "drift comparison requires ordered non-overlapping time windows"
                )

            comparison_id = _stable_id(
                "fdrift",
                baseline.aggregate_id,
                recent.aggregate_id,
                DRIFT_COMPARISON_METHOD,
                DRIFT_COMPARISON_METHOD_VERSION,
            )
            existing_row = connection.execute(
                """SELECT comparison_id, baseline_aggregate_id, recent_aggregate_id,
                          baseline_sample_count, recent_sample_count,
                          mean_raw_probability_delta,
                          mean_calibrated_probability_delta, observed_rate_delta,
                          mean_brier_raw_delta, mean_brier_calibrated_delta,
                          calibration_error_raw_delta,
                          calibration_error_calibrated_delta, bias_raw_shift,
                          bias_calibrated_shift, comparison_method,
                          comparison_method_version, created_at
                   FROM forecast_performance_drift_comparisons
                   WHERE comparison_id = ?""",
                (comparison_id,),
            ).fetchone()
            if existing_row is not None:
                return self._comparison_from_row(existing_row)

            comparison = PerformanceDriftComparison(
                comparison_id=comparison_id,
                baseline_aggregate_id=baseline.aggregate_id,
                recent_aggregate_id=recent.aggregate_id,
                baseline_sample_count=baseline.sample_count,
                recent_sample_count=recent.sample_count,
                mean_raw_probability_delta=recent.mean_raw_probability - baseline.mean_raw_probability,
                mean_calibrated_probability_delta=recent.mean_calibrated_probability - baseline.mean_calibrated_probability,
                observed_rate_delta=recent.observed_rate - baseline.observed_rate,
                mean_brier_raw_delta=recent.mean_brier_raw - baseline.mean_brier_raw,
                mean_brier_calibrated_delta=recent.mean_brier_calibrated - baseline.mean_brier_calibrated,
                calibration_error_raw_delta=(
                    recent.expected_calibration_error_raw - baseline.expected_calibration_error_raw
                ),
                calibration_error_calibrated_delta=(
                    recent.expected_calibration_error_calibrated
                    - baseline.expected_calibration_error_calibrated
                ),
                bias_raw_shift=recent.bias_raw - baseline.bias_raw,
                bias_calibrated_shift=recent.bias_calibrated - baseline.bias_calibrated,
                comparison_method=DRIFT_COMPARISON_METHOD,
                comparison_method_version=DRIFT_COMPARISON_METHOD_VERSION,
                created_at=created_time,
            )
            connection.execute(
                """INSERT INTO forecast_performance_drift_comparisons(
                       comparison_id, baseline_aggregate_id, recent_aggregate_id,
                       baseline_sample_count, recent_sample_count,
                       mean_raw_probability_delta,
                       mean_calibrated_probability_delta, observed_rate_delta,
                       mean_brier_raw_delta, mean_brier_calibrated_delta,
                       calibration_error_raw_delta,
                       calibration_error_calibrated_delta, bias_raw_shift,
                       bias_calibrated_shift, comparison_method,
                       comparison_method_version, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    comparison.comparison_id,
                    comparison.baseline_aggregate_id,
                    comparison.recent_aggregate_id,
                    comparison.baseline_sample_count,
                    comparison.recent_sample_count,
                    comparison.mean_raw_probability_delta,
                    comparison.mean_calibrated_probability_delta,
                    comparison.observed_rate_delta,
                    comparison.mean_brier_raw_delta,
                    comparison.mean_brier_calibrated_delta,
                    comparison.calibration_error_raw_delta,
                    comparison.calibration_error_calibrated_delta,
                    comparison.bias_raw_shift,
                    comparison.bias_calibrated_shift,
                    comparison.comparison_method,
                    comparison.comparison_method_version,
                    comparison.created_at.isoformat(),
                ),
            )
            return comparison


__all__ = [
    "P15_4_GATE",
    "AGGREGATE_METHOD",
    "AGGREGATE_METHOD_VERSION",
    "DRIFT_COMPARISON_METHOD",
    "DRIFT_COMPARISON_METHOD_VERSION",
    "BIAS_OVER_PREDICTION",
    "BIAS_UNDER_PREDICTION",
    "BIAS_WITHIN_TOLERANCE",
    "PerformanceIntelligenceError",
    "PerformanceCohortDefinition",
    "PerformanceAggregate",
    "PerformanceDriftComparison",
    "ForecastPerformanceIntelligenceEngine",
    "classify_bias",
]
