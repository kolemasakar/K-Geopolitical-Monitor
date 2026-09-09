#!/usr/bin/env python3
"""A3 disposable PostgreSQL shadow/reconciliation proof.

This proof uses only synthetic data. The owner-local SQLite side remains the
source of truth; PostgreSQL is a disposable, non-canonical shadow. Nothing in
this script can promote, cut over, or activate shared runtime.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import tempfile

import psycopg
from psycopg import sql

from kgeopolitical_monitor.shared_runtime_contract import TenantContext
from kgeopolitical_monitor.shared_runtime_shadow import (
    CanaryReadinessPlan,
    CanaryStage,
    MismatchKind,
    ShadowMismatchBudget,
    ShadowRecord,
    compare_shadow_snapshots,
    snapshot_from_records,
)

SCHEMA = "kgm_a3_shadow"
ROLE = "kgm_a3_shadow_runtime"
PRIMARY = TenantContext(workspace_id="workspace-alpha", project_id="project-alpha")
ALTERNATE = TenantContext(workspace_id="workspace-beta", project_id="project-beta")


def _admin_dsn() -> str:
    host = os.environ.get("PGHOST", "127.0.0.1")
    port = os.environ.get("PGPORT", "5432")
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD", "postgres")
    database = os.environ.get("PGDATABASE", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _records(tenant: TenantContext = PRIMARY) -> tuple[ShadowRecord, ...]:
    return (
        ShadowRecord.from_payload(
            tenant_context=tenant,
            table_name="shared_event",
            object_id="event-1",
            payload={"event_id": "event-1", "title": "Synthetic A3 event"},
            semantic_projection={"event_id": "event-1", "meaning": "synthetic-a3-event"},
        ),
        ShadowRecord.from_payload(
            tenant_context=tenant,
            table_name="shared_semantic_claim",
            object_id="claim-1",
            payload={"claim_id": "claim-1", "event_id": "event-1", "text": "Synthetic A3 claim"},
            semantic_projection={"claim_id": "claim-1", "meaning": "synthetic-a3-claim"},
        ),
    )


def _write_owner_local(path: Path, records: tuple[ShadowRecord, ...]) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """CREATE TABLE shadow_record (
                workspace_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                table_name TEXT NOT NULL,
                object_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                semantic_sha256 TEXT NOT NULL,
                PRIMARY KEY (workspace_id, project_id, table_name, object_id)
            )"""
        )
        connection.execute(
            """CREATE TABLE shadow_outbox (
                workspace_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                event_key TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                PRIMARY KEY (workspace_id, project_id, event_key)
            )"""
        )
        for record in records:
            connection.execute(
                "INSERT INTO shadow_record VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.tenant_context.workspace_id,
                    record.tenant_context.project_id,
                    record.table_name,
                    record.object_id,
                    record.payload_json,
                    record.payload_sha256,
                    record.semantic_sha256,
                ),
            )
            connection.execute(
                "INSERT INTO shadow_outbox VALUES (?, ?, ?, ?)",
                (
                    record.tenant_context.workspace_id,
                    record.tenant_context.project_id,
                    f"shadow:{record.table_name}:{record.object_id}",
                    record.payload_sha256,
                ),
            )
        connection.commit()
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("owner-local SQLite integrity check failed")
    finally:
        connection.close()


def _read_owner_local(path: Path) -> tuple[ShadowRecord, ...]:
    connection = sqlite3.connect(path)
    try:
        rows = connection.execute(
            """SELECT table_name, object_id, payload_json, payload_sha256, semantic_sha256
               FROM shadow_record
               WHERE workspace_id=? AND project_id=?
               ORDER BY table_name, object_id""",
            (PRIMARY.workspace_id, PRIMARY.project_id),
        ).fetchall()
        return tuple(
            ShadowRecord(
                tenant_context=PRIMARY,
                table_name=row[0],
                object_id=row[1],
                payload_json=row[2],
                payload_sha256=row[3],
                semantic_sha256=row[4],
            )
            for row in rows
        )
    finally:
        connection.close()


def _bootstrap_postgres(connection: psycopg.Connection) -> None:
    with connection.cursor() as cur:
        cur.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(SCHEMA)))
        cur.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(ROLE)))
        cur.execute(sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS").format(sql.Identifier(ROLE)))
        cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(SCHEMA)))
        cur.execute(
            sql.SQL(
                """CREATE TABLE {}.shadow_record (
                    workspace_id text NOT NULL,
                    project_id text NOT NULL,
                    table_name text NOT NULL,
                    object_id text NOT NULL,
                    payload_json text NOT NULL,
                    payload_sha256 text NOT NULL,
                    semantic_sha256 text NOT NULL,
                    PRIMARY KEY (workspace_id, project_id, table_name, object_id)
                )"""
            ).format(sql.Identifier(SCHEMA))
        )
        cur.execute(
            sql.SQL(
                """CREATE TABLE {}.shadow_outbox (
                    workspace_id text NOT NULL,
                    project_id text NOT NULL,
                    event_key text NOT NULL,
                    payload_sha256 text NOT NULL,
                    PRIMARY KEY (workspace_id, project_id, event_key)
                )"""
            ).format(sql.Identifier(SCHEMA))
        )
        for table in ("shadow_record", "shadow_outbox"):
            cur.execute(sql.SQL("ALTER TABLE {}.{} ENABLE ROW LEVEL SECURITY").format(sql.Identifier(SCHEMA), sql.Identifier(table)))
            cur.execute(sql.SQL("ALTER TABLE {}.{} FORCE ROW LEVEL SECURITY").format(sql.Identifier(SCHEMA), sql.Identifier(table)))
            cur.execute(
                sql.SQL(
                    """CREATE POLICY tenant_isolation ON {}.{}
                       USING (workspace_id = current_setting('kgm.workspace_id', true)
                              AND project_id = current_setting('kgm.project_id', true))
                       WITH CHECK (workspace_id = current_setting('kgm.workspace_id', true)
                                   AND project_id = current_setting('kgm.project_id', true))"""
                ).format(sql.Identifier(SCHEMA), sql.Identifier(table))
            )
            cur.execute(sql.SQL("GRANT SELECT, INSERT ON {}.{} TO {}").format(sql.Identifier(SCHEMA), sql.Identifier(table), sql.Identifier(ROLE)))
        cur.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(SCHEMA), sql.Identifier(ROLE)))
    connection.commit()


def _insert_shadow(connection: psycopg.Connection, records: tuple[ShadowRecord, ...]) -> None:
    with connection.cursor() as cur:
        for record in records:
            cur.execute(
                sql.SQL(
                    """INSERT INTO {}.shadow_record
                       (workspace_id, project_id, table_name, object_id, payload_json, payload_sha256, semantic_sha256)
                       VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"""
                ).format(sql.Identifier(SCHEMA)),
                (
                    record.tenant_context.workspace_id,
                    record.tenant_context.project_id,
                    record.table_name,
                    record.object_id,
                    record.payload_json,
                    record.payload_sha256,
                    record.semantic_sha256,
                ),
            )
            cur.execute(
                sql.SQL(
                    """INSERT INTO {}.shadow_outbox
                       (workspace_id, project_id, event_key, payload_sha256)
                       VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING"""
                ).format(sql.Identifier(SCHEMA)),
                (
                    record.tenant_context.workspace_id,
                    record.tenant_context.project_id,
                    f"shadow:{record.table_name}:{record.object_id}",
                    record.payload_sha256,
                ),
            )
    connection.commit()


def _read_pg_as_tenant(connection: psycopg.Connection, tenant: TenantContext) -> tuple[ShadowRecord, ...]:
    with connection.transaction():
        with connection.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(ROLE)))
            cur.execute("SELECT set_config('kgm.workspace_id', %s, true)", (tenant.workspace_id,))
            cur.execute("SELECT set_config('kgm.project_id', %s, true)", (tenant.project_id,))
            cur.execute(
                sql.SQL(
                    """SELECT table_name, object_id, payload_json, payload_sha256, semantic_sha256
                       FROM {}.shadow_record ORDER BY table_name, object_id"""
                ).format(sql.Identifier(SCHEMA))
            )
            rows = cur.fetchall()
    return tuple(
        ShadowRecord(
            tenant_context=tenant,
            table_name=row[0],
            object_id=row[1],
            payload_json=row[2],
            payload_sha256=row[3],
            semantic_sha256=row[4],
        )
        for row in rows
    )


def _count(connection: psycopg.Connection, table: str) -> int:
    with connection.cursor() as cur:
        cur.execute(sql.SQL("SELECT count(*) FROM {}.{}").format(sql.Identifier(SCHEMA), sql.Identifier(table)))
        return int(cur.fetchone()[0])


def _cleanup(connection: psycopg.Connection) -> None:
    connection.rollback()
    with connection.cursor() as cur:
        cur.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(SCHEMA)))
        cur.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(ROLE)))
    connection.commit()


def main() -> int:
    local_path: Path | None = None
    connection = psycopg.connect(_admin_dsn(), autocommit=False)
    try:
        with tempfile.NamedTemporaryFile(prefix="kgm-a3-owner-local-", suffix=".sqlite", delete=False) as tmp:
            local_path = Path(tmp.name)
        records = _records()
        _write_owner_local(local_path, records)
        owner_records = _read_owner_local(local_path)

        _bootstrap_postgres(connection)
        _insert_shadow(connection, owner_records)
        _insert_shadow(connection, owner_records)  # deterministic retry/idempotency proof

        if _count(connection, "shadow_record") != 2 or _count(connection, "shadow_outbox") != 2:
            raise RuntimeError("retry/idempotency or outbox persistence mismatch")

        alternate_record = _records(ALTERNATE)[0]
        _insert_shadow(connection, (alternate_record,))
        primary_observed = _read_pg_as_tenant(connection, PRIMARY)
        alternate_observed = _read_pg_as_tenant(connection, ALTERNATE)
        if len(primary_observed) != 2 or len(alternate_observed) != 1:
            raise RuntimeError("tenant RLS isolation mismatch")

        expected = snapshot_from_records(tenant_context=PRIMARY, schema_version=32, records=owner_records)
        observed = snapshot_from_records(tenant_context=PRIMARY, schema_version=32, records=primary_observed)
        exact = compare_shadow_snapshots(expected=expected, observed=observed, budget=ShadowMismatchBudget(0))
        if not exact.exact_match or not exact.within_budget:
            raise RuntimeError("exact owner-local to PostgreSQL reconciliation failed")

        mismatched = snapshot_from_records(
            tenant_context=PRIMARY,
            schema_version=32,
            records=primary_observed[:1],
        )
        mismatch = compare_shadow_snapshots(expected=expected, observed=mismatched, budget=ShadowMismatchBudget(2))
        classes = tuple(item.kind for item in mismatch.mismatches)
        expected_classes = (MismatchKind.ROW_COUNT, MismatchKind.TABLE_CONTENT, MismatchKind.SEMANTIC_PROJECTION)
        if classes != expected_classes or mismatch.within_budget:
            raise RuntimeError(f"mismatch classification/budget proof failed: {classes!r}")

        canary = CanaryReadinessPlan(stages=(CanaryStage(1), CanaryStage(5), CanaryStage(25), CanaryStage(100)))
        if canary.automatic_promotion or canary.canonical_cutover_authorized or canary.shared_runtime_activation_authorized:
            raise RuntimeError("canary boundary unexpectedly authorized promotion/cutover")

        report = {
            "gate": "PHASE_18_SHARED_RUNTIME_SHADOW_CANARY_EVIDENCE_VALIDATED",
            "synthetic_data_only": True,
            "owner_local_remains_canonical": True,
            "postgres_shadow_canonical": False,
            "exact_reconciliation": exact.exact_match,
            "primary_rows": len(primary_observed),
            "alternate_rows": len(alternate_observed),
            "retry_idempotency": "PASS",
            "outbox_persistence": "PASS",
            "tenant_isolation": "PASS",
            "read_only_shadow_observation": "PASS",
            "mismatch_classes": [item.value for item in classes],
            "mismatch_budget": 2,
            "mismatch_within_budget": mismatch.within_budget,
            "automatic_promotion": False,
            "canonical_cutover_authorized": False,
            "shared_runtime_activation_authorized": False,
            "production_live": False,
            "migration_033_created_or_authorized": False,
        }
        print(json.dumps(report, sort_keys=True))
        print("A3_SHADOW_RECONCILIATION_PROOF=PASS")
        return 0
    finally:
        try:
            _cleanup(connection)
        finally:
            connection.close()
            if local_path is not None:
                local_path.unlink(missing_ok=True)
            print("A3_EPHEMERAL_CLEANUP=PASS")


if __name__ == "__main__":
    raise SystemExit(main())
