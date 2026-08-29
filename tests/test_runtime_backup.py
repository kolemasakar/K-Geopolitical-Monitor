from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.runtime_backup import (
    backup_project_database,
    restore_project_database,
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
