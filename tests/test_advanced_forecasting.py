from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    ForecastVersion,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
    forecast_id,
    forecast_version_id,
    validate_scenario_distribution,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType


NOW = datetime(2026, 8, 26, 16, 0, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)


def _forecast():
    return ForecastRecord.create(
        "ua-security-30d",
        "Will a material Ukraine security agreement be announced within 30 days?",
        ForecastHorizon.SHORT,
        DEADLINE,
        created_at=NOW,
    )


def _version(forecast, number=1, reason="Initial forecast"):
    return ForecastVersion.create(
        forecast.forecast_id,
        number,
        input_snapshot={"event_ids": ["event-1"], "graph_edge_ids": ["edge-1"]},
        provenance_refs=("event:event-1", "graph_edge:edge-1"),
        assumptions=("Negotiations continue",),
        change_reason=reason,
        created_at=NOW + timedelta(hours=number - 1),
    )


def _scenarios(version):
    return (
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.BASELINE,
            "Agreement announced",
            0.6,
            0.55,
            0.7,
            drivers=("Negotiation momentum",),
            constraints=("Domestic approval",),
            triggers=("Joint communique",),
            inhibitors=("Negotiation breakdown",),
            uncertainty_factors=("Timing",),
            invalidation_signals=("Formal suspension",),
        ),
        ScenarioVersion.create(
            version.forecast_version_id,
            ScenarioType.NEGATIVE,
            "No agreement announced",
            0.4,
            0.45,
            0.65,
            drivers=("Negotiation delay",),
            constraints=("Time horizon",),
            triggers=("Deadline passes",),
            inhibitors=("Rapid political breakthrough",),
            uncertainty_factors=("Private talks",),
            invalidation_signals=("Agreement signed",),
        ),
    )


def test_durable_forecast_and_versioned_scenarios_survive_restart(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedForecastRepository(db)
    forecast = _forecast()
    version = _version(forecast)
    scenarios = _scenarios(version)

    repo.save_forecast(forecast)
    repo.save_version(version, scenarios)

    restarted = SQLiteAdvancedForecastRepository(db)
    loaded_forecast = restarted.get_forecast(forecast.forecast_id)
    versions = restarted.list_versions(forecast.forecast_id)
    loaded_scenarios = restarted.list_scenarios(version.forecast_version_id)

    assert loaded_forecast == forecast
    assert versions == (version,)
    assert loaded_scenarios == tuple(sorted(scenarios, key=lambda item: (item.scenario_type, item.label, item.scenario_version_id)))
    assert restarted.next_version_number(forecast.forecast_id) == 2


def test_forecast_and_version_identity_are_deterministic_and_idempotent(tmp_path):
    repo = SQLiteAdvancedForecastRepository(tmp_path / "project.db")
    first = _forecast()
    second = _forecast()
    assert first.forecast_id == second.forecast_id
    assert first.forecast_id == forecast_id("ua-security-30d", ForecastHorizon.SHORT, DEADLINE)

    repo.save_forecast(first)
    repo.save_forecast(second)

    version = _version(first)
    assert version.forecast_version_id == forecast_version_id(first.forecast_id, 1)
    scenarios = _scenarios(version)
    repo.save_version(version, scenarios)
    repo.save_version(version, scenarios)

    assert len(repo.list_versions(first.forecast_id)) == 1
    assert len(repo.list_scenarios(version.forecast_version_id)) == 2


def test_forecast_versions_are_monotonic_and_immutable(tmp_path):
    repo = SQLiteAdvancedForecastRepository(tmp_path / "project.db")
    forecast = _forecast()
    repo.save_forecast(forecast)

    version1 = _version(forecast, 1)
    repo.save_version(version1, _scenarios(version1))

    version2 = ForecastVersion.create(
        forecast.forecast_id,
        2,
        input_snapshot={"event_ids": ["event-1", "event-2"]},
        provenance_refs=("event:event-1", "event:event-2"),
        assumptions=("New evidence received",),
        change_reason="New evidence",
        created_at=NOW + timedelta(hours=1),
    )
    scenarios2 = (
        ScenarioVersion.create(version2.forecast_version_id, ScenarioType.BASELINE, "Agreement announced", 0.7, 0.65, 0.75),
        ScenarioVersion.create(version2.forecast_version_id, ScenarioType.NEGATIVE, "No agreement announced", 0.3, 0.35, 0.65),
    )
    repo.save_version(version2, scenarios2)

    skipped = ForecastVersion.create(
        forecast.forecast_id,
        4,
        input_snapshot={},
        provenance_refs=("event:event-4",),
        assumptions=(),
        change_reason="Skipped version",
        created_at=NOW + timedelta(hours=2),
    )
    skipped_scenarios = (
        ScenarioVersion.create(skipped.forecast_version_id, ScenarioType.BASELINE, "A", 0.5, 0.5, 0.5),
        ScenarioVersion.create(skipped.forecast_version_id, ScenarioType.NEGATIVE, "B", 0.5, 0.5, 0.5),
    )
    try:
        repo.save_version(skipped, skipped_scenarios)
    except ValueError as exc:
        assert "monotonic" in str(exc)
    else:
        raise AssertionError("skipping forecast version numbers must fail")

    conflicting = ForecastVersion.create(
        forecast.forecast_id,
        1,
        input_snapshot={"changed": True},
        provenance_refs=("event:event-x",),
        assumptions=(),
        change_reason="Rewrite old version",
        created_at=NOW,
    )
    conflicting_scenarios = (
        ScenarioVersion.create(conflicting.forecast_version_id, ScenarioType.BASELINE, "Agreement announced", 0.6, 0.55, 0.7),
        ScenarioVersion.create(conflicting.forecast_version_id, ScenarioType.NEGATIVE, "No agreement announced", 0.4, 0.45, 0.65),
    )
    try:
        repo.save_version(conflicting, conflicting_scenarios)
    except ValueError as exc:
        assert "immutable" in str(exc)
    else:
        raise AssertionError("existing forecast version must be immutable")


def test_scenario_distribution_requires_normalized_raw_and_calibrated_probabilities():
    version_id = forecast_version_id(_forecast().forecast_id, 1)
    invalid_raw = (
        ScenarioVersion.create(version_id, ScenarioType.BASELINE, "A", 0.8, 0.5, 0.5),
        ScenarioVersion.create(version_id, ScenarioType.NEGATIVE, "B", 0.4, 0.5, 0.5),
    )
    try:
        validate_scenario_distribution(invalid_raw)
    except ValueError as exc:
        assert "raw scenario probabilities" in str(exc)
    else:
        raise AssertionError("non-normalized raw probabilities must fail")

    invalid_calibrated = (
        ScenarioVersion.create(version_id, ScenarioType.BASELINE, "A", 0.5, 0.7, 0.5),
        ScenarioVersion.create(version_id, ScenarioType.NEGATIVE, "B", 0.5, 0.4, 0.5),
    )
    try:
        validate_scenario_distribution(invalid_calibrated)
    except ValueError as exc:
        assert "calibrated scenario probabilities" in str(exc)
    else:
        raise AssertionError("non-normalized calibrated probabilities must fail")


def test_existing_forecast_horizon_and_scenario_type_contracts_are_preserved():
    forecast = _forecast()
    version = _version(forecast)
    scenarios = _scenarios(version)

    assert forecast.horizon == ForecastHorizon.SHORT.value
    assert {item.scenario_type for item in scenarios} == {
        ScenarioType.BASELINE.value,
        ScenarioType.NEGATIVE.value,
    }
    assert sum(item.raw_probability for item in scenarios) == 1.0
    assert sum(item.calibrated_probability for item in scenarios) == 1.0
