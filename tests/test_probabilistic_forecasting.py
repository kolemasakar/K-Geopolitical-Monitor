from kgeopolitical_monitor.probabilistic_forecasting import (
    ForecastScenario,
    ProbabilisticForecastEngine,
    ScenarioType,
)


def test_forecast_probabilities_are_normalized():
    engine = ProbabilisticForecastEngine()
    result = engine.generate([
        ForecastScenario(ScenarioType.BASELINE, 0.6, [], []),
        ForecastScenario(ScenarioType.NEGATIVE, 0.4, [], []),
    ])

    assert result[0]["probability"] == 0.6
    assert result[1]["probability"] == 0.4
