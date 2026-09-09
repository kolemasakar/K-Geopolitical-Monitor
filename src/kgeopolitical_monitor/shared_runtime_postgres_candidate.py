"""Concrete PostgreSQL adapter for the disposable Phase 18 activation preflight.

This module is deliberately *not* the canonical shared-runtime repository.  It
creates and accesses only the isolated ``kgm_preflight`` PostgreSQL schema with
synthetic data.  It never reads or mutates the owner-local SQLite store, never
allocates migration 033, and never authorizes shared-runtime activation.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Callable, Iterable

import psycopg


PREFLIGHT_SCHEMA = "kgm_preflight"
PREFLIGHT_TABLE = "tenant_probe"
PREFLIGHT_RUNTIME_ROLE = "kgm_preflight_runtime"
PREFLIGHT_PROFILE = "shared_runtime_nonprod_candidate"
PREFLIGHT_MODE = "synthetic_nonprod"
RENDER_PRIVATE_NETWORK_MARKER = "render_private"
RAILWAY_PRIVATE_NETWORK_MARKER = "railway_private"
APPROVED_PRIVATE_NETWORK_MARKERS = frozenset(
    {RENDER_PRIVATE_NETWORK_MARKER, RAILWAY_PRIVATE_NETWORK_MARKER}
)
# Preserve the historical Render default for backward-compatible tests and
# previously recorded Render evidence. Concrete deployments should set the
# provider-accurate marker explicitly.
PRIVATE_NETWORK_MARKER = RENDER_PRIVATE_NETWORK_MARKER
RLS_ISOLATION_PROBE_ID = "rls-isolation-marker"

_TEXT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class PreflightCandidateError(RuntimeError):
    """Base error for fail-closed disposable candidate operations."""


class PreflightConfigurationError(PreflightCandidateError, ValueError):
    """Raised when the disposable candidate is not safely configured."""


class PreflightDatabaseError(PreflightCandidateError):
    """Raised when a concrete candidate database operation fails."""


def _required_identifier(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise PreflightConfigurationError(f"{field_name} must be a string")
    normalized = value.strip()
    if not _TEXT_RE.fullmatch(normalized):
        raise PreflightConfigurationError(f"{field_name} is invalid")
    return normalized


def _required_secret(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PreflightConfigurationError(f"{field_name} is required")
    return value.strip()


@dataclass(frozen=True)
class PreflightCandidateSettings:
    """Fail-closed settings for one synthetic non-production candidate."""

    database_url: str
    bearer_token: str
    workspace_id: str
    project_id: str
    mode: str = PREFLIGHT_MODE
    database_network: str = PRIVATE_NETWORK_MARKER

    def __post_init__(self) -> None:
        dsn = _required_secret(self.database_url, field_name="database_url")
        if not dsn.startswith(("postgresql://", "postgres://")):
            raise PreflightConfigurationError("database_url must use PostgreSQL")
        object.__setattr__(self, "database_url", dsn)
        object.__setattr__(
            self,
            "bearer_token",
            _required_secret(self.bearer_token, field_name="bearer_token"),
        )
        object.__setattr__(
            self,
            "workspace_id",
            _required_identifier(self.workspace_id, field_name="workspace_id"),
        )
        object.__setattr__(
            self,
            "project_id",
            _required_identifier(self.project_id, field_name="project_id"),
        )
        if self.mode != PREFLIGHT_MODE:
            raise PreflightConfigurationError(
                "candidate mode must be synthetic_nonprod"
            )
        if self.database_network not in APPROVED_PRIVATE_NETWORK_MARKERS:
            raise PreflightConfigurationError(
                "candidate database network must use an approved private-network marker"
            )

    @property
    def safe_metadata(self) -> dict[str, object]:
        """Return public-safe metadata without credentials, hosts or endpoints."""

        return {
            "profile": PREFLIGHT_PROFILE,
            "mode": self.mode,
            "canonical": False,
            "production_live": False,
            "shared_runtime_active": False,
            "synthetic_data_only": True,
            "database_network": self.database_network,
        }


# Bootstrap may use a provider-created privileged principal, but tenant DML must
# never execute with that principal because PostgreSQL superusers/BYPASSRLS roles
# bypass row-level security even when FORCE ROW LEVEL SECURITY is enabled.  The
# dedicated NOLOGIN role is intentionally non-owner and NOBYPASSRLS; every tenant
# transaction switches to it before setting tenant context or touching rows.
PREFLIGHT_DDL: tuple[str, ...] = (
    f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{PREFLIGHT_RUNTIME_ROLE}') THEN
            CREATE ROLE {PREFLIGHT_RUNTIME_ROLE}
                NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
        END IF;
    END
    $$
    """.strip(),
    f"ALTER ROLE {PREFLIGHT_RUNTIME_ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS",
    f"GRANT {PREFLIGHT_RUNTIME_ROLE} TO CURRENT_USER",
    f"CREATE SCHEMA IF NOT EXISTS {PREFLIGHT_SCHEMA}",
    f"""
    CREATE TABLE IF NOT EXISTS {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE} (
        workspace_id text NOT NULL,
        project_id text NOT NULL,
        probe_id text NOT NULL,
        payload_sha256 text NOT NULL CHECK (length(payload_sha256) = 64),
        created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (workspace_id, project_id, probe_id)
    )
    """.strip(),
    f"ALTER TABLE {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE} ENABLE ROW LEVEL SECURITY",
    f"ALTER TABLE {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE} FORCE ROW LEVEL SECURITY",
    f"DROP POLICY IF EXISTS kgm_preflight_tenant_isolation ON {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE}",
    f"""
    CREATE POLICY kgm_preflight_tenant_isolation
    ON {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE}
    USING (
        workspace_id = current_setting('kgm.workspace_id', true)
        AND project_id = current_setting('kgm.project_id', true)
    )
    WITH CHECK (
        workspace_id = current_setting('kgm.workspace_id', true)
        AND project_id = current_setting('kgm.project_id', true)
    )
    """.strip(),
    f"GRANT USAGE ON SCHEMA {PREFLIGHT_SCHEMA} TO {PREFLIGHT_RUNTIME_ROLE}",
    f"GRANT SELECT, INSERT, UPDATE ON {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE} TO {PREFLIGHT_RUNTIME_ROLE}",
)

_SET_RUNTIME_ROLE_SQL = f"SET LOCAL ROLE {PREFLIGHT_RUNTIME_ROLE}"
_SET_WORKSPACE_SQL = "SELECT set_config('kgm.workspace_id', %s, true)"
_SET_PROJECT_SQL = "SELECT set_config('kgm.project_id', %s, true)"
_INSERT_SQL = f"""
    INSERT INTO {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE}
        (workspace_id, project_id, probe_id, payload_sha256)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (workspace_id, project_id, probe_id)
    DO UPDATE SET payload_sha256 = EXCLUDED.payload_sha256,
                  created_at = CURRENT_TIMESTAMP
    RETURNING probe_id, payload_sha256
""".strip()
_LIST_SQL = f"""
    SELECT probe_id, payload_sha256
    FROM {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE}
    ORDER BY probe_id
""".strip()
_READ_PROBE_SQL = f"""
    SELECT probe_id
    FROM {PREFLIGHT_SCHEMA}.{PREFLIGHT_TABLE}
    WHERE probe_id = %s
""".strip()


ConnectFunction = Callable[..., object]


class PostgreSQLPreflightCandidate:
    """Small concrete adapter for live A1/A2 evidence only."""

    def __init__(
        self,
        settings: PreflightCandidateSettings,
        *,
        connect: ConnectFunction = psycopg.connect,
    ) -> None:
        if not isinstance(settings, PreflightCandidateSettings):
            raise PreflightConfigurationError("PreflightCandidateSettings required")
        self.settings = settings
        self._connect = connect

    def _connection(self):
        # DSN is intentionally never interpolated into messages or return values.
        return self._connect(
            self.settings.database_url,
            connect_timeout=5,
            autocommit=False,
        )

    @staticmethod
    def _set_tenant(cursor, *, workspace_id: str, project_id: str) -> None:
        cursor.execute(_SET_RUNTIME_ROLE_SQL)
        cursor.execute(_SET_WORKSPACE_SQL, (workspace_id,))
        cursor.execute(_SET_PROJECT_SQL, (project_id,))

    def initialize(self) -> None:
        """Bootstrap only the disposable schema and constrained runtime role."""

        try:
            with self._connection() as connection:
                with connection.cursor() as cursor:
                    for statement in PREFLIGHT_DDL:
                        cursor.execute(statement)
                connection.commit()
        except Exception as exc:  # psycopg subclasses vary by failure mode
            raise PreflightDatabaseError("candidate database initialization failed") from exc

    def write_probe(self, *, probe_id: str, payload: str) -> dict[str, str]:
        """Write one deterministic synthetic marker inside the configured tenant."""

        normalized_probe_id = _required_identifier(probe_id, field_name="probe_id")
        if not isinstance(payload, str) or not payload:
            raise PreflightConfigurationError("payload must be a non-empty string")
        digest = sha256(payload.encode("utf-8")).hexdigest()
        try:
            with self._connection() as connection:
                with connection.cursor() as cursor:
                    self._set_tenant(
                        cursor,
                        workspace_id=self.settings.workspace_id,
                        project_id=self.settings.project_id,
                    )
                    cursor.execute(
                        _INSERT_SQL,
                        (
                            self.settings.workspace_id,
                            self.settings.project_id,
                            normalized_probe_id,
                            digest,
                        ),
                    )
                    row = cursor.fetchone()
                connection.commit()
        except Exception as exc:
            raise PreflightDatabaseError("candidate probe write failed") from exc
        if row is None:
            raise PreflightDatabaseError("candidate probe write returned no row")
        return {"probe_id": str(row[0]), "payload_sha256": str(row[1])}

    def list_probes(self) -> tuple[dict[str, str], ...]:
        """Read only rows visible to the configured transaction-local tenant."""

        try:
            with self._connection() as connection:
                with connection.cursor() as cursor:
                    self._set_tenant(
                        cursor,
                        workspace_id=self.settings.workspace_id,
                        project_id=self.settings.project_id,
                    )
                    cursor.execute(_LIST_SQL)
                    rows: Iterable[tuple[object, object]] = cursor.fetchall()
        except Exception as exc:
            raise PreflightDatabaseError("candidate probe read failed") from exc
        return tuple(
            {"probe_id": str(row[0]), "payload_sha256": str(row[1])}
            for row in rows
        )

    def observe_rls_isolation(self) -> dict[str, object]:
        """Prove a known configured-tenant marker is hidden from another tenant."""

        # Establish a known-positive row first; otherwise an empty table could
        # make a broken RLS configuration look isolated.
        self.write_probe(
            probe_id=RLS_ISOLATION_PROBE_ID,
            payload="kgm synthetic rls isolation marker",
        )

        alternate_workspace = "kgm-preflight-isolation"
        alternate_project = "other-project"
        try:
            with self._connection() as connection:
                with connection.cursor() as cursor:
                    self._set_tenant(
                        cursor,
                        workspace_id=alternate_workspace,
                        project_id=alternate_project,
                    )
                    cursor.execute(_READ_PROBE_SQL, (RLS_ISOLATION_PROBE_ID,))
                    rows = cursor.fetchall()
        except Exception as exc:
            raise PreflightDatabaseError("candidate RLS isolation probe failed") from exc
        return {
            "alternate_tenant_visible_rows": len(rows),
            "rls_isolation_observed": len(rows) == 0,
        }
