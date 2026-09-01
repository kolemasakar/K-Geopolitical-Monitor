# E9A.5 Deployment and Security Hardening Result

Status: BASELINE_REGRESSION_VALIDATED_WITH_REAL_HOST_NETWORK_EVIDENCE_PENDING_E9A_6
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — Owner-Only Production Runtime Hardening

## Scope

Complete the repository/deployment security-hardening baseline for the existing owner-only OCI unattended runtime without activating public ingress, shared runtime storage, Business migration, GPT publication/public sharing, a public API/dashboard, a new external provider, or production/live operation.

## Implemented Hardening

### systemd least privilege

The canonical monitoring service now preserves the dedicated `kgm:kgm` identity and `/opt/k-geopolitical-monitor/data` as the only explicit service-writable path while adding:
- `PYTHONDONTWRITEBYTECODE=1`;
- `PrivateDevices=true`;
- `ProtectKernelTunables=true`;
- `ProtectKernelModules=true`;
- `ProtectKernelLogs=true`;
- `ProtectControlGroups=true`;
- `ProtectClock=true`;
- `ProtectHostname=true`;
- `LockPersonality=true`;
- `RestrictRealtime=true`;
- `RestrictSUIDSGID=true`;
- `RestrictNamespaces=true`;
- `SystemCallArchitectures=native`;
- `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`;
- empty `CapabilityBoundingSet`;
- empty `AmbientCapabilities`.

Existing controls remain:
- `UMask=0077`;
- `NoNewPrivileges=true`;
- `PrivateTmp=true`;
- `ProtectSystem=strict`;
- `ProtectHome=true`;
- `ReadWritePaths=/opt/k-geopolitical-monitor/data`.

No monitoring HTTP/HTTPS/API/dashboard/database listener was added.

### repository / credential hygiene

A canonical `.gitignore` now excludes common local secret material and runtime state, including:
- `.env` variants;
- `.ssh/`;
- common private-key/certificate formats;
- SSH identity files;
- project-local runtime database formats;
- copied local host evidence directories.

Targeted repository searches did not identify obvious literal private-key or common API-key patterns. This is supporting evidence only and is not represented as an exhaustive historical/encoded-secret proof.

The existing real-host workflow continues to use GitHub Actions secret storage, pinned `known_hosts`, strict SSH host-key checking and restrictive SSH file permissions. No routine key echo or shell tracing was introduced.

### security policy and operations

Added:
- `docs/runbooks/E9A_DEPLOYMENT_SECURITY_HARDENING.md`;
- `tests/test_e9a_security_hardening.py`.

Updated:
- `SECURITY_AND_DATA_POLICY.md`;
- `deployment/systemd/kgm-monitor.service`.

The runbook records:
- exact privilege/writable-path boundary;
- repository/log secret hygiene;
- SSH development exception and Bastion/private-admin alternatives;
- runtime vs maintenance outbound network requirements;
- emergency kill/rollback procedure;
- monitoring failure isolation;
- public-ingress boundary;
- remaining E9A.6 security evidence.

## Start.me Policy

Owner decision recorded:
`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`

Start.me remains a non-canonical operator/OSINT navigation tool only. It is not a runtime dependency, evidence/provenance store, source-of-truth, source registry, persisted monitoring store or coverage authority.

No credentials, private endpoints, canonical runtime state, private findings/alerts, non-public project documents, personal data or other sensitive information are approved for Start.me.

## Network Review

### Required unattended runtime access

Current live acquisition requires:
- DNS/name resolution;
- outbound HTTPS to approved public source adapters, currently including GDELT DOC 2.0 and the Council of the EU / European Council RSS surface.

### Required administrative/deployment access

Bootstrap/update activity additionally requires access to:
- Ubuntu package repositories;
- GitHub repository endpoints;
- Python package indexes/files required by the approved dependency installation process.

Fixed public-source/CDN IP allowlists are not assumed safe or maintainable without real-host measurement.

## Validation Evidence

### x64

GitHub Actions CI:
- run: `33486068223`;
- job: `99786317558`;
- validated HEAD: `802e67b66fe19d6a387789f98c11d52052d9785a`;
- result: SUCCESS;
- full regression: `317 passed, 1 warning`.

### native ARM64

GitHub Actions E4 ARM64 Validation:
- run: `33485986978`;
- job: `99786055273`;
- validated hardening/test HEAD: `888932b8e9bbe65c231fb5d0ed18be01b3a53a0b`;
- native architecture: `aarch64`;
- result: SUCCESS;
- full regression: `317 passed, 1 warning`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- `systemd-analyze verify`: PASS.

The later documentation-only commits do not alter the already validated runtime/test/deployment files.

## Commits in the E9A.5 Baseline

- `f3548f2e373536fbaf8281fe78f145df895105a0` — Harden local secret and runtime ignore policy.
- `9cd6a63d32b75a0c87d8673cb41a53b19c93c894` — Harden E9A systemd runtime sandbox.
- `888932b8e9bbe65c231fb5d0ed18be01b3a53a0b` — Add E9A deployment security regression contract.
- `0ac687d92ed92fa71a205ba4b195fc2b25f34539` — Document E9A deployment security runbook.
- `802e67b66fe19d6a387789f98c11d52052d9785a` — Define E9A owner-only security and Start.me data policy.

## Remaining Explicit Security Exceptions / Evidence for E9A.6

These are not production acceptance:
- public SSH TCP/22 from `0.0.0.0/0` remains a temporary development/real-host-validation exception;
- broad outbound egress remains a temporary development exception;
- effective hardened systemd properties and exact writable paths still require real OCI-host validation after deployment of this baseline;
- refreshed OCI Security List/NSG evidence for absence of unintended public ingress remains required;
- host/journal/log review for accidental secret exposure remains required;
- a practical stop/disable/rollback exercise remains to be evidenced where safe;
- clean-host/project-local restore drill and measured RPO/RTO remain E9A.6 work from E9A.3;
- no off-host backup provider has been activated.

Preferred SSH disposition for the candidate gate is to restrict owner administration to a trusted CIDR or a separately approved private/Bastion administration path, then remove unrestricted public SSH when that replacement is proven. No Bastion/provider activation is authorized by this result.

## Architecture / Truth Boundaries

PASS at the repository/regression level:
- `PROJECT_LOCAL_ONLY` remains unchanged;
- no shared/mixed canonical runtime storage;
- no public API/dashboard deployment;
- no Business migration;
- no GPT publication/public sharing;
- no new external provider activation;
- monitoring failure remains visible/fail-isolated;
- runtime-health semantics do not promote coverage/verification/uptime claims;
- public-web research is not a substitute for unavailable persisted backend state.

## Gate Decision

`E9A.5_DEPLOYMENT_SECURITY_HARDENING = BASELINE_REGRESSION_VALIDATED_WITH_REAL_HOST_NETWORK_EVIDENCE_PENDING_E9A_6`

E9A.5 software/configuration/policy regression is green on x64 and native ARM64. Real-host/network/security-exception disposition belongs to the final E9A.6 validation matrix and is not claimed complete here.

`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = NOT_YET_ESTABLISHED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

Next engineering subgate:
`E9A.6_VALIDATION_MATRIX`
