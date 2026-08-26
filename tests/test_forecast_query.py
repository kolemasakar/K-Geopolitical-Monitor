from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
)
from kgeopolitical_monitor.forecast_calibration_history import (
    CalibrationCohort,
    SQLiteForecastCalibrationRepository,
)
from kgeopolitical_monitor.forecast_evaluation import (
    OBSERVED,
    ForecastOutcome,
    SQLiteForecastEvaluationRepository,
)
from kgeopolitical_monitor.forecast_inputs import (
    ANALYST_ASSUMPTION,
    GRAPH_RELATIONSHIP,
    SOURCE_EVIDENCE,
    ForecastInputRef,
    SQLiteForecastInputRepository,
    create_forecast_version_with_inputs,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.forecast_query import AdvancedForecastQuery
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType
from kgeopolitical_monitor.runtime_storage import RuntimeStoragePolicy


NOW = datetime(2026, 8, 26, 16, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)


def _seed_upstream(db):
    repo = SQLiteAdvancedForecastRepository(db)
    with sqlite3.connect(db) as connection:
        connection.execute("INSERT INTO sources(id, name, source_class, reliability) VALUES ('source-1', 'Source 1', 'Official sources', 'HIGH')")
        connection.execute("INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES ('raw-1', 'source-1', 'Evidence', 'Evidence body', ?)", (NOW.isoformat(),))
        connection.execute(
            """
            INSERT INTO graph_edges(
                edge_id, source_node_id, target_node_id, relation_type, relation_class,
                confidence, status, valid_from, valid_to, first_observed_at,
                last_observed_at, explanation, created_at, updated_at
            ) VALUES ('edge-1', 'node-a', 'node-b', 'influences', 'INFLUENCE',
                      0.62, 'ACTIVE', NULL, NULL, ?, ?, 'Observed influence', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat(), NOW.isoformat(), NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title, verification_status,
                confidence, importance, independent_origin_count, source_class_count, origins_json
            ) VALUES ('claim-1', 'analysis-1', 'claim-key', 'Claim', 'DETECTED', 0.57, 0.8, 1, 1, '["origin.example"]')
            """
        )
    return repo


def _scenario_set(version_id, baseline_raw, baseline_calibrated, confidence=0.7):
    return (
        ScenarioVersion.create(
            version_id,
            ScenarioType.BASELINE,
            "Agreement announced",
            baseline_raw,
            baseline_calibrated,
            confidence,
            drivers=("Negotiation momentum",),
            constraints=("Domestic approval",),
            triggers=("Joint communique",),
            inhibitors=("Negotiation breakdown",),
            uncertainty_factors=("Timing",),
            invalidation_signals=("Formal suspension",),
        ),
        ScenarioVersion.create(
            version_id,
            ScenarioType.NEGATIVE,
            "No agreement announced",
            1.0 - baseline_raw,
            1.0 - baseline_calibrated,
            confidence - 0.05,
            drivers=("Negotiation delay",),
            constraints=("Time horizon",),
            triggers=("Deadline passes",),
            inhibitors=("Rapid breakthrough",),
            uncertainty_factors=("Private talks",),
            invalidation_signals=("Agreement signed",),
        ),
    )


def _forecast_with_two_versions(db):
    repo = _seed_upstream(db)
    input_repo = SQLiteForecastInputRepository(db)
    forecast = ForecastRecord.create(
        "ua-security-30d",
        "Will a material Ukraine security agreement be announced within 30 days?",
        ForecastHorizon.SHORT,
        DEADLINE,
        created_at=NOW,
    )
    repo.save_forecast(forecast)

    v1_id = repo.next_version_number(forecast.forecast_id)
    assert v1_id == 1
    version1_inputs = (
        ForecastInputRef.durable("placeholder", SOURCE_EVIDENCE, "raw-1", created_at=NOW),
    )
    # Rebuild inputs with the deterministic version identity before materialization.
    from kgeopolitical_monitor.advanced_forecasting import forecast_version_id
    version1_id_value = forecast_version_id(forecast.forecast_id, 1)
    version1_inputs = (
        ForecastInputRef.durable(version1_id_value, SOURCE_EVIDENCE, "raw-1", created_at=NOW),
        ForecastInputRef.durable(version1_id_value, GRAPH_RELATIONSHIP, "edge-1", created_at=NOW),
        ForecastInputRef.assumption(version1_id_value, "Negotiations continue", created_at=NOW),
    )
    version1 = create_forecast_version_with_inputs(
        forecast.forecast_id,
        1,
        inputs=version1_inputs,
        constraints=("No automatic promotion to fact",),
        change_reason="Initial forecast",
        created_at=NOW,
    )
    repo.save_version(version1, _scenario_set(version1.forecast_version_id, 0.6, 0.55))
    input_repo.bind(version1, version1_inputs, constraints=("No automatic promotion to fact",))

    version2_id_value = forecast_version_id(forecast.forecast_id, 2)
    version2_inputs = (
        ForecastInputRef.durable(version2_id_value, SOURCE_EVIDENCE, "raw-1", created_at=NOW + timedelta(hours=1)),
        ForecastInputRef.durable(version2_id_value, GRAPH_RELATIONSHIP, "edge-1", created_at=NOW + timedelta(hours=1)),
        ForecastInputRef.assumption(version2_id_value, "Negotiations accelerated", created_at=NOW + timedelta(hours=1)),
    )
    version2 = create_forecast_version_with_inputs(
        forecast.forecast_id,
        2,
        inputs=version2_inputs,
        constraints=("No automatic promotion to fact",),
        change_reason="New evidence increased baseline probability",
        created_at=NOW + timedelta(hours=1),
    )
    repo.save_version(version2, _scenario_set(version2.forecast_version_id, 0.7, 0.65, 0.75))
    input_repo.bind(version2, version2_inputs, constraints=("No automatic promotion to fact",))
    return forecast, version1, version2


def test_current_forecast_history_and_scenario_comparison_are_deterministic(tmp_path):
    db = tmp_path / "project.db"
    forecast, version1, version2 = _forecast_with_two_versions(db)
    query = AdvancedForecastQuery(db)

    current = query.current_forecast(forecast.forecast_id)
    history = query.version_history(forecast.forecast_id)
    deltas = query.compare_scenarios(forecast.forecast_id, 1, 2)

    assert current.version == version2
    assert tuple(item.version for item in history) == (version1, version2)
    baseline = next(item for item in deltas if item.scenario_type == ScenarioType.BASELINE.value)
    assert baseline.from_raw_probability == 0.6
    assert baseline.to_raw_probability == 0.7
    assert baseline.from_calibrated_probability == 0.55
    assert baseline.to_calibrated_probability == 0.65


def test_forecast_explanation_keeps_graph_relationships_separate_from_source_evidence(tmp_path):
    db = tmp_path / "project.db"
    forecast, _, version2 = _forecast_with_two_versions(db)
    explanation = AdvancedForecastQuery(db).explain_version(version2.forecast_version_id)

    assert explanation.forecast_id == forecast.forecast_id
    assert explanation.source_evidence_refs == ("raw-1",)
    assert explanation.graph_relationship_refs == ("edge-1",)
    assert explanation.analyst_assumptions == ("Negotiations accelerated",)
    assert "not independent source evidence" in explanation.text


def test_outcome_and_evaluation_history_are_queryable_by_forecast(tmp_path):
    db = tmp_path / "project.db"
    forecast, _, version2 = _forecast_with_two_versions(db)
    evaluation_repo = SQLiteForecastEvaluationRepository(db)
    outcome = ForecastOutcome.create(
        forecast.forecast_id,
        NOW + timedelta(days=20),
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-1",),
        explanation="Agreement was announced.",
        created_at=NOW + timedelta(days=20),
    )
    evaluation_repo.save_outcome(outcome)
    evaluation_repo.evaluate_version(outcome.outcome_id, version2.forecast_version_id, evaluated_at=NOW + timedelta(days=20))

    history = AdvancedForecastQuery(db).outcome_history(forecast.forecast_id)
    assert len(history) == 1
    assert history[0].outcome == outcome
    assert len(history[0].evaluations) == 2
    assert sum(item.sample_count for item in history[0].evaluations) == 2


def _add_resolved_forecast(db, index):
    repo = SQLiteAdvancedForecastRepository(db)
    evaluation_repo = SQLiteForecastEvaluationRepository(db)
    forecast = ForecastRecord.create(
        f"calibration-{index}",
        f"Calibration forecast {index}?",
        ForecastHorizon.SHORT,
        DEADLINE + timedelta(days=index),
        created_at=NOW,
    )
    repo.save_forecast(forecast)
    from kgeopolitical_monitor.advanced_forecasting import ForecastVersion
    version = ForecastVersion.create(
        forecast.forecast_id,
        1,
        input_snapshot={"calibration_fixture": index},
        provenance_refs=("SOURCE_EVIDENCE:raw-1",),
        assumptions=("Calibration fixture",),
        change_reason="Calibration fixture",
        created_at=NOW,
    )
    baseline_raw = 0.55 + index * 0.05
    baseline_cal = 0.5 + index * 0.05
    repo.save_version(version, _scenario_set(version.forecast_version_id, baseline_raw, baseline_cal))
    outcome = ForecastOutcome.create(
        forecast.forecast_id,
        NOW + timedelta(days=10 + index),
        OBSERVED,
        observed_scenario_type=ScenarioType.BASELINE,
        evidence_refs=("raw-1",),
        explanation="Observed baseline outcome.",
        created_at=NOW + timedelta(days=10 + index),
    )
    evaluation_repo.save_outcome(outcome)
    evaluation_repo.evaluate_version(outcome.outcome_id, version.forecast_version_id, evaluated_at=NOW + timedelta(days=10 + index))
    return forecast


def test_calibration_history_is_filterable_to_forecast_membership(tmp_path):
    db = tmp_path / "project.db"
    _seed_upstream(db)
    forecasts = tuple(_add_resolved_forecast(db, index) for index in range(1, 4))
    calibration_repo = SQLiteForecastCalibrationRepository(db)
    run, buckets = calibration_repo.create_run(CalibrationCohort(horizon=ForecastHorizon.SHORT), created_at=NOW + timedelta(days=30))

    views = AdvancedForecastQuery(db).calibration_history(forecasts[0].forecast_id)
    assert len(views) == 1
    assert views[0].run == run
    assert views[0].buckets == buckets
    assert views[0].run.sample_count == 6


def test_advanced_forecast_queries_do_not_mutate_m8_or_m11_truth(tmp_path):
    db = tmp_path / "project.db"
    forecast, _, version2 = _forecast_with_two_versions(db)
    with sqlite3.connect(db) as connection:
        claim_before = connection.execute(
            "SELECT verification_status, confidence, independent_origin_count, origins_json FROM live_analysis_claims WHERE claim_id = 'claim-1'"
        ).fetchone()
        edge_before = connection.execute(
            "SELECT confidence, status, explanation FROM graph_edges WHERE edge_id = 'edge-1'"
        ).fetchone()

    query = AdvancedForecastQuery(db)
    query.current_forecast(forecast.forecast_id)
    query.version_history(forecast.forecast_id)
    query.compare_scenarios(forecast.forecast_id, 1, 2)
    query.explain_version(version2.forecast_version_id)
    query.outcome_history(forecast.forecast_id)
    query.calibration_history(forecast.forecast_id)

    with sqlite3.connect(db) as connection:
        claim_after = connection.execute(
            "SELECT verification_status, confidence, independent_origin_count, origins_json FROM live_analysis_claims WHERE claim_id = 'claim-1'"
        ).fetchone()
        edge_after = connection.execute(
            "SELECT confidence, status, explanation FROM graph_edges WHERE edge_id = 'edge-1'"
        ).fetchone()
    assert claim_after == claim_before == ("DETECTED", 0.57, 1, '["origin.example"]')
    assert edge_after == edge_before == (0.62, "ACTIVE", "Observed influence")


def test_m12_query_preserves_project_local_runtime_storage_boundary(tmp_path):
    project_root = tmp_path / "project"
    policy = RuntimeStoragePolicy(project_root)
    allowed = policy.resolve_database("data/forecast.db")
    assert allowed == (project_root / "data" / "forecast.db").resolve()

    with pytest.raises(ValueError, match="project-local data directory"):
        policy.resolve_database(tmp_path / "external" / "forecast.db")
