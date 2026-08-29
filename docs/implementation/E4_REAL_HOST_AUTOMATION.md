# E4 Real Host Automation

Status: IMPLEMENTED_FOR_VALIDATION
Project: K-Geopolitical Monitor
Date: 2026-08-29

## Purpose

Automate the real-host portion of E4 after one manual OCI VM provisioning step.

The automation is intentionally limited to an owner-only Ubuntu 24.04 ARM64 pilot and preserves PROJECT_LOCAL_ONLY storage.

## Added artifacts

- `.github/workflows/e4-real-host-validation.yml`
- `docs/runbooks/E4_OCI_REAL_HOST_PROVISIONING.md`
- `tests/test_e4_real_host_workflow.py`

## Security contract

- manual `workflow_dispatch` only;
- pinned SSH host key via `E4_SSH_KNOWN_HOSTS`;
- no `StrictHostKeyChecking=no`;
- dedicated SSH private key stored only in GitHub Actions secrets;
- default Ubuntu SSH user `ubuntu`;
- passwordless sudo is required and checked;
- fresh-host only: existing `/opt/k-geopolitical-monitor` causes fail-closed exit;
- no HTTP/HTTPS server is launched;
- no database listener is opened;
- OCI cloud firewall remains a separately evidenced gate.

## Automated validation sequence

1. resolve an immutable deployment SHA;
2. validate native aarch64 and Ubuntu 24.04;
3. clone and deploy the exact SHA;
4. run the validated E4 bootstrap;
5. verify pre-reboot host runtime state;
6. create deterministic interrupted-run sentinel state;
7. issue a real `systemctl reboot`;
8. wait for pinned SSH recovery;
9. prove Linux `boot_id` changed;
10. prove systemd auto-start;
11. prove interrupted-run recovery;
12. prove due-watch resumption;
13. re-run final host runtime gate;
14. collect JSON evidence into a GitHub Actions artifact.

## Explicit non-claims

This implementation does not prove that an OCI VM currently exists.
It does not prove OCI Security List/NSG state.
It does not mark unattended cloud runtime DEPLOYED until a successful real-host workflow run and separate cloud-firewall evidence exist.
It does not mark production/live operational.

## Current gate

`E4_REAL_HOST_AUTOMATION_READY`

Next required action: owner manually provisions the OCI A1 VM and adds the three repository secrets documented in the runbook, then launches the manual workflow.
