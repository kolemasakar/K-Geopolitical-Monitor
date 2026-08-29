from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi.testclient import TestClient

from kgeopolitical_monitor.backend_action_api import create_action_app
from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_reputation import SourceReputationService
from kgeopolitical_monitor.strategic_alerts import StrategicAlertService


NOW = datetime(2026, 8, 29, 11, 0, tzinfo=timezone.utc)
TOKEN = "owner-test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


class StaticAdapter:
    def __init__(self, source_id, url):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources"
        self.reliability = "official"
        self.url = url

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id=f"item-{self.source_id}-{int(collected_at.timestamp())}",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Shared strategic event",
                summary="Shared strategic event summary",
                original_url=self.url,
                collected_at=collected_at,
                reliability=self.reliability,
            )
        ]


class FailingAdapter:
    def __init__(self, source_id):
        self.source_id = source_id
        self.source_name = source_id
        self.source_class = "Official sources"
        self.reliability = "official"

    def fetch(self, watch, collected_at):
        raise RuntimeError("source temporarily unavailable")


def _runtime_with_state(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Action API test",
        "shared strategic event",
        60,
        watch_id="watch-api",
        created_at=NOW,
    )

    collection = LiveSourceCollector(
        runtime,
        [
            StaticAdapter("source-a", "https://origin-a.example/story"),
            StaticAdapter("source-b", "https://origin-b.example/story"),
        ],
    ).collect("watch-api", NOW)
    analysis = LiveEndToEndProcessor(runtime).process_collection(
        collection.collection_id,
        processed_at=NOW,
    )

    alerts = StrategicAlertService(runtime)
    alerts.configure_watch(
        "watch-api",
        priority="HIGH",
        minimum_importance=0.5,
        minimum_confidence=0.0,
        minimum_verification_rank=1,
        configured_at=NOW,
    )
    alert = alerts.evaluate_finding(
        analysis.findings[0].finding_id,
        evaluated_at=NOW,
    )
    assert alert is not None

    SourceReputationService(runtime).record_assessment(
        "source-a",
        status="COMPROMISED",
        reliability_rating="LOW",
        reason="Documented source-reputation test state",
        evidence_refs=("review:api-test",),
        policy_name="KGM_SOURCE_REPUTATION",
        policy_version="1",
        assessed_at=NOW,
    )

    LiveSourceCollector(runtime, [FailingAdapter("source-a")]).collect(
        "watch-api",
        NOW + timedelta(minutes=1),
    )

    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO operational_coverage_contracts(
                coverage_contract_id, scope_key, name, watch_id,
                assessment_window_seconds, freshness_requirement_seconds,
                active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                "coverage-api",
                "GLOBAL",
                "API coverage",
                "watch-api",
                3600,
                900,
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO operational_coverage_requirements(
                requirement_id, coverage_contract_id, dimension,
                requirement_key, required, parameters_json, created_at
            ) VALUES (?, ?, 'SOURCE_ID', ?, 1, '{}', ?)
            """,
            ("requirement-api", "coverage-api", "source-b", NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO operational_coverage_snapshots(
                coverage_snapshot_id, coverage_contract_id, assessed_at,
                window_start, window_end, required_count, satisfied_count,
                gap_count, unavailable_count, stale_count, unknown_count,
                unmeasured_count, coverage_ratio, coverage_confidence,
                limitations_json, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, 1, 0, 0, 0, 0, 0, 1.0, 1.0, '[]', ?)
            """,
            (
                "snapshot-api",
                "coverage-api",
                NOW.isoformat(),
                (NOW - timedelta(hours=1)).isoformat(),
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO operational_coverage_requirement_results(
                coverage_snapshot_id, requirement_id, status,
                evidence_refs_json, explanation, measured_at
            ) VALUES (?, ?, 'SATISFIED', '[]', ?, ?)
            """,
            (
                "snapshot-api",
                "requirement-api",
                "source-b observed",
                NOW.isoformat(),
            ),
        )

    return runtime, alert


def test_action_api_requires_owner_auth_and_exposes_openapi(tmp_path):
    runtime, _ = _runtime_with_state(tmp_path)
    client = TestClient(create_action_app(runtime, owner_token=TOKEN))

    assert client.get("/health").status_code == 200
    assert client.get("/v1/alerts").status_code == 401
    assert client.get(
        "/v1/alerts", headers={"Authorization": "Bearer wrong"}
    ).status_code == 401
    assert client.get("/v1/alerts", headers=AUTH).status_code == 200

    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "K-Geopolitical Monitor Owner Action API"
    operation_ids = {
        operation["operationId"]
        for path in schema["paths"].values()
        for operation in path.values()
        if isinstance(operation, dict) and "operationId" in operation
    }
    assert {
        "getPersistedStateSummary",
        "getRecentAlerts",
        "getAlert",
        "getActiveMonitoringWatches",
        "getMonitoringRuns",
        "getSourceCollectionAttempts",
        "getDegradedSources",
        "getLatestCoverage",
    }.issubset(operation_ids)


def test_recent_alerts_return_persisted_verification_and_importance(tmp_path):
    runtime, alert = _runtime_with_state(tmp_path)
    client = TestClient(create_action_app(runtime, owner_token=TOKEN))

    response = client.get("/v1/alerts?limit=10", headers=AUTH)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    item = items[0]
    assert item["alert_id"] == alert.alert_id
    assert item["event"] == "Shared strategic event"
    assert item["verification_state"] == "PARTLY_VERIFIED"
    assert item["verification_state_available"] is True
    assert item["importance_score"] == 0.5
    assert item["priority"] == "HIGH"

    detail = client.get(f"/v1/alerts/{alert.alert_id}", headers=AUTH)
    assert detail.status_code == 200
    assert detail.json()["verification_state"] == "PARTLY_VERIFIED"
    assert client.get("/v1/alerts/missing", headers=AUTH).status_code == 404


def test_action_api_exposes_watches_runs_attempts_coverage_and_degraded_state(tmp_path):
    runtime, _ = _runtime_with_state(tmp_path)
    client = TestClient(create_action_app(runtime, owner_token=TOKEN))

    watches = client.get("/v1/watches", headers=AUTH).json()
    assert [item["watch_id"] for item in watches] == ["watch-api"]

    runs = client.get("/v1/monitoring-runs", headers=AUTH).json()
    assert runs
    assert all("run_id" in item and "status" in item for item in runs)

    attempts = client.get(
        "/v1/source-collection-attempts", headers=AUTH
    ).json()
    assert any(
        item["source_id"] == "source-a" and item["status"] == "FAILED"
        for item in attempts
    )

    degraded = client.get("/v1/sources/degraded", headers=AUTH).json()
    source_a = next(item for item in degraded if item["source_id"] == "source-a")
    assert source_a["availability_state"] == "UNAVAILABLE"
    assert source_a["source_status"] == "COMPROMISED"
    assert source_a["reliability_rating"] == "LOW"

    coverage = client.get("/v1/coverage/latest", headers=AUTH).json()
    assert coverage == [
        {
            "coverage_snapshot_id": "snapshot-api",
            "coverage_contract_id": "coverage-api",
            "scope_key": "GLOBAL",
            "contract_name": "API coverage",
            "watch_id": "watch-api",
            "assessed_at": NOW.isoformat(),
            "window_start": (NOW - timedelta(hours=1)).isoformat(),
            "window_end": NOW.isoformat(),
            "required_count": 1,
            "satisfied_count": 1,
            "gap_count": 0,
            "unavailable_count": 0,
            "stale_count": 0,
            "unknown_count": 0,
            "unmeasured_count": 0,
            "coverage_ratio": 1.0,
            "coverage_confidence": 1.0,
            "limitations": [],
        }
    ]


def test_unattended_cycle_timestamp_fails_closed_when_not_instrumented(tmp_path):
    runtime, _ = _runtime_with_state(tmp_path)
    client = TestClient(create_action_app(runtime, owner_token=TOKEN))

    summary = client.get("/v1/state/summary", headers=AUTH).json()
    assert summary["active_monitoring_watches"] == 1
    assert summary["last_monitoring_cycle"] is not None
    assert summary["last_unattended_cycle_at"] is None
    assert summary["unattended_cycle_instrumentation"] == "NOT_INSTRUMENTED"
    assert "do not distinguish unattended" in summary["note"]


def test_action_api_get_requests_do_not_mutate_project_database(tmp_path):
    runtime, _ = _runtime_with_state(tmp_path)
    client = TestClient(create_action_app(runtime, owner_token=TOKEN))

    with sqlite3.connect(runtime.database_path) as connection:
        before = {
            "alerts": connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0],
            "events": connection.execute("SELECT COUNT(*) FROM strategic_alert_events").fetchone()[0],
            "runs": connection.execute("SELECT COUNT(*) FROM monitoring_runs").fetchone()[0],
            "assessments": connection.execute(
                "SELECT COUNT(*) FROM source_reputation_history"
            ).fetchone()[0],
        }

    for endpoint in (
        "/v1/state/summary",
        "/v1/alerts",
        "/v1/watches",
        "/v1/monitoring-runs",
        "/v1/source-collection-attempts",
        "/v1/sources/degraded",
        "/v1/coverage/latest",
    ):
        assert client.get(endpoint, headers=AUTH).status_code == 200

    with sqlite3.connect(runtime.database_path) as connection:
        after = {
            "alerts": connection.execute("SELECT COUNT(*) FROM strategic_alerts").fetchone()[0],
            "events": connection.execute("SELECT COUNT(*) FROM strategic_alert_events").fetchone()[0],
            "runs": connection.execute("SELECT COUNT(*) FROM monitoring_runs").fetchone()[0],
            "assessments": connection.execute(
                "SELECT COUNT(*) FROM source_reputation_history"
            ).fetchone()[0],
        }

    assert after == before


def test_empty_owner_token_is_rejected(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    try:
        create_action_app(runtime, owner_token="   ")
    except ValueError as exc:
        assert "owner_token" in str(exc)
    else:
        raise AssertionError("empty owner token must fail closed")
