from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "deployment/scripts/e4_bootstrap_ubuntu_arm64.sh"
UNIT = ROOT / "deployment/systemd/kgm-monitor.service"


def test_bootstrap_is_fresh_host_fail_closed_and_arm64_specific():
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert "set -Eeuo pipefail" in text
    assert '[[ "$(uname -m)" == "aarch64" ]]' in text
    assert '[[ "${ID:-}" == "ubuntu" ]]' in text
    assert '[[ "${VERSION_ID:-}" == "24.04" ]]' in text
    assert "KGM_ALLOW_EXISTING_STATE" in text
    assert "existing runtime DB detected" in text
    assert "requires native aarch64 host" in text


def test_bootstrap_runs_full_regression_backup_restore_and_host_status_gate():
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert 'python" -m pytest -q' in text
    assert "backup_project_database" in text
    assert "restore_project_database" in text
    assert "PRAGMA integrity_check" in text
    assert "systemd-analyze verify" in text
    assert 'systemctl enable --now "$SERVICE_NAME"' in text
    assert "kgeopolitical_monitor.e4_host_validation" in text
    assert "status" in text
    assert "--require-pass" in text


def test_bootstrap_preserves_project_local_data_ownership_boundary():
    text = BOOTSTRAP.read_text(encoding="utf-8")
    unit = UNIT.read_text(encoding="utf-8")

    assert 'chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_ROOT/data"' in text
    assert "User=kgm" in unit
    assert "Group=kgm" in unit
    assert "ProtectSystem=strict" in unit
    assert "ReadWritePaths=/opt/k-geopolitical-monitor/data" in unit
    assert "production_live=NOT_OPERATIONAL" in text
