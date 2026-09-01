# E9A Deployment and Security Hardening Runbook

Status: OWNER_ONLY_CANDIDATE_BASELINE
Date: 2026-09-01
Project: K-Geopolitical Monitor
Scope: `E9A.5_DEPLOYMENT_SECURITY_HARDENING`

This runbook defines the owner-only deployment/security baseline for the existing OCI unattended runtime. It does not authorize production/live operation, public ingress, shared runtime storage, Business migration, GPT publication, public sharing, or activation of a new external provider.

## 1. Runtime privilege boundary

Canonical service unit:
`deployment/systemd/kgm-monitor.service`

Required service boundary:
- dedicated system account `kgm:kgm` with no login shell;
- deployed code, virtual environment and service unit remain root-owned/read-only to the service;
- only `/opt/k-geopolitical-monitor/data` is service-writable;
- `UMask=0077` protects newly created runtime state;
- Python bytecode writes outside the runtime data tree are disabled;
- no Linux capabilities are granted to the service;
- systemd sandboxing protects devices, home, kernel tunables/modules/logs, control groups, clock and hostname;
- namespace creation, realtime scheduling and SUID/SGID creation are restricted;
- runtime address families are limited to UNIX/IPv4/IPv6 because approved collection requires outbound network access;
- no public API, dashboard, database or socket listener is launched by the monitoring unit.

Do not broaden `ReadWritePaths` to the project root or `/opt` merely to solve a runtime write error. Investigate the attempted write first.

## 2. Repository and secret hygiene

Repository rules:
- secrets, tokens, passwords, private keys and credentials must never be committed;
- runtime databases and local runtime data are ignored by Git;
- `.env`, SSH material and common private-key formats are ignored by Git;
- GitHub Actions credentials remain platform secrets;
- SSH host-key checking remains enabled and uses a pinned `known_hosts` value;
- do not print private keys, authorization headers, environment dumps or secret-bearing command lines to logs.

Targeted repository searches are useful evidence but are not proof that every historical or encoded secret is absent. Candidate validation must combine repository review, GitHub secret-storage policy and host/log review.

## 3. Public SSH exception and administrative alternatives

Current development exception:
- OCI public SSH TCP/22 from `0.0.0.0/0` may remain temporarily enabled while active engineering and GitHub-hosted real-host validation require it.

This exception is not accepted as final production security.

Preferred candidate/admin alternatives, in order of architectural simplicity:
- restrict TCP/22 to a trusted owner administration CIDR when a stable source is available;
- use OCI Bastion/private endpoint administration if adopted by a separate infrastructure decision;
- remove public SSH entirely when a tested private administration path exists.

Do not remove the only functioning administration path before an alternative is validated. Do not activate OCI Bastion or another provider/service implicitly from this runbook.

## 4. Outbound network requirements

### Runtime collection

The unattended runtime currently requires:
- DNS/name resolution;
- outbound HTTPS for approved source adapters;
- currently implemented live destinations include GDELT DOC 2.0 and the Council of the EU / European Council press-release RSS feed.

The runtime transport requires HTTPS and does not use source credentials for these adapters.

### Deployment and maintenance

Administrative bootstrap/update activity additionally requires network access to:
- Ubuntu package repositories;
- GitHub repository endpoints;
- Python package indexes/files used by the approved dependency installation process.

These maintenance flows are distinct from unattended collection traffic.

Current broad outbound egress is a development exception. Before a final production/live launch decision, E9A.6 must record real-host/network evidence and determine a maintainable least-privilege rule. Fixed destination IP allowlists should not be assumed safe or stable for public source/CDN endpoints without measurement.

## 5. Emergency kill and rollback

Emergency containment procedure:

1. Stop monitoring:
   `sudo systemctl stop kgm-monitor.service`
2. If continued automatic start is unsafe, disable it:
   `sudo systemctl disable kgm-monitor.service`
3. Verify the service is inactive and no second unattended instance is running.
4. Preserve `/opt/k-geopolitical-monitor/data`; do not delete or overwrite the canonical database as a containment shortcut.
5. Run SQLite integrity and create/verify a project-local backup before any state-changing repair when the database is readable.
6. Roll code back only to a reviewed immutable commit/deployment state. Do not use an unreviewed in-place update against the live canonical runtime.
7. Re-enable/start only after the failure cause, writable-path boundary and database integrity are understood.

If network compromise is suspected, cloud firewall/NSG containment may be applied separately. Avoid removing the only owner administration path unless an alternative is already verified.

## 6. Monitoring failure isolation

Security/failure boundary requirements:
- one source adapter failure remains visible as a failed source attempt and must not be converted into fabricated success;
- failure of Start.me or any other non-canonical operator tool must not affect KGM runtime execution;
- monitoring failure must not cause writes to another project's store;
- systemd restart behavior remains bounded by `StartLimitIntervalSec` / `StartLimitBurst`;
- runtime-health labels remain tick-local instrumentation and must not be used to infer unavailable source/coverage/uptime facts;
- no public-web research may substitute for unavailable persisted backend state.

## 7. Public ingress boundary

The monitoring service requires no inbound HTTP/HTTPS/database/API port.

Candidate evidence must continue to show:
- no monitoring listener on public TCP 80/443;
- no exposed SQLite/database listener;
- E3 backend remains not deployed publicly;
- E5 dashboard remains local/protected/read-only/not deployed;
- public SSH is tracked separately as an administration exception rather than described as monitoring ingress.

## 8. Start.me external operator-tool policy

Owner-approved policy:
`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`

Start.me may be used only as a non-canonical operator/OSINT navigation portal for public, non-sensitive material such as public URLs, RSS feeds, source names, categories and public analytical resources.

It must not contain or receive:
- API keys, bearer tokens, passwords or SSH/OCI credentials;
- private backend endpoints or secret-bearing URLs;
- canonical database/runtime state;
- private findings/alerts or non-public project documents;
- personal or other sensitive data.

Start.me is not a runtime dependency, evidence store, provenance store, source-of-truth or monitoring-coverage authority. Its availability cannot strengthen KGM verification or coverage status.

## 9. Remaining E9A.6 security evidence

The following remain explicit E9A.6 candidate-gate evidence items:
- real-host verification that the hardened unit starts and operates normally;
- real-host verification of effective service properties and exact writable paths;
- OCI Security List/NSG evidence for unintended public ingress;
- disposition of public SSH TCP/22 from `0.0.0.0/0`;
- measured/approved outbound egress policy;
- host/log review for accidental secret exposure;
- kill/rollback exercise where practical;
- full x64/native ARM64/real-host regression and DR validation matrix.

Until those gates are completed:
`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = NOT_YET_ESTABLISHED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`
