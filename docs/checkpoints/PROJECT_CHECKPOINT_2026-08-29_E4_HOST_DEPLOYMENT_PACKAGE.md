# Project Checkpoint - 2026-08-29 E4 Host Deployment Package

Status: CONTROL_STATE_RECOVERY_POINT
Project: K-Geopolitical Monitor
Repository: kolemasakar/K-Geopolitical-Monitor
Branch: main
Checkpoint date: 2026-08-29
Previous E4 checkpoint: d936d696ce8efa15ec97d8512038e84710e5000e
Validated host-package anchor: 52a1a159ab83d70080525d325e98d487bb72efec

This checkpoint records a validated real-host deployment package for E4. It does not claim that Oracle OCI, Google Cloud, or any other external VM has been created or rebooted.

## 1. Canonical State

- Product concept: APPROVED
- ROADMAP phases through Phase 11: BASELINE_VALIDATED where implemented
- Owner-only private GPT pilot: SUCCESSFUL
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- E3 Private GPT Backend Action API: BASELINE_VALIDATED_LOCAL_READ_ONLY
- E4 Free Unattended Runtime Deployment: HOST_DEPLOYMENT_PACKAGE_VALIDATED / REAL_HOST_GATE_PENDING
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared infrastructure architecture: HYBRID
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Private GPT backend Action/API: NOT_CONNECTED
- HTTPS Action deployment: NOT_DEPLOYED
- Unattended cloud runtime: NOT_DEPLOYED
- Public GPT sharing: DEFERRED
- Shared production runtime: NOT_APPROVED
- Production/live: NOT_OPERATIONAL
- Next ROADMAP phase: NONE_APPROVED
- M14: NOT_CREATED / NOT_APPROVED

## 2. E4 Host Package Artifacts

New runtime/deployment validation:
- `src/kgeopolitical_monitor/e4_host_validation.py`
- `deployment/scripts/e4_bootstrap_ubuntu_arm64.sh`
- `tests/test_e4_host_validation.py`
- `tests/test_e4_bootstrap_contract.py`

Updated validation workflow:
- `.github/workflows/e4-arm64-validation.yml`

Implementation record:
- `docs/implementation/E4_HOST_DEPLOYMENT_PACKAGE.md`

Existing E4 dependencies retained:
- `src/kgeopolitical_monitor/unattended_service.py`
- `src/kgeopolitical_monitor/live_operational_cycle.py`
- `src/kgeopolitical_monitor/unattended_runner.py`
- `src/kgeopolitical_monitor/runtime_backup.py`
- `deployment/systemd/kgm-monitor.service`

## 3. Implementation Commits

- `b44f951413bb488faa4c93b8add662f27317653a` - Add E4 real-host validation CLI
- `0e473812aaf291c4bbcbe588046dd457e17d611c` - Add E4 Ubuntu ARM64 host bootstrap
- `6b4c88093ece3b3d3d40c48f585a4d54a377ce52` - Add E4 host validation regression tests
- `5d0ee17b5f50d16015ec7e1c2ac886a4fad73f09` - Add E4 bootstrap contract tests
- `52a1a159ab83d70080525d325e98d487bb72efec` - Extend E4 ARM64 validation for host package

## 4. Validation Anchors

Standard x64 CI:
- run: `33248327621`
- job: `99089541679`
- result: SUCCESS
- pytest: `270 passed, 1 warning in 21.78s`

Native ARM64 CI:
- run: `33248327636`
- job: `99089541701`
- runner label: `ubuntu-24.04-arm`
- observed architecture: `aarch64`
- result: SUCCESS
- pytest: `270 passed, 1 warning in 25.05s`
- bootstrap shell syntax: PASS
- host validator CLI smoke: PASS
- unattended one-tick smoke: PASS
- systemd-analyze verify: PASS

## 5. Validated Host-Package Semantics

- fresh-host bootstrap fails closed outside Ubuntu 24.04 aarch64;
- bootstrap fails closed over an existing runtime DB unless explicit override is supplied;
- bootstrap runs full regression before service activation;
- project-local database is initialized under `data/`;
- SQLite backup and restore integrity smoke is part of bootstrap;
- systemd unit is installed, verified, enabled and started by the bootstrap;
- host status is machine-readable and does not equate local listener checks with external cloud-firewall proof;
- local public listeners on 80/443 fail the host runtime gate;
- reboot preparation stops the service before creating the sentinel RUNNING run to remove recovery races;
- prepared reboot test records the kernel boot ID;
- reboot verification requires a changed boot ID;
- exact interrupted run must be recovered as FAILED with `recovered=1` and `interrupted runtime recovered`;
- due sentinel watch must produce a new terminal run after reboot;
- sentinel watch is disabled after successful validation;
- source failure after reboot remains visible and does not invalidate proof of due-watch resumption;
- production/live remains NOT_OPERATIONAL throughout validation output.

## 6. Current Provider Baseline

Primary candidate remains Oracle OCI Always Free A1, if owner account/home-region capacity is available.

Provider facts rechecked on 2026-08-29 against official Oracle material:
- Always Free Arm allocation is currently 2 OCPUs and 12 GB memory total;
- 1,500 OCPU hours and 9,000 GB-hours per month;
- Ubuntu 24.04 supports Arm-based shapes and current aarch64 platform images exist.

These are provider facts, not evidence that an instance exists for this project.

## 7. Explicitly Unvalidated Real-Host Facts

Do not infer any of the following from CI or this checkpoint:
- no OCI/GCP VM was created in this session;
- no free-tier compute capacity was reserved;
- no deployed VM identifier/region has been recorded;
- bootstrap has not run on a real cloud VM;
- `systemctl enable --now` has not run on a real cloud VM;
- no real host reboot has been performed;
- boot-ID change has not been observed on a deployed VM;
- interrupted-run recovery has not been observed across a real host reboot;
- due-watch resumption has not been observed across a real host reboot;
- no provider firewall/security-list state has been evidenced;
- no controlled live-source cycle from a real cloud host has been evidenced.

Therefore unattended cloud runtime remains NOT_DEPLOYED and production/live remains NOT_OPERATIONAL.

## 8. Exact Resume Point

Resume E4 at external VM creation and actual-host execution.

Preferred sequence:
1. create owner-only Oracle OCI `VM.Standard.A1.Flex` host if account/capacity is available;
2. use 2 OCPUs / 12 GB RAM and Ubuntu 24.04 LTS Arm64;
3. restrict inbound SSH and keep 80/443/database ingress closed;
4. clone repository to `/opt/k-geopolitical-monitor`;
5. checkout an exact green host-package SHA;
6. run `deployment/scripts/e4_bootstrap_ubuntu_arm64.sh`;
7. preserve machine-readable `status --require-pass` evidence;
8. separately evidence provider firewall/security-list configuration;
9. run `prepare-reboot`;
10. perform a real `sudo reboot`;
11. reconnect and run `verify-reboot`;
12. inspect systemd journal and persisted monitoring/source state;
13. execute/observe a controlled live source cycle from that host;
14. only then evaluate E4 closure.

## 9. Global Invariants

- no new ROADMAP Phase 12;
- no M14;
- no shared runtime database;
- no implicit mixed storage;
- no public Action/API connection without a separate HTTPS/security gate;
- no public-web substitution for persisted backend state;
- no translation/graph/forecast/coverage/report truth inflation;
- cloud credentials, SSH private keys and tokens must never be persisted in Git;
- production/live status remains NOT_OPERATIONAL until explicitly evidenced and approved.
