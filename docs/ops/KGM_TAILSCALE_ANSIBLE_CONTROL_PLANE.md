# KGM Tailscale + Ansible Control Plane

Status: **ACCEPTED / OPERATIONAL / SENTINELX RETIRED**

Date: 2026-09-09

## Strategic role

K-Trader remains the dominant SentinelX-managed production host. KGM uses an independent multi-host-capable management plane so the SentinelX Free 1/1 active-host limit cannot displace K-Trader.

Accepted path:

```text
GitHub workflow_dispatch
  -> GitHub OIDC federated identity
  -> ephemeral Tailscale node tagged tag:github-actions
  -> tailnet policy permits TCP/22 only to tag:kgm
  -> Tailscale SSH as dedicated local user kgmops
  -> pinned ansible-core control playbook
  -> narrow sudoers for kgm-monitor only
```

## Security invariants

- K-Trader SentinelX is unchanged.
- KGM SentinelX has been removed from the KGM host after replacement acceptance.
- `kgmops` is a dedicated unprivileged account.
- `kgmops` is not in `docker`, `kgm`, or other application groups.
- No unrestricted sudo.
- No arbitrary Docker access.
- KGM runtime database is unreadable by `kgmops`.
- Only exact `kgm-monitor.service` systemd status/restart operations and bounded KGM journal access are allowed through sudo.
- GitHub runner is ephemeral and receives only `tag:github-actions`.
- Tailnet policy grants that tag only TCP/22 to `tag:kgm`.
- Tailscale SSH permits that source/destination pair only as OS user `kgmops`.
- Existing owner SSH remains the recovery/bootstrap channel.
- Git repository ownership is unchanged; the read-only SHA probe uses a per-command `safe.directory` override and does not persist Git trust.

## Repository components

- `.github/workflows/tailscale-kgm-bootstrap.yml`
- `.github/workflows/tailscale-kgm-control.yml`
- `ops/tailscale/kgm-tailnet-policy.hujson`
- `ops/ansible/kgm_control.yml`
- `docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE_ACCEPTANCE_2026_09_09.md`
- `docs/ops/KGM_SENTINELX_RETIREMENT_2026_09_09.md`

The former `.github/workflows/sentinelx-kgm-bootstrap.yml` and the one-shot `.github/workflows/sentinelx-kgm-cleanup.yml` were removed after successful retirement to prevent accidental reinstallation or rerun.

## Tailnet policy state

The original unrestricted default policy was replaced before enrollment.

Accepted relationship:

```text
tag:github-actions -> tag:kgm -> TCP/22 only
Tailscale SSH user -> kgmops only
```

The default `src=* / dst=* / ip=*` grant and default self-SSH rule are no longer part of the intended KGM policy.

## KGM server enrollment — PASS

Observed live state:

```text
TAILSCALE_KGM_ENROLL=PASS
TAILSCALE_VERSION=1.102.3
TAILSCALE_IPV4=100.102.136.23
KGM_TAILSCALE_SECURITY_GATES=PASS
```

## GitHub OIDC + Ansible health acceptance — PASS

Run: `34385314619`

- OIDC: PASS
- ephemeral `tag:github-actions`: PASS
- KGM peer discovery: PASS
- Tailscale SSH as `kgmops`: PASS
- Ansible: PASS
- service before: `active`
- service after: `active`
- runtime DB read: denied
- arbitrary root escalation: denied
- restart skipped as required
- recap: `ok=10 changed=0 unreachable=0 failed=0 skipped=1`
- terminal gate: `KGM_TAILSCALE_ANSIBLE_CONTROL=PASS`

## Bounded restart acceptance — PASS

Run: `34385726741`

- OIDC/Tailscale/SSH path: PASS
- service before: `active`
- bounded restart executed
- service after: `active`
- runtime DB read: denied
- arbitrary root escalation: denied
- recap: `ok=11 changed=1 unreachable=0 failed=0 skipped=0`
- terminal gate: `KGM_TAILSCALE_ANSIBLE_CONTROL=PASS`

## KGM SentinelX retirement — PASS

Cleanup run: `34388121721`

Pre-removal audit confirmed the exact retired KGM SentinelX footprint:

- host ID: `host_a2767ee5915c4cfe`
- core SHA: `e1be3162b22a4b0c744e0443c9f9b62f8fdb21a4`
- KGM Tailscale address: `100.102.136.23`
- KGM service active and enabled
- Tailscale active, enabled, online, and tagged `tag:kgm`
- `kgmops` least-privilege gates intact

The cleanup then removed only the KGM SentinelX footprint:

- `sentinelx-cloud-core.service`
- `/etc/sentinelx`
- `/opt/sentinelx-cloud-core`
- `/etc/sudoers.d/sentinelx-kgm`
- `/usr/local/sbin/sentinelx-kgm-journal`
- `/var/lib/sentinelx/uploads`
- local `sentinelx` user/group

Post-removal validation:

```text
KGM_SENTINELX_CLEANUP=PASS
kgm_service=active
kgm_tailscale_ip=100.102.136.23
runtime_db_read=DENIED
kgmops_arbitrary_root=DENIED
```

SentinelX hub inventory after cleanup shows only the operational K-Trader host; KGM is no longer connected/parked.

## Credential hygiene — COMPLETE

Owner-verified in the GitHub repository secrets UI on 2026-09-09:

Removed obsolete secrets:

- `SENTINELX_ENROLL_TOKEN`
- `TS_KGM_AUTH_KEY`

Retained operational/recovery secrets:

- `TS_OAUTH_CLIENT_ID`
- `TS_AUDIENCE`
- `E4_HOST`
- `E4_SSH_PRIVATE_KEY`
- `E4_SSH_KNOWN_HOSTS`

No retained KGM workflow depends on either removed secret.

## Current decision

The KGM Tailscale + GitHub Actions OIDC + Tailscale SSH + Ansible control plane is accepted for normal remote operational control.

KGM SentinelX is retired and its obsolete repository credentials are removed. K-Trader remains the sole SentinelX-managed dominant host.

KRC-Cobalt remains outside this KGM acceptance boundary and must use its own independently authorized control plane.

## Version baselines

- KGM Tailscale server: `1.102.3`
- Tailscale GitHub Action: `tailscale/github-action@v4`
- Ansible control runtime: `ansible-core==2.20.9`

## 2026-09-11 control-plane reconciliation with Sentinel-Remote

The cross-project infrastructure inventory in `kolemasakar/Sentinel-Remote` was revalidated on 2026-09-11. Its canonical `main` at reconciliation time was `ca15f4e6b66daa1eb047be742c4aee8fc6770d02` and records the KGM host as **ACTIVE / OPERATIONAL** with SentinelX intentionally retired.

The absence of `kgm-e4-owner-pilot` from SentinelX or Remote Desktop Commander is therefore **not a KGM recovery/access defect** and must not be treated as an unresolved recovery blocker.

Primary KGM operational path remains:

```text
GitHub Actions
  -> KGM project-scoped GitHub OIDC
  -> ephemeral Tailscale identity / tag:github-actions
  -> tag:kgm / TCP 22 only
  -> Tailscale SSH
  -> kgmops
  -> bounded Ansible
  -> kgm-e4-owner-pilot
```

Canonical live target identity:

```text
host = kgm-e4-owner-pilot
Tailscale IPv4 = 100.102.136.23
OS automation user = kgmops
service = kgm-monitor.service
project root = /opt/k-geopolitical-monitor
runtime DB = /opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db
```

Operational interpretation rules:

- SentinelX is **RETIRED BY DESIGN** for KGM; do not re-enroll it without a new explicit owner-approved architecture decision.
- Remote Desktop Commander is not required for normal KGM control and is not a prerequisite for Phase 19 validation.
- owner SSH remains recovery/bootstrap/break-glass only, not the normal automation path.
- `kgmops` must remain unable to read the runtime database and must not receive arbitrary root authority.
- KGM identities, tags, trust credentials, and privileges must not be reused by K-Trader or KRC.
- for host/control-plane topology, `Sentinel-Remote` is the infrastructure inventory reference; for executable KGM control semantics, the KGM repository workflow and Ansible playbook remain authoritative.

### Phase 19 application

`kgm-e4-owner-pilot` remains the owner-local canonical runtime and real-soak target for Phase 19. The accepted bounded `health` control is a valid fresh live owner-local observation path for P19 evidence.

Current deployed candidate remains:

```text
b31b2136b5fe982d0b63b0135479b1549041906c
```

Documentation-only repository advancement during the soak does not by itself imply runtime-candidate drift or require redeployment. Runtime mutation, restart, baseline/cadence/evaluator/trust-path changes, or SentinelX re-enrollment require their own explicit authorization boundaries.

Owner pause recorded on 2026-09-11: no manual KGM work is planned until `2026-09-13 07:00 Europe/Kyiv`; existing already-authorized safeguards/evidence collection are not broadened by this note.
