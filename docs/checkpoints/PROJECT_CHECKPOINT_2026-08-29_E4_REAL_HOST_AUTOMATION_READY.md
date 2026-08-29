# Project Checkpoint - 2026-08-29 E4 Real Host Automation Ready

Status: CONTROL_STATE_RECOVERY_POINT
Project: K-Geopolitical Monitor
Repository: kolemasakar/K-Geopolitical-Monitor
Branch: main
Checkpoint date: 2026-08-29
Anchor E4 host package checkpoint: 14e7a662b63259ca6e705113147fb77a2b1e370c
Automation implementation commit: b20ec49bdb522111b4ba029f791a157fcf3d9f9f

This checkpoint records completion and CI validation of the automation needed to validate a manually provisioned OCI ARM64 host. It does not claim that a VM exists or that the real-host gate has passed.

## Canonical State

- E1: BASELINE_VALIDATED
- E2: BASELINE_VALIDATED
- E3: BASELINE_VALIDATED_LOCAL_READ_ONLY
- E4 engineering baseline: VALIDATED
- E4 host deployment package: VALIDATED
- E4 real-host automation: VALIDATED_READY
- OCI VM: NOT_YET_PROVISIONED
- GitHub E4 SSH secrets: MANUAL_OWNER_ACTION_PENDING
- real host reboot/recovery gate: NOT_YET_EXECUTED
- OCI external firewall gate: NOT_YET_EVIDENCED
- unattended cloud runtime: NOT_DEPLOYED
- production/live: NOT_OPERATIONAL
- runtime storage: PROJECT_LOCAL_ONLY
- public GPT sharing: DEFERRED
- shared production runtime: NOT_APPROVED
- Phase 12: NOT_CREATED
- M14: NOT_CREATED / NOT_APPROVED

## New Artifacts

- `.github/workflows/e4-real-host-validation.yml`
- `docs/runbooks/E4_OCI_REAL_HOST_PROVISIONING.md`
- `docs/implementation/E4_REAL_HOST_AUTOMATION.md`
- `tests/test_e4_real_host_workflow.py`

## Validation Anchors

Automation implementation commit:
- `b20ec49bdb522111b4ba029f791a157fcf3d9f9f` - Add E4 OCI real-host validation automation

Standard x64 CI:
- run: `33248924585`
- job: `99091099878`
- result: SUCCESS
- pytest: 275 passed, 1 warning in 28.39s

Native ARM64 CI:
- run: `33248924591`
- job: `99091099853`
- runner: `ubuntu-24.04-arm`
- observed architecture: `aarch64`
- result: SUCCESS
- pytest: 275 passed, 1 warning in 26.86s
- bootstrap shell/validator CLI smoke: PASS
- unattended one-tick smoke: PASS
- systemd unit contract: PASS

Automation gate:
`E4_REAL_HOST_AUTOMATION_READY`

## Manual Owner Inputs Required

Provision one OCI instance with:
- Ubuntu 24.04 LTS standard Arm image;
- `VM.Standard.A1.Flex`;
- 1 OCPU;
- 6 GB RAM;
- public IPv4 for validation;
- dedicated E4 SSH key;
- Ubuntu SSH user `ubuntu`.

Then create these GitHub Actions repository secrets directly in GitHub:
- `E4_HOST`
- `E4_SSH_PRIVATE_KEY`
- `E4_SSH_KNOWN_HOSTS`

Never place the SSH private key into chat or repository content.

## Automated Gate After Manual Provisioning

Run workflow:
`E4 Real Host Validation`

It will:
- deploy an immutable SHA;
- bootstrap the unattended service;
- validate host state;
- create interrupted-run sentinel state;
- reboot the real VM;
- verify boot_id change;
- verify systemd restart;
- verify interrupted-run recovery;
- verify due-watch continuation;
- collect evidence artifacts.

## Remaining External Gate

OCI Security List/NSG configuration must still be evidenced separately after the workflow because host-local inspection cannot prove the cloud perimeter.

Required perimeter truth:
- no inbound 80;
- no inbound 443;
- no exposed database port;
- SSH 22 restricted or removed after validation;
- outbound monitoring access only as required by approved adapters.

## Exact Resume Point

Resume from manual OCI VM provisioning using:
`docs/runbooks/E4_OCI_REAL_HOST_PROVISIONING.md`

After the VM and GitHub secrets exist, launch `.github/workflows/e4-real-host-validation.yml` and inspect the resulting workflow/artifact evidence before changing any E4 deployment status.
