import json

from kgeopolitical_monitor.live_operational_cycle import LiveOperationalCycle
from kgeopolitical_monitor.unattended_runner import build_unattended_service, main


def test_build_unattended_service_preserves_project_local_storage(tmp_path):
    service = build_unattended_service(tmp_path, poll_seconds=17)

    assert service.poll_seconds == 17.0
    assert isinstance(service.cycle, LiveOperationalCycle)
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
    assert (tmp_path / "data" / "kgeopolitical_monitor.db").is_file()


def test_runner_rejects_non_positive_poll_interval(tmp_path):
    try:
        build_unattended_service(tmp_path, poll_seconds=0)
    except ValueError as exc:
        assert "poll_seconds" in str(exc)
    else:
        raise AssertionError("non-positive poll interval must fail closed")
