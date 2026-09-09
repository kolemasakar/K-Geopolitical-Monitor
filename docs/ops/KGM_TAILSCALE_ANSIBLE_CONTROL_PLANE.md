# KGM Tailscale + Ansible Control Plane

Status: **APPROVED FOR KGM ONLY**

Date: 2026-09-09

## Strategic role

K-Trader remains the dominant SentinelX-managed production host. KGM uses a separate multi-host-capable management plane so the SentinelX Free 1/1 active-host limit cannot displace K-Trader.

Target path:

```text
GitHub-hosted runner
  -> ephemeral Tailscale node tagged tag:github-actions
  -> tailnet policy allows only TCP/22 to tag:kgm
  -> Tailscale SSH as dedicated local user kgmops
  -> pinned ansible-core control playbook
  -> narrow sudoers for kgm-monitor only
```

## Security invariants

- K-Trader SentinelX is unchanged.
- KGM SentinelX may remain enrolled/parked until this replacement path is validated; it is not used by this workflow.
- `kgmops` is a dedicated unprivileged account.
- `kgmops` is not in `docker`, `kgm`, or other application groups.
- No unrestricted sudo.
- No arbitrary Docker access.
- KGM runtime database must remain unreadable by `kgmops`.
- Only exact `kgm-monitor.service` systemd status/restart operations and bounded KGM journal access are allowed through sudo.
- The GitHub runner is ephemeral and receives only the `tag:github-actions` identity.
- Tailnet network policy grants that tag only TCP/22 to `tag:kgm`.
- Tailscale SSH permits that source/destination pair only as OS user `kgmops`.
- Existing owner SSH remains the bootstrap/recovery channel until the new path passes acceptance.

## Repository components

- `.github/workflows/tailscale-kgm-bootstrap.yml`
- `.github/workflows/tailscale-kgm-control.yml`
- `ops/tailscale/kgm-tailnet-policy.hujson`
- `ops/ansible/kgm_control.yml`

## One-time external Tailscale prerequisites

The following values must be created in the owner's Tailscale account; they cannot be generated from the repository alone.

### 1. Tailnet policy

Merge `ops/tailscale/kgm-tailnet-policy.hujson` into the existing tailnet policy. If the tailnet already has `tagOwners`, `grants`, or `ssh` sections, merge entries rather than replacing unrelated rules.

Required tags:

- `tag:kgm`
- `tag:github-actions`

### 2. KGM server enrollment key

Create a tagged auth key allowed to apply `tag:kgm`, then store it in the KGM GitHub repository as encrypted Actions secret:

```text
TS_KGM_AUTH_KEY
```

This key is used only by the existing pinned-SSH bootstrap workflow to enroll the KGM server.

### 3. GitHub workload identity federation

Create a Tailscale federated identity for GitHub Actions with `auth_keys` scope and restrictions appropriate to:

```text
repository: kolemasakar/K-Geopolitical-Monitor
workflow: .github/workflows/tailscale-kgm-control.yml
```

Store its values as repository Actions secrets:

```text
TS_OAUTH_CLIENT_ID
TS_AUDIENCE
```

The control workflow requests GitHub OIDC with `id-token: write`; it does not require a long-lived Tailscale OAuth secret.

## Acceptance sequence

1. Merge this control-plane implementation to `main`.
2. Bootstrap workflow prepares `kgmops` and narrow sudoers. If `TS_KGM_AUTH_KEY` is absent, it stops successfully at `PREPARED_AWAITING_TS_KGM_AUTH_KEY`.
3. After tailnet policy and `TS_KGM_AUTH_KEY` are configured, re-run bootstrap and require:
   - Tailscale online;
   - `tag:kgm` present;
   - KGM service still active;
   - runtime DB unreadable to `kgmops`;
   - arbitrary root escalation denied.
4. Configure workload identity secrets.
5. Manually run `KGM Tailscale Ansible Control` with `operation=health`.
6. Require full Ansible health PASS.
7. Only after health PASS, test `operation=restart` once and verify KGM service returns active.
8. Only after both PASS, assess retirement/disablement of parked KGM SentinelX. Do not remove the existing SSH recovery channel in the same change.

## Version baselines at implementation

- Tailscale server minimum accepted version: `1.102.1`.
- Tailscale GitHub Action: `tailscale/github-action@v4`.
- Ansible control runtime: `ansible-core==2.20.9`.

These are control-plane baselines, not application dependencies.
