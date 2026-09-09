# KGM Tailscale + Ansible Control Plane — Acceptance Record

Date: 2026-09-09
Status: **ACCEPTED / OPERATIONAL**

## Accepted architecture

```text
GitHub workflow_dispatch
  -> GitHub OIDC federated identity
  -> ephemeral Tailscale node tagged tag:github-actions
  -> tailnet grant: TCP/22 only to tag:kgm
  -> Tailscale SSH
  -> OS user kgmops
  -> bounded Ansible playbook
  -> exact kgm-monitor service operations
```

K-Trader remains the dominant SentinelX-managed host. This KGM control plane is independent of the SentinelX Free 1/1 operational-host limit.

## Live server baseline

- KGM Tailscale address: `100.102.136.23`
- KGM Tailscale version observed at enrollment: `1.102.3`
- Tailscale tag: `tag:kgm`
- GitHub runner tag: `tag:github-actions`
- Ansible runtime: `ansible-core==2.20.9`
- dedicated OS identity: `kgmops`
- deployed KGM application SHA observed by acceptance runs: `b31b2136b5fe982d0b63b0135479b1549041906c`

## Security boundary validated

- `kgmops` is not in the `docker` group;
- `kgmops` is not in the `kgm` application group;
- runtime DB `/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db` is unreadable to `kgmops`;
- arbitrary root escalation through `sudo -n /bin/bash` is denied;
- sudo remains bounded to exact `kgm-monitor.service` status/restart checks and the bounded KGM journal helper;
- Git repository ownership was not changed;
- Git safe-directory trust is not persisted; the read-only SHA probe uses a per-command `git -c safe.directory=...` override only;
- no direct Docker access is granted;
- existing owner SSH remains the recovery/bootstrap channel.

## Health acceptance

Workflow: `KGM Tailscale Ansible Control`

Run: `34385314619`

Result: **PASS**

Observed:

- GitHub OIDC authentication: PASS;
- ephemeral Tailscale runner connection: PASS;
- peer discovery for `kgm-e4-owner-pilot`: PASS;
- Tailscale path to `100.102.136.23`: PASS;
- Tailscale SSH as `kgmops`: PASS;
- Ansible execution: PASS;
- service before: `active`;
- service after: `active`;
- runtime DB read: denied;
- arbitrary root escalation: denied;
- restart task: skipped as required for `operation=health`;
- recap: `ok=10 changed=0 unreachable=0 failed=0 skipped=1`;
- terminal gate: `KGM_TAILSCALE_ANSIBLE_CONTROL=PASS`.

## Restart acceptance

Workflow: `KGM Tailscale Ansible Control`

Run: `34385726741`

Result: **PASS**

Observed:

- OIDC/Tailscale/SSH path: PASS;
- service before restart: `active`;
- exact bounded restart of `kgm-monitor.service`: executed;
- service after restart: `active`;
- runtime DB read: denied;
- arbitrary root escalation: denied;
- recap: `ok=11 changed=1 unreachable=0 failed=0 skipped=0`;
- terminal gate: `KGM_TAILSCALE_ANSIBLE_CONTROL=PASS`;
- operation reported: `restart`.

The restart command completed successfully and the service returned to active state.

## Acceptance decision

The KGM Tailscale + GitHub Actions OIDC + Tailscale SSH + Ansible control plane is accepted for operational use.

No KRC-Cobalt deployment is authorized by this acceptance. Expansion to another VM requires a separate review and approval.

The parked KGM SentinelX enrollment is now redundant for normal operation, but retirement/removal should be handled as a separate cleanup change so it is not coupled to control-plane acceptance.
