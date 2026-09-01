import json

import pytest

from kgeopolitical_monitor.live_operational_cycle import LiveOperationalCycle
from kgeopolitical_monitor.runtime_health import IDLE, RuntimeHealthStore
from kgeopolitical_monitor.runtime_lease import (
    RuntimeInstanceLease,
    RuntimeLeaseError,
    default_runtime_lease_path,
)
from kgeopolitical_monitor.unattended_runner import build_unattended_service, main


def test_build_unattended_service_preserves_project_local_storage(tmp_path):
    service = build_unattended_service(tmp_path, poll_seconds=17)

    assert service.poll_seconds == 17.0
    assert isinstance(service.cycle, LiveOperationalCycle)
    assert service.health_recorder is not None
    assert service.runtime.database_path == (
        tmp_path / "data" / "kgeopolitical_monitor.db"
    ).resolve()
    assert service.runtime.database_path.exists()


def test_once_mode_initializes_runtime_without_network_when_no_watches(tmp_path, capsys):
    result = main(["--project-root", str(tmp_path), "--once"])

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execution_count"] == 0
    assert payload["executions"] == []
    assert payload["recovered_runs"] == 0
    database_path = (tmp_path / "data" / "kgeopolitical_monitor.db").resolve()
    assert database_path.is_file()
    assert default_runtime_lease_path(tmp_path).is_file()
    health = RuntimeHealthStore(database_path).latest()
    assert health is not None
    assert health.tick_status == IDLE
    assert health.execution_count == 0
    assert health.last_successful_execution_at is None


def test_once_mode_fails_closed_before_database_initialization_when_lease_is_held(tmp_path):
    lease_path = default_runtime_lease_path(tmp_path)

    with RuntimeInstanceLease(lease_path):
        with pytest.raises(RuntimeLeaseError, match="already holds the lease"):
            main(["--project-root", str(tmp_path), "--once"])

    assert not (tmp_path / "data" / "kgeopolitical_monitor.db").exists()


def test_runner_rejects_non_positive_poll_interval(tmp_path):
    try:
        build_unattended_service(tmp_path, poll_seconds=0)
    except ValueError as exc:
        assert "poll_seconds" in str(exc)
    else:
        raise AssertionError("non-positive poll interval must fail closed")
