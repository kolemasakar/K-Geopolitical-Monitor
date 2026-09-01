"""Owner-only SQLite backup, manifest and restore helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime
from .runtime_storage import RuntimeStoragePolicy


BACKUP_FORMAT = "KGM_RUNTIME_BACKUP_V1"
BACKUP_DATABASE_NAME = "runtime.db"
BACKUP_MANIFEST_NAME = "manifest.json"


def _integrity_check(database_path: Path) -> None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute("PRAGMA integrity_check").fetchone()
    if row is None or str(row[0]).casefold() != "ok":
        raise RuntimeError("SQLite integrity check failed")


def _database_sha256(database_path: Path) -> str:
    digest = hashlib.sha256()
    with database_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_migrations(database_path: Path) -> list[str]:
    with sqlite3.connect(database_path) as connection:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        ).fetchone()
        if exists is None:
            return []
        rows = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    return [str(row[0]) for row in rows]


def _normalized_capture_time(captured_at: datetime | None) -> datetime:
    value = captured_at or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("backup capture timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def backup_project_database(
    project_root: str | Path,
    backup_path: str | Path,
) -> Path:
    """Create a non-overwriting consistent SQLite backup of project-local runtime state."""

    runtime = OperationalMonitoringRuntime(Path(project_root))
    source = runtime.database_path.resolve()
    destination = Path(backup_path).expanduser().resolve()

    if destination == source:
        raise ValueError("backup destination must differ from the runtime database")
    if destination.exists():
        raise FileExistsError("backup destination already exists")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_connection, sqlite3.connect(
        destination
    ) as destination_connection:
        source_connection.backup(destination_connection)

    _integrity_check(destination)
    return destination


def restore_project_database(
    backup_path: str | Path,
    project_root: str | Path,
) -> Path:
    """Restore a validated backup into a fresh project-local data directory."""

    source = Path(backup_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError("backup database does not exist")
    _integrity_check(source)

    policy = RuntimeStoragePolicy(Path(project_root))
    destination = policy.resolve_database().resolve()
    if destination.exists():
        raise FileExistsError("restore refuses to overwrite an existing runtime database")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_connection, sqlite3.connect(
        destination
    ) as destination_connection:
        source_connection.backup(destination_connection)

    _integrity_check(destination)
    return destination


def create_runtime_backup_bundle(
    project_root: str | Path,
    bundle_path: str | Path,
    *,
    source_commit: str | None = None,
    captured_at: datetime | None = None,
) -> Path:
    """Create a versioned backup directory with integrity and schema metadata.

    `source_commit` is caller-supplied instrumentation. It is never inferred from
    repository state because a deployed working tree may not be authoritative.
    """

    bundle = Path(bundle_path).expanduser().resolve()
    if bundle.exists():
        raise FileExistsError("backup bundle destination already exists")

    bundle.mkdir(parents=True)
    try:
        database_path = backup_project_database(
            project_root,
            bundle / BACKUP_DATABASE_NAME,
        )
        capture_time = _normalized_capture_time(captured_at)
        manifest = {
            "format": BACKUP_FORMAT,
            "captured_at": capture_time.isoformat(),
            "source_commit": source_commit,
            "source_commit_status": "INSTRUMENTED" if source_commit else "NOT_INSTRUMENTED",
            "database_file": BACKUP_DATABASE_NAME,
            "database_sha256": _database_sha256(database_path),
            "database_size_bytes": database_path.stat().st_size,
            "integrity_check": "ok",
            "schema_migrations": _schema_migrations(database_path),
            "latest_schema_migration": (
                _schema_migrations(database_path)[-1]
                if _schema_migrations(database_path)
                else None
            ),
            "canonical_storage_policy": "PROJECT_LOCAL_ONLY",
        }
        manifest_path = bundle / BACKUP_MANIFEST_NAME
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except BaseException:
        for child in bundle.iterdir():
            if child.is_file():
                child.unlink()
        bundle.rmdir()
        raise

    return bundle


def load_runtime_backup_manifest(bundle_path: str | Path) -> dict[str, object]:
    """Load and validate the non-secret backup manifest structure."""

    bundle = Path(bundle_path).expanduser().resolve()
    manifest_path = bundle / BACKUP_MANIFEST_NAME
    if not manifest_path.is_file():
        raise FileNotFoundError("backup manifest does not exist")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("format") != BACKUP_FORMAT:
        raise ValueError("unsupported runtime backup format")
    if payload.get("database_file") != BACKUP_DATABASE_NAME:
        raise ValueError("backup manifest contains an unexpected database filename")
    return payload


def verify_runtime_backup_bundle(bundle_path: str | Path) -> dict[str, object]:
    """Verify manifest, SHA-256, file size and SQLite integrity before restore."""

    bundle = Path(bundle_path).expanduser().resolve()
    manifest = load_runtime_backup_manifest(bundle)
    database_path = bundle / BACKUP_DATABASE_NAME
    if not database_path.is_file():
        raise FileNotFoundError("backup database does not exist")

    expected_size = int(manifest["database_size_bytes"])
    if database_path.stat().st_size != expected_size:
        raise RuntimeError("backup database size does not match manifest")

    expected_hash = str(manifest["database_sha256"])
    actual_hash = _database_sha256(database_path)
    if actual_hash != expected_hash:
        raise RuntimeError("backup database SHA-256 does not match manifest")

    _integrity_check(database_path)
    migrations = _schema_migrations(database_path)
    if migrations != list(manifest.get("schema_migrations", [])):
        raise RuntimeError("backup schema migration snapshot does not match manifest")
    return manifest


def restore_runtime_backup_bundle(
    bundle_path: str | Path,
    project_root: str | Path,
) -> Path:
    """Verify a bundle and restore it into a fresh canonical project-local DB."""

    bundle = Path(bundle_path).expanduser().resolve()
    verify_runtime_backup_bundle(bundle)
    return restore_project_database(bundle / BACKUP_DATABASE_NAME, project_root)
