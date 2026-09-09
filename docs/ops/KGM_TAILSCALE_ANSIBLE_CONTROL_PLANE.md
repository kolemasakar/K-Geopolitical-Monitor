# KGM Tailscale + Ansible Control Plane

Status: **ACCEPTED / OPERATIONAL**

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

## Current decision

The KGM Tailscale + GitHub Actions OIDC + Tailscale SSH + Ansible control plane is accepted for normal remote operational control.

KGM SentinelX is still enrolled but parked and is no longer required for normal KGM operations. Any retirement/removal of that parked SentinelX enrollment is a separate cleanup decision.

KRC-Cobalt remains outside this acceptance and on implementation HOLD until separately reviewed and approved.

## Version baselines

- KGM Tailscale server: `1.102.3`
- Tailscale GitHub Action: `tailscale/github-action@v4`
- Ansible control runtime: `ansible-core==2.20.9`
