"""E4 real-host validation helpers for the owner-only unattended pilot.

This module validates host/runtime facts that CI cannot prove. It does not create
cloud infrastructure and it never upgrades production/live status by itself.
"""

from __future__ import annotations

import argparse
from datetime import timedelta
import json
import platform
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from typing import Callable, Sequence
from uuid import uuid4

from .operational_monitoring import COMPLETED, FAILED, OperationalMonitoringRuntime, utc_now
from .runtime_storage import RuntimeStoragePolicy


SERVICE_NAME = "kgm-monitor.service"
EXPECTED_ARCHITECTURE = "aarch64"
EXPECTED_OS_ID = "ubuntu"
EXPECTED_OS_VERSION = "24.04"
DEFAULT_PROJECT_ROOT = Path("/opt/k-geopolitical-monitor")
PENDING_REBOOT_MARKER = Path("data/e4_host_validation/reboot_pending.json")


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def _run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_os_release(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"').strip("'")
    return values


def _read_boot_id(path: Path = Path("/proc/sys/kernel/random/boot_id")) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError("host boot_id is empty")
    return value


def _systemctl_value(
    runner: CommandRunner,
    *arguments: str,
) -> tuple[int, str]:
    result = runner(["systemctl", *arguments])
    return result.returncode, result.stdout.strip()


def _systemctl_properties(runner: CommandRunner) -> dict[str, str]:
    result = runner(
        [
            "systemctl",
            "show",
            SERVICE_NAME,
            "--property=User",
            "--property=Group",
            "--property=WorkingDirectory",
            "--property=ExecStart",
            "--no-pager",
        ]
    )
    if result.returncode != 0:
        return {}
    properties: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            properties[key] = value
    return properties


def _database_integrity(database_path: Path) -> str:
    if not database_path.is_file():
        return "NOT_PRESENT"
    try:
        with sqlite3.connect(database_path) as connection:
            row = connection.execute("PRAGMA integrity_check").fetchone()
    except sqlite3.Error as exc:
        return f"FAILED:{exc.__class__.__name__}"
    if row is None or str(row[0]).casefold() != "ok":
        return "FAILED"
    return "OK"


def _public_listener_ports(runner: CommandRunner) -> tuple[int, ...]:
    result = runner(["ss", "-ltnH"])
    if result.returncode != 0:
        return ()

    ports: set[int] = set()
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue
        local = fields[3]
        if ":" not in local:
            continue
        address, raw_port = local.rsplit(":", 1)
        address = address.strip("[]")
        if address not in {"0.0.0.0", "::", "*"}:
            continue
        try:
            ports.add(int(raw_port))
        except ValueError:
            continue
    return tuple(sorted(ports))


def collect_host_status(
    project_root: str | Path = DEFAULT_PROJECT_ROOT,
    *,
    runner: CommandRunner = _run_command,
    os_release_path: Path = Path("/etc/os-release"),
    boot_id_path: Path = Path("/proc/sys/kernel/random/boot_id"),
    architecture: str | None = None,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    policy = RuntimeStoragePolicy(root)
    database_path = policy.resolve_database().resolve()
    os_release = _parse_os_release(os_release_path)
    machine = architecture or platform.machine()

    enabled_code, enabled_value = _systemctl_value(runner, "is-enabled", SERVICE_NAME)
    active_code, active_value = _systemctl_value(runner, "is-active", SERVICE_NAME)
    properties = _systemctl_properties(runner)
    public_ports = _public_listener_ports(runner)
    integrity = _database_integrity(database_path)

    exec_start = properties.get("ExecStart", "")
    checks = {
        "architecture_arm64": machine == EXPECTED_ARCHITECTURE,
        "ubuntu_24_04": (
            os_release.get("ID", "").casefold() == EXPECTED_OS_ID
            and os_release.get("VERSION_ID") == EXPECTED_OS_VERSION
        ),
        "project_local_database": database_path.parent == policy.data_root,
        "database_integrity_ok": integrity == "OK",
        "service_enabled": enabled_code == 0 and enabled_value == "enabled",
        "service_active": active_code == 0 and active_value == "active",
        "service_user_kgm": properties.get("User") == "kgm",
        "service_group_kgm": properties.get("Group") == "kgm",
        "service_working_directory": properties.get("WorkingDirectory") == str(root),
        "service_execstart_project_local": (
            str(root / ".venv" / "bin" / "python") in exec_start
            and "kgeopolitical_monitor.unattended_runner" in exec_start
        ),
        "no_public_http_https_listener": not ({80, 443} & set(public_ports)),
    }

    return {
        "gate": "E4_HOST_RUNTIME",
        "project_root": str(root),
        "database_path": str(database_path),
        "database_integrity": integrity,
        "architecture": machine,
        "os_id": os_release.get("ID"),
        "os_version": os_release.get("VERSION_ID"),
        "boot_id": _read_boot_id(boot_id_path),
        "service": {
            "name": SERVICE_NAME,
            "enabled": enabled_value,
            "active": active_value,
            "properties": properties,
        },
        "public_listener_ports": list(public_ports),
        "checks": checks,
        "host_runtime_gate_pass": all(checks.values()),
        "external_cloud_firewall_gate": "NOT_VERIFIED_BY_HOST",
        "production_live": "NOT_OPERATIONAL",
    }


def _marker_path(project_root: Path) -> Path:
    return (project_root / PENDING_REBOOT_MARKER).resolve()


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def prepare_reboot_test(
    project_root: str | Path = DEFAULT_PROJECT_ROOT,
    *,
    runner: CommandRunner = _run_command,
    boot_id_path: Path = Path("/proc/sys/kernel/random/boot_id"),
) -> dict[str, object]:
    root = Path(project_root).resolve()
    status = collect_host_status(root, runner=runner, boot_id_path=boot_id_path)
    checks = status["checks"]
    if not isinstance(checks, dict) or not checks.get("service_enabled"):
        raise RuntimeError("kgm-monitor.service must be enabled before reboot preparation")
    if not checks.get("service_active"):
        raise RuntimeError("kgm-monitor.service must be active before reboot preparation")

    marker = _marker_path(root)
    if marker.exists():
        raise FileExistsError("an E4 reboot validation is already pending")

    stop = runner(["systemctl", "stop", SERVICE_NAME])
    if stop.returncode != 0:
        raise RuntimeError("failed to stop kgm-monitor.service for deterministic reboot test")

    current = utc_now()
    runtime = OperationalMonitoringRuntime(root)
    watch_id = f"e4-reboot-{uuid4().hex[:12]}"
    run_id = f"e4-reboot-run-{uuid4().hex[:12]}"

    try:
        runtime.create_watch(
            "E4 reboot recovery sentinel",
            "KGM E4 reboot validation sentinel",
            1,
            watch_id=watch_id,
            created_at=current - timedelta(minutes=10),
        )
        runtime.start_run(
            watch_id,
            run_id=run_id,
            started_at=current - timedelta(minutes=5),
        )
        payload: dict[str, object] = {
            "gate": "E4_REBOOT_RECOVERY",
            "prepared_at": current.isoformat(),
            "project_root": str(root),
            "database_path": str(runtime.database_path.resolve()),
            "prepared_boot_id": _read_boot_id(boot_id_path),
            "watch_id": watch_id,
            "run_id": run_id,
            "expected_recovery_status": FAILED,
            "expected_recovery_error": "interrupted runtime recovered",
            "service_left_stopped_for_reboot": True,
            "next_action": "reboot_host",
            "production_live": "NOT_OPERATIONAL",
        }
        _write_json_atomic(marker, payload)
        return payload
    except Exception:
        runner(["systemctl", "start", SERVICE_NAME])
        raise


def _run_row(database_path: Path, run_id: str) -> tuple[str, str | None, int] | None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT status, error, recovered
            FROM monitoring_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
    if row is None:
        return None
    return str(row[0]), row[1], int(row[2])


def _disable_watch(database_path: Path, watch_id: str) -> None:
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            "UPDATE monitoring_watches SET enabled = 0 WHERE watch_id = ?",
            (watch_id,),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("reboot validation watch disappeared before cleanup")


def verify_reboot_test(
    project_root: str | Path = DEFAULT_PROJECT_ROOT,
    *,
    runner: CommandRunner = _run_command,
    boot_id_path: Path = Path("/proc/sys/kernel/random/boot_id"),
    wait_seconds: float = 90.0,
    poll_seconds: float = 2.0,
    sleeper: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    if wait_seconds < 0:
        raise ValueError("wait_seconds must not be negative")
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be positive")

    root = Path(project_root).resolve()
    marker = _marker_path(root)
    if not marker.is_file():
        raise FileNotFoundError("no pending E4 reboot validation marker exists")
    prepared = json.loads(marker.read_text(encoding="utf-8"))

    current_boot_id = _read_boot_id(boot_id_path)
    if current_boot_id == prepared.get("prepared_boot_id"):
        raise RuntimeError("host boot_id has not changed; a real reboot is not evidenced")

    status = collect_host_status(root, runner=runner, boot_id_path=boot_id_path)
    checks = status["checks"]
    if not isinstance(checks, dict) or not checks.get("service_enabled"):
        raise RuntimeError("kgm-monitor.service is not enabled after reboot")
    if not checks.get("service_active"):
        raise RuntimeError("kgm-monitor.service is not active after reboot")

    database_path = Path(str(prepared["database_path"]))
    original = _run_row(database_path, str(prepared["run_id"]))
    if original is None:
        raise RuntimeError("prepared RUNNING monitoring run is missing after reboot")
    original_status, original_error, original_recovered = original
    if (
        original_status != FAILED
        or original_error != "interrupted runtime recovered"
        or original_recovered != 1
    ):
        raise RuntimeError("interrupted monitoring run was not recovered after reboot")

    runtime = OperationalMonitoringRuntime(root)
    watch_id = str(prepared["watch_id"])
    original_run_id = str(prepared["run_id"])
    deadline = monotonic() + wait_seconds
    resumed = runtime.repository.latest_run(watch_id)
    while (
        resumed is None
        or resumed.run_id == original_run_id
        or resumed.status not in {COMPLETED, FAILED}
    ):
        if monotonic() >= deadline:
            raise RuntimeError("due reboot sentinel watch did not resume after reboot")
        sleeper(poll_seconds)
        resumed = runtime.repository.latest_run(watch_id)

    _disable_watch(database_path, watch_id)

    completed_at = utc_now()
    result: dict[str, object] = {
        "gate": "E4_REBOOT_RECOVERY",
        "verified_at": completed_at.isoformat(),
        "prepared_boot_id": prepared["prepared_boot_id"],
        "verified_boot_id": current_boot_id,
        "boot_id_changed": True,
        "service_enabled_after_reboot": True,
        "service_active_after_reboot": True,
        "interrupted_run_id": original_run_id,
        "interrupted_run_recovered": True,
        "resumed_run_id": resumed.run_id,
        "resumed_run_status": resumed.status,
        "due_watch_resumed": True,
        "sentinel_watch_disabled_after_validation": True,
        "reboot_recovery_gate_pass": True,
        "live_collection_success_observed": resumed.status == COMPLETED,
        "external_cloud_firewall_gate": "NOT_VERIFIED_BY_HOST",
        "production_live": "NOT_OPERATIONAL",
    }

    completed_marker = marker.with_name(f"reboot_completed_{original_run_id}.json")
    marker.replace(completed_marker)
    _write_json_atomic(
        marker.parent / f"reboot_result_{original_run_id}.json",
        result,
    )
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the E4 real-host deployment gate.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=DEFAULT_PROJECT_ROOT,
        help="Deployed K-Geopolitical Monitor project root.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Report real-host runtime status.")
    status_parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Return non-zero unless the host runtime gate passes.",
    )

    subparsers.add_parser(
        "prepare-reboot",
        help="Stop the service and prepare a deterministic interrupted-run reboot test.",
    )

    verify_parser = subparsers.add_parser(
        "verify-reboot",
        help="Verify real reboot, recovery and due-watch resumption.",
    )
    verify_parser.add_argument("--wait-seconds", type=float, default=90.0)
    verify_parser.add_argument("--poll-seconds", type=float, default=2.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "status":
            payload = collect_host_status(args.project_root)
            print(json.dumps(payload, indent=2, sort_keys=True))
            if args.require_pass and not payload["host_runtime_gate_pass"]:
                return 1
            return 0
        if args.command == "prepare-reboot":
            payload = prepare_reboot_test(args.project_root)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.command == "verify-reboot":
            payload = verify_reboot_test(
                args.project_root,
                wait_seconds=args.wait_seconds,
                poll_seconds=args.poll_seconds,
            )
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "gate": "E4_HOST_VALIDATION",
                    "status": "FAILED",
                    "error": str(exc).strip() or exc.__class__.__name__,
                    "production_live": "NOT_OPERATIONAL",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    raise RuntimeError("unsupported E4 host validation command")


if __name__ == "__main__":
    raise SystemExit(main())
