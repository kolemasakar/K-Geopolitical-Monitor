"""Owner-only read-only backend API foundation for future GPT Actions.

The API exposes persisted K-Geopolitical Monitor state. It never substitutes public
web research for unavailable backend state and opens SQLite in read-only mode.
"""

from pathlib import Path
import json
import secrets
import sqlite3
from typing import Annotated
from urllib.parse import quote

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .forecast_semantics import forecast_semantic_contract
from .operational_monitoring import OperationalMonitoringRuntime


API_VERSION = "1.1.0"
UNATTENDED_CYCLE_NOT_INSTRUMENTED = "NOT_INSTRUMENTED"


def _read_only_database_uri(path: Path) -> str:
    normalized = str(path.resolve()).replace("\\", "/")
    return f"file:{quote(normalized, safe='/:')}?mode=ro"


class BackendStateReader:
    """Explicit read-only query facade over persisted project-local runtime state."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path.resolve()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            _read_only_database_uri(self.database_path),
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    @staticmethod
    def _json_tuple(value: str | None) -> tuple[str, ...]:
        if not value:
            return ()
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            return ()
        return tuple(str(item) for item in parsed)

    def _verification_state(
        self,
        connection: sqlite3.Connection,
        evidence_refs_json: str | None,
    ) -> str | None:
        claim_ids = [
            ref.split(":", 1)[1]
            for ref in self._json_tuple(evidence_refs_json)
            if ref.startswith("claim:") and len(ref.split(":", 1)) == 2
        ]
        if len(claim_ids) != 1:
            return None
        row = connection.execute(
            "SELECT verification_status FROM live_analysis_claims WHERE claim_id = ?",
            (claim_ids[0],),
        ).fetchone()
        return None if row is None else str(row[0])

    def recent_alerts(self, limit: int = 10) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT a.alert_id, a.watch_id, a.finding_id, a.priority, a.status,
                       a.first_triggered_at, a.last_updated_at, a.explanation,
                       a.invalidation_reason, f.title, f.summary, f.importance,
                       f.confidence, f.evidence_refs
                FROM strategic_alerts a
                JOIN operational_findings f ON f.finding_id = a.finding_id
                ORDER BY a.last_updated_at DESC, a.alert_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            result: list[dict[str, object]] = []
            for row in rows:
                verification = self._verification_state(connection, row[13])
                result.append(
                    {
                        "alert_id": row[0],
                        "watch_id": row[1],
                        "finding_id": row[2],
                        "priority": row[3],
                        "status": row[4],
                        "first_triggered_at": row[5],
                        "last_updated_at": row[6],
                        "event": row[9],
                        "summary": row[10],
                        "importance_score": float(row[11]),
                        "finding_confidence": float(row[12]),
                        "verification_state": verification,
                        "verification_state_available": verification is not None,
                    }
                )
            return result

    def alert_detail(self, alert_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT a.alert_id, a.watch_id, a.finding_id, a.trigger_type,
                       a.dedup_key, a.priority, a.status, a.first_triggered_at,
                       a.last_updated_at, a.evidence_refs, a.explanation,
                       a.invalidation_reason, f.title, f.summary, f.importance,
                       f.confidence, f.evidence_refs
                FROM strategic_alerts a
                JOIN operational_findings f ON f.finding_id = a.finding_id
                WHERE a.alert_id = ?
                """,
                (alert_id,),
            ).fetchone()
            if row is None:
                return None
            verification = self._verification_state(connection, row[16])
            return {
                "alert_id": row[0],
                "watch_id": row[1],
                "finding_id": row[2],
                "trigger_type": row[3],
                "dedup_key": row[4],
                "priority": row[5],
                "status": row[6],
                "first_triggered_at": row[7],
                "last_updated_at": row[8],
                "evidence_refs": self._json_tuple(row[9]),
                "explanation": row[10],
                "invalidation_reason": row[11],
                "event": row[12],
                "summary": row[13],
                "importance_score": float(row[14]),
                "finding_confidence": float(row[15]),
                "verification_state": verification,
                "verification_state_available": verification is not None,
            }

    def active_watches(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT watch_id, name, query, cadence_minutes, created_at
                FROM monitoring_watches
                WHERE enabled = 1
                ORDER BY watch_id
                """
            ).fetchall()
        return [
            {
                "watch_id": row[0],
                "name": row[1],
                "query": row[2],
                "cadence_minutes": int(row[3]),
                "created_at": row[4],
            }
            for row in rows
        ]

    def monitoring_runs(self, limit: int = 100) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT run_id, watch_id, status, started_at, completed_at,
                       result_count, error, retry_count, recovered
                FROM monitoring_runs
                ORDER BY started_at DESC, run_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "run_id": row[0],
                "watch_id": row[1],
                "status": row[2],
                "started_at": row[3],
                "completed_at": row[4],
                "result_count": int(row[5]),
                "error": row[6],
                "retry_count": int(row[7]),
                "recovered": bool(row[8]),
            }
            for row in rows
        ]

    def source_collection_attempts(self, limit: int = 100) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT collection_id, source_id, source_name, source_class,
                       status, item_count, error, attempted_at
                FROM source_collection_attempts
                ORDER BY attempted_at DESC, collection_id DESC, source_id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "collection_id": row[0],
                "source_id": row[1],
                "source_name": row[2],
                "source_class": row[3],
                "status": row[4],
                "item_count": int(row[5]),
                "error": row[6],
                "attempted_at": row[7],
            }
            for row in rows
        ]

    def degraded_sources(self) -> list[dict[str, object]]:
        degraded: dict[str, dict[str, object]] = {}
        with self._connect() as connection:
            attempt_rows = connection.execute(
                """
                WITH ranked AS (
                    SELECT collection_id, source_id, source_name, source_class,
                           status, item_count, error, attempted_at,
                           ROW_NUMBER() OVER (
                               PARTITION BY source_id
                               ORDER BY attempted_at DESC, collection_id DESC
                           ) AS rn
                    FROM source_collection_attempts
                )
                SELECT collection_id, source_id, source_name, source_class,
                       status, item_count, error, attempted_at
                FROM ranked
                WHERE rn = 1 AND status = 'FAILED'
                ORDER BY source_id
                """
            ).fetchall()
            for row in attempt_rows:
                degraded[str(row[1])] = {
                    "source_id": row[1],
                    "source_name": row[2],
                    "source_class": row[3],
                    "availability_state": "UNAVAILABLE",
                    "state_origin": "LATEST_COLLECTION_ATTEMPT",
                    "observed_at": row[7],
                    "error": row[6],
                    "collection_id": row[0],
                }

            coverage_rows = connection.execute(
                """
                WITH latest_snapshot AS (
                    SELECT coverage_contract_id, MAX(assessed_at) AS assessed_at
                    FROM operational_coverage_snapshots
                    GROUP BY coverage_contract_id
                )
                SELECT r.requirement_key, rr.status, rr.explanation,
                       rr.measured_at, s.coverage_snapshot_id,
                       s.coverage_contract_id
                FROM operational_coverage_requirement_results rr
                JOIN operational_coverage_requirements r
                  ON r.requirement_id = rr.requirement_id
                JOIN operational_coverage_snapshots s
                  ON s.coverage_snapshot_id = rr.coverage_snapshot_id
                JOIN latest_snapshot latest
                  ON latest.coverage_contract_id = s.coverage_contract_id
                 AND latest.assessed_at = s.assessed_at
                WHERE r.dimension IN ('SOURCE_ID', 'SOURCE_AVAILABILITY')
                  AND rr.status IN ('UNAVAILABLE', 'STALE')
                ORDER BY r.requirement_key, rr.measured_at DESC
                """
            ).fetchall()
            for row in coverage_rows:
                source_id = str(row[0])
                existing = degraded.get(source_id)
                if existing is None or row[1] == "STALE":
                    degraded[source_id] = {
                        "source_id": source_id,
                        "source_name": None,
                        "source_class": None,
                        "availability_state": row[1],
                        "state_origin": "LATEST_COVERAGE_SNAPSHOT",
                        "observed_at": row[3],
                        "error": None,
                        "explanation": row[2],
                        "coverage_snapshot_id": row[4],
                        "coverage_contract_id": row[5],
                    }

            reputation_rows = connection.execute(
                """
                SELECT h.source_id, h.status, h.reliability_rating,
                       h.assessment_id, h.assessed_at
                FROM source_reputation_history h
                JOIN (
                    SELECT source_id, MAX(assessment_version) AS max_version
                    FROM source_reputation_history
                    GROUP BY source_id
                ) latest
                  ON latest.source_id = h.source_id
                 AND latest.max_version = h.assessment_version
                """
            ).fetchall()
            reputation_by_source = {
                str(row[0]): {
                    "source_status": row[1],
                    "reliability_rating": row[2],
                    "reputation_assessment_id": row[3],
                    "reputation_assessed_at": row[4],
                }
                for row in reputation_rows
            }

        for source_id, item in degraded.items():
            item.update(
                reputation_by_source.get(
                    source_id,
                    {
                        "source_status": None,
                        "reliability_rating": None,
                        "reputation_assessment_id": None,
                        "reputation_assessed_at": None,
                    },
                )
            )
        return [degraded[key] for key in sorted(degraded)]

    def latest_coverage(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                WITH latest AS (
                    SELECT coverage_contract_id, MAX(assessed_at) AS assessed_at
                    FROM operational_coverage_snapshots
                    GROUP BY coverage_contract_id
                )
                SELECT s.coverage_snapshot_id, s.coverage_contract_id,
                       c.scope_key, c.name, c.watch_id, s.assessed_at,
                       s.window_start, s.window_end, s.required_count,
                       s.satisfied_count, s.gap_count, s.unavailable_count,
                       s.stale_count, s.unknown_count, s.unmeasured_count,
                       s.coverage_ratio, s.coverage_confidence,
                       s.limitations_json
                FROM operational_coverage_snapshots s
                JOIN latest l
                  ON l.coverage_contract_id = s.coverage_contract_id
                 AND l.assessed_at = s.assessed_at
                JOIN operational_coverage_contracts c
                  ON c.coverage_contract_id = s.coverage_contract_id
                ORDER BY s.coverage_contract_id
                """
            ).fetchall()
        return [
            {
                "coverage_snapshot_id": row[0],
                "coverage_contract_id": row[1],
                "scope_key": row[2],
                "contract_name": row[3],
                "watch_id": row[4],
                "assessed_at": row[5],
                "window_start": row[6],
                "window_end": row[7],
                "required_count": int(row[8]),
                "satisfied_count": int(row[9]),
                "gap_count": int(row[10]),
                "unavailable_count": int(row[11]),
                "stale_count": int(row[12]),
                "unknown_count": int(row[13]),
                "unmeasured_count": int(row[14]),
                "coverage_ratio": float(row[15]),
                "coverage_confidence": float(row[16]),
                "limitations": list(self._json_tuple(row[17])),
            }
            for row in rows
        ]

    def active_forecasts(self, limit: int = 20) -> dict[str, object]:
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

        forecasts = [
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
        return {
            "forecast_semantics": forecast_semantic_contract(),
            "forecasts": forecasts,
        }

    def state_summary(self) -> dict[str, object]:
        with self._connect() as connection:
            active_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM monitoring_watches WHERE enabled = 1"
                ).fetchone()[0]
            )
            last_run = connection.execute(
                """
                SELECT run_id, watch_id, status, started_at, completed_at
                FROM monitoring_runs
                ORDER BY COALESCE(completed_at, started_at) DESC, run_id DESC
                LIMIT 1
                """
            ).fetchone()
        return {
            "active_monitoring_watches": active_count,
            "last_monitoring_cycle": None
            if last_run is None
            else {
                "run_id": last_run[0],
                "watch_id": last_run[1],
                "status": last_run[2],
                "started_at": last_run[3],
                "completed_at": last_run[4],
            },
            "last_unattended_cycle_at": None,
            "unattended_cycle_instrumentation": UNATTENDED_CYCLE_NOT_INSTRUMENTED,
            "note": (
                "Current persisted monitoring_runs do not distinguish unattended "
                "execution provenance. The API returns null rather than inferring it."
            ),
        }


def create_action_app(
    runtime: OperationalMonitoringRuntime,
    *,
    owner_token: str,
) -> FastAPI:
    """Create an owner-only API app. No token is stored in repository state."""

    token = owner_token.strip()
    if not token:
        raise ValueError("owner_token must not be empty")

    reader = BackendStateReader(runtime)
    bearer = HTTPBearer(auto_error=False)
    app = FastAPI(
        title="K-Geopolitical Monitor Owner Action API",
        version=API_VERSION,
        description=(
            "Read-only owner API for persisted K-Geopolitical Monitor runtime state. "
            "Public web research is not substituted for unavailable backend state."
        ),
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

    @app.get("/health", operation_id="getHealth")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "api_version": API_VERSION,
            "runtime_storage": "PROJECT_LOCAL_ONLY",
            "production_live": "NOT_OPERATIONAL",
        }

    @app.get("/v1/state/summary", operation_id="getPersistedStateSummary")
    def get_state_summary(_: OwnerAuth) -> dict[str, object]:
        return reader.state_summary()

    @app.get("/v1/alerts", operation_id="getRecentAlerts")
    def get_recent_alerts(
        _: OwnerAuth,
        limit: int = Query(default=10, ge=1, le=100),
    ) -> list[dict[str, object]]:
        return reader.recent_alerts(limit)

    @app.get("/v1/alerts/{alert_id}", operation_id="getAlert")
    def get_alert(alert_id: str, _: OwnerAuth) -> dict[str, object]:
        item = reader.alert_detail(alert_id)
        if item is None:
            raise HTTPException(status_code=404, detail="alert not found")
        return item

    @app.get("/v1/watches", operation_id="getActiveMonitoringWatches")
    def get_active_watches(_: OwnerAuth) -> list[dict[str, object]]:
        return reader.active_watches()

    @app.get("/v1/monitoring-runs", operation_id="getMonitoringRuns")
    def get_monitoring_runs(
        _: OwnerAuth,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        return reader.monitoring_runs(limit)

    @app.get(
        "/v1/source-collection-attempts",
        operation_id="getSourceCollectionAttempts",
    )
    def get_source_collection_attempts(
        _: OwnerAuth,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        return reader.source_collection_attempts(limit)

    @app.get("/v1/sources/degraded", operation_id="getDegradedSources")
    def get_degraded_sources(_: OwnerAuth) -> list[dict[str, object]]:
        return reader.degraded_sources()

    @app.get("/v1/coverage/latest", operation_id="getLatestCoverage")
    def get_latest_coverage(_: OwnerAuth) -> list[dict[str, object]]:
        return reader.latest_coverage()

    @app.get("/v1/forecasts/active", operation_id="getActiveForecasts")
    def get_active_forecasts(
        _: OwnerAuth,
        limit: int = Query(default=20, ge=1, le=100),
    ) -> dict[str, object]:
        return reader.active_forecasts(limit)

    return app