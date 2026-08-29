from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi.testclient import TestClient

from kgeopolitical_monitor.admin_dashboard import render_admin_dashboard
from kgeopolitical_monitor.backend_action_api import create_action_app
from kgeopolitical_monitor.forecast_semantics import (
    FORECAST_SEMANTICS_VERSION,
    forecast_semantic_contract,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.report_rendering import ReportRenderer
from kgeopolitical_monitor.reporting_environment import (
    FORECAST_SCENARIO,
    GLOBAL_GEOPOLITICAL_BRIEF,
    ReportBundle,
    ReportSection,
    ReportSnapshot,
)


NOW = datetime(2026, 8, 29, 18, 0, tzinfo=timezone.utc)
TOKEN = "e7-owner-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _seed_high_probability_forecast(runtime: OperationalMonitoringRuntime) -> None:
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title, verification_status,
                confidence, importance, independent_origin_count, source_class_count,
                origins_json
            ) VALUES (
                'claim-e7', 'analysis-e7', 'claim-key-e7', 'Weakly verified claim',
                'DETECTED', 0.31, 0.8, 1, 1, '["origin.example"]'
            )
            """
        )
        connection.execute(
            """
            INSERT INTO forecasts(
                forecast_id, target_key, question, horizon, evaluation_deadline,
                status, created_at, updated_at
            ) VALUES (?, ?, ?, 'short_term', ?, 'ACTIVE', ?, ?)
            """,
            (
                "forecast-e7",
                "target-e7",
                "Will the analytical scenario occur?",
                (NOW + timedelta(days=30)).isoformat(),
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO forecast_versions(
                forecast_version_id, forecast_id, version_number,
                input_snapshot_json, provenance_refs_json, assumptions_json,
                change_reason, created_at
            ) VALUES (?, ?, 1, '{}', '[]', '[]', ?, ?)
            """,
            (
                "forecast-version-e7",
                "forecast-e7",
                "E7 semantic isolation fixture",
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO forecast_scenario_versions(
                scenario_version_id, forecast_version_id, scenario_type, label,
                raw_probability, calibrated_probability, scenario_confidence,
                drivers_json, constraints_json, triggers_json, inhibitors_json,
                uncertainty_factors_json, invalidation_signals_json
            ) VALUES (
                'scenario-e7', 'forecast-version-e7', 'baseline', 'High probability',
                0.95, 0.98, 0.99, '[]', '[]', '[]', '[]', '[]', '[]'
            )
            """
        )


def _claim_truth(runtime: OperationalMonitoringRuntime):
    with sqlite3.connect(runtime.database_path) as connection:
        return connection.execute(
            """
            SELECT verification_status, confidence, independent_origin_count,
                   origins_json
            FROM live_analysis_claims WHERE claim_id = 'claim-e7'
            """
        ).fetchone()


def test_canonical_contract_separates_probability_confidence_and_verification():
    contract = forecast_semantic_contract()

    assert contract["version"] == FORECAST_SEMANTICS_VERSION
    fields = contract["fields"]
    assert set(fields) == {
        "raw_probability",
        "calibrated_probability",
        "scenario_confidence",
    }
    assert fields["raw_probability"]["is_factual_confidence"] is False
    assert fields["raw_probability"]["is_verification_confidence"] is False
    assert fields["calibrated_probability"]["is_factual_confidence"] is False
    assert fields["scenario_confidence"]["is_probability"] is False
    assert fields["scenario_confidence"]["is_verification_confidence"] is False
    assert any(
        "do not modify claim verification state" in item
        for item in contract["invariants"]
    )


def test_owner_api_exposes_explicit_forecast_semantics_without_truth_promotion(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    _seed_high_probability_forecast(runtime)
    before = _claim_truth(runtime)

    client = TestClient(create_action_app(runtime, owner_token=TOKEN))
    response = client.get("/v1/forecasts/active", headers=AUTH)

    assert response.status_code == 200
    payload = response.json()
    assert payload["forecast_semantics"]["version"] == FORECAST_SEMANTICS_VERSION
    assert len(payload["forecasts"]) == 1
    scenario = payload["forecasts"][0]["scenarios"][0]
    assert scenario["raw_probability"] == 0.95
    assert scenario["calibrated_probability"] == 0.98
    assert scenario["scenario_confidence"] == 0.99
    assert "probability" not in scenario
    assert "confidence" not in scenario
    assert _claim_truth(runtime) == before
    assert before[0] == "DETECTED"
    assert before[1] == 0.31
    assert before[2] == 1


def test_dashboard_renders_all_three_forecast_metrics_with_explicit_labels():
    snapshot = {
        "generated_at": NOW.isoformat(),
        "dashboard_contract_version": "1.0",
        "system": {
            "runtime_storage": "PROJECT_LOCAL_ONLY",
            "production_live": "NOT_OPERATIONAL",
            "system_uptime_instrumentation": "NOT_INSTRUMENTED",
            "state_summary": {"active_monitoring_watches": 0},
            "current_error_count": 0,
            "current_errors": [],
        },
        "watches": [],
        "sources": [],
        "coverage": [],
        "findings": [],
        "alerts": [],
        "forecasts": [
            {
                "forecast_id": "forecast-e7",
                "question": "Will the analytical scenario occur?",
                "horizon": "short_term",
                "status": "ACTIVE",
                "evaluation_deadline": (NOW + timedelta(days=30)).isoformat(),
                "version_number": 1,
                "scenarios": [
                    {
                        "label": "High probability",
                        "raw_probability": 0.95,
                        "calibrated_probability": 0.98,
                        "scenario_confidence": 0.99,
                    }
                ],
            }
        ],
        "collection_attempts": [],
    }

    html = render_admin_dashboard(snapshot)

    assert "Raw 95.0%" in html
    assert "Calibrated 98.0%" in html
    assert "Scenario confidence 99.0%" in html
    assert FORECAST_SEMANTICS_VERSION in html
    assert "not factual or verification confidence" in html
    assert "never strengthen verification state or evidence" in html


def test_report_renderer_adds_machine_and_markdown_forecast_semantics():
    snapshot = ReportSnapshot.create(
        GLOBAL_GEOPOLITICAL_BRIEF,
        "global:e7",
        "E7 forecast semantics",
        "Forecast metrics must remain analytical outputs.",
        NOW,
        created_at=NOW,
        generator_version="e7",
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "FORECAST",
        "Forecast",
        FORECAST_SCENARIO,
        {
            "raw_probability": 0.95,
            "calibrated_probability": 0.98,
            "scenario_confidence": 0.99,
        },
        "Forecast probabilities and scenario confidence are analytical outputs.",
        created_at=NOW,
    )
    bundle = ReportBundle(snapshot, (section,), ())

    structured = ReportRenderer.structured_bundle(bundle)
    semantics = structured["forecast_semantics"]
    assert semantics["version"] == FORECAST_SEMANTICS_VERSION
    assert set(semantics["fields"]) == {
        "raw_probability",
        "calibrated_probability",
        "scenario_confidence",
    }
    assert structured["sections"][0]["presentation_class"] == FORECAST_SCENARIO

    markdown = ReportRenderer.markdown_bundle(bundle)
    assert "## Forecast semantics" in markdown
    assert "Raw probability" in markdown
    assert "Calibrated probability" in markdown
    assert "Scenario confidence" in markdown
    assert "never modify verification state" in markdown
