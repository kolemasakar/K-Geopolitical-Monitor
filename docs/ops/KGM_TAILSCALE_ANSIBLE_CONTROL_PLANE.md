# KGM Tailscale + Ansible Control Plane

Status: **KGM SERVER ENROLLED / OIDC CONTROL IDENTITY PENDING**

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
- KGM SentinelX remains enrolled/parked until this replacement path is fully accepted; it is not used by this workflow.
- `kgmops` is a dedicated unprivileged account.
- `kgmops` is not in `docker`, `kgm`, or other application groups.
- No unrestricted sudo.
- No arbitrary Docker access.
- KGM runtime database remains unreadable by `kgmops`.
- Only exact `kgm-monitor.service` systemd status/restart operations and bounded KGM journal access are allowed through sudo.
- The GitHub runner will be ephemeral and receive only the `tag:github-actions` identity.
- Tailnet network policy grants that tag only TCP/22 to `tag:kgm`.
- Tailscale SSH permits that source/destination pair only as OS user `kgmops`.
- Existing owner SSH remains the bootstrap/recovery channel until the new path passes acceptance.

## Repository components

- `.github/workflows/tailscale-kgm-bootstrap.yml`
- `.github/workflows/tailscale-kgm-control.yml`
- `ops/tailscale/kgm-tailnet-policy.hujson`
- `ops/ansible/kgm_control.yml`

## Tailnet policy state

The default unrestricted Tailscale policy was reviewed and replaced with the KGM-specific least-privilege policy before enrollment.

Current intended control relationship:

```text
tag:github-actions -> tag:kgm -> TCP/22 only
Tailscale SSH user -> kgmops only
```

The default `src=* / dst=* / ip=*` grant was removed. The default self-SSH rule was also replaced by the KGM-specific Tailscale SSH rule.

## KGM server enrollment — PASS

Bootstrap workflow run `34377282915`, re-run job `102564787863`, completed successfully after repository secret `TS_KGM_AUTH_KEY` was supplied.

Observed live results:

```text
KGMOPS_PREPARE=PASS
TAILSCALE_KGM_ENROLL=PASS
TAILSCALE_VERSION=1.102.3
TAILSCALE_IPV4=100.102.136.23
KGM_TAILSCALE_SECURITY_GATES=PASS
```

Validated conditions:

- Tailscale installed from the official stable Ubuntu Noble repository;
- architecture package: ARM64;
- `tailscaled` active and enabled;
- KGM node online;
- `tag:kgm` present;
- Tailscale SSH enabled;
- KGM application service remained active;
- `kgmops` remains outside `docker` and `kgm` groups;
- runtime DB remains unreadable by `kgmops`;
- arbitrary root escalation remains denied.

Tailscale assigned address:

```text
100.102.136.23
```

The one-time KGM auth key was created non-reusable and with one-day expiry. It is no longer required for normal operation after successful enrollment.

## Remaining external Tailscale prerequisite

### GitHub workload identity federation

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

## Remaining acceptance sequence

1. Configure the GitHub/Tailscale workload identity.
2. Manually run `KGM Tailscale Ansible Control` with `operation=health`.
3. Require full Ansible health PASS over the Tailscale path.
4. Only after health PASS, test `operation=restart` once and verify KGM service returns active.
5. Only after both PASS, assess retirement/disablement of parked KGM SentinelX.
6. Do not remove the existing owner SSH recovery channel in the same change.

## Version baselines at implementation

- Tailscale server: `1.102.3` observed live after enrollment; minimum accepted baseline was `1.102.1`.
- Tailscale GitHub Action: `tailscale/github-action@v4`.
- Ansible control runtime: `ansible-core==2.20.9`.

These are control-plane baselines, not application dependencies.
