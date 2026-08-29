from pathlib import Path
import sqlite3
import subprocess

import pytest

from kgeopolitical_monitor.e4_host_validation import (
    collect_host_status,
    prepare_reboot_test,
    verify_reboot_test,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


def _completed(command, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def _write_host_files(tmp_path: Path, *, boot_id: str = "boot-a") -> tuple[Path, Path]:
    os_release = tmp_path / "os-release"
    os_release.write_text('ID=ubuntu\nVERSION_ID="24.04"\n', encoding="utf-8")
    boot = tmp_path / "boot-id"
    boot.write_text(boot_id + "\n", encoding="utf-8")
    return os_release, boot


def _runner_for(root: Path, *, public_ports: tuple[int, ...] = ()):
    calls = []

    def runner(command):
        command = list(command)
        calls.append(command)
        if command[:2] == ["systemctl", "is-enabled"]:
            return _completed(command, stdout="enabled\n")
        if command[:2] == ["systemctl", "is-active"]:
            return _completed(command, stdout="active\n")
        if command[:2] == ["systemctl", "show"]:
            return _completed(
                command,
                stdout=(
                    "User=kgm\n"
                    "Group=kgm\n"
                    f"WorkingDirectory={root}\n"
                    "ExecStart={ path="
                    f"{root}/.venv/bin/python ; argv[]={root}/.venv/bin/python "
                    "-m kgeopolitical_monitor.unattended_runner "
                    f"--project-root {root} --poll-seconds 60 ; }}\n"
                ),
            )
        if command[:2] == ["systemctl", "stop"]:
            return _completed(command)
        if command[:2] == ["systemctl", "start"]:
            return _completed(command)
        if command[:2] == ["ss", "-ltnH"]:
            lines = [
                f"LISTEN 0 4096 0.0.0.0:{port} 0.0.0.0:*"
                for port in public_ports
            ]
            return _completed(command, stdout="\n".join(lines))
        raise AssertionError(f"unexpected command: {command}")

    return runner, calls


def test_collect_host_status_passes_only_with_expected_host_contract(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path)
    os_release, boot = _write_host_files(tmp_path)
    runner, _calls = _runner_for(tmp_path)

    status = collect_host_status(
        tmp_path,
        runner=runner,
        os_release_path=os_release,
        boot_id_path=boot,
        architecture="aarch64",
    )

    assert runtime.database_path.exists()
    assert status["database_integrity"] == "OK"
    assert status["host_runtime_gate_pass"] is True
    assert status["checks"]["service_active"] is True
    assert status["checks"]["service_enabled"] is True
    assert status["checks"]["no_public_http_https_listener"] is True
    assert status["external_cloud_firewall_gate"] == "NOT_VERIFIED_BY_HOST"
    assert status["production_live"] == "NOT_OPERATIONAL"


def test_collect_host_status_rejects_public_https_listener(tmp_path):
    OperationalMonitoringRuntime(tmp_path)
    os_release, boot = _write_host_files(tmp_path)
    runner, _calls = _runner_for(tmp_path, public_ports=(443,))

    status = collect_host_status(
        tmp_path,
        runner=runner,
        os_release_path=os_release,
        boot_id_path=boot,
        architecture="aarch64",
    )

    assert status["public_listener_ports"] == [443]
    assert status["checks"]["no_public_http_https_listener"] is False
    assert status["host_runtime_gate_pass"] is False


def test_prepare_reboot_test_stops_service_and_persists_running_sentinel(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path)
    os_release, boot = _write_host_files(tmp_path)
    runner, calls = _runner_for(tmp_path)

    payload = prepare_reboot_test(
        tmp_path,
        runner=runner,
        boot_id_path=boot,
    )

    assert ["systemctl", "stop", "kgm-monitor.service"] in calls
    assert payload["prepared_boot_id"] == "boot-a"
    assert payload["service_left_stopped_for_reboot"] is True
    assert payload["next_action"] == "reboot_host"
    assert payload["production_live"] == "NOT_OPERATIONAL"
    assert (tmp_path / "data/e4_host_validation/reboot_pending.json").is_file()

    with sqlite3.connect(runtime.database_path) as connection:
        row = connection.execute(
            "SELECT status, recovered FROM monitoring_runs WHERE run_id = ?",
            (payload["run_id"],),
        ).fetchone()
    assert row == ("RUNNING", 0)


def test_verify_reboot_test_requires_real_boot_id_change(tmp_path):
    OperationalMonitoringRuntime(tmp_path)
    _os_release, boot = _write_host_files(tmp_path)
    runner, _calls = _runner_for(tmp_path)
    prepare_reboot_test(tmp_path, runner=runner, boot_id_path=boot)

    with pytest.raises(RuntimeError, match="boot_id has not changed"):
        verify_reboot_test(
            tmp_path,
            runner=runner,
            boot_id_path=boot,
            wait_seconds=0,
        )


def test_verify_reboot_test_confirms_recovery_and_due_watch_resumption(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path)
    _os_release, boot = _write_host_files(tmp_path)
    runner, _calls = _runner_for(tmp_path)
    prepared = prepare_reboot_test(tmp_path, runner=runner, boot_id_path=boot)

    boot.write_text("boot-b\n", encoding="utf-8")
    runtime = OperationalMonitoringRuntime(tmp_path)
    recovered = runtime.recover_interrupted_runs()
    assert recovered == 1

    resumed = runtime.start_run(str(prepared["watch_id"]))
    runtime.complete_run(resumed.run_id, result_count=0)

    result = verify_reboot_test(
        tmp_path,
        runner=runner,
        boot_id_path=boot,
        wait_seconds=0,
    )

    assert result["boot_id_changed"] is True
    assert result["interrupted_run_recovered"] is True
    assert result["due_watch_resumed"] is True
    assert result["resumed_run_id"] == resumed.run_id
    assert result["resumed_run_status"] == "COMPLETED"
    assert result["reboot_recovery_gate_pass"] is True
    assert result["production_live"] == "NOT_OPERATIONAL"

    with sqlite3.connect(runtime.database_path) as connection:
        enabled = connection.execute(
            "SELECT enabled FROM monitoring_watches WHERE watch_id = ?",
            (prepared["watch_id"],),
        ).fetchone()
    assert enabled == (0,)

    validation_dir = tmp_path / "data/e4_host_validation"
    assert not (validation_dir / "reboot_pending.json").exists()
    assert list(validation_dir.glob("reboot_completed_*.json"))
    assert list(validation_dir.glob("reboot_result_*.json"))
