# E4 Real Host Automation

Status: REAL_HOST_VALIDATED_FIREWALL_EVIDENCE_PENDING
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
- retry cleanup is fail-closed and allowed only for validated pre-service bootstrap residue with no runtime database and no installed/active service;
- application code remains root-owned while the service account receives write access only to project-local runtime data;
- no HTTP/HTTPS server is launched;
- no database listener is opened;
- OCI cloud firewall remains a separately evidenced gate.

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
- run: `33258520620`
- job: `99116323168`
- run result: `SUCCESS`

Real OCI ARM64 host observations:
- architecture: `aarch64`
- OS: Ubuntu 24.04
- host pytest: `277 passed, 2 warnings`
- project-local database integrity: `OK`
- `kgm-monitor.service`: enabled and active
- service user/group: `kgm`
- no public HTTP/HTTPS listener: PASS
- runtime storage: `PROJECT_LOCAL_ONLY`

Real reboot/recovery evidence:
- prepared boot ID: `a9a984b3-910e-424a-b86c-c2a59240044e`
- verified boot ID: `5dae868e-5672-4674-8b55-0adcfcb4f520`
- `boot_id_changed`: true
- interrupted run recovered: true
- due watch resumed: true
- resumed run status: `COMPLETED`
- service active after reboot: true
- service enabled after reboot: true
- sentinel watch disabled after validation: true
- controlled live collection success observed: true
- reboot recovery gate: PASS
- final host runtime gate: PASS

Evidence artifact:
- artifact ID: `9716593540`
- artifact name: `e4-host-evidence-6f8fb938590aa7ddabba96ee3a4c0e108e225d97`
- digest: `sha256:b1258d91eab65702009af48e4e1844bf7392221c7050c268ef7a37840944315c`
- retention: 30 days from the validation run

## Explicit non-claims

The successful real-host workflow proves the owner-only host runtime and reboot/recovery behavior for the validated SHA.

It does not prove OCI Security List/NSG state because a host-local check cannot establish the external cloud perimeter.
It does not mark the canonical unattended cloud deployment complete until separate cloud-firewall evidence exists.
It does not mark production/live operational.
It does not approve public GPT sharing or a shared production runtime.

## Current gate

`E4_REAL_HOST_VALIDATED / OCI_FIREWALL_EVIDENCE_PENDING`

Next required gate: capture and verify OCI Security List/NSG evidence showing no inbound 80/443 or database/API exposure, with SSH 22 restricted or removed after validation and outbound access limited to approved monitoring needs.
