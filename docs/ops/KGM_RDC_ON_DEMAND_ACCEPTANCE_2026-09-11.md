# KGM RDC On-Demand Acceptance - 2026-09-11

Status: ACCEPTED / ON-DEMAND / FROZEN

## Scope

This record accepts a supplemental direct interactive access channel for the KGM host without replacing the canonical automation control plane.

Primary control plane remains:

```text
GitHub Actions OIDC -> Tailscale -> Tailscale SSH -> kgmops -> bounded Ansible
```

Supplemental operator path:

```text
owner workstation -> SSH -> kgmops -> foreground Remote Desktop Commander
```

The supplemental path is for interactive diagnostics and maintenance under the existing unprivileged `kgmops` identity only.

## Accepted host identity

```text
host=kgm-e4-owner-pilot
user=kgmops
uid=1002
gid=1002
arch=aarch64
home=/home/kgmops
```

## SSH key boundary

A dedicated ED25519 key was installed only for `kgmops`.

```text
fingerprint=SHA256:A2t15sXOQhJ2PGd05n1XMaanuf/mXsbOJgEcwGfDUlI
```

The authorized key entry disables agent forwarding, port forwarding, X11 forwarding, and user rc execution. No private key material is stored in this repository.

## RDC runtime

```text
node=v24.21.0
install_scope=user-local under /home/kgmops/.local
rdc_version=0.2.50
rdc_mode=foreground/on-demand
```

The RDC process is not installed as a system service and persistence is not authorized.

## Live acceptance evidence

RDC registration and connectivity passed for `kgm-e4-owner-pilot`.

Observed direct boundary:

```text
USER=kgmops
UID=1002
GROUPS=kgmops
/root=not accessible
/opt/k-geopolitical-monitor=root:root 0755
Docker CLI=not installed
```

RDC command policy additionally blocks privilege and host-control commands including `sudo`, `su`, user-management commands, `visudo`, `shutdown`, `reboot`, `iptables`, `mount`, `dd`, and `fdisk`.

## Bootstrap evidence

One-time GitHub Actions bootstrap:

```text
workflow=KGM RDC key bootstrap
run_id=34629164436
commit=698b9115cddee41d540a91dc2a18708521b93264
result=SUCCESS
```

Acceptance output included:

```text
KGM_RDC_KEY_BOOTSTRAP=PASS
kgmops_home=/home/kgmops
authorized_keys_owner=kgmops:kgmops
authorized_keys_mode=600
```

The one-time bootstrap workflow was removed after successful key installation and is not part of the accepted steady-state control plane.

## Frozen authority

Accepted:

- direct SSH only as `kgmops` using the dedicated key;
- foreground/on-demand RDC under `kgmops`;
- normal read and write capabilities of the `kgmops` account within OS permissions;
- interactive diagnostics that do not expand authority.

Not accepted:

- root or `ubuntu` RDC;
- persistent RDC daemon or systemd unit;
- arbitrary sudo/root escalation;
- Docker authority;
- firewall, network, systemd, package, or kernel mutation through RDC;
- replacement of the GitHub/OIDC/Tailscale/Ansible primary control plane.

Any expansion requires a separate explicit authorization and acceptance gate.
