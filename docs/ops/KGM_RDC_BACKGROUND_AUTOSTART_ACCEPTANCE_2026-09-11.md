# KGM RDC Background Autostart Acceptance - 2026-09-11

Status: ACCEPTED FOR DEVELOPMENT / LOW-FRICTION MODE

## Decision

During active development, operator convenience is prioritized over final hardening. RDC keeps its persisted pairing and is started automatically after host reboot.

## Runtime identity

```text
host=kgm-e4-owner-pilot
user=kgmops
uid=1002
rdc_version=0.2.50
node=v24.21.0
```

## Persistence model

```text
pairing=persistent
process=background
startup=crontab @reboot
service_account=kgmops
systemd_service=none
root_rdc=not used
```

Accepted crontab entry starts the user-local Node/RDC runtime from `/home/kgmops` and writes logs under `/home/kgmops/.local/state/desktop-commander/remote.log`.

## Live evidence

The existing session was restored without browser re-pairing. RDC reported the device online and ready. The SSH session used to start the background process was then closed, and the device remained ONLINE and answered a remote ping.

```text
logout_survival=PASS
remote_ping=PASS
device_status=ONLINE
```

A deliberate host reboot was not performed solely for this acceptance. Therefore the `@reboot` path is configured but awaits confirmation at the next natural reboot.

## Security disposition

This is a temporary development-access policy. Final hardening, token rotation/revocation policy, and tighter startup controls are deferred until project development is substantially complete. The canonical GitHub OIDC -> Tailscale -> Tailscale SSH -> kgmops -> bounded Ansible control plane remains unchanged.