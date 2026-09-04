from datetime import datetime, timedelta, timezone
from hashlib import sha256
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.forecast_calibration_engine import (
    SCORING_METHOD,
    SCORING_METHOD_VERSION,
    reliability_bucket,
)
from kgeopolitical_monitor.forecast_performance_intelligence import (
    ForecastPerformanceIntelligenceEngine,
    PerformanceCohortDefinition,
)
from kgeopolitical_monitor.forecast_performance_projection import (
    P15_5_GATE,
    PROJECTION_VERSION,
    OwnerForecastPerformanceProjection,
    PerformanceProjectionError,
)


NOW = datetime(2026, 9, 4, 21, 0, tzinfo=timezone.utc)


def _insert_observation(
    db_path,
    observation_id,
    forecast_id,
    evaluated_at,
    *,
    raw_probability,
    calibrated_probability,
    observed_value,
):
    raw_probability = float(raw_probability)
    calibrated_probability = float(calibrated_probability)
    observed_value = float(observed_value)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecast_calibration_observations(
                   observation_id, assessment_id, forecast_id, forecast_version_id,
                   scenario_version_id, legacy_outcome_id, horizon, scenario_type,
                   scenario_label, legacy_outcome_state, observed_value,
                   raw_probability, calibrated_probability, brier_score_raw,
                   brier_score_calibrated, raw_reliability_bucket,
                   calibrated_reliability_bucket, reliability_bucket_count,
                   scoring_method, scoring_method_version, evaluated_at, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, 'short_term', 'baseline', ?, ?, ?, ?, ?, ?, ?, ?, ?, 10, ?, ?, ?, ?)""",
            (
                observation_id,
                f"assessment-{observation_id}",
                forecast_id,
                f"version-{observation_id}",
                f"scenario-{observation_id}",
                f"outcome-{observation_id}",
                f"Scenario {observation_id}",
                "OBSERVED" if observed_value == 1.0 else "NOT_OBSERVED",
                observed_value,
                raw_probability,
                calibrated_probability,
                (raw_probability - observed_value) ** 2,
                (calibrated_probability - observed_value) ** 2,
                reliability_bucket(raw_probability, 10),
                reliability_bucket(calibrated_probability, 10),
                SCORING_METHOD,
                SCORING_METHOD_VERSION,
                evaluated_at.isoformat(),
                evaluated_at.isoformat(),
            ),
        )


def _seed_performance_state(db_path):
    initialize_database(str(db_path))
    _insert_observation(
        db_path,
        "obs-owner-baseline-1",
        "forecast-owner-a",
        NOW,
        raw_probability=0.80,
        calibrated_probability=0.70,
        observed_value=1.0,
    )
    _insert_observation(
        db_path,
        "obs-owner-baseline-2",
        "forecast-owner-b",
        NOW + timedelta(hours=1),
        raw_probability=0.82,
        calibrated_probability=0.70,
        observed_value=0.0,
    )
    _insert_observation(
        db_path,
        "obs-owner-recent-1",
        "forecast-owner-c",
        NOW + timedelta(days=2),
        raw_probability=0.90,
        calibrated_probability=0.80,
        observed_value=0.0,
    )
    _insert_observation(
        db_path,
        "obs-owner-recent-2",
        "forecast-owner-d",
        NOW + timedelta(days=2, hours=1),
        raw_probability=0.70,
        calibrated_probability=0.60,
        observed_value=0.0,
    )
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    baseline = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW,
            evaluated_to=NOW + timedelta(days=1),
        ),
        generated_at=NOW + timedelta(days=3),
    )
    recent = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW + timedelta(days=2),
            evaluated_to=NOW + timedelta(days=3),
        ),
        generated_at=NOW + timedelta(days=3, minutes=1),
    )
    comparison = engine.compare_drift(
        baseline.aggregate_id,
        recent.aggregate_id,
        created_at=NOW + timedelta(days=3, minutes=2),
    )
    return baseline, recent, comparison


def _file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def test_p15_5_gate_and_projection_version():
    assert P15_5_GATE == "P15_5_OWNER_READ_ONLY_PERFORMANCE_PROJECTION_VALIDATED"
    assert PROJECTION_VERSION == "KGM_OWNER_FORECAST_PERFORMANCE_PROJECTION_V1"


def test_owner_projection_reads_persisted_p15_4_state_without_mutation(tmp_path):
    db_path = tmp_path / "kgm.db"
    baseline, recent, comparison = _seed_performance_state(db_path)
    before_hash = _file_hash(db_path)

    snapshot = OwnerForecastPerformanceProjection(db_path).snapshot(projected_at=NOW)

    assert _file_hash(db_path) == before_hash
    assert snapshot["projection"]["data_state"] == "AVAILABLE"
    assert snapshot["projection"]["database_access"] == "SQLITE_MODE_RO_QUERY_ONLY"
    assert snapshot["summary"]["persisted_aggregate_count"] == 2
    assert snapshot["summary"]["persisted_drift_comparison_count"] == 1
    assert snapshot["summary"]["returned_aggregate_count"] == 2
    assert snapshot["summary"]["returned_drift_comparison_count"] == 1

    aggregates = {item["aggregate_id"]: item for item in snapshot["aggregates"]}
    assert aggregates[baseline.aggregate_id]["observation_set_hash"] == baseline.observation_set_hash
    assert aggregates[baseline.aggregate_id]["sample_count"] == 2
    assert aggregates[baseline.aggregate_id]["forecast_count"] == 2
    assert aggregates[baseline.aggregate_id]["sample_qualification"] == "N_LT_5"
    assert (
        aggregates[baseline.aggregate_id]["sample_limitation"]
        == "VERY_SMALL_SAMPLE_DESCRIPTIVE_ONLY"
    )
    assert aggregates[recent.aggregate_id]["cohort"]["horizon"] == "short_term"

    drift = snapshot["drift_comparisons"][0]
    assert drift["comparison_id"] == comparison.comparison_id
    assert drift["baseline_aggregate_id"] == baseline.aggregate_id
    assert drift["recent_aggregate_id"] == recent.aggregate_id
    assert (
        drift["interpretation_boundary"]
        == "DESCRIPTIVE_TEMPORAL_DELTA_ONLY_NOT_CAUSAL_NOT_SIGNIFICANCE_TEST"
    )


def test_projection_connection_is_physically_query_only(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    projection = OwnerForecastPerformanceProjection(db_path)
    with projection._connect() as connection:
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError):
            connection.execute("CREATE TABLE forbidden_owner_projection_write(id TEXT)")


def test_empty_p15_4_state_projects_explicit_no_data_without_creating_records(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    before_hash = _file_hash(db_path)
    snapshot = OwnerForecastPerformanceProjection(db_path).snapshot(projected_at=NOW)
    assert _file_hash(db_path) == before_hash
    assert snapshot["projection"]["data_state"] == "NO_PERSISTED_PERFORMANCE_DATA"
    assert snapshot["summary"]["persisted_aggregate_count"] == 0
    assert snapshot["summary"]["persisted_drift_comparison_count"] == 0
    assert snapshot["aggregates"] == []
    assert snapshot["drift_comparisons"] == []


def test_missing_database_fails_closed_instead_of_creating_one(tmp_path):
    db_path = tmp_path / "missing.db"
    with pytest.raises(PerformanceProjectionError, match="unavailable"):
        OwnerForecastPerformanceProjection(db_path).snapshot(projected_at=NOW)
    assert not db_path.exists()


def test_projection_limits_are_bounded_and_do_not_change_persisted_counts(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_performance_state(db_path)
    snapshot = OwnerForecastPerformanceProjection(db_path).snapshot(
        aggregate_limit=1,
        drift_limit=1,
        projected_at=NOW,
    )
    assert snapshot["summary"]["persisted_aggregate_count"] == 2
    assert snapshot["summary"]["returned_aggregate_count"] == 1
    with pytest.raises(PerformanceProjectionError, match="between 1 and 100"):
        OwnerForecastPerformanceProjection(db_path).snapshot(aggregate_limit=0, projected_at=NOW)
    with pytest.raises(PerformanceProjectionError, match="between 1 and 100"):
        OwnerForecastPerformanceProjection(db_path).snapshot(drift_limit=101, projected_at=NOW)


def test_owner_projection_preserves_truth_runtime_and_activation_boundaries(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_performance_state(db_path)
    snapshot = OwnerForecastPerformanceProjection(db_path).snapshot(projected_at=NOW)
    boundaries = snapshot["boundaries"]
    assert boundaries["read_only"] is True
    assert boundaries["creates_calibration_observations"] is False
    assert boundaries["creates_performance_aggregates"] is False
    assert boundaries["creates_drift_comparisons"] is False
    assert boundaries["forecast_probability_is_factual_verification"] is False
    assert boundaries["performance_metric_is_factual_verification"] is False
    assert boundaries["drift_metric_is_factual_verification"] is False
    assert boundaries["canonical_factual_verification"] == "P13_5_P13_6_ONLY"
    assert boundaries["sample_qualification_is_statistical_confidence"] is False
    assert boundaries["production_live"] == "NOT_OPERATIONAL"
    assert boundaries["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert boundaries["mixed_shared_canonical_runtime"] == "BLOCKED"
    assert boundaries["owner_only_operational_activation"] == "OWNER_DECISION_REQUIRED"


def test_projected_performance_records_contain_no_truth_promotion_fields(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_performance_state(db_path)
    snapshot = OwnerForecastPerformanceProjection(db_path).snapshot(projected_at=NOW)
    forbidden = {
        "verification_status",
        "verification_state",
        "factual_confidence",
        "coverage_confidence",
        "source_count",
        "host_count",
        "domain_count",
        "scenario_confidence",
    }
    for item in snapshot["aggregates"] + snapshot["drift_comparisons"]:
        assert set(item).isdisjoint(forbidden)
