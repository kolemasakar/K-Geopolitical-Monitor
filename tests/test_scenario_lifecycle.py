from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    SQLiteAdvancedForecastRepository,
    forecast_version_id,
)
from kgeopolitical_monitor.forecast_inputs import (
    CANONICAL_EVENT,
    ForecastInputRef,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType
from kgeopolitical_monitor.scenario_lifecycle import (
    INHIBITED,
    INVALIDATED,
    TRIGGERED,
    UNCHANGED,
    ScenarioDraft,
    ScenarioLifecycleService,
    evaluate_scenario_signals,
)


NOW = datetime(2026, 8, 26, 17, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)


def _forecast():
    return ForecastRecord.create(
        "ua-scenario-lifecycle-30d",
        "Will a material Ukraine security agreement be announced within 30 days?",
        ForecastHorizon.SHORT,
        DEADLINE,
        created_at=NOW,
    )


def _seed_events(db):
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-1", "Negotiation round", "ACTIVE", "0.8"),
        )
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-2", "Joint communique", "ACTIVE", "0.9"),
        )


def _inputs(version_id, event_id, assumption):
    return (
        ForecastInputRef.durable(
            version_id,
            CANONICAL_EVENT,
            event_id,
            created_at=NOW,
        ),
        ForecastInputRef.assumption(
            version_id,
            assumption,
            created_at=NOW,
        ),
    )


def _drafts(raw_baseline=0.60, calibrated_baseline=0.55, confidence=0.80):
    return (
        ScenarioDraft(
            scenario_type=ScenarioType.BASELINE.value,
            label="Agreement announced",
            raw_probability=raw_baseline,
            calibrated_probability=calibrated_baseline,
            scenario_confidence=confidence,
            drivers=("Negotiation momentum",),
            constraints=("Domestic approval",),
            triggers=("Joint communique",),
            inhibitors=("Negotiation breakdown",),
            uncertainty_factors=("Private negotiation timing",),
            invalidation_signals=("Formal suspension",),
        ),
        ScenarioDraft(
            scenario_type=ScenarioType.NEGATIVE.value,
            label="No agreement announced",
            raw_probability=1.0 - raw_baseline,
            calibrated_probability=1.0 - calibrated_baseline,
            scenario_confidence=0.65,
            drivers=("Negotiation delay",),
            constraints=("Evaluation deadline",),
            triggers=("Deadline passes",),
            inhibitors=("Rapid political breakthrough",),
            uncertainty_factors=("Unreported bilateral talks",),
            invalidation_signals=("Agreement signed",),
        ),
    )


def _setup(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedForecastRepository(db)
    _seed_events(db)
    forecast = _forecast()
    repo.save_forecast(forecast)
    return db, repo, forecast


def test_scenario_lifecycle_creates_new_immutable_versions_and_preserves_history(tmp_path):
    db, repo, forecast = _setup(tmp_path)
    service = ScenarioLifecycleService(db)

    version1_id = forecast_version_id(forecast.forecast_id, 1)
    state1 = service.create_next_version(
        forecast.forecast_id,
        inputs=_inputs(version1_id, "event-1", "Negotiations remain active"),
        constraints=("No external provider",),
        scenarios=_drafts(0.60, 0.55),
        change_reason="Initial scenario assessment",
        created_at=NOW,
    )

    version2_id = forecast_version_id(forecast.forecast_id, 2)
    state2 = service.create_next_version(
        forecast.forecast_id,
        inputs=_inputs(version2_id, "event-2", "Joint communique changes the baseline"),
        constraints=("Formal signature still required",),
        scenarios=_drafts(0.75, 0.70),
        change_reason="New canonical event changed scenario weights",
        created_at=NOW + timedelta(hours=1),
    )

    restarted = ScenarioLifecycleService(db)
    history = restarted.history(forecast.forecast_id)

    assert [item.version.version_number for item in history] == [1, 2]
    assert history[0].version == state1.version
    assert history[1].version == state2.version
    assert history[0].scenarios[0].raw_probability == 0.60
    assert history[1].scenarios[0].raw_probability == 0.75
    assert history[0].version.change_reason == "Initial scenario assessment"
    assert history[1].version.change_reason == "New canonical event changed scenario weights"
    assert repo.next_version_number(forecast.forecast_id) == 3


def test_scenario_lifecycle_prevalidates_canonical_inputs_without_partial_version(tmp_path):
    db, repo, forecast = _setup(tmp_path)
    service = ScenarioLifecycleService(db)
    version1_id = forecast_version_id(forecast.forecast_id, 1)
    inputs = _inputs(version1_id, "event-missing", "Explicit assumption")

    with pytest.raises(ValueError, match="unknown canonical reference"):
        service.create_next_version(
            forecast.forecast_id,
            inputs=inputs,
            constraints=("Constraint",),
            scenarios=_drafts(),
            change_reason="Should not persist",
            created_at=NOW,
        )

    assert repo.list_versions(forecast.forecast_id) == ()


def test_scenario_lifecycle_requires_complete_approved_scenario_structure():
    with pytest.raises(ValueError, match="complete scenario draft requires triggers"):
        ScenarioDraft(
            scenario_type=ScenarioType.BASELINE.value,
            label="Incomplete scenario",
            raw_probability=1.0,
            calibrated_probability=1.0,
            scenario_confidence=0.5,
            drivers=("Driver",),
            constraints=("Constraint",),
            triggers=(),
            inhibitors=("Inhibitor",),
            uncertainty_factors=("Uncertainty",),
            invalidation_signals=("Invalidation",),
        )


def test_scenario_signal_evaluation_is_deterministic_and_non_mutating():
    scenario = _drafts()[0].materialize("fver-test")

    assert evaluate_scenario_signals(scenario, ()).state == UNCHANGED
    assert evaluate_scenario_signals(scenario, ("Joint communique",)).state == TRIGGERED
    assert evaluate_scenario_signals(scenario, ("Negotiation breakdown",)).state == INHIBITED

    mixed = evaluate_scenario_signals(
        scenario,
        ("Joint communique", "Negotiation breakdown", "Formal suspension"),
    )
    assert mixed.state == INVALIDATED
    assert mixed.triggered_signals == ("Joint communique",)
    assert mixed.inhibitor_signals == ("Negotiation breakdown",)
    assert mixed.invalidation_signals == ("Formal suspension",)
    assert scenario.raw_probability == 0.60
    assert scenario.calibrated_probability == 0.55


def test_raw_calibrated_probability_and_scenario_confidence_remain_separate(tmp_path):
    db, _, forecast = _setup(tmp_path)
    service = ScenarioLifecycleService(db)
    version1_id = forecast_version_id(forecast.forecast_id, 1)
    state = service.create_next_version(
        forecast.forecast_id,
        inputs=_inputs(version1_id, "event-1", "Analyst assumption"),
        constraints=("Constraint",),
        scenarios=_drafts(0.60, 0.55, 0.80),
        change_reason="Separate probability and confidence test",
        created_at=NOW,
    )

    baseline = state.scenarios[0]
    assert baseline.raw_probability == 0.60
    assert baseline.calibrated_probability == 0.55
    assert baseline.scenario_confidence == 0.80
    assert sum(item.raw_probability for item in state.scenarios) == pytest.approx(1.0)
    assert sum(item.calibrated_probability for item in state.scenarios) == pytest.approx(1.0)


def test_scenario_update_requires_explicit_change_reason(tmp_path):
    db, repo, forecast = _setup(tmp_path)
    service = ScenarioLifecycleService(db)
    version1_id = forecast_version_id(forecast.forecast_id, 1)

    with pytest.raises(ValueError, match="change_reason must not be empty"):
        service.create_next_version(
            forecast.forecast_id,
            inputs=_inputs(version1_id, "event-1", "Assumption"),
            constraints=("Constraint",),
            scenarios=_drafts(),
            change_reason="   ",
            created_at=NOW,
        )

    assert repo.list_versions(forecast.forecast_id) == ()
