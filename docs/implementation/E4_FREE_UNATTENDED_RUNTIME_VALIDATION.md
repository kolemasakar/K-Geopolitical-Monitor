# E4 Free Unattended Runtime Deployment Validation

Status: PRE_DEPLOYMENT_BASELINE_VALIDATED / HOST_VALIDATION_PENDING
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E4 - unnumbered post-Phase-11 expansion

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains NOT_OPERATIONAL.

## 1. Purpose

E4 validates that the existing unattended monitoring runtime can be packaged for an owner-only, monitoring-only Linux service while preserving PROJECT_LOCAL_ONLY storage, restart recovery, visible source failures and existing truth boundaries.

This record does not claim that a cloud VM has been created or that unattended cloud operation is already running.

## 2. Pre-Deployment Delta Audit

Existing validated foundations before E4:
- OperationalMonitoringRuntime project-local persistence and cadence;
- interrupted RUNNING recovery;
- UnattendedMonitoringService startup recovery and bounded polling;
- LiveOperationalCycle persisted success/failure behavior;
- Consilium RSS and GDELT DOC 2.0 approved controlled live adapters;
- HTTPS-only public-source transport;
- source-failure isolation;
- production/live status NOT_OPERATIONAL.

Missing deployment artifacts found by the E4 audit:
- no concrete unattended executable entry point;
- no final systemd service unit;
- no project-local SQLite backup/restore helper;
- no native ARM64 regression gate.

## 3. Implemented Pre-Deployment Harness

Implementation commit:
- eba5199dd5e783faa15625d5077049f8f58302f1 - Add E4 unattended deployment validation harness

Added runtime entry point:
- src/kgeopolitical_monitor/unattended_runner.py

Runner behavior:
- constructs OperationalMonitoringRuntime under the supplied project root;
- uses only the approved Consilium RSS and GDELT DOC 2.0 adapters;
- uses UrllibHttpTransport, which retains HTTPS-only transport enforcement;
- connects LiveSourceCollector -> LiveEndToEndProcessor -> LiveOperationalCycle -> UnattendedMonitoringService;
- default supervisor poll interval is 60 seconds while persisted watch cadence remains authoritative;
- SIGTERM/SIGINT request graceful supervisor stop;
- --once executes one deterministic service tick for smoke validation;
- it does not open an inbound API, dashboard or database port.

Added project-local backup/restore:
- src/kgeopolitical_monitor/runtime_backup.py

Backup/restore rules:
- SQLite online backup API is used;
- backup destination cannot overwrite an existing file;
- restore target is resolved through RuntimeStoragePolicy;
- restore always targets the project-local data directory;
- restore refuses to overwrite an existing runtime database;
- PRAGMA integrity_check must pass for backup and restored database.

Added monitoring-only systemd unit:
- deployment/systemd/kgm-monitor.service

Service contract:
- User/Group: kgm;
- WorkingDirectory: /opt/k-geopolitical-monitor;
- Restart=on-failure;
- RestartSec=10;
- StartLimitIntervalSec=300;
- StartLimitBurst=10;
- PYTHONUNBUFFERED=1;
- UMask=0077;
- NoNewPrivileges=true;
- ProtectSystem=strict;
- writable path limited to /opt/k-geopolitical-monitor/data;
- WantedBy=multi-user.target;
- no API/dashboard listener is started by this unit.

## 4. Regression Coverage

Added tests:
- tests/test_unattended_runner.py;
- tests/test_runtime_backup.py;
- tests/test_e4_deployment_contract.py.

Validated behavior:
- runner initializes the default database only under PROJECT_LOCAL_ONLY data/;
- one-tick smoke with no watches performs no source request and exits normally;
- invalid poll interval fails closed;
- backup/restore preserves monitoring state;
- destructive backup overwrite fails closed;
- destructive restore overwrite fails closed;
- systemd unit contains the approved restart/storage/security contract;
- monitoring unit contains no API/dashboard/database port exposure configuration.

## 5. Native ARM64 Validation

Workflow:
- .github/workflows/e4-arm64-validation.yml

Runner:
- ubuntu-24.04-arm;
- native architecture check returned aarch64;
- Python 3.11.16 arm64.

ARM64 validation:
- GitHub Actions run: 33247791094;
- job: 99088172894;
- result: SUCCESS;
- pytest: 262 passed, 1 warning in 23.50s;
- unattended --once smoke: PASS;
- project-local database creation: PASS;
- systemd-analyze verify: PASS.

Standard x64 regression:
- GitHub Actions run: 33247791132;
- job: 99088173062;
- result: SUCCESS;
- pytest: 262 passed, 1 warning in 29.09s.

The warning is the existing Starlette TestClient/httpx deprecation warning and is non-blocking for this gate.

## 6. E4 Gate Classification

Pre-deployment engineering gates:
- concrete service entry point: PASS;
- PROJECT_LOCAL_ONLY runtime path: PASS;
- backup/restore integrity: PASS;
- non-overwriting restore policy: PASS;
- systemd unit static verification: PASS;
- native ARM64 dependency/runtime compatibility: PASS;
- full ARM64 regression: PASS;
- no inbound API/dashboard/database exposure in monitoring unit: PASS.

Actual host gates not yet executed:
- free host/account/capacity availability: NOT_YET_EXECUTED;
- VM creation: NOT_YET_EXECUTED;
- Ubuntu host patch/base configuration: NOT_YET_EXECUTED;
- service user and repository installation on the VM: NOT_YET_EXECUTED;
- systemctl enable/start on the VM: NOT_YET_EXECUTED;
- physical VM reboot and automatic restart validation: NOT_YET_EXECUTED;
- interrupted-run recovery after an actual reboot: NOT_YET_EXECUTED;
- live controlled source cycle on the VM: NOT_YET_EXECUTED;
- host network-rule verification: NOT_YET_EXECUTED.

Therefore E4 is not declared fully BASELINE_VALIDATED and cloud unattended runtime remains NOT_DEPLOYED.

## 7. Next Validation Sequence

Primary host candidate remains Oracle OCI Always Free A1 if account/capacity is available.
Fallback remains Google Cloud e2-micro if the primary path is unavailable.

Required host sequence:
1. create the owner-only test VM within the chosen free allowance;
2. use Ubuntu 24.04 LTS and create non-root user kgm;
3. install the repository under /opt/k-geopolitical-monitor and a local .venv;
4. run the full test suite on the actual host;
5. create and restore a project-local SQLite backup smoke;
6. install deployment/systemd/kgm-monitor.service;
7. verify, enable and start the service;
8. confirm database ports and HTTP/HTTPS remain closed for the monitoring-only gate;
9. create an interrupted RUNNING state, reboot the VM and verify recovery plus automatic service restart;
10. execute an approved live controlled cycle and verify persisted source attempts, monitoring runs and coverage state.

Only after those host gates pass may E4 be considered for full closure.

## 8. Invariants

- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared runtime database;
- no database network exposure;
- no API/dashboard exposure is introduced by the E4 monitoring service;
- public web data is not substituted for missing persisted backend state;
- GDELT remains discovery/index metadata rather than independent factual corroboration;
- source failures remain visible;
- graph, forecast, coverage and report layers do not inflate verification truth;
- E3 Action API remains code-validated but NOT_CONNECTED until a separate HTTPS connection gate;
- production/live remains NOT_OPERATIONAL.
