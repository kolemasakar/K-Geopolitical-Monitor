import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.controlled_pilot import (
    ControlledPilotRunner,
    ProjectLocalJsonlSourceAdapter,
)
from kgeopolitical_monitor.operational_monitoring import COMPLETED, FAILED, OperationalMonitoringRuntime


def _write_items(project_root, items):
    path = project_root / "data" / "pilot_sources" / "pilot.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(item) for item in items) + "\n",
        encoding="utf-8",
    )
    return path


def _base_items(now):
    collected = now.isoformat()
    return [
        {
            "item_id": "item-official-1",
            "source_id": "source-official",
            "source_name": "Official Monitor",
            "source_class": "Official sources",
            "title": "Ukraine security council update",
            "content": "Ukraine security authorities published a controlled pilot update.",
            "collected_at": collected,
            "importance": 0.9,
            "confidence": 0.95,
            "reliability": "high",
        },
        {
            "item_id": "item-media-1",
            "source_id": "source-media",
            "source_name": "International Monitor",
            "source_class": "International media",
            "title": "Ukraine security developments",
            "content": "International monitoring summary of Ukraine security developments.",
            "collected_at": collected,
            "importance": 0.7,
            "confidence": 0.8,
            "reliability": "medium",
        },
        {
            "item_id": "item-regional-1",
            "source_id": "source-regional",
            "source_name": "Regional Monitor",
            "source_class": "Regional media",
            "title": "Regional economic update",
            "content": "A regional economic item unrelated to the active security watch.",
            "collected_at": collected,
            "importance": 0.4,
            "confidence": 0.65,
            "reliability": "medium",
        },
    ]


def test_controlled_pilot_persists_provenance_coverage_and_ranked_findings(tmp_path):
    project_root = tmp_path / "project"
    now = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)
    source_path = _write_items(project_root, _base_items(now))

    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-pilot",
        created_at=now,
    )
    adapter = ProjectLocalJsonlSourceAdapter(project_root, source_path)
    runner = ControlledPilotRunner(
        runtime,
        adapter,
        required_source_classes=("Official sources", "International media"),
    )

    executions = runner.execute_due(now)

    assert len(executions) == 1
    assert executions[0].status == COMPLETED
    assert executions[0].result_count == 2

    findings = runner.ranked_findings(run_id=executions[0].run_id)
    assert [finding.title for finding in findings] == [
        "Ukraine security council update",
        "Ukraine security developments",
    ]
    assert findings[0].evidence_refs == (
        "raw_item:item-official-1",
        "source:source-official",
    )

    coverage = runner.coverage.get(executions[0].run_id)
    assert coverage is not None
    assert coverage.examined_count == 3
    assert coverage.matched_count == 2
    assert coverage.coverage_confidence == 1.0
    assert coverage.gaps == ()
    assert coverage.source_classes == (
        "International media",
        "Official sources",
        "Regional media",
    )

    with sqlite3.connect(runtime.database_path) as connection:
        source_count = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        raw_count = connection.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0]
    assert source_count == 3
    assert raw_count == 3


def test_controlled_pilot_reports_source_class_gap(tmp_path):
    project_root = tmp_path / "project"
    now = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)
    _write_items(project_root, [_base_items(now)[0]])

    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-gap",
        created_at=now,
    )
    runner = ControlledPilotRunner(
        runtime,
        ProjectLocalJsonlSourceAdapter(
            project_root, "data/pilot_sources/pilot.jsonl"
        ),
        required_source_classes=("Official sources", "OSINT"),
    )

    execution = runner.execute_due(now)[0]
    coverage = runner.coverage.get(execution.run_id)

    assert execution.status == COMPLETED
    assert coverage is not None
    assert coverage.coverage_confidence == 0.5
    assert coverage.gaps == ("OSINT",)


def test_controlled_pilot_is_deterministic_across_cadence_and_restart(tmp_path):
    project_root = tmp_path / "project"
    now = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)
    source_path = _write_items(project_root, _base_items(now))

    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-repeat",
        created_at=now,
    )
    runner = ControlledPilotRunner(
        runtime,
        ProjectLocalJsonlSourceAdapter(project_root, source_path),
        required_source_classes=("Official sources", "International media"),
    )

    first = runner.execute_due(now)
    inside_cadence = runner.execute_due(now + timedelta(minutes=30))

    restarted_runtime = OperationalMonitoringRuntime(project_root)
    restarted_runner = ControlledPilotRunner(
        restarted_runtime,
        ProjectLocalJsonlSourceAdapter(project_root, source_path),
        required_source_classes=("Official sources", "International media"),
    )
    second = restarted_runner.execute_due(now + timedelta(minutes=61))

    assert first[0].result_count == 2
    assert inside_cadence == []
    assert second[0].status == COMPLETED
    assert second[0].result_count == 2

    with sqlite3.connect(restarted_runtime.database_path) as connection:
        raw_count = connection.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0]
        run_count = connection.execute(
            "SELECT COUNT(*) FROM monitoring_runs WHERE watch_id = ?",
            ("watch-repeat",),
        ).fetchone()[0]
    assert raw_count == 3
    assert run_count == 2


def test_controlled_pilot_rejects_source_path_outside_project_local_boundary(tmp_path):
    project_root = tmp_path / "project"
    external = tmp_path / "external.jsonl"
    external.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="data/pilot_sources"):
        ProjectLocalJsonlSourceAdapter(project_root, external)


def test_controlled_pilot_invalid_source_class_fails_run_without_findings(tmp_path):
    project_root = tmp_path / "project"
    now = datetime(2026, 8, 26, 9, 0, tzinfo=timezone.utc)
    invalid = _base_items(now)[0]
    invalid["source_class"] = "Unknown source class"
    _write_items(project_root, [invalid])

    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Ukraine security",
        "Ukraine security",
        60,
        watch_id="watch-invalid-source",
        created_at=now,
    )
    runner = ControlledPilotRunner(
        runtime,
        ProjectLocalJsonlSourceAdapter(
            project_root, "data/pilot_sources/pilot.jsonl"
        ),
        required_source_classes=("Official sources",),
    )

    execution = runner.execute_due(now)[0]

    assert execution.status == FAILED
    assert execution.result_count == 0
    assert "invalid pilot source item" in execution.error
    assert runner.ranked_findings(run_id=execution.run_id) == []
