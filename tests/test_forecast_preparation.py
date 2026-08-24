from kgeopolitical_monitor.forecast_preparation import (
    ForecastHorizon,
    ForecastPreparation,
)


def test_forecast_signal_creation():
    result = ForecastPreparation().prepare(
        "event-1",
        0.8,
        0.7,
        0.9,
        ForecastHorizon.SHORT,
    )

    assert result.event_id == "event-1"
    assert result.confidence == 0.9
