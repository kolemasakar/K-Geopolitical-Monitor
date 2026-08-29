from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIT_PATH = PROJECT_ROOT / "deployment" / "systemd" / "kgm-monitor.service"


def test_systemd_unit_preserves_e4_runtime_and_restart_contract():
    unit = UNIT_PATH.read_text(encoding="utf-8")

    required = (
        "Wants=network-online.target",
        "After=network-online.target",
        "StartLimitIntervalSec=300",
        "StartLimitBurst=10",
        "User=kgm",
        "Group=kgm",
        "WorkingDirectory=/opt/k-geopolitical-monitor",
        "Environment=PYTHONUNBUFFERED=1",
        "Restart=on-failure",
        "RestartSec=10",
        "UMask=0077",
        "NoNewPrivileges=true",
        "ProtectSystem=strict",
        "ReadWritePaths=/opt/k-geopolitical-monitor/data",
        "WantedBy=multi-user.target",
    )
    for value in required:
        assert value in unit

    exec_start = next(
        line for line in unit.splitlines() if line.startswith("ExecStart=")
    )
    assert "/opt/k-geopolitical-monitor/.venv/bin/python" in exec_start
    assert "-m kgeopolitical_monitor.unattended_runner" in exec_start
    assert "--project-root /opt/k-geopolitical-monitor" in exec_start
    assert "--poll-seconds 60" in exec_start


def test_monitoring_unit_does_not_expose_api_dashboard_or_database_ports():
    unit = UNIT_PATH.read_text(encoding="utf-8").casefold()

    forbidden = (
        "uvicorn",
        "backend_action_api",
        "dashboard",
        "--host",
        "--port",
        "0.0.0.0",
        ":80",
        ":443",
        ":3306",
        ":5432",
    )
    for value in forbidden:
        assert value not in unit
