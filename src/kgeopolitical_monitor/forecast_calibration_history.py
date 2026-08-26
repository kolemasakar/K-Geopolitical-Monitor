"""M12.5 reproducible calibration and forecast performance history."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from statistics import fmean
from typing import Iterable

from .database import initialize_database
from .forecast_evaluation import BINARY_ONE_VS_REST, BINARY_ONE_VS_REST_VERSION
from .forecast_preparation import ForecastHorizon
from .operational_monitoring import _normalize_time, utc_now
from .probabilistic_forecasting import ScenarioType


MIN_CALIBRATION_SAMPLE_COUNT = 5
EMPIRICAL_CALIBRATION_REPORT = "EMPIRICAL_CALIBRATION_REPORT"
EMPIRICAL_CALIBRATION_REPORT_VERSION = "1"
RAW = "RAW"
CALIBRATED = "CALIBRATED"
PROBABILITY_BASES = {RAW, CALIBRATED}
DEFAULT_BUCKET_COUNT = 5


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _horizon_value(value: ForecastHorizon | str | None) -> str | None:
    if value is None:
        return None
    raw = value.value if isinstance(value, ForecastHorizon) else str(value).strip()
    allowed = {item.value for item in ForecastHorizon}
    if raw not in allowed:
        raise ValueError(f"unsupported forecast horizon: {raw}")
    return raw


def _scenario_type_value(value: ScenarioType | str | None) -> str | None:
    if value is None:
        return None
    raw = value.value if isinstance(value, ScenarioType) else str(value).strip().lower()
    allowed = {item.value for item in ScenarioType}
    if raw not in allowed:
        raise ValueError(f"unsupported scenario type: {raw}")
    return raw


@dataclass(frozen=True)
class CalibrationCohort:
    horizon: str | None = None
    scenario_type: str | None = None
    evaluation_method: str = BINARY_ONE_VS_REST
    evaluation_method_version: str = BINARY_ONE_VS_REST_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizon", _horizon_value(self.horizon))
        object.__setattr__(self, "scenario_type", _scenario_type_value(self.scenario_type))
        object.__setattr__(
            self,
            "evaluation_method",
            _nonempty(self.evaluation_method, "evaluation_method"),
        )
        object.__setattr__(
            self,
            "evaluation_method_version",
            _nonempty(self.evaluation_method_version, "evaluation_method_version"),
        )

    @property
    def key(self) -> str:
        return json.dumps(
            {
                "horizon": self.horizon,
                "scenario_type": self.scenario_type,
                "evaluation_method": self.evaluation_method,
                "evaluation_method_version": self.evaluation_method_version,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True)
class CalibrationBucket:
    calibration_id: str
    probability_basis: str
    bucket_index: int
    bucket_lower: float
    bucket_upper: float
    sample_count: int
    mean_probability: float
    observed_frequency: float
    mean_brier_score: float
    mean_calibration_error: float

    def __post_init__(self) -> None:
        basis = _nonempty(self.probability_basis, "probability_basis").upper()
        if basis not in PROBABILITY_BASES:
            raise ValueError(f"unsupported probability basis: {basis}")
        if self.bucket_index < 0:
            raise ValueError("bucket_index must not be negative")
        if self.sample_count <= 0:
            raise ValueError("calibration bucket requires at least one sample")
        for field_name in (
            "bucket_lower",
            "bucket_upper",
            "mean_probability",
            "observed_frequency",
            "mean_brier_score",
            "mean_calibration_error",
        ):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        if self.bucket_upper < self.bucket_lower:
            raise ValueError("bucket_upper must not be below bucket_lower")
        object.__setattr__(self, "probability_basis", basis)


@dataclass(frozen=True)
class CalibrationRun:
    calibration_id: str
    calibration_method: str
    calibration_method_version: str
    cohort: CalibrationCohort
    min_sample_count: int
    sample_count: int
    evaluation_ids: tuple[str, ...]
    raw_mean_probability: float
    calibrated_mean_probability: float
    observed_frequency: float
    raw_brier_mean: float
    calibrated_brier_mean: float
    raw_calibration_error_mean: float
    calibrated_calibration_error_mean: float
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.min_sample_count <= 0:
            raise ValueError("min_sample_count must be positive")
        if self.sample_count < self.min_sample_count:
            raise ValueError("calibration run does not satisfy minimum sample count")
        evaluation_ids = tuple(sorted({_nonempty(value, "evaluation_id") for value in self.evaluation_ids}))
        if len(evaluation_ids) != self.sample_count:
            raise ValueError("sample_count must equal unique evaluation ID count")
        for field_name in (
            "raw_mean_probability",
            "calibrated_mean_probability",
            "observed_frequency",
            "raw_brier_mean",
            "calibrated_brier_mean",
            "raw_calibration_error_mean",
            "calibrated_calibration_error_mean",
        ):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        object.__setattr__(self, "evaluation_ids", evaluation_ids)
        object.__setattr__(self, "created_at", _normalize_time(self.created_at))
        object.__setattr__(
            self,
            "calibration_method",
            _nonempty(self.calibration_method, "calibration_method"),
        )
        object.__setattr__(
            self,
            "calibration_method_version",
            _nonempty(self.calibration_method_version, "calibration_method_version"),
        )


@dataclass(frozen=True)
class ForecastPerformanceBreakdown:
    horizon: str
    scenario_type: str
    sample_count: int
    forecast_count: int
    raw_brier_mean: float
    calibrated_brier_mean: float
    raw_calibration_error_mean: float
    calibrated_calibration_error_mean: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizon", _horizon_value(self.horizon))
        object.__setattr__(self, "scenario_type", _scenario_type_value(self.scenario_type))


def calibration_id(
    cohort: CalibrationCohort,
    evaluation_ids: Iterable[str],
    *,
    calibration_method: str = EMPIRICAL_CALIBRATION_REPORT,
    calibration_method_version: str = EMPIRICAL_CALIBRATION_REPORT_VERSION,
    min_sample_count: int = MIN_CALIBRATION_SAMPLE_COUNT,
) -> str:
    ids = tuple(sorted({_nonempty(value, "evaluation_id") for value in evaluation_ids}))
    if not ids:
        raise ValueError("calibration identity requires evaluation IDs")
    return _stable_id(
        "cal",
        _nonempty(calibration_method, "calibration_method"),
        _nonempty(calibration_method_version, "calibration_method_version"),
        cohort.key,
        str(int(min_sample_count)),
        *ids,
    )


class SQLiteForecastCalibrationRepository:
    """Immutable empirical calibration snapshots derived from M12.4 evaluations."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def _select_samples(self, cohort: CalibrationCohort) -> list[tuple[object, ...]]:
        clauses = [
            "sample_count = 1",
            "observed_value IS NOT NULL",
            "evaluation_method = ?",
            "evaluation_method_version = ?",
        ]
        params: list[object] = [cohort.evaluation_method, cohort.evaluation_method_version]
        if cohort.horizon is not None:
            clauses.append("horizon = ?")
            params.append(cohort.horizon)
        if cohort.scenario_type is not None:
            clauses.append("scenario_type = ?")
            params.append(cohort.scenario_type)
        query = f"""
            SELECT evaluation_id, forecast_id, horizon, scenario_type,
                   raw_probability, calibrated_probability, observed_value,
                   brier_score_raw, brier_score_calibrated,
                   calibration_error_raw, calibration_error_calibrated
            FROM forecast_evaluations
            WHERE {' AND '.join(clauses)}
            ORDER BY evaluation_id
        """
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute(query, tuple(params)).fetchall()

    @staticmethod
    def _bucket_rows(
        calibration_id_value: str,
        rows: list[tuple[object, ...]],
        *,
        basis: str,
        bucket_count: int,
    ) -> tuple[CalibrationBucket, ...]:
        if bucket_count <= 0:
            raise ValueError("bucket_count must be positive")
        probability_index = 4 if basis == RAW else 5
        brier_index = 7 if basis == RAW else 8
        error_index = 9 if basis == RAW else 10
        width = 1.0 / bucket_count
        grouped: dict[int, list[tuple[object, ...]]] = {}
        for row in rows:
            probability = float(row[probability_index])
            index = min(bucket_count - 1, int(probability * bucket_count))
            grouped.setdefault(index, []).append(row)

        buckets: list[CalibrationBucket] = []
        for index in sorted(grouped):
            items = grouped[index]
            lower = index * width
            upper = 1.0 if index == bucket_count - 1 else (index + 1) * width
            buckets.append(
                CalibrationBucket(
                    calibration_id=calibration_id_value,
                    probability_basis=basis,
                    bucket_index=index,
                    bucket_lower=lower,
                    bucket_upper=upper,
                    sample_count=len(items),
                    mean_probability=fmean(float(row[probability_index]) for row in items),
                    observed_frequency=fmean(float(row[6]) for row in items),
                    mean_brier_score=fmean(float(row[brier_index]) for row in items),
                    mean_calibration_error=fmean(float(row[error_index]) for row in items),
                )
            )
        return tuple(buckets)

    def create_run(
        self,
        cohort: CalibrationCohort,
        *,
        min_sample_count: int = MIN_CALIBRATION_SAMPLE_COUNT,
        bucket_count: int = DEFAULT_BUCKET_COUNT,
        calibration_method: str = EMPIRICAL_CALIBRATION_REPORT,
        calibration_method_version: str = EMPIRICAL_CALIBRATION_REPORT_VERSION,
        created_at: datetime | None = None,
    ) -> tuple[CalibrationRun, tuple[CalibrationBucket, ...]]:
        if min_sample_count <= 0:
            raise ValueError("min_sample_count must be positive")
        rows = self._select_samples(cohort)
        if len(rows) < min_sample_count:
            raise ValueError(
                f"calibration cohort requires at least {min_sample_count} scorable evaluations; found {len(rows)}"
            )
        ids = tuple(str(row[0]) for row in rows)
        cal_id = calibration_id(
            cohort,
            ids,
            calibration_method=calibration_method,
            calibration_method_version=calibration_method_version,
            min_sample_count=min_sample_count,
        )
        run = CalibrationRun(
            calibration_id=cal_id,
            calibration_method=calibration_method,
            calibration_method_version=calibration_method_version,
            cohort=cohort,
            min_sample_count=min_sample_count,
            sample_count=len(rows),
            evaluation_ids=ids,
            raw_mean_probability=fmean(float(row[4]) for row in rows),
            calibrated_mean_probability=fmean(float(row[5]) for row in rows),
            observed_frequency=fmean(float(row[6]) for row in rows),
            raw_brier_mean=fmean(float(row[7]) for row in rows),
            calibrated_brier_mean=fmean(float(row[8]) for row in rows),
            raw_calibration_error_mean=fmean(float(row[9]) for row in rows),
            calibrated_calibration_error_mean=fmean(float(row[10]) for row in rows),
            created_at=_normalize_time(created_at or utc_now()),
        )
        buckets = (
            self._bucket_rows(cal_id, rows, basis=RAW, bucket_count=bucket_count)
            + self._bucket_rows(cal_id, rows, basis=CALIBRATED, bucket_count=bucket_count)
        )
        run_payload = (
            run.calibration_method,
            run.calibration_method_version,
            run.cohort.evaluation_method,
            run.cohort.evaluation_method_version,
            run.cohort.horizon,
            run.cohort.scenario_type,
            run.min_sample_count,
            run.sample_count,
            json.dumps(run.evaluation_ids),
            run.raw_mean_probability,
            run.calibrated_mean_probability,
            run.observed_frequency,
            run.raw_brier_mean,
            run.calibrated_brier_mean,
            run.raw_calibration_error_mean,
            run.calibrated_calibration_error_mean,
            run.created_at.isoformat(),
        )
        bucket_payloads = tuple(
            (
                item.calibration_id,
                item.probability_basis,
                item.bucket_index,
                item.bucket_lower,
                item.bucket_upper,
                item.sample_count,
                item.mean_probability,
                item.observed_frequency,
                item.mean_brier_score,
                item.mean_calibration_error,
            )
            for item in buckets
        )

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            existing = connection.execute(
                """
                SELECT calibration_method, calibration_method_version,
                       evaluation_method, evaluation_method_version,
                       cohort_horizon, cohort_scenario_type,
                       min_sample_count, sample_count, evaluation_ids_json,
                       raw_mean_probability, calibrated_mean_probability,
                       observed_frequency, raw_brier_mean, calibrated_brier_mean,
                       raw_calibration_error_mean, calibrated_calibration_error_mean,
                       created_at
                FROM forecast_calibration_runs WHERE calibration_id = ?
                """,
                (cal_id,),
            ).fetchone()
            if existing is not None:
                persisted_core = tuple(existing[:-1])
                expected_core = tuple(run_payload[:-1])
                if persisted_core != expected_core:
                    raise ValueError("calibration run is immutable")
                return self.get_run(cal_id), self.list_buckets(cal_id)

            connection.execute(
                """
                INSERT INTO forecast_calibration_runs(
                    calibration_id, calibration_method, calibration_method_version,
                    evaluation_method, evaluation_method_version,
                    cohort_horizon, cohort_scenario_type,
                    min_sample_count, sample_count, evaluation_ids_json,
                    raw_mean_probability, calibrated_mean_probability,
                    observed_frequency, raw_brier_mean, calibrated_brier_mean,
                    raw_calibration_error_mean, calibrated_calibration_error_mean,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (cal_id, *run_payload),
            )
            connection.executemany(
                """
                INSERT INTO forecast_calibration_buckets(
                    calibration_id, probability_basis, bucket_index,
                    bucket_lower, bucket_upper, sample_count,
                    mean_probability, observed_frequency,
                    mean_brier_score, mean_calibration_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                bucket_payloads,
            )
        return run, buckets

    def get_run(self, calibration_id_value: str) -> CalibrationRun | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT calibration_id, calibration_method, calibration_method_version,
                       evaluation_method, evaluation_method_version,
                       cohort_horizon, cohort_scenario_type,
                       min_sample_count, sample_count, evaluation_ids_json,
                       raw_mean_probability, calibrated_mean_probability,
                       observed_frequency, raw_brier_mean, calibrated_brier_mean,
                       raw_calibration_error_mean, calibrated_calibration_error_mean,
                       created_at
                FROM forecast_calibration_runs WHERE calibration_id = ?
                """,
                (calibration_id_value,),
            ).fetchone()
        if row is None:
            return None
        return CalibrationRun(
            calibration_id=str(row[0]),
            calibration_method=str(row[1]),
            calibration_method_version=str(row[2]),
            cohort=CalibrationCohort(
                horizon=row[5],
                scenario_type=row[6],
                evaluation_method=str(row[3]),
                evaluation_method_version=str(row[4]),
            ),
            min_sample_count=int(row[7]),
            sample_count=int(row[8]),
            evaluation_ids=tuple(json.loads(str(row[9]))),
            raw_mean_probability=float(row[10]),
            calibrated_mean_probability=float(row[11]),
            observed_frequency=float(row[12]),
            raw_brier_mean=float(row[13]),
            calibrated_brier_mean=float(row[14]),
            raw_calibration_error_mean=float(row[15]),
            calibrated_calibration_error_mean=float(row[16]),
            created_at=datetime.fromisoformat(str(row[17])),
        )

    def list_buckets(self, calibration_id_value: str) -> tuple[CalibrationBucket, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT calibration_id, probability_basis, bucket_index,
                       bucket_lower, bucket_upper, sample_count,
                       mean_probability, observed_frequency,
                       mean_brier_score, mean_calibration_error
                FROM forecast_calibration_buckets
                WHERE calibration_id = ?
                ORDER BY probability_basis, bucket_index
                """,
                (calibration_id_value,),
            ).fetchall()
        return tuple(
            CalibrationBucket(
                calibration_id=str(row[0]),
                probability_basis=str(row[1]),
                bucket_index=int(row[2]),
                bucket_lower=float(row[3]),
                bucket_upper=float(row[4]),
                sample_count=int(row[5]),
                mean_probability=float(row[6]),
                observed_frequency=float(row[7]),
                mean_brier_score=float(row[8]),
                mean_calibration_error=float(row[9]),
            )
            for row in rows
        )

    def performance_breakdown(self) -> tuple[ForecastPerformanceBreakdown, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT horizon, scenario_type, COUNT(*), COUNT(DISTINCT forecast_id),
                       AVG(brier_score_raw), AVG(brier_score_calibrated),
                       AVG(calibration_error_raw), AVG(calibration_error_calibrated)
                FROM forecast_evaluations
                WHERE sample_count = 1 AND observed_value IS NOT NULL
                GROUP BY horizon, scenario_type
                ORDER BY horizon, scenario_type
                """
            ).fetchall()
        return tuple(
            ForecastPerformanceBreakdown(
                horizon=str(row[0]),
                scenario_type=str(row[1]),
                sample_count=int(row[2]),
                forecast_count=int(row[3]),
                raw_brier_mean=float(row[4]),
                calibrated_brier_mean=float(row[5]),
                raw_calibration_error_mean=float(row[6]),
                calibrated_calibration_error_mean=float(row[7]),
            )
            for row in rows
        )


__all__ = [
    "MIN_CALIBRATION_SAMPLE_COUNT",
    "EMPIRICAL_CALIBRATION_REPORT",
    "EMPIRICAL_CALIBRATION_REPORT_VERSION",
    "RAW",
    "CALIBRATED",
    "CalibrationCohort",
    "CalibrationBucket",
    "CalibrationRun",
    "ForecastPerformanceBreakdown",
    "SQLiteForecastCalibrationRepository",
    "calibration_id",
]
