# E4 Free Unattended Runtime Deployment Validation

Status: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E4 - unnumbered post-Phase-11 expansion

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains NOT_OPERATIONAL.

## 1. Purpose

E4 validates that the existing unattended monitoring runtime can be packaged and operated as an owner-only, monitoring-only Linux service while preserving PROJECT_LOCAL_ONLY storage, restart recovery, visible source failures and existing truth boundaries.

The workstream now includes both pre-deployment engineering validation and successful execution on a real OCI Ubuntu 24.04 ARM64 host.

## 2. Pre-Deployment Foundation

Existing validated foundations before E4:
- OperationalMonitoringRuntime project-local persistence and cadence;
- interrupted RUNNING recovery;
- UnattendedMonitoringService startup recovery and bounded polling;
- LiveOperationalCycle persisted success/failure behavior;
- Consilium RSS and GDELT DOC 2.0 approved controlled live adapters;
- HTTPS-only public-source transport at the application adapter layer;
- source-failure isolation;
- production/live status NOT_OPERATIONAL.

E4 added the missing deployment artifacts:
- concrete unattended executable entry point;
- monitoring-only systemd service unit;
- project-local SQLite backup/restore helper;
- native ARM64 regression gate;
- Ubuntu ARM64 bootstrap and host validation tooling;
- automated immutable deploy/reboot/recovery workflow.

## 3. Implemented Deployment Harness

Runtime entry point:
- `src/kgeopolitical_monitor/unattended_runner.py`

Runner behavior:
- constructs OperationalMonitoringRuntime under the supplied project root;
- uses only the approved Consilium RSS and GDELT DOC 2.0 adapters;
- uses UrllibHttpTransport with HTTPS-only application transport enforcement;
- connects LiveSourceCollector -> LiveEndToEndProcessor -> LiveOperationalCycle -> UnattendedMonitoringService;
- default supervisor poll interval is 60 seconds while persisted watch cadence remains authoritative;
- SIGTERM/SIGINT request graceful supervisor stop;
- `--once` executes one deterministic service tick;
- it does not open an inbound API, dashboard or database port.

Project-local backup/restore:
- `src/kgeopolitical_monitor/runtime_backup.py`

Backup/restore rules:
- SQLite online backup API is used;
- backup destination cannot overwrite an existing file;
- restore target is resolved through RuntimeStoragePolicy;
- restore always targets the project-local data directory;
- restore refuses to overwrite an existing runtime database;
- `PRAGMA integrity_check` must pass for backup and restored database.

Monitoring-only systemd unit:
- `deployment/systemd/kgm-monitor.service`

Service contract:
- User/Group: `kgm`;
- WorkingDirectory: `/opt/k-geopolitical-monitor`;
- Restart=on-failure;
- RestartSec=10;
- StartLimitIntervalSec=300;
- StartLimitBurst=10;
- PYTHONUNBUFFERED=1;
- UMask=0077;
- NoNewPrivileges=true;
- ProtectSystem=strict;
- writable path limited to `/opt/k-geopolitical-monitor/data`;
- WantedBy=multi-user.target;
- no API/dashboard listener is started by this unit.

## 4. Pre-Deployment Regression Coverage

Validated behavior includes:
- runner initializes the default database only under PROJECT_LOCAL_ONLY `data/`;
- one-tick smoke with no watches performs no source request and exits normally;
- invalid poll interval fails closed;
- backup/restore preserves monitoring state;
- destructive backup overwrite fails closed;
- destructive restore overwrite fails closed;
- systemd unit contains the approved restart/storage/security contract;
- monitoring unit contains no API/dashboard/database port exposure configuration.

Native ARM64 workflow:
- `.github/workflows/e4-arm64-validation.yml`
- native architecture: `aarch64`
- ARM64 and standard x64 regressions: PASS.

Later hardened E4 deployment SHA `6f8fb938590aa7ddabba96ee3a4c0e108e225d97` passed both standard x64 and native ARM64 CI before real-host validation with `277 passed, 1 warning` on each architecture.

## 5. Real OCI Host Validation

Host:
- Oracle Cloud Infrastructure;
- region: Germany Central (Frankfurt), `eu-frankfurt-1`;
- availability domain: AD-2;
- shape: `VM.Standard.A1.Flex`;
- resources: 1 OCPU / 6 GB RAM;
- image family: Ubuntu 24.04 ARM64;
- observed architecture: `aarch64`.

Immutable deployment SHA:
`6f8fb938590aa7ddabba96ee3a4c0e108e225d97`

Real-host GitHub Actions validation:
- workflow: `E4 Real Host Validation`;
- run number: `4`;
- run ID: `33258520620`;
- job ID: `99116323168`;
- result: `SUCCESS`.

Observed real-host regression/runtime:
- pytest: `277 passed, 2 warnings`;
- project-local database integrity: `OK`;
- `kgm-monitor.service`: enabled and active;
- service user/group: `kgm`;
- project-local ExecStart/WorkingDirectory: PASS;
- no public HTTP/HTTPS application listener: PASS;
- runtime storage: `PROJECT_LOCAL_ONLY`.

The two host warnings were non-blocking deprecation warnings and did not change the gate result.

## 6. Real Reboot and Recovery Validation

Prepared boot ID:
`a9a984b3-910e-424a-b86c-c2a59240044e`

Verified post-reboot boot ID:
`5dae868e-5672-4674-8b55-0adcfcb4f520`

Validated:
- Linux boot ID changed: true;
- systemd service enabled after reboot: true;
- systemd service active after reboot: true;
- prepared interrupted run `e4-reboot-run-6196246cd89a` recovered: true;
- expected recovery status: FAILED;
- expected recovery error: `interrupted runtime recovered`;
- due watch resumed: true;
- resumed run `run-26ee9f2b851d4228ae13fe482b66115f` status: COMPLETED;
- controlled live collection success observed: true;
- sentinel watch disabled after validation: true;
- reboot recovery gate: PASS;
- final host runtime gate: PASS.

Evidence artifact:
- artifact ID: `9716593540`;
- name: `e4-host-evidence-6f8fb938590aa7ddabba96ee3a4c0e108e225d97`;
- digest: `sha256:b1258d91eab65702009af48e4e1844bf7392221c7050c268ef7a37840944315c`.

## 7. OCI Network Evidence

Observed VCN/subnet:
- `kgm-e4-vcn`;
- `kgm-e4-public-subnet`;
- exactly one attached Security List observed: `Default Security List for kgm-e4-vcn`.

Observed ingress rules:
- `0.0.0.0/0` -> TCP 22: ALLOW;
- `0.0.0.0/0` -> ICMP type 3/code 4: ALLOW;
- `10.0.0.0/16` -> ICMP type 3: ALLOW.

Observed ingress conclusions:
- TCP 80: ABSENT;
- TCP 443: ABSENT;
- TCP/UDP 111: ABSENT at OCI Security List;
- database/API ingress: no rule observed;
- SSH TCP 22 remains open from `0.0.0.0/0`.

Observed egress:
- destination `0.0.0.0/0`;
- All Protocols;
- all destination ports.

Host-local listener observation included ports 22 and 111. The OCI inspection confirms no Security List ingress rule for 111, so the host-local observation is not treated as proof of Internet reachability.

## 8. Owner-Approved Temporary Security Exception

On 2026-08-29 the owner explicitly decided to keep public SSH TCP/22 open from `0.0.0.0/0` during active project development because administration may occur from different networks and changing public IP addresses.

The owner also deferred broad-egress least-privilege hardening until full project completion, subject to a compatibility review for operating-system maintenance and approved monitoring adapters.

Accordingly:
- do not narrow/remove current public SSH during active development unless the owner changes the decision;
- do not tighten current broad egress without a separate compatibility review;
- revisit SSH restriction, OCI Bastion/private administration and egress least privilege at final project hardening;
- classify the current network state as a temporary owner-approved development exception, not final production hardening.

## 9. E4 Gate Classification

Pre-deployment engineering gates:
- concrete service entry point: PASS;
- PROJECT_LOCAL_ONLY runtime path: PASS;
- backup/restore integrity: PASS;
- non-overwriting restore policy: PASS;
- systemd unit static verification: PASS;
- native ARM64 compatibility: PASS;
- full ARM64 regression: PASS;
- no inbound API/dashboard/database exposure in monitoring unit: PASS.

Real-host gates:
- OCI ARM64 VM provisioned and reachable: PASS;
- Ubuntu 24.04 host bootstrap: PASS;
- service user/repository installation: PASS;
- full test suite on actual host: PASS;
- project-local SQLite integrity/backup validation: PASS;
- systemd enable/start: PASS;
- physical reboot and automatic restart: PASS;
- interrupted-run recovery after actual reboot: PASS;
- due-watch resumption: PASS;
- controlled live source cycle on VM: PASS;
- host runtime gate: PASS;
- OCI Security List evidence captured: PASS;
- no OCI ingress for 80/443/database/API/111: PASS;
- SSH least-privilege hardening: DEFERRED_BY_OWNER_EXCEPTION;
- egress least-privilege hardening: DEFERRED_BY_OWNER_EXCEPTION.

E4 state:

`BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`

Supporting state:

`E4_REAL_HOST_VALIDATED / OCI_FIREWALL_EVIDENCED / SECURITY_HARDENING_DEFERRED`

This closes the E4 validation workstream for active development. It does not approve production/live operation.

## 10. Invariants and Non-Claims

- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared runtime database;
- no database network exposure;
- no API/dashboard exposure is introduced by the E4 monitoring service;
- public web data is not substituted for missing persisted backend state;
- GDELT remains discovery/index metadata rather than independent factual corroboration;
- source failures remain visible;
- graph, forecast, coverage and report layers do not inflate verification truth;
- E3 Action API remains code-validated but NOT_CONNECTED until a separate HTTPS connection gate;
- public GPT sharing remains DEFERRED;
- shared production runtime remains NOT_APPROVED;
- production/live remains NOT_OPERATIONAL;
- no ROADMAP Phase 12 or M14 is created.

## 11. Next Engineering Activity

Continue the approved post-pilot sequence with E5 Admin Read-Only Dashboard.

E5 must remain owner/admin-only and read-only, reuse persisted canonical state rather than create a parallel backend, preserve PROJECT_LOCAL_ONLY storage, and avoid any public unauthenticated dashboard exposure.
