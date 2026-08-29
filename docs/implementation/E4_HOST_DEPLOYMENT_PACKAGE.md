# E4 Host Deployment Package

Status: HOST_DEPLOYMENT_PACKAGE_VALIDATED_IN_CI / REAL_HOST_PENDING
Date: 2026-08-29
Project: K-Geopolitical Monitor
Deployment class: OWNER_ONLY_TEST
Runtime storage: PROJECT_LOCAL_ONLY
Production/live: NOT_OPERATIONAL

## Purpose

This package converts the E4 pre-deployment runtime into a reproducible real-host procedure for Ubuntu 24.04 Arm64. It does not create a cloud tenancy, reserve capacity, prove an external firewall rule, or claim that a host has actually rebooted.

Validated implementation anchor:
- `52a1a159ab83d70080525d325e98d487bb72efec`

## Package Artifacts

- `deployment/scripts/e4_bootstrap_ubuntu_arm64.sh`
- `src/kgeopolitical_monitor/e4_host_validation.py`
- `deployment/systemd/kgm-monitor.service`
- `src/kgeopolitical_monitor/unattended_runner.py`
- `src/kgeopolitical_monitor/runtime_backup.py`
- `tests/test_e4_host_validation.py`
- `tests/test_e4_bootstrap_contract.py`
- `.github/workflows/e4-arm64-validation.yml`

## Current Primary Host Target

Oracle OCI Always Free A1 remains the preferred owner-only test target if the owner's account and home-region capacity are available.

Official Oracle material rechecked on 2026-08-29 states:
- Arm-based Ampere A1 Always Free allocation: 2 OCPUs and 12 GB memory total;
- 1,500 OCPU hours and 9,000 GB-hours per month;
- Ubuntu 24.04 supports Arm-based shapes;
- current Ubuntu 24.04 aarch64 platform images are published by Oracle/Canonical.

Preferred pilot shape:
- `VM.Standard.A1.Flex`;
- 2 OCPUs;
- 12 GB RAM;
- Ubuntu 24.04 LTS Arm64 standard image;
- project root `/opt/k-geopolitical-monitor`.

Authoritative provider references:
- https://www.oracle.com/cloud/free/
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- https://docs.oracle.com/en-us/iaas/Content/Compute/References/images.htm
- https://docs.oracle.com/en-us/iaas/images/ubuntu-2404/

Provider availability is an external fact and must be rechecked when the VM is actually created.

## Required Cloud Network Baseline

Before bootstrap:
- inbound SSH 22 only from the owner's source IP/range where practical;
- inbound 80 CLOSED;
- inbound 443 CLOSED;
- no database port exposed;
- no public dashboard/API listener;
- outbound HTTPS allowed for the already approved controlled source adapters.

The host validator can prove absence of a public local 80/443 listener. It cannot prove OCI/GCP security-list or firewall configuration; that remains a separate external evidence item.

## Fresh Host Procedure

Create the VM manually in the selected provider, connect by SSH, then place the repository at the canonical path:

```bash
sudo apt-get update
sudo apt-get install -y git
sudo git clone https://github.com/kolemasakar/K-Geopolitical-Monitor.git /opt/k-geopolitical-monitor
sudo git -C /opt/k-geopolitical-monitor checkout <validated-e4-host-package-sha>
```

Use a SHA whose x64 CI and native ARM64 CI are both green. Do not deploy an unvalidated moving `main` without recording the exact SHA.

Run the fresh-host bootstrap:

```bash
sudo /opt/k-geopolitical-monitor/deployment/scripts/e4_bootstrap_ubuntu_arm64.sh \
  --project-root /opt/k-geopolitical-monitor
```

The bootstrap fails closed unless:
- it runs as root;
- host architecture is `aarch64`;
- OS is Ubuntu 24.04;
- required repository files are present;
- no prior runtime database exists, unless `KGM_ALLOW_EXISTING_STATE=1` was explicitly set after review.

Bootstrap actions:
- installs minimal host dependencies;
- creates/reuses the non-login `kgm` service account;
- rebuilds the project-local virtual environment;
- runs the full pytest suite;
- creates the project-local database with one unattended smoke tick;
- performs SQLite backup and restore integrity smoke;
- installs and verifies the hardened systemd unit;
- enables and starts `kgm-monitor.service`;
- runs the machine-readable E4 host status gate.

## Host Runtime Evidence

After bootstrap:

```bash
sudo -u kgm /opt/k-geopolitical-monitor/.venv/bin/python \
  -m kgeopolitical_monitor.e4_host_validation \
  --project-root /opt/k-geopolitical-monitor \
  status --require-pass
```

Required machine checks include:
- native aarch64;
- Ubuntu 24.04;
- database under project-local `data/`;
- SQLite integrity OK;
- systemd service enabled and active;
- service User/Group = `kgm`;
- canonical WorkingDirectory and ExecStart;
- no public local listener on 80 or 443.

A passing host status still reports:
- `external_cloud_firewall_gate = NOT_VERIFIED_BY_HOST`;
- `production_live = NOT_OPERATIONAL`.

## Real Reboot / Recovery Gate

Prepare a deterministic interrupted-run test:

```bash
sudo /opt/k-geopolitical-monitor/.venv/bin/python \
  -m kgeopolitical_monitor.e4_host_validation \
  --project-root /opt/k-geopolitical-monitor \
  prepare-reboot
```

This command:
- requires the monitoring service to be enabled and active;
- stops the service to eliminate a recovery race;
- creates a dedicated one-minute sentinel watch;
- persists a synthetic RUNNING monitoring run with a deliberately old start time;
- stores the pre-reboot kernel boot ID;
- leaves the service stopped so only a real boot-start can recover the run.

Then perform a real host reboot:

```bash
sudo reboot
```

After reconnecting, verify:

```bash
sudo /opt/k-geopolitical-monitor/.venv/bin/python \
  -m kgeopolitical_monitor.e4_host_validation \
  --project-root /opt/k-geopolitical-monitor \
  verify-reboot --wait-seconds 90
```

The reboot gate passes only if:
- kernel boot ID changed;
- service is enabled and active after reboot;
- the exact prepared RUNNING run became FAILED with `recovered=1` and `interrupted runtime recovered`;
- the due sentinel watch produced a new terminal monitoring run after reboot;
- the sentinel watch is disabled after validation.

A terminal resumed run may be COMPLETED or FAILED. FAILED still proves restart/resumption but does not prove source availability. Live-source success remains separately visible.

## Evidence to Preserve

For the actual host gate record:
- provider, region, VM shape and image identifier;
- deployed Git SHA;
- host status JSON;
- bootstrap full pytest result;
- `systemctl is-enabled kgm-monitor.service`;
- `systemctl is-active kgm-monitor.service`;
- relevant `journalctl -u kgm-monitor.service` excerpt/timestamps;
- pre/post reboot boot IDs;
- reboot validation JSON files under `data/e4_host_validation/`;
- SQLite integrity result;
- external cloud firewall/security-list evidence;
- controlled live source collection attempts and persisted monitoring state.

Do not store cloud credentials, private keys, tokens or account secrets in these evidence files or in Git.

## Validation Anchors

Standard x64 CI for host package:
- run `33248327621`;
- job `99089541679`;
- SUCCESS;
- `270 passed, 1 warning in 21.78s`.

Native ARM64 CI for host package:
- run `33248327636`;
- job `99089541701`;
- runner `ubuntu-24.04-arm` / observed `aarch64`;
- SUCCESS;
- `270 passed, 1 warning in 25.05s`;
- bootstrap `bash -n`: PASS;
- host validator CLI smoke: PASS;
- unattended one-tick smoke: PASS;
- systemd-analyze verify: PASS.

## Boundary

This package completes engineering preparation for the E4 actual-host gate only.

It does not prove:
- a cloud VM exists;
- free-tier capacity is available;
- the service survived a real reboot;
- provider firewall rules are correct;
- unattended cloud monitoring is deployed;
- production/live is operational.

No Phase 12 or M14 is created by this work.
