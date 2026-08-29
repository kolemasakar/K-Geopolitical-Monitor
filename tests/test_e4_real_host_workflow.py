from pathlib import Path
import stat


WORKFLOW_PATH = Path(".github/workflows/e4-real-host-validation.yml")
RUNBOOK_PATH = Path("docs/runbooks/E4_OCI_REAL_HOST_PROVISIONING.md")
BOOTSTRAP_PATH = Path("deployment/scripts/e4_bootstrap_ubuntu_arm64.sh")


def _workflow() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _bootstrap() -> str:
    return BOOTSTRAP_PATH.read_text(encoding="utf-8")


def test_real_host_workflow_is_manual_and_retry_safe():
    text = _workflow()

    assert "workflow_dispatch:" in text
    assert "\n  push:" not in text
    assert "pre-service bootstrap residue" in text
    assert "test ! -e /opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db" in text
    assert "! -name e4_host_validation" in text
    assert "data/e4_host_validation -mindepth 1" in text
    assert "test ! -e /etc/systemd/system/kgm-monitor.service" in text
    assert "systemctl is-active kgm-monitor.service" in text
    assert "chmod 0755 \"$temp_root\"" in text
    assert "cancel-in-progress: false" in text


def test_real_host_workflow_pins_ssh_host_key_and_uses_required_secrets():
    text = _workflow()

    assert "secrets.E4_HOST" in text
    assert "secrets.E4_SSH_PRIVATE_KEY" in text
    assert "secrets.E4_SSH_KNOWN_HOSTS" in text
    assert "StrictHostKeyChecking=yes" in text
    assert "StrictHostKeyChecking=no" not in text
    assert "E4_SSH_USER: ubuntu" in text


def test_real_host_workflow_executes_real_reboot_recovery_gate():
    text = _workflow()

    assert "prepare-reboot" in text
    assert "systemctl reboot" in text
    assert "verify-reboot" in text
    assert "status --require-pass" in text
    assert "actions/upload-artifact@v4" in text


def test_real_host_workflow_preserves_monitoring_only_boundary():
    text = _workflow()

    assert 'sudo -n bash \\"$PROJECT_ROOT/deployment/scripts/e4_bootstrap_ubuntu_arm64.sh\\"' in text
    assert "kgeopolitical_monitor.e4_host_validation" in text
    assert "uvicorn" not in text
    assert "--host 0.0.0.0" not in text


def test_bootstrap_script_is_executable_in_checkout():
    mode = BOOTSTRAP_PATH.stat().st_mode
    assert mode & stat.S_IXUSR


def test_bootstrap_keeps_code_root_owned_but_service_traversable():
    text = _bootstrap()

    assert 'chown -R root:root "$PROJECT_ROOT"' in text
    assert 'chmod 0755 "$PROJECT_ROOT"' in text
    assert 'chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_ROOT/data"' in text
    assert 'chmod 0750 "$PROJECT_ROOT/data" "$PROJECT_ROOT/data/e4_host_validation"' in text
    assert 'runuser -u "$SERVICE_USER"' in text


def test_oci_runbook_keeps_external_firewall_gate_explicit():
    text = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "VM.Standard.A1.Flex" in text
    assert "1 OCPU" in text
    assert "6 GB" in text
    assert "E4_SSH_PRIVATE_KEY" in text
    assert "Never paste the SSH private key into ChatGPT" in text
    assert "do not add inbound TCP 80" in text
    assert "do not add inbound TCP 443" in text
    assert "REAL_HOST_GATE_PENDING" in text
