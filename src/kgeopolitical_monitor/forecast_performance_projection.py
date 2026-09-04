"""Phase 15.5 owner read-only forecast-performance projection.

This module projects already-persisted Phase 15.4 performance aggregates and
non-overlapping temporal drift comparisons for the owner. It never creates
calibration observations, aggregates or drift comparisons, and it never treats
forecast-performance metrics as factual-verification operators.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3
from urllib.parse import quote

from .operational_monitoring import _normalize_time, utc_now


P15_5_GATE = "P15_5_OWNER_READ_ONLY_PERFORMANCE_PROJECTION_VALIDATED"
PROJECTION_VERSION = "KGM_OWNER_FORECAST_PERFORMANCE_PROJECTION_V1"

_REQUIRED_TABLES = {
    "forecast_calibration_observations",
    "forecast_performance_aggregates",
    "forecast_performance_aggregate_observations",
    "forecast_performance_drift_comparisons",
}

_SAMPLE_LIMITATIONS = {
    "N_LT_5": "VERY_SMALL_SAMPLE_DESCRIPTIVE_ONLY",
    "N_5_TO_19": "LIMITED_SAMPLE_DESCRIPTIVE_ONLY",
    "N_GE_20": "DESCRIPTIVE_ONLY_NO_INFERENTIAL_CONFIDENCE",
}


class PerformanceProjectionError(RuntimeError):
    """Raised when persisted P15.4 performance state cannot be projected safely."""


def _read_only_database_uri(path: Path) -> str:
    normalized = str(path.resolve()).replace("\\", "/")
    return f"file:{quote(normalized, safe='/:')}?mode=ro"


def _bounded_limit(value: int, field_name: str) -> int:
    normalized = int(value)
    if not 1 <= normalized <= 100:
        raise PerformanceProjectionError(f"{field_name} must be between 1 and 100")
    return normalized


def _cohort_payload(value: str) -> dict[str, object]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise PerformanceProjectionError("persisted cohort_definition_json is invalid") from exc
    if not isinstance(parsed, dict):
        raise PerformanceProjectionError("persisted cohort_definition_json must be an object")
    return {str(key): item for key, item in parsed.items()}


class OwnerForecastPerformanceProjection:
    """Read-only/query-only owner projection over persisted P15.4 state."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path).resolve()

    def _connect(self) -> sqlite3.Connection:
        if not self.database_path.is_file():
            raise PerformanceProjectionError("canonical project-local database is unavailable")
        try:
            connection = sqlite3.connect(
                _read_only_database_uri(self.database_path),
                uri=True,
            )
        except sqlite3.Error as exc:
            raise PerformanceProjectionError(
                "canonical project-local database cannot be opened read-only"
            ) from exc
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    @staticmethod
    def _assert_p15_4_schema(connection: sqlite3.Connection) -> None:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        missing = sorted(_REQUIRED_TABLES - tables)
        if missing:
            raise PerformanceProjectionError(
                "required persisted P15.4 performance tables are unavailable: "
                + ", ".join(missing)
            )

    @staticmethod
    def _aggregate_payload(row: sqlite3.Row) -> dict[str, object]:
        qualification = str(row[13])
        limitation = _SAMPLE_LIMITATIONS.get(
            qualification,
            "UNKNOWN_SAMPLE_QUALIFICATION_DESCRIPTIVE_ONLY",
        )
        return {
            "aggregate_id": str(row[0]),
            "cohort": _cohort_payload(str(row[1])),
            "observation_set_hash": str(row[2]),
            "forecast_id": None if row[3] is None else str(row[3]),
            "horizon": None if row[4] is None else str(row[4]),
            "scenario_type": None if row[5] is None else str(row[5]),
            "scoring_method": str(row[6]),
            "scoring_method_version": str(row[7]),
            "reliability_bucket_count": int(row[8]),
            "evaluated_from": row[9],
            "evaluated_to": row[10],
            "sample_count": int(row[11]),
            "forecast_count": int(row[12]),
            "sample_qualification": qualification,
            "sample_limitation": limitation,
            "mean_raw_probability": float(row[14]),
            "mean_calibrated_probability": float(row[15]),
            "observed_rate": float(row[16]),
            "mean_brier_raw": float(row[17]),
            "mean_brier_calibrated": float(row[18]),
            "expected_calibration_error_raw": float(row[19]),
            "expected_calibration_error_calibrated": float(row[20]),
            "bias_raw": float(row[21]),
            "bias_calibrated": float(row[22]),
            "brier_improvement": float(row[23]),
            "calibration_error_improvement": float(row[24]),
            "aggregate_method": str(row[25]),
            "aggregate_method_version": str(row[26]),
            "generated_at": str(row[27]),
            "interpretation_boundary": "FORECAST_PERFORMANCE_ONLY_NOT_FACTUAL_VERIFICATION",
        }

    @staticmethod
    def _drift_payload(row: sqlite3.Row) -> dict[str, object]:
        return {
            "comparison_id": str(row[0]),
            "baseline_aggregate_id": str(row[1]),
            "recent_aggregate_id": str(row[2]),
            "baseline_sample_count": int(row[3]),
            "recent_sample_count": int(row[4]),
            "mean_raw_probability_delta": float(row[5]),
            "mean_calibrated_probability_delta": float(row[6]),
            "observed_rate_delta": float(row[7]),
            "mean_brier_raw_delta": float(row[8]),
            "mean_brier_calibrated_delta": float(row[9]),
            "calibration_error_raw_delta": float(row[10]),
            "calibration_error_calibrated_delta": float(row[11]),
            "bias_raw_shift": float(row[12]),
            "bias_calibrated_shift": float(row[13]),
            "comparison_method": str(row[14]),
            "comparison_method_version": str(row[15]),
            "created_at": str(row[16]),
            "interpretation_boundary": (
                "DESCRIPTIVE_TEMPORAL_DELTA_ONLY_NOT_CAUSAL_NOT_SIGNIFICANCE_TEST"
            ),
        }

    def snapshot(
        self,
        *,
        aggregate_limit: int = 20,
        drift_limit: int = 20,
        projected_at: datetime | None = None,
    ) -> dict[str, object]:
        aggregate_limit_value = _bounded_limit(aggregate_limit, "aggregate_limit")
        drift_limit_value = _bounded_limit(drift_limit, "drift_limit")
        projected_time = _normalize_time(projected_at or utc_now())

        with self._connect() as connection:
            self._assert_p15_4_schema(connection)
            query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
            if query_only != 1:
                raise PerformanceProjectionError("SQLite query_only protection is not active")

            aggregate_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM forecast_performance_aggregates"
                ).fetchone()[0]
            )
            drift_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM forecast_performance_drift_comparisons"
                ).fetchone()[0]
            )
            qualification_counts = {
                str(row[0]): int(row[1])
                for row in connection.execute(
                    """SELECT sample_qualification, COUNT(*)
                       FROM forecast_performance_aggregates
                       GROUP BY sample_qualification
                       ORDER BY sample_qualification"""
                ).fetchall()
            }
            latest_generated_at_row = connection.execute(
                "SELECT MAX(generated_at) FROM forecast_performance_aggregates"
            ).fetchone()
            latest_generated_at = (
                None
                if latest_generated_at_row is None or latest_generated_at_row[0] is None
                else str(latest_generated_at_row[0])
            )

            aggregate_rows = connection.execute(
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
                   FROM forecast_performance_aggregates
                   ORDER BY generated_at DESC, aggregate_id DESC
                   LIMIT ?""",
                (aggregate_limit_value,),
            ).fetchall()
            drift_rows = connection.execute(
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
                   ORDER BY created_at DESC, comparison_id DESC
                   LIMIT ?""",
                (drift_limit_value,),
            ).fetchall()

        aggregates = [self._aggregate_payload(row) for row in aggregate_rows]
        drift_comparisons = [self._drift_payload(row) for row in drift_rows]
        return {
            "projection": {
                "version": PROJECTION_VERSION,
                "gate": P15_5_GATE,
                "projected_at": projected_time.isoformat(),
                "data_state": (
                    "AVAILABLE"
                    if aggregate_count > 0
                    else "NO_PERSISTED_PERFORMANCE_DATA"
                ),
                "database_access": "SQLITE_MODE_RO_QUERY_ONLY",
            },
            "summary": {
                "persisted_aggregate_count": aggregate_count,
                "persisted_drift_comparison_count": drift_count,
                "returned_aggregate_count": len(aggregates),
                "returned_drift_comparison_count": len(drift_comparisons),
                "latest_aggregate_generated_at": latest_generated_at,
                "sample_qualification_counts": qualification_counts,
            },
            "aggregates": aggregates,
            "drift_comparisons": drift_comparisons,
            "boundaries": {
                "read_only": True,
                "creates_calibration_observations": False,
                "creates_performance_aggregates": False,
                "creates_drift_comparisons": False,
                "forecast_probability_is_factual_verification": False,
                "performance_metric_is_factual_verification": False,
                "drift_metric_is_factual_verification": False,
                "canonical_factual_verification": "P13_5_P13_6_ONLY",
                "sample_qualification_is_statistical_confidence": False,
                "production_live": "NOT_OPERATIONAL",
                "runtime_storage": "PROJECT_LOCAL_ONLY",
                "mixed_shared_canonical_runtime": "BLOCKED",
                "owner_only_operational_activation": "OWNER_DECISION_REQUIRED",
            },
        }


__all__ = [
    "P15_5_GATE",
    "PROJECTION_VERSION",
    "PerformanceProjectionError",
    "OwnerForecastPerformanceProjection",
]
