# E4 Real Host Automation

Status: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION
Project: K-Geopolitical Monitor
Date: 2026-08-29

## Purpose

Automate and validate the real-host portion of E4 after one manual OCI VM provisioning step.

The automation is intentionally limited to an owner-only Ubuntu 24.04 ARM64 pilot and preserves PROJECT_LOCAL_ONLY storage.

This workstream does not create ROADMAP Phase 12 or M14 and does not mark production/live operational.

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
- retry cleanup is fail-closed and allowed only for validated pre-service bootstrap residue with no runtime database and no installed/active service;
- application code remains root-owned while the service account receives write access only to project-local runtime data;
- no HTTP/HTTPS server is launched by the E4 monitoring workflow;
- no database listener is opened by the application;
- OCI cloud firewall is separately evidenced from host-local state.

## Automated validation sequence

1. resolve an immutable deployment SHA;
2. validate native aarch64 and Ubuntu 24.04;
3. validate any prior pre-service residue fail-closed;
4. clone and deploy the exact SHA;
5. run the validated E4 bootstrap;
6. verify pre-reboot host runtime state;
7. create deterministic interrupted-run sentinel state;
8. issue a real `systemctl reboot`;
9. wait for pinned SSH recovery;
10. prove Linux `boot_id` changed;
11. prove systemd auto-start;
12. prove interrupted-run recovery;
13. prove due-watch resumption;
14. re-run final host runtime gate;
15. collect JSON evidence into a GitHub Actions artifact.

## Real-host validation result

Validated deployment SHA:
`6f8fb938590aa7ddabba96ee3a4c0e108e225d97`

GitHub Actions:
- workflow: `E4 Real Host Validation`
- run number: `4`
- run ID: `33258520620`
- job ID: `99116323168`
- result: `SUCCESS`

Real OCI ARM64 host observations:
- provider: Oracle Cloud Infrastructure;
- region: `eu-frankfurt-1`;
- shape: `VM.Standard.A1.Flex`, 1 OCPU / 6 GB RAM;
- architecture: `aarch64`;
- OS: Ubuntu 24.04;
- host pytest: `277 passed, 2 warnings`;
- project-local database integrity: `OK`;
- `kgm-monitor.service`: enabled and active;
- service user/group: `kgm`;
- no public HTTP/HTTPS application listener: PASS;
- runtime storage: `PROJECT_LOCAL_ONLY`.

Real reboot/recovery evidence:
- prepared boot ID: `a9a984b3-910e-424a-b86c-c2a59240044e`;
- verified boot ID: `5dae868e-5672-4674-8b55-0adcfcb4f520`;
- `boot_id_changed`: true;
- interrupted run ID: `e4-reboot-run-6196246cd89a`;
- interrupted run recovered: true;
- due watch resumed: true;
- resumed run ID: `run-26ee9f2b851d4228ae13fe482b66115f`;
- resumed run status: `COMPLETED`;
- service active after reboot: true;
- service enabled after reboot: true;
- sentinel watch disabled after validation: true;
- controlled live collection success observed: true;
- reboot recovery gate: PASS;
- final host runtime gate: PASS.

Evidence artifact:
- artifact ID: `9716593540`;
- name: `e4-host-evidence-6f8fb938590aa7ddabba96ee3a4c0e108e225d97`;
- digest: `sha256:b1258d91eab65702009af48e4e1844bf7392221c7050c268ef7a37840944315c`;
- retention: 30 days from the validation run.

## OCI cloud-perimeter evidence

Observed VCN/subnet:
- VCN: `kgm-e4-vcn`;
- subnet: `kgm-e4-public-subnet`;
- one attached Security List observed: `Default Security List for kgm-e4-vcn`.

Observed ingress:
- `0.0.0.0/0` -> TCP 22: ALLOW;
- `0.0.0.0/0` -> ICMP type 3/code 4: ALLOW;
- `10.0.0.0/16` -> ICMP type 3: ALLOW;
- inbound TCP 80: ABSENT;
- inbound TCP 443: ABSENT;
- inbound TCP/UDP 111: ABSENT at OCI Security List;
- database/API ingress: no rule observed.

Observed egress:
- destination `0.0.0.0/0`;
- protocol: All Protocols;
- destination ports: all.

The host-local observation of listener port 111 does not imply Internet reachability; OCI perimeter inspection showed no ingress rule for 111.

## Owner-approved temporary security exception

On 2026-08-29 the owner explicitly decided to keep public SSH TCP/22 open from `0.0.0.0/0` during active development because administration may occur from changing networks and IP addresses.

The owner also deferred broad-egress least-privilege hardening until project completion so active development, package maintenance and approved monitoring adapters are not broken without a separate compatibility review.

Therefore:
- do not narrow/remove TCP/22 during active development unless the owner changes this decision;
- do not tighten the current broad egress rule without a separate compatibility review;
- revisit SSH restriction/Bastion/private administration and egress least privilege during final project security hardening;
- treat this as a documented temporary development exception, not production-grade perimeter hardening.

## Explicit non-claims

The successful workflow and OCI inspection prove the owner-only E4 host runtime, reboot/recovery behavior and observed Security List state for this validation checkpoint.

They do not prove:
- production readiness;
- public GPT readiness;
- shared production runtime approval;
- complete global coverage;
- final least-privilege network hardening.

The E3 Action API remains code-validated but not connected to the private GPT, and no HTTPS backend/dashboard deployment is approved by E4.

## Current gate

Use state:

`E4_BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`

Supporting state:

`E4_REAL_HOST_VALIDATED / OCI_FIREWALL_EVIDENCED / SECURITY_HARDENING_DEFERRED`

Production/live remains `NOT_OPERATIONAL`.

## Next activity

Continue the approved post-pilot execution sequence with E5 Admin Read-Only Dashboard while preserving PROJECT_LOCAL_ONLY storage and keeping the dashboard owner/admin-only and read-only.

At full project completion, perform a final network-security review covering SSH exposure, Bastion/private administration alternatives, egress least privilege, public listeners, OCI Security Lists/NSGs and production launch criteria.
