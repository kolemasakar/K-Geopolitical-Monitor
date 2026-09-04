from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.forecast_calibration_engine import (
    SCORING_METHOD,
    SCORING_METHOD_VERSION,
    reliability_bucket,
)
from kgeopolitical_monitor.forecast_performance_intelligence import (
    BIAS_OVER_PREDICTION,
    BIAS_UNDER_PREDICTION,
    BIAS_WITHIN_TOLERANCE,
    P15_4_GATE,
    ForecastPerformanceIntelligenceEngine,
    PerformanceCohortDefinition,
    PerformanceIntelligenceError,
    classify_bias,
)


NOW = datetime(2026, 9, 4, 20, 0, tzinfo=timezone.utc)


def _insert_observation(
    db_path,
    observation_id,
    forecast_id,
    evaluated_at,
    *,
    raw_probability,
    calibrated_probability,
    observed_value,
    horizon="short_term",
    scenario_type="baseline",
    bucket_count=10,
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
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                observation_id,
                f"assessment-{observation_id}",
                forecast_id,
                f"version-{observation_id}",
                f"scenario-{observation_id}",
                f"outcome-{observation_id}",
                horizon,
                scenario_type,
                f"Scenario {observation_id}",
                "OBSERVED" if observed_value == 1.0 else "NOT_OBSERVED",
                observed_value,
                raw_probability,
                calibrated_probability,
                (raw_probability - observed_value) ** 2,
                (calibrated_probability - observed_value) ** 2,
                reliability_bucket(raw_probability, bucket_count),
                reliability_bucket(calibrated_probability, bucket_count),
                bucket_count,
                SCORING_METHOD,
                SCORING_METHOD_VERSION,
                evaluated_at.isoformat(),
                evaluated_at.isoformat(),
            ),
        )


def _seed_short_term_baseline_history(db_path):
    initialize_database(str(db_path))
    _insert_observation(
        db_path,
        "obs-baseline-1",
        "forecast-a",
        NOW,
        raw_probability=0.80,
        calibrated_probability=0.70,
        observed_value=1.0,
    )
    _insert_observation(
        db_path,
        "obs-baseline-2",
        "forecast-b",
        NOW + timedelta(hours=1),
        raw_probability=0.82,
        calibrated_probability=0.70,
        observed_value=0.0,
    )
    _insert_observation(
        db_path,
        "obs-recent-1",
        "forecast-c",
        NOW + timedelta(days=2),
        raw_probability=0.90,
        calibrated_probability=0.80,
        observed_value=0.0,
    )
    _insert_observation(
        db_path,
        "obs-recent-2",
        "forecast-d",
        NOW + timedelta(days=2, hours=1),
        raw_probability=0.70,
        calibrated_probability=0.60,
        observed_value=0.0,
    )


def test_p15_4_gate_name():
    assert P15_4_GATE == "P15_4_PERFORMANCE_INTELLIGENCE_DRIFT_BIAS_VALIDATED"


def test_migration_030_is_applied_additively(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        migrations = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert "030_forecast_performance_intelligence.sql" in migrations
    assert "forecast_performance_aggregates" in tables
    assert "forecast_performance_aggregate_observations" in tables
    assert "forecast_performance_drift_comparisons" in tables
    assert "forecast_calibration_observations" in tables
    assert "forecast_evaluations" in tables
    assert "forecast_calibration_runs" in tables
    assert "forecast_calibration_buckets" in tables


def test_aggregate_exposes_exact_cohort_membership_hash_and_sample_size(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    cohort = PerformanceCohortDefinition(
        horizon="short_term",
        scenario_type="baseline",
        evaluated_from=NOW,
        evaluated_to=NOW + timedelta(days=1),
    )
    aggregate = ForecastPerformanceIntelligenceEngine(db_path).aggregate(
        cohort, generated_at=NOW + timedelta(days=3)
    )

    assert aggregate.sample_count == 2
    assert aggregate.forecast_count == 2
    assert aggregate.sample_qualification == "N_LT_5"
    assert aggregate.observation_ids == ("obs-baseline-1", "obs-baseline-2")
    expected_hash = sha256("obs-baseline-1\x1fobs-baseline-2".encode("utf-8")).hexdigest()
    assert aggregate.observation_set_hash == expected_hash
    assert json.loads(aggregate.cohort_definition_json) == cohort.payload()


def test_raw_and_calibrated_performance_bias_and_ece_remain_separate(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    aggregate = ForecastPerformanceIntelligenceEngine(db_path).aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW,
            evaluated_to=NOW + timedelta(days=1),
        ),
        generated_at=NOW + timedelta(days=3),
    )

    assert aggregate.mean_raw_probability == pytest.approx(0.81)
    assert aggregate.mean_calibrated_probability == pytest.approx(0.70)
    assert aggregate.observed_rate == pytest.approx(0.50)
    assert aggregate.mean_brier_raw == pytest.approx((0.04 + 0.6724) / 2)
    assert aggregate.mean_brier_calibrated == pytest.approx((0.09 + 0.49) / 2)
    # Both raw observations occupy reliability bucket 8; both calibrated
    # observations occupy bucket 7. ECE therefore compares bucket means.
    assert aggregate.expected_calibration_error_raw == pytest.approx(0.31)
    assert aggregate.expected_calibration_error_calibrated == pytest.approx(0.20)
    assert aggregate.bias_raw == pytest.approx(0.31)
    assert aggregate.bias_calibrated == pytest.approx(0.20)
    assert aggregate.brier_improvement == pytest.approx(((0.04 + 0.6724) / 2) - 0.29)
    assert aggregate.calibration_error_improvement == pytest.approx(0.11)


def test_bias_classification_is_descriptive_and_tolerance_explicit():
    assert classify_bias(0.051, tolerance=0.05) == BIAS_OVER_PREDICTION
    assert classify_bias(-0.051, tolerance=0.05) == BIAS_UNDER_PREDICTION
    assert classify_bias(0.05, tolerance=0.05) == BIAS_WITHIN_TOLERANCE
    with pytest.raises(PerformanceIntelligenceError, match="tolerance"):
        classify_bias(0.1, tolerance=1.1)


def test_performance_aggregate_is_deterministic_idempotent_and_append_only(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    cohort = PerformanceCohortDefinition(
        horizon="short_term",
        scenario_type="baseline",
        evaluated_from=NOW,
        evaluated_to=NOW + timedelta(days=1),
    )
    first = engine.aggregate(cohort, generated_at=NOW + timedelta(days=3))
    second = engine.aggregate(cohort, generated_at=NOW + timedelta(days=4))
    assert first.aggregate_id == second.aggregate_id
    assert first.generated_at == second.generated_at

    with sqlite3.connect(db_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM forecast_performance_aggregates"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM forecast_performance_aggregate_observations"
        ).fetchone()[0] == 2
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE forecast_performance_aggregates SET sample_count = 3"
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM forecast_performance_aggregate_observations"
            )


def test_new_observation_creates_new_snapshot_without_rewriting_old_aggregate(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    cohort = PerformanceCohortDefinition(
        horizon="short_term",
        scenario_type="baseline",
    )
    first = engine.aggregate(cohort, generated_at=NOW + timedelta(days=3))
    _insert_observation(
        db_path,
        "obs-later",
        "forecast-e",
        NOW + timedelta(days=4),
        raw_probability=0.4,
        calibrated_probability=0.5,
        observed_value=1.0,
    )
    second = engine.aggregate(cohort, generated_at=NOW + timedelta(days=5))
    assert first.aggregate_id != second.aggregate_id
    assert first.sample_count == 4
    assert second.sample_count == 5
    with sqlite3.connect(db_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM forecast_performance_aggregates"
        ).fetchone()[0] == 2


def test_drift_comparison_uses_compatible_ordered_non_overlapping_windows(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
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
        generated_at=NOW + timedelta(days=3),
    )
    comparison = engine.compare_drift(
        baseline.aggregate_id,
        recent.aggregate_id,
        created_at=NOW + timedelta(days=3),
    )

    assert comparison.baseline_sample_count == 2
    assert comparison.recent_sample_count == 2
    assert comparison.mean_raw_probability_delta == pytest.approx(0.80 - 0.81)
    assert comparison.mean_calibrated_probability_delta == pytest.approx(0.70 - 0.70)
    assert comparison.observed_rate_delta == pytest.approx(-0.50)
    assert comparison.mean_brier_raw_delta == pytest.approx(0.65 - ((0.04 + 0.6724) / 2))
    assert comparison.mean_brier_calibrated_delta == pytest.approx(0.50 - 0.29)
    assert comparison.calibration_error_raw_delta == pytest.approx(0.80 - 0.31)
    assert comparison.calibration_error_calibrated_delta == pytest.approx(0.70 - 0.20)
    assert comparison.bias_raw_shift == pytest.approx(0.80 - 0.31)
    assert comparison.bias_calibrated_shift == pytest.approx(0.70 - 0.20)


def test_drift_comparison_rejects_dimension_mismatch_and_overlap(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    _insert_observation(
        db_path,
        "obs-medium",
        "forecast-medium",
        NOW + timedelta(days=2),
        raw_probability=0.5,
        calibrated_probability=0.5,
        observed_value=1.0,
        horizon="medium_term",
    )
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    baseline = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW,
            evaluated_to=NOW + timedelta(days=1),
        )
    )
    different_dimension = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="medium_term",
            scenario_type="baseline",
            evaluated_from=NOW + timedelta(days=2),
            evaluated_to=NOW + timedelta(days=3),
        )
    )
    with pytest.raises(PerformanceIntelligenceError, match="identical non-temporal"):
        engine.compare_drift(baseline.aggregate_id, different_dimension.aggregate_id)

    overlapping_recent = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW + timedelta(minutes=30),
            evaluated_to=NOW + timedelta(days=3),
        )
    )
    with pytest.raises(PerformanceIntelligenceError, match="non-overlapping"):
        engine.compare_drift(baseline.aggregate_id, overlapping_recent.aggregate_id)


def test_drift_comparison_is_idempotent_and_append_only(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    baseline = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW,
            evaluated_to=NOW + timedelta(days=1),
        )
    )
    recent = engine.aggregate(
        PerformanceCohortDefinition(
            horizon="short_term",
            scenario_type="baseline",
            evaluated_from=NOW + timedelta(days=2),
            evaluated_to=NOW + timedelta(days=3),
        )
    )
    first = engine.compare_drift(baseline.aggregate_id, recent.aggregate_id, created_at=NOW)
    second = engine.compare_drift(
        baseline.aggregate_id,
        recent.aggregate_id,
        created_at=NOW + timedelta(days=10),
    )
    assert first.comparison_id == second.comparison_id
    assert first.created_at == second.created_at
    with sqlite3.connect(db_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM forecast_performance_drift_comparisons"
        ).fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE forecast_performance_drift_comparisons SET recent_sample_count = 9"
            )


def test_performance_intelligence_does_not_write_factual_verification_state(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_short_term_baseline_history(db_path)
    engine = ForecastPerformanceIntelligenceEngine(db_path)
    with sqlite3.connect(db_path) as connection:
        before = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    baseline = engine.aggregate(
        PerformanceCohortDefinition(
            evaluated_from=NOW,
            evaluated_to=NOW + timedelta(days=1),
        )
    )
    recent = engine.aggregate(
        PerformanceCohortDefinition(
            evaluated_from=NOW + timedelta(days=2),
            evaluated_to=NOW + timedelta(days=3),
        )
    )
    engine.compare_drift(baseline.aggregate_id, recent.aggregate_id)
    with sqlite3.connect(db_path) as connection:
        after = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    assert after == before


def test_p15_4_schema_contains_no_truth_promotion_fields(tmp_path):
    db_path = tmp_path / "kgm.db"
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        columns = set()
        for table in (
            "forecast_performance_aggregates",
            "forecast_performance_drift_comparisons",
        ):
            columns.update(
                row[1] for row in connection.execute(f"PRAGMA table_info({table})")
            )
    forbidden = {
        "verification_status",
        "verification_state",
        "factual_confidence",
        "independent_origin_count",
        "coverage_confidence",
        "source_count",
        "host_count",
        "domain_count",
        "scenario_confidence",
        "performance_rank",
    }
    assert columns.isdisjoint(forbidden)
