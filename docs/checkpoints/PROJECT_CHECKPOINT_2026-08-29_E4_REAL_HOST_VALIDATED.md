# Project Checkpoint - 2026-08-29 E4 Real Host Validated

Status: CONTROL_STATE_RECOVERY_POINT
Project: K-Geopolitical Monitor
Repository: kolemasakar/K-Geopolitical-Monitor
Branch: main
Checkpoint date: 2026-08-29
Validated deployment SHA: 6f8fb938590aa7ddabba96ee3a4c0e108e225d97

This checkpoint records successful execution of the E4 real-host workflow on the owner-only OCI Ubuntu 24.04 ARM64 pilot. It records host runtime and reboot/recovery facts only. It does not claim that the OCI external firewall perimeter has been verified and does not mark production/live operational.

## Canonical State

- E1: BASELINE_VALIDATED
- E2: BASELINE_VALIDATED
- E3: BASELINE_VALIDATED_LOCAL_READ_ONLY
- E4 engineering baseline: VALIDATED
- E4 host deployment package: VALIDATED
- E4 real-host automation: VALIDATED
- OCI VM: PROVISIONED / RUNNING
- real SSH trust: VERIFIED
- GitHub E4 SSH secrets: CONFIGURED
- E4 immutable deployment: VERIFIED
- E4 bootstrap on real ARM64 host: PASS
- E4 pre-reboot host runtime gate: PASS
- E4 real reboot/recovery gate: PASS
- E4 final host runtime gate: PASS
- controlled live collection during recovery validation: SUCCESS_OBSERVED
- OCI external firewall gate: NOT_YET_EVIDENCED
- canonical unattended cloud deployment: FIREWALL_EVIDENCE_PENDING
- production/live: NOT_OPERATIONAL
- runtime storage: PROJECT_LOCAL_ONLY
- public GPT sharing: DEFERRED
- shared production runtime: NOT_APPROVED
- Phase 12: NOT_CREATED
- M14: NOT_CREATED / NOT_APPROVED

## Validated Host

- provider: Oracle Cloud Infrastructure
- region: Germany Central (Frankfurt) / `eu-frankfurt-1`
- availability domain: AD-2
- shape: `VM.Standard.A1.Flex`
- resources: 1 OCPU / 6 GB RAM
- image family: Canonical Ubuntu 24.04 ARM64
- observed runtime architecture: `aarch64`
- observed OS: Ubuntu 24.04
- service: `kgm-monitor.service`
- service user/group: `kgm`
- runtime database: `/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db`
- runtime storage boundary: `PROJECT_LOCAL_ONLY`

## Validation Anchors

GitHub Actions real-host validation:
- workflow: `E4 Real Host Validation`
- run number: `4`
- run ID: `33258520620`
- job ID: `99116323168`
- validated deployment SHA: `6f8fb938590aa7ddabba96ee3a4c0e108e225d97`
- result: `SUCCESS`

Real host regression:
- pytest: `277 passed, 2 warnings`
- database integrity: `OK`
- service enabled: true
- service active: true
- application ExecStart project-local: true
- application WorkingDirectory project-local: true
- no public HTTP/HTTPS listener: PASS

Reboot recovery:
- prepared boot ID: `a9a984b3-910e-424a-b86c-c2a59240044e`
- verified boot ID: `5dae868e-5672-4674-8b55-0adcfcb4f520`
- boot ID changed: true
- interrupted run ID: `e4-reboot-run-6196246cd89a`
- interrupted run recovered: true
- expected recovery status: `FAILED`
- expected recovery error: `interrupted runtime recovered`
- due watch resumed: true
- resumed run ID: `run-26ee9f2b851d4228ae13fe482b66115f`
- resumed run status: `COMPLETED`
- service active after reboot: true
- service enabled after reboot: true
- sentinel watch disabled after validation: true
- controlled live collection success observed: true
- reboot recovery gate: PASS
- final host runtime gate: PASS

Evidence artifact:
- artifact ID: `9716593540`
- name: `e4-host-evidence-6f8fb938590aa7ddabba96ee3a4c0e108e225d97`
- size: 13891 bytes
- digest: `sha256:b1258d91eab65702009af48e4e1844bf7392221c7050c268ef7a37840944315c`
- created: `2026-08-29T14:51:12Z`
- expires: `2026-09-28T14:51:12Z`

## Security Boundary Preserved

- SSH uses a pinned host key.
- SSH private key remains outside repository content and chat.
- no HTTP/HTTPS server was launched by the E4 workflow.
- no database listener was opened by the application.
- code is root-owned after bootstrap.
- service user `kgm` owns the project-local runtime data tree.
- production/live remains `NOT_OPERATIONAL`.

Host-local listener observation showed ports 22 and 111. This does not establish OCI ingress reachability. External cloud perimeter remains a separate evidence gate.

## Remaining External Gate

OCI Security List/NSG state must be captured from the OCI control plane and verified separately.

Required perimeter truth:
- inbound TCP 80: CLOSED / absent;
- inbound TCP 443: CLOSED / absent;
- database/API ingress: CLOSED / absent;
- SSH TCP 22: restricted or removed after validation;
- outbound access: only as required by approved monitoring adapters.

Until that evidence is captured, use state:

`E4_REAL_HOST_VALIDATED / OCI_FIREWALL_EVIDENCE_PENDING`

Do not use `E4_COMPLETE`, `PRODUCTION_LIVE`, or `GLOBAL_COVERAGE`.

## Exact Resume Point

1. Inspect `kgm-e4-vcn` / `kgm-e4-public-subnet` security controls in OCI.
2. Capture Security List and any NSG ingress/egress rules.
3. Prove that 80/443 and database/API ingress are absent.
4. Restrict or remove temporary SSH ingress after validation.
5. Record the cloud-perimeter evidence in the repository.
6. Only then evaluate whether E4 can move from firewall-evidence-pending to complete.
