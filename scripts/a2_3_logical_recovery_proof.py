"""Phase 18 A2.3 no-charge disposable PostgreSQL recovery proof.

The script is intended for an ephemeral PostgreSQL 16 instance in CI. It does
not connect to Railway and never reads provider credentials. It exercises the
same kgm_preflight schema/RLS contract used by the disposable shared-runtime
candidate, performs pg_dump -> pg_restore, compares deterministic state, and
cleans up all transient databases/files.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import subprocess
import tempfile

import psycopg
from psycopg import sql

from kgeopolitical_monitor.shared_runtime_postgres_candidate import (
    PREFLIGHT_DDL,
    PREFLIGHT_RUNTIME_ROLE,
    PREFLIGHT_SCHEMA,
    PREFLIGHT_TABLE,
    PostgreSQLPreflightCandidate,
    PreflightCandidateSettings,
)


SOURCE_DB = "kgm_a2_3_source"
RESTORE_DB = "kgm_a2_3_restore"
DB_PREFIX = "kgm_a2_3_"
PRIMARY_WORKSPACE = "workspace-recovery"
PRIMARY_PROJECT = "project-recovery"
ALT_WORKSPACE = "workspace-alternate"
ALT_PROJECT = "project-alternate"


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable {name} is missing")
    return value


def _admin_dsn(database: str) -> str:
    host = _required_env("PGHOST")
    port = _required_env("PGPORT")
    user = _required_env("PGUSER")
    password = _required_env("PGPASSWORD")
    # This DSN is used only in-process and is never printed.
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _run(*args: str) -> None:
    subprocess.run(args, check=True, env=os.environ.copy())


def _recreate_database(name: str) -> None:
    if not name.startswith(DB_PREFIX):
        raise RuntimeError("refusing to manage database outside A2.3 prefix")
    with psycopg.connect(_admin_dsn("postgres"), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()"),
                (name,),
            )
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(name)))
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))


def _drop_database(name: str) -> None:
    if not name.startswith(DB_PREFIX):
        raise RuntimeError("refusing to drop database outside A2.3 prefix")
    with psycopg.connect(_admin_dsn("postgres"), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                (name,),
            )
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(name)))


def _initialize_source() -> None:
    with psycopg.connect(_admin_dsn(SOURCE_DB), autocommit=False) as conn:
        with conn.cursor() as cur:
            for statement in PREFLIGHT_DDL:
                cur.execute(statement)
        conn.commit()

    settings = PreflightCandidateSettings(
        database_url=_admin_dsn(SOURCE_DB),
        bearer_token="synthetic-a2-3-token",
        workspace_id=PRIMARY_WORKSPACE,
        project_id=PRIMARY_PROJECT,
        mode="synthetic_nonprod",
        database_network="railway_private",
    )
    adapter = PostgreSQLPreflightCandidate(settings)
    adapter.write_probe(probe_id="recovery-alpha", payload="synthetic alpha")
    adapter.write_probe(probe_id="recovery-beta", payload="synthetic beta")

    # Seed one alternate-tenant row through the bootstrap/admin principal so the
    # restored RLS proof is a known-positive isolation test rather than an empty
    # alternate tenant.
    alt_digest = sha256(b"synthetic alternate").hexdigest()
    with psycopg.connect(_admin_dsn(SOURCE_DB), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "INSERT INTO {}.{} (workspace_id, project_id, probe_id, payload_sha256) VALUES (%s, %s, %s, %s)"
                ).format(sql.Identifier(PREFLIGHT_SCHEMA), sql.Identifier(PREFLIGHT_TABLE)),
                (ALT_WORKSPACE, ALT_PROJECT, "recovery-alt", alt_digest),
            )
        conn.commit()


def _snapshot(database: str) -> dict[str, object]:
    with psycopg.connect(_admin_dsn(database), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "SELECT workspace_id, project_id, probe_id, payload_sha256 FROM {}.{} ORDER BY workspace_id, project_id, probe_id"
                ).format(sql.Identifier(PREFLIGHT_SCHEMA), sql.Identifier(PREFLIGHT_TABLE))
            )
            rows = cur.fetchall()
            cur.execute(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = %s AND c.relname = %s",
                (PREFLIGHT_SCHEMA, PREFLIGHT_TABLE),
            )
            rls = cur.fetchone()
            cur.execute(
                "SELECT policyname FROM pg_policies WHERE schemaname = %s AND tablename = %s ORDER BY policyname",
                (PREFLIGHT_SCHEMA, PREFLIGHT_TABLE),
            )
            policies = tuple(row[0] for row in cur.fetchall())
            cur.execute(
                "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, rolinherit, rolbypassrls FROM pg_roles WHERE rolname = %s",
                (PREFLIGHT_RUNTIME_ROLE,),
            )
            role = cur.fetchone()

    canonical = "\n".join("|".join(map(str, row)) for row in rows).encode("utf-8")
    return {
        "row_count": len(rows),
        "rows_sha256": sha256(canonical).hexdigest(),
        "rls": tuple(rls) if rls else None,
        "policies": policies,
        "role": tuple(role) if role else None,
    }


def _assert_restored_rls_isolation() -> None:
    with psycopg.connect(_admin_dsn(RESTORE_DB), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(PREFLIGHT_RUNTIME_ROLE)))
            cur.execute("SELECT set_config('kgm.workspace_id', %s, true)", (PRIMARY_WORKSPACE,))
            cur.execute("SELECT set_config('kgm.project_id', %s, true)", (PRIMARY_PROJECT,))
            cur.execute(
                sql.SQL("SELECT probe_id FROM {}.{} ORDER BY probe_id").format(
                    sql.Identifier(PREFLIGHT_SCHEMA), sql.Identifier(PREFLIGHT_TABLE)
                )
            )
            primary = tuple(row[0] for row in cur.fetchall())

    if primary != ("recovery-alpha", "recovery-beta"):
        raise RuntimeError(f"restored RLS primary tenant mismatch: {primary!r}")

    with psycopg.connect(_admin_dsn(RESTORE_DB), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(PREFLIGHT_RUNTIME_ROLE)))
            cur.execute("SELECT set_config('kgm.workspace_id', %s, true)", (ALT_WORKSPACE,))
            cur.execute("SELECT set_config('kgm.project_id', %s, true)", (ALT_PROJECT,))
            cur.execute(
                sql.SQL("SELECT probe_id FROM {}.{} ORDER BY probe_id").format(
                    sql.Identifier(PREFLIGHT_SCHEMA), sql.Identifier(PREFLIGHT_TABLE)
                )
            )
            alternate = tuple(row[0] for row in cur.fetchall())

    if alternate != ("recovery-alt",):
        raise RuntimeError(f"restored RLS alternate tenant mismatch: {alternate!r}")


def main() -> int:
    dump_path: Path | None = None
    try:
        _recreate_database(SOURCE_DB)
        _recreate_database(RESTORE_DB)
        _initialize_source()
        source = _snapshot(SOURCE_DB)

        with tempfile.NamedTemporaryFile(prefix="kgm-a2-3-", suffix=".dump", delete=False) as tmp:
            dump_path = Path(tmp.name)

        _run(
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--dbname",
            _admin_dsn(SOURCE_DB),
            "--file",
            str(dump_path),
        )
        dump_bytes = dump_path.stat().st_size
        dump_sha256 = sha256(dump_path.read_bytes()).hexdigest()
        if dump_bytes <= 0:
            raise RuntimeError("logical dump is empty")

        _run(
            "pg_restore",
            "--exit-on-error",
            "--no-owner",
            "--dbname",
            _admin_dsn(RESTORE_DB),
            str(dump_path),
        )

        restored = _snapshot(RESTORE_DB)
        if restored != source:
            raise RuntimeError(f"restored snapshot mismatch: source={source!r} restored={restored!r}")
        if restored["rls"] != (True, True):
            raise RuntimeError("restored table did not preserve ENABLE/FORCE RLS")
        if "kgm_preflight_tenant_isolation" not in restored["policies"]:
            raise RuntimeError("restored tenant isolation policy missing")
        if restored["role"] != (False, False, False, False, False, False):
            raise RuntimeError("runtime role privilege contract mismatch after restore")

        _assert_restored_rls_isolation()

        print(f"A2_3_LOGICAL_DUMP_BYTES={dump_bytes}")
        print(f"A2_3_LOGICAL_DUMP_SHA256={dump_sha256}")
        print(f"A2_3_SOURCE_ROWS={source['row_count']}")
        print(f"A2_3_ROWS_SHA256={source['rows_sha256']}")
        print("A2_3_RLS_RESTORE=PASS")
        print("A2_3_LOGICAL_RECOVERY_PROOF=PASS")
        return 0
    finally:
        if dump_path is not None:
            dump_path.unlink(missing_ok=True)
        _drop_database(RESTORE_DB)
        _drop_database(SOURCE_DB)
        print("A2_3_EPHEMERAL_CLEANUP=PASS")


if __name__ == "__main__":
    raise SystemExit(main())
