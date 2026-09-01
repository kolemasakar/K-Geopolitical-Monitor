from datetime import datetime, timezone
import json

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.runtime_backup import (
    BACKUP_DATABASE_NAME,
    BACKUP_FORMAT,
    BACKUP_MANIFEST_NAME,
    backup_project_database,
    create_runtime_backup_bundle,
    load_runtime_backup_manifest,
    restore_project_database,
    restore_runtime_backup_bundle,
    verify_runtime_backup_bundle,
)


NOW = datetime(2026, 8, 29, 10, 30, tzinfo=timezone.utc)


def test_backup_restore_preserves_project_local_runtime_state(tmp_path):
    source_root = tmp_path / "source-project"
    runtime = OperationalMonitoringRuntime(source_root)
    runtime.create_watch(
        "Deployment watch",
        "geopolitical deployment",
        30,
        watch_id="watch-e4",
        created_at=NOW,
    )

    backup = backup_project_database(source_root, tmp_path / "backups" / "runtime.db")
    target_root = tmp_path / "restored-project"
    restored_path = restore_project_database(backup, target_root)

    assert restored_path == (
        target_root / "data" / "kgeopolitical_monitor.db"
    ).resolve()
    restored = OperationalMonitoringRuntime(target_root)
    watch = restored.repository.get_watch("watch-e4")
    assert watch is not None
    assert watch.name == "Deployment watch"
    assert watch.query == "geopolitical deployment"


def test_backup_and_restore_refuse_destructive_overwrite(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    backup_path = tmp_path / "runtime-backup.db"

    backup_project_database(project_root, backup_path)
    with pytest.raises(FileExistsError, match="already exists"):
        backup_project_database(project_root, backup_path)

    with pytest.raises(FileExistsError, match="overwrite"):
        restore_project_database(backup_path, project_root)

    assert runtime.database_path.exists()


def test_restore_rejects_missing_backup(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        restore_project_database(tmp_path / "missing.db", tmp_path / "target")


def test_backup_bundle_records_integrity_schema_and_instrumented_commit(tmp_path):
    source_root = tmp_path / "source-project"
    runtime = OperationalMonitoringRuntime(source_root)
    runtime.create_watch(
        "DR watch",
        "disaster recovery",
        60,
        watch_id="watch-dr",
        created_at=NOW,
    )

    bundle = create_runtime_backup_bundle(
        source_root,
        tmp_path / "backups" / "bundle-001",
        source_commit="abc123",
        captured_at=NOW,
    )
    manifest = verify_runtime_backup_bundle(bundle)

    assert (bundle / BACKUP_DATABASE_NAME).is_file()
    assert (bundle / BACKUP_MANIFEST_NAME).is_file()
    assert manifest["format"] == BACKUP_FORMAT
    assert manifest["captured_at"] == NOW.isoformat()
    assert manifest["source_commit"] == "abc123"
    assert manifest["source_commit_status"] == "INSTRUMENTED"
    assert manifest["integrity_check"] == "ok"
    assert manifest["canonical_storage_policy"] == "PROJECT_LOCAL_ONLY"
    assert manifest["database_size_bytes"] > 0
    assert len(manifest["database_sha256"]) == 64
    assert manifest["schema_migrations"]
    assert manifest["latest_schema_migration"] == manifest["schema_migrations"][-1]


def test_backup_bundle_does_not_infer_source_commit(tmp_path):
    source_root = tmp_path / "source-project"
    OperationalMonitoringRuntime(source_root)

    bundle = create_runtime_backup_bundle(
        source_root,
        tmp_path / "backups" / "bundle-unknown-commit",
        captured_at=NOW,
    )
    manifest = load_runtime_backup_manifest(bundle)

    assert manifest["source_commit"] is None
    assert manifest["source_commit_status"] == "NOT_INSTRUMENTED"


def test_backup_bundle_restore_preserves_state_into_clean_project(tmp_path):
    source_root = tmp_path / "source-project"
    runtime = OperationalMonitoringRuntime(source_root)
    runtime.create_watch(
        "Restore drill watch",
        "restore drill",
        15,
        watch_id="watch-restore",
        created_at=NOW,
    )
    bundle = create_runtime_backup_bundle(
        source_root,
        tmp_path / "backups" / "bundle-restore",
        captured_at=NOW,
    )

    target_root = tmp_path / "clean-host-project"
    restored_path = restore_runtime_backup_bundle(bundle, target_root)

    assert restored_path == (
        target_root / "data" / "kgeopolitical_monitor.db"
    ).resolve()
    restored = OperationalMonitoringRuntime(target_root)
    watch = restored.repository.get_watch("watch-restore")
    assert watch is not None
    assert watch.query == "restore drill"

    with pytest.raises(FileExistsError, match="overwrite"):
        restore_runtime_backup_bundle(bundle, target_root)


def test_backup_bundle_detects_database_tampering_before_restore(tmp_path):
    source_root = tmp_path / "source-project"
    OperationalMonitoringRuntime(source_root)
    bundle = create_runtime_backup_bundle(
        source_root,
        tmp_path / "backups" / "bundle-tampered",
        captured_at=NOW,
    )

    database_path = bundle / BACKUP_DATABASE_NAME
    database_path.write_bytes(database_path.read_bytes() + b"tamper")

    with pytest.raises(RuntimeError, match="size does not match manifest"):
        verify_runtime_backup_bundle(bundle)
    with pytest.raises(RuntimeError, match="size does not match manifest"):
        restore_runtime_backup_bundle(bundle, tmp_path / "restore-target")


def test_backup_bundle_rejects_manifest_tampering(tmp_path):
    source_root = tmp_path / "source-project"
    OperationalMonitoringRuntime(source_root)
    bundle = create_runtime_backup_bundle(
        source_root,
        tmp_path / "backups" / "bundle-manifest-tampered",
        captured_at=NOW,
    )

    manifest_path = bundle / BACKUP_MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="SHA-256"):
        verify_runtime_backup_bundle(bundle)
