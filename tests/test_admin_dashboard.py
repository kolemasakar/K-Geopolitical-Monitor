from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi.testclient import TestClient

from kgeopolitical_monitor.admin_dashboard_app import create_admin_dashboard_app
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
TOKEN = "dashboard-owner-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _runtime_with_dashboard_state(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")

    runtime.create_watch(
        "Due watch",
        "due query",
        60,
        watch_id="watch-due",
        created_at=NOW - timedelta(hours=2),
    )
    runtime.create_watch(
        "Running watch",
        "running query",
        60,
        watch_id="watch-running",
        created_at=NOW - timedelta(hours=2),
    )
    runtime.start_run(
        "watch-running",
        run_id="run-running",
        started_at=NOW - timedelta(minutes=5),
    )

    runtime.create_watch(
        "Failed watch",
        "failed query",
        60,
        watch_id="watch-failed",
        created_at=NOW - timedelta(hours=3),
    )
    failed_run = runtime.start_run(
        "watch-failed",
        run_id="run-failed",
        started_at=NOW - timedelta(hours=2),
    )
    runtime.fail_run(
        failed_run.run_id,
        "collector failure",
        completed_at=NOW - timedelta(hours=2) + timedelta(minutes=1),
    )

    runtime.create_watch(
        "Completed watch",
        "completed query",
        60,
        watch_id="watch-completed",
        created_at=NOW - timedelta(hours=2),
    )
    completed_run = runtime.start_run(
        "watch-completed",
        run_id="run-completed",
        started_at=NOW - timedelta(minutes=10),
    )
    runtime.complete_run(
        completed_run.run_id,
        result_count=1,
        completed_at=NOW - timedelta(minutes=9),
    )

    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executemany(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            [
                (
                    "source-a",
                    "<script>alert('x')</script>",
                    "Official sources",
                    "official",
                ),
                ("source-b", "Source B", "International media", "high"),
            ],
        )
        connection.execute(
            """
            INSERT INTO source_collection_runs(
                collection_id, watch_id, status, started_at, completed_at,
                item_count, source_success_count, source_failure_count, failures
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "collection-dashboard",
                "watch-completed",
                "COMPLETED",
                (NOW - timedelta(minutes=8)).isoformat(),
                (NOW - timedelta(minutes=7)).isoformat(),
                0,
                0,
                1,
                '["source-a"]',
            ),
        )
        connection.execute(
            """
            INSERT INTO source_collection_attempts(
                collection_id, source_id, source_name, source_class,
                status, item_count, error, attempted_at
            ) VALUES (?, ?, ?, ?, 'FAILED', 0, ?, ?)
            """,
            (
                "collection-dashboard",
                "source-a",
                "Source A",
                "Official sources",
                "source temporarily unavailable",
                (NOW - timedelta(minutes=7)).isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO source_reputation_history(
                assessment_id, source_id, assessment_version, status,
                reliability_rating, reason, evidence_refs_json,
                policy_name, policy_version, assessed_at, reviewed_at,
                review_due_at, supersedes_assessment_id,
                restoration_of_assessment_id, created_at
            ) VALUES (?, ?, 1, 'COMPROMISED', 'LOW', ?, '[]', ?, ?, ?, ?, NULL, NULL, NULL, ?)
            """,
            (
                "assessment-dashboard",
                "source-a",
                "Dashboard regression assessment",
                "KGM_SOURCE_REPUTATION",
                "1",
                NOW.isoformat(),
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO operational_findings(
                finding_id, run_id, watch_id, title, summary,
                importance, confidence, evidence_refs, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, '[]', ?, ?)
            """,
            (
                "finding-dashboard",
                "run-completed",
                "watch-completed",
                "<script>alert(1)</script>",
                "Persisted finding summary",
                0.9,
                0.7,
                "Persisted finding explanation",
                (NOW - timedelta(minutes=6)).isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO forecasts(
                forecast_id, target_key, question, horizon,
                evaluation_deadline, status, created_at, updated_at
            ) VALUES (?, ?, ?, 'short_term', ?, 'ACTIVE', ?, ?)
            """,
            (
                "forecast-dashboard",
                "target-dashboard",
                "Will the test condition occur?",
                (NOW + timedelta(days=7)).isoformat(),
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
                "forecast-version-dashboard",
                "forecast-dashboard",
                "Initial dashboard version",
                NOW.isoformat(),
            ),
        )
        connection.executemany(
            """
            INSERT INTO forecast_scenario_versions(
                scenario_version_id, forecast_version_id, scenario_type, label,
                raw_probability, calibrated_probability, scenario_confidence,
                drivers_json, constraints_json, triggers_json, inhibitors_json,
                uncertainty_factors_json, invalidation_signals_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', '[]', '[]')
            """,
            [
                (
                    "scenario-baseline-dashboard",
                    "forecast-version-dashboard",
                    "baseline",
                    "Baseline",
                    0.6,
                    0.6,
                    0.5,
                ),
                (
                    "scenario-negative-dashboard",
                    "forecast-version-dashboard",
                    "negative",
                    "Escalation",
                    0.4,
                    0.4,
                    0.4,
                ),
            ],
        )

    return runtime


def test_dashboard_is_owner_only_and_disables_interactive_docs(tmp_path):
    runtime = _runtime_with_dashboard_state(tmp_path)
    client = TestClient(create_admin_dashboard_app(runtime, owner_token=TOKEN))

    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404

    response = client.get("/admin/dashboard")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert client.get(
        "/admin/dashboard", headers={"Authorization": "Bearer wrong"}
    ).status_code == 401
    assert client.get("/admin/dashboard", headers=AUTH).status_code == 200
    assert client.get("/admin/dashboard.json", headers=AUTH).status_code == 200


def test_dashboard_json_projects_due_source_finding_and_forecast_state(tmp_path):
    runtime = _runtime_with_dashboard_state(tmp_path)
    client = TestClient(create_admin_dashboard_app(runtime, owner_token=TOKEN))

    payload = client.get("/admin/dashboard.json", headers=AUTH).json()
    assert payload["dashboard_contract_version"] == "1.0"
    assert payload["system"]["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert payload["system"]["production_live"] == "NOT_OPERATIONAL"
    assert payload["system"]["system_uptime_seconds"] is None
    assert payload["system"]["system_uptime_instrumentation"] == "NOT_INSTRUMENTED"

    watches = {item["watch_id"]: item for item in payload["watches"]}
    assert watches["watch-due"]["due"] is True
    assert watches["watch-due"]["state"] == "DUE"
    assert watches["watch-running"]["running"] is True
    assert watches["watch-running"]["state"] == "RUNNING"
    assert watches["watch-failed"]["failed"] is True
    assert watches["watch-failed"]["due"] is True
    assert watches["watch-failed"]["state"] == "FAILED_DUE"

    sources = {item["source_id"]: item for item in payload["sources"]}
    assert sources["source-a"]["source_status"] == "COMPROMISED"
    assert sources["source-a"]["reliability_rating"] == "LOW"
    assert sources["source-a"]["availability_state"] == "UNAVAILABLE"
    assert sources["source-b"]["availability_state"] == "UNKNOWN"

    assert payload["coverage"] == []
    assert payload["alerts"] == []
    assert payload["findings"][0]["finding_id"] == "finding-dashboard"
    assert payload["findings"][0]["verification_state"] is None
    assert payload["findings"][0]["verification_state_available"] is False

    forecast = payload["forecasts"][0]
    assert forecast["forecast_id"] == "forecast-dashboard"
    assert forecast["version_number"] == 1
    assert [item["calibrated_probability"] for item in forecast["scenarios"]] == [
        0.6,
        0.4,
    ]

    attempts = payload["collection_attempts"]
    assert attempts[0]["source_id"] == "source-a"
    assert attempts[0]["status"] == "FAILED"
    assert payload["system"]["current_error_count"] >= 2


def test_dashboard_html_escapes_persisted_text_and_sets_security_headers(tmp_path):
    runtime = _runtime_with_dashboard_state(tmp_path)
    client = TestClient(create_admin_dashboard_app(runtime, owner_token=TOKEN))

    response = client.get("/admin/dashboard", headers=AUTH)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "Coverage confidence measures assessment observability" in response.text
    assert "Forecast probability is analytical" in response.text


def test_dashboard_get_requests_do_not_mutate_project_database(tmp_path):
    runtime = _runtime_with_dashboard_state(tmp_path)
    client = TestClient(create_admin_dashboard_app(runtime, owner_token=TOKEN))

    def counts():
        with sqlite3.connect(runtime.database_path) as connection:
            return {
                "runs": connection.execute("SELECT COUNT(*) FROM monitoring_runs").fetchone()[0],
                "findings": connection.execute("SELECT COUNT(*) FROM operational_findings").fetchone()[0],
                "forecasts": connection.execute("SELECT COUNT(*) FROM forecasts").fetchone()[0],
                "versions": connection.execute("SELECT COUNT(*) FROM forecast_versions").fetchone()[0],
                "scenarios": connection.execute(
                    "SELECT COUNT(*) FROM forecast_scenario_versions"
                ).fetchone()[0],
                "reputation": connection.execute(
                    "SELECT COUNT(*) FROM source_reputation_history"
                ).fetchone()[0],
                "attempts": connection.execute(
                    "SELECT COUNT(*) FROM source_collection_attempts"
                ).fetchone()[0],
            }

    before = counts()
    assert client.get("/admin/dashboard.json", headers=AUTH).status_code == 200
    assert client.get("/admin/dashboard", headers=AUTH).status_code == 200
    assert counts() == before


def test_empty_dashboard_owner_token_fails_closed(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    try:
        create_admin_dashboard_app(runtime, owner_token="   ")
    except ValueError as exc:
        assert "owner_token" in str(exc)
    else:
        raise AssertionError("empty owner token must fail closed")
