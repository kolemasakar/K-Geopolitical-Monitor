"""Owner/admin-only read-only dashboard over canonical persisted runtime state."""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .admin_dashboard import DASHBOARD_SECURITY_HEADERS, render_admin_dashboard
from .backend_action_api import BackendStateReader
from .operational_monitoring import OperationalMonitoringRuntime


DASHBOARD_API_VERSION = "1.0.0"
DASHBOARD_CONTRACT_VERSION = "1.0"


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("dashboard timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


class AdminDashboardReader(BackendStateReader):
    """Read-only dashboard projection using the existing E3 persisted-state reader."""

    def watch_states(self, *, now: datetime | None = None) -> list[dict[str, object]]:
        current = _normalize_time(now or datetime.now(timezone.utc))
        with self._connect() as connection:
            rows = connection.execute(
                """
                WITH ranked_runs AS (
                    SELECT run_id, watch_id, status, started_at, completed_at,
                           result_count, error, retry_count, recovered,
                           ROW_NUMBER() OVER (
                               PARTITION BY watch_id
                               ORDER BY started_at DESC, run_id DESC
                           ) AS rn
                    FROM monitoring_runs
                )
                SELECT w.watch_id, w.name, w.query, w.cadence_minutes,
                       w.created_at, r.run_id, r.status, r.started_at,
                       r.completed_at, r.result_count, r.error,
                       r.retry_count, r.recovered
                FROM monitoring_watches w
                LEFT JOIN ranked_runs r
                  ON r.watch_id = w.watch_id AND r.rn = 1
                WHERE w.enabled = 1
                ORDER BY w.watch_id
                """
            ).fetchall()

        result: list[dict[str, object]] = []
        for row in rows:
            cadence_minutes = int(row[3])
            latest_status = row[6]
            latest_started_at = row[7]
            running = latest_status == "RUNNING"
            failed = latest_status == "FAILED"

            if latest_status is None:
                due = True
                next_due_at = _normalize_time(datetime.fromisoformat(row[4]))
                state = "DUE"
            elif running:
                due = False
                next_due_at = None
                state = "RUNNING"
            else:
                started_at = _normalize_time(datetime.fromisoformat(latest_started_at))
                next_due_at = started_at + timedelta(minutes=cadence_minutes)
                due = current >= next_due_at
                if failed:
                    state = "FAILED_DUE" if due else "FAILED_WAITING"
                else:
                    state = "DUE" if due else "WAITING"

            result.append(
                {
                    "watch_id": row[0],
                    "name": row[1],
                    "query": row[2],
                    "cadence_minutes": cadence_minutes,
                    "created_at": row[4],
                    "state": state,
                    "due": due,
                    "running": running,
                    "failed": failed,
                    "next_due_at": None
                    if next_due_at is None
                    else next_due_at.isoformat(),
                    "latest_run_id": row[5],
                    "latest_run_status": latest_status,
                    "latest_run_started_at": latest_started_at,
                    "latest_run_completed_at": row[8],
                    "latest_result_count": None
                    if row[9] is None
                    else int(row[9]),
                    "latest_error": row[10],
                    "latest_retry_count": None
                    if row[11] is None
                    else int(row[11]),
                    "latest_recovered": None
                    if row[12] is None
                    else bool(row[12]),
                }
            )
        return result

    def source_states(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                WITH source_ids AS (
                    SELECT id AS source_id FROM sources
                    UNION
                    SELECT source_id FROM source_collection_attempts
                    UNION
                    SELECT source_id FROM source_reputation_history
                ),
                ranked_attempts AS (
                    SELECT source_id, source_name, source_class, status,
                           item_count, error, attempted_at,
                           ROW_NUMBER() OVER (
                               PARTITION BY source_id
                               ORDER BY attempted_at DESC, collection_id DESC
                           ) AS rn
                    FROM source_collection_attempts
                ),
                ranked_reputation AS (
                    SELECT source_id, status, reliability_rating,
                           assessment_id, assessed_at,
                           ROW_NUMBER() OVER (
                               PARTITION BY source_id
                               ORDER BY assessment_version DESC, assessed_at DESC
                           ) AS rn
                    FROM source_reputation_history
                )
                SELECT ids.source_id, s.name, s.source_class, s.reliability,
                       a.source_name, a.source_class, a.status, a.item_count,
                       a.error, a.attempted_at, r.status, r.reliability_rating,
                       r.assessment_id, r.assessed_at
                FROM source_ids ids
                LEFT JOIN sources s ON s.id = ids.source_id
                LEFT JOIN ranked_attempts a
                  ON a.source_id = ids.source_id AND a.rn = 1
                LEFT JOIN ranked_reputation r
                  ON r.source_id = ids.source_id AND r.rn = 1
                ORDER BY ids.source_id
                """
            ).fetchall()

        degraded = {
            str(item["source_id"]): item
            for item in self.degraded_sources()
            if item.get("source_id") is not None
        }
        result: list[dict[str, object]] = []
        for row in rows:
            source_id = str(row[0])
            latest_attempt_status = row[6]
            if latest_attempt_status == "SUCCESS":
                availability = "AVAILABLE"
            elif latest_attempt_status == "FAILED":
                availability = "UNAVAILABLE"
            else:
                availability = "UNKNOWN"

            degraded_item = degraded.get(source_id)
            availability_explanation = None
            if degraded_item is not None:
                availability = str(degraded_item.get("availability_state") or availability)
                availability_explanation = degraded_item.get("explanation")

            result.append(
                {
                    "source_id": source_id,
                    "source_name": row[1] or row[4] or source_id,
                    "source_class": row[2] or row[5],
                    "legacy_reliability": row[3],
                    "source_status": row[10],
                    "reliability_rating": row[11],
                    "reputation_assessment_id": row[12],
                    "reputation_assessed_at": row[13],
                    "availability_state": availability,
                    "availability_explanation": availability_explanation,
                    "last_attempt_status": latest_attempt_status,
                    "last_attempt_item_count": None
                    if row[7] is None
                    else int(row[7]),
                    "last_attempt_error": row[8],
                    "last_attempt_at": row[9],
                }
            )
        return result

    def recent_findings(self, limit: int = 20) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT finding_id, run_id, watch_id, title, summary,
                       importance, confidence, evidence_refs, explanation, created_at
                FROM operational_findings
                ORDER BY created_at DESC, importance DESC, finding_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            result: list[dict[str, object]] = []
            for row in rows:
                verification = self._verification_state(connection, row[7])
                result.append(
                    {
                        "finding_id": row[0],
                        "run_id": row[1],
                        "watch_id": row[2],
                        "title": row[3],
                        "summary": row[4],
                        "importance_score": float(row[5]),
                        "finding_confidence": float(row[6]),
                        "verification_state": verification,
                        "verification_state_available": verification is not None,
                        "explanation": row[8],
                        "created_at": row[9],
                    }
                )
            return result

    def active_forecasts(self, limit: int = 20) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                WITH latest_versions AS (
                    SELECT forecast_id, MAX(version_number) AS version_number
                    FROM forecast_versions
                    GROUP BY forecast_id
                )
                SELECT f.forecast_id, f.target_key, f.question, f.horizon,
                       f.evaluation_deadline, f.status, f.created_at, f.updated_at,
                       v.forecast_version_id, v.version_number, v.created_at
                FROM forecasts f
                LEFT JOIN latest_versions latest
                  ON latest.forecast_id = f.forecast_id
                LEFT JOIN forecast_versions v
                  ON v.forecast_id = f.forecast_id
                 AND v.version_number = latest.version_number
                WHERE f.status = 'ACTIVE'
                ORDER BY f.evaluation_deadline, f.forecast_id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            version_ids = [str(row[8]) for row in rows if row[8] is not None]
            scenarios_by_version: dict[str, list[dict[str, object]]] = {
                version_id: [] for version_id in version_ids
            }
            if version_ids:
                placeholders = ",".join("?" for _ in version_ids)
                scenario_rows = connection.execute(
                    f"""
                    SELECT forecast_version_id, scenario_version_id,
                           scenario_type, label, raw_probability,
                           calibrated_probability, scenario_confidence
                    FROM forecast_scenario_versions
                    WHERE forecast_version_id IN ({placeholders})
                    ORDER BY forecast_version_id, scenario_type, label
                    """,
                    version_ids,
                ).fetchall()
                for scenario in scenario_rows:
                    scenarios_by_version[str(scenario[0])].append(
                        {
                            "scenario_version_id": scenario[1],
                            "scenario_type": scenario[2],
                            "label": scenario[3],
                            "raw_probability": float(scenario[4]),
                            "calibrated_probability": float(scenario[5]),
                            "scenario_confidence": float(scenario[6]),
                        }
                    )

        return [
            {
                "forecast_id": row[0],
                "target_key": row[1],
                "question": row[2],
                "horizon": row[3],
                "evaluation_deadline": row[4],
                "status": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "forecast_version_id": row[8],
                "version_number": None if row[9] is None else int(row[9]),
                "version_created_at": row[10],
                "scenarios": []
                if row[8] is None
                else scenarios_by_version.get(str(row[8]), []),
            }
            for row in rows
        ]

    def dashboard_snapshot(
        self,
        *,
        now: datetime | None = None,
        finding_limit: int = 20,
        alert_limit: int = 20,
        forecast_limit: int = 20,
        attempt_limit: int = 50,
    ) -> dict[str, object]:
        generated_at = _normalize_time(now or datetime.now(timezone.utc))
        watches = self.watch_states(now=generated_at)
        sources = self.source_states()
        summary = self.state_summary()

        errors: list[dict[str, object]] = []
        for watch in watches:
            if watch.get("failed"):
                errors.append(
                    {
                        "kind": "WATCH_RUN",
                        "identifier": watch.get("watch_id"),
                        "status": watch.get("latest_run_status"),
                        "error": watch.get("latest_error"),
                        "observed_at": watch.get("latest_run_completed_at")
                        or watch.get("latest_run_started_at"),
                    }
                )
        for source in sources:
            if source.get("availability_state") in {"UNAVAILABLE", "STALE"}:
                errors.append(
                    {
                        "kind": "SOURCE",
                        "identifier": source.get("source_id"),
                        "status": source.get("availability_state"),
                        "error": source.get("last_attempt_error")
                        or source.get("availability_explanation"),
                        "observed_at": source.get("last_attempt_at")
                        or source.get("reputation_assessed_at"),
                    }
                )

        return {
            "dashboard_contract_version": DASHBOARD_CONTRACT_VERSION,
            "generated_at": generated_at.isoformat(),
            "system": {
                "runtime_storage": "PROJECT_LOCAL_ONLY",
                "production_live": "NOT_OPERATIONAL",
                "system_uptime_seconds": None,
                "system_uptime_instrumentation": "NOT_INSTRUMENTED",
                "state_summary": summary,
                "current_error_count": len(errors),
                "current_errors": errors,
            },
            "watches": watches,
            "sources": sources,
            "coverage": self.latest_coverage(),
            "findings": self.recent_findings(finding_limit),
            "alerts": self.recent_alerts(alert_limit),
            "forecasts": self.active_forecasts(forecast_limit),
            "collection_attempts": self.source_collection_attempts(attempt_limit),
        }


def create_admin_dashboard_app(
    runtime: OperationalMonitoringRuntime,
    *,
    owner_token: str,
) -> FastAPI:
    """Create a protected read-only dashboard app over project-local persisted state."""

    token = owner_token.strip()
    if not token:
        raise ValueError("owner_token must not be empty")

    reader = AdminDashboardReader(runtime)
    bearer = HTTPBearer(auto_error=False)
    app = FastAPI(
        title="K-Geopolitical Monitor Admin Read-Only Dashboard",
        version=DASHBOARD_API_VERSION,
        description=(
            "Owner/admin-only read-only dashboard over persisted K-Geopolitical "
            "Monitor state. No public-web substitution and no state mutation."
        ),
        docs_url=None,
        redoc_url=None,
    )

    def authorize(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer),
        ],
    ) -> str:
        if credentials is None or credentials.scheme.casefold() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not secrets.compare_digest(credentials.credentials, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.credentials

    OwnerAuth = Annotated[str, Depends(authorize)]

    @app.get("/health", operation_id="getAdminDashboardHealth")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "dashboard_version": DASHBOARD_API_VERSION,
            "runtime_storage": "PROJECT_LOCAL_ONLY",
            "production_live": "NOT_OPERATIONAL",
        }

    @app.get("/admin/dashboard.json", operation_id="getAdminDashboardData")
    def dashboard_data(_: OwnerAuth) -> JSONResponse:
        return JSONResponse(
            content=reader.dashboard_snapshot(),
            headers=DASHBOARD_SECURITY_HEADERS,
        )

    @app.get("/admin/dashboard", operation_id="getAdminDashboard")
    def dashboard(_: OwnerAuth) -> HTMLResponse:
        snapshot = reader.dashboard_snapshot()
        return HTMLResponse(
            content=render_admin_dashboard(snapshot),
            headers=DASHBOARD_SECURITY_HEADERS,
        )

    return app
