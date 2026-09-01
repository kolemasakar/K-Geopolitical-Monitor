from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "deployment/systemd/kgm-monitor.service"
GITIGNORE = ROOT / ".gitignore"
WORKFLOW = ROOT / ".github/workflows/e4-real-host-validation.yml"


def test_e9a_systemd_least_privilege_contract():
    unit = UNIT.read_text(encoding="utf-8")

    required = (
        "User=kgm",
        "Group=kgm",
        "UMask=0077",
        "NoNewPrivileges=true",
        "PrivateTmp=true",
        "PrivateDevices=true",
        "ProtectSystem=strict",
        "ProtectHome=true",
        "ProtectKernelTunables=true",
        "ProtectKernelModules=true",
        "ProtectKernelLogs=true",
        "ProtectControlGroups=true",
        "ProtectClock=true",
        "ProtectHostname=true",
        "LockPersonality=true",
        "RestrictRealtime=true",
        "RestrictSUIDSGID=true",
        "RestrictNamespaces=true",
        "SystemCallArchitectures=native",
        "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
        "CapabilityBoundingSet=",
        "AmbientCapabilities=",
        "ReadWritePaths=/opt/k-geopolitical-monitor/data",
        "Environment=PYTHONDONTWRITEBYTECODE=1",
    )
    for value in required:
        assert value in unit

    assert "ReadWritePaths=/opt/k-geopolitical-monitor\n" not in unit
    assert "ReadWritePaths=/opt\n" not in unit


def test_e9a_monitoring_service_keeps_inbound_surface_closed():
    unit = UNIT.read_text(encoding="utf-8").casefold()

    forbidden = (
        "uvicorn",
        "backend_action_api",
        "admin_dashboard",
        "--host",
        "--port",
        "listenstream",
        "0.0.0.0",
        ":80",
        ":443",
        ":3306",
        ":5432",
    )
    for value in forbidden:
        assert value not in unit


def test_e9a_gitignore_blocks_local_secrets_and_runtime_state():
    ignored = set(GITIGNORE.read_text(encoding="utf-8").splitlines())

    required = {
        ".env",
        ".env.*",
        ".ssh/",
        "*.pem",
        "*.key",
        "*.p12",
        "*.pfx",
        "id_rsa*",
        "id_ed25519*",
        "/data/",
        "*.db",
        "*.db-*",
        "*.sqlite",
        "*.sqlite3",
    }
    assert required <= ignored


def test_e9a_real_host_workflow_uses_pinned_secret_backed_ssh_without_echoing_key():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "E4_SSH_PRIVATE_KEY: ${{ secrets.E4_SSH_PRIVATE_KEY }}" in workflow
    assert "E4_SSH_KNOWN_HOSTS: ${{ secrets.E4_SSH_KNOWN_HOSTS }}" in workflow
    assert "StrictHostKeyChecking=yes" in workflow
    assert 'chmod 0600 "$HOME/.ssh/id_e4"' in workflow
    assert 'chmod 0600 "$HOME/.ssh/known_hosts"' in workflow
    assert 'echo "$E4_SSH_PRIVATE_KEY"' not in workflow
    assert 'set -x' not in workflow
