# Project Checkpoint - 2026-08-29 E4 Real Host Validated

Status: CONTROL_STATE_RECOVERY_POINT
Project: K-Geopolitical Monitor
Repository: kolemasakar/K-Geopolitical-Monitor
Branch: main
Checkpoint date: 2026-08-29
Validated deployment SHA: 6f8fb938590aa7ddabba96ee3a4c0e108e225d97

This checkpoint records successful execution of the E4 real-host workflow on the owner-only OCI Ubuntu 24.04 ARM64 pilot and subsequent OCI Security List inspection. It records host runtime, reboot/recovery, and observed cloud-perimeter facts. Production/live is not marked operational.

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
- OCI external firewall evidence: CAPTURED
- OCI ingress 80/443 and database/API exposure: ABSENT
- OCI SSH TCP/22: OPEN_FROM_0.0.0.0/0_BY_OWNER_DECISION
- OCI egress: 0.0.0.0/0 ALL_PROTOCOLS / ALL_PORTS
- network hardening: DEFERRED_UNTIL_PROJECT_COMPLETION_BY_OWNER_DECISION
- canonical unattended cloud deployment: REAL_HOST_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION
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

## OCI Cloud-Perimeter Evidence

Observed VCN/subnet:
- VCN: `kgm-e4-vcn`
- subnet: `kgm-e4-public-subnet`
- attached Security Lists: exactly one observed, `Default Security List for kgm-e4-vcn`

Observed ingress rules:
- `0.0.0.0/0` -> TCP destination port 22: ALLOW
- `0.0.0.0/0` -> ICMP type 3/code 4: ALLOW
- `10.0.0.0/16` -> ICMP type 3: ALLOW

Observed ingress conclusions:
- inbound TCP 80: ABSENT
- inbound TCP 443: ABSENT
- inbound TCP/UDP 111: ABSENT at OCI Security List
- database/API ingress: no rule observed
- SSH TCP 22 remains reachable from `0.0.0.0/0`

Observed egress rule:
- destination `0.0.0.0/0`
- IP protocol: All Protocols
- destination ports: all
- effect: all outbound traffic allowed by the Security List

## Security Boundary Preserved

- SSH uses a pinned host key.
- SSH private key remains outside repository content and chat.
- no HTTP/HTTPS server was launched by the E4 workflow.
- no database listener was opened by the application.
- code is root-owned after bootstrap.
- service user `kgm` owns the project-local runtime data tree.
- production/live remains `NOT_OPERATIONAL`.

Host-local listener observation showed ports 22 and 111. OCI perimeter inspection confirms no ingress rule for port 111. Port 22 is intentionally left open from `0.0.0.0/0` at this stage.

## Owner Security Exception / Deferred Hardening

On 2026-08-29 the owner explicitly decided not to restrict or close public SSH access during active project development because administration may occur from changing networks/IP addresses.

Therefore:
- do not remove or narrow the current TCP/22 `0.0.0.0/0` ingress rule during the current development phase unless the owner changes this decision;
- do not tighten the current broad egress rule during the current development phase without a separate compatibility review;
- revisit SSH ingress restriction, Bastion/private administration options, and egress least-privilege hardening after full project completion;
- treat the current network configuration as a documented temporary security exception, not as final production hardening.

This exception does not convert the system to `PRODUCTION_LIVE` and does not prove production-grade perimeter hardening.

## Current Gate

Use state:

`E4_REAL_HOST_VALIDATED / OCI_FIREWALL_EVIDENCED / SECURITY_HARDENING_DEFERRED`

Development may continue under the documented owner-approved temporary security exception.

Do not use `PRODUCTION_LIVE` or `GLOBAL_COVERAGE` based on this validation.

## Exact Resume Point

1. Continue the project roadmap after E4 real-host validation.
2. Preserve current SSH and egress configuration unless the owner explicitly changes the temporary exception.
3. At full project completion, perform final network-security hardening review.
4. That final review must cover SSH exposure, Bastion/private administration alternatives, egress least privilege, public listeners, OCI Security Lists/NSGs, and production launch criteria.
