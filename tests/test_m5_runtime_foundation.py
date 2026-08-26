from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.operational_monitoring import (
    COMPLETED,
    RUNNING,
    OperationalMonitoringRuntime,
)


def test_m5_runtime_watch_and_run_lifecycle_survives_restart(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    t0 = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)

    runtime = OperationalMonitoringRuntime(project_root)
    watch = runtime.create_watch(
        "Ukraine strategic watch",
        "Ukraine security diplomacy",
        60,
        watch_id="watch-ukraine",
        created_at=t0,
    )

    assert [item.watch_id for item in runtime.due_watches(t0)] == [watch.watch_id]

    run = runtime.start_run(watch.watch_id, run_id="run-001", started_at=t0)
    assert run.status == RUNNING
    assert runtime.due_watches(t0 + timedelta(hours=2)) == []

    runtime.complete_run(
        run.run_id,
        result_count=4,
        completed_at=t0 + timedelta(minutes=5),
    )

    latest = runtime.repository.latest_run(watch.watch_id)
    assert latest is not None
    assert latest.status == COMPLETED
    assert latest.result_count == 4
    assert runtime.due_watches(t0 + timedelta(minutes=59)) == []
    assert [item.watch_id for item in runtime.due_watches(t0 + timedelta(minutes=60))] == [
        watch.watch_id
    ]

    restarted = OperationalMonitoringRuntime(project_root)
    restored_watch = restarted.repository.get_watch(watch.watch_id)
    restored_run = restarted.repository.latest_run(watch.watch_id)

    assert restored_watch == watch
    assert restored_run == latest


def test_m5_runtime_prevents_overlapping_runs_for_same_watch(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    t0 = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)

    runtime = OperationalMonitoringRuntime(project_root)
    watch = runtime.create_watch(
        "Europe watch",
        "European security",
        30,
        watch_id="watch-europe",
        created_at=t0,
    )
    runtime.start_run(watch.watch_id, run_id="run-active", started_at=t0)

    with pytest.raises(ValueError, match="already has a RUNNING run"):
        runtime.start_run(
            watch.watch_id,
            run_id="run-overlap",
            started_at=t0 + timedelta(minutes=1),
        )


def test_m5_runtime_records_failed_run_and_respects_cadence(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    t0 = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)

    runtime = OperationalMonitoringRuntime(project_root)
    watch = runtime.create_watch(
        "Middle East watch",
        "Middle East security",
        15,
        watch_id="watch-middle-east",
        created_at=t0,
    )
    run = runtime.start_run(watch.watch_id, run_id="run-failed", started_at=t0)
    runtime.fail_run(
        run.run_id,
        "provider unavailable",
        completed_at=t0 + timedelta(minutes=2),
    )

    latest = runtime.repository.latest_run(watch.watch_id)
    assert latest is not None
    assert latest.status == "FAILED"
    assert latest.error == "provider unavailable"
    assert runtime.due_watches(t0 + timedelta(minutes=14)) == []
    assert [item.watch_id for item in runtime.due_watches(t0 + timedelta(minutes=15))] == [
        watch.watch_id
    ]


def test_m5_operational_runtime_rejects_mixed_runtime_storage(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    with pytest.raises(ValueError, match="project-local data directory"):
        OperationalMonitoringRuntime(
            project_root,
            database_path=tmp_path / "other-project" / "shared-runtime.db",
        )
