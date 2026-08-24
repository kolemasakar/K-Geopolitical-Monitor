from kgeopolitical_monitor.historical_validation import (
    ForecastOutcome,
    HistoricalValidator,
)


def test_validation_accuracy():
    result = HistoricalValidator().evaluate(
        [ForecastOutcome("1", 0.8, True)]
    )
    assert result["accuracy"] == 1.0
