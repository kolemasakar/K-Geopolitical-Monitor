# KGM SentinelX Retirement — 2026-09-09

Status: **COMPLETE / VERIFIED**

## Decision

K-Trader remains the sole dominant SentinelX-managed host. KGM uses the accepted Tailscale + GitHub OIDC + Tailscale SSH + bounded Ansible control plane. After both health and bounded restart acceptance passed, the parked KGM SentinelX agent was approved for retirement.

## Replacement control plane acceptance

- health run: `34385314619` — PASS
- restart run: `34385726741` — PASS
- KGM Tailscale address: `100.102.136.23`
- Tailscale tag: `tag:kgm`
- SSH identity: `kgmops`
- runtime DB read by `kgmops`: denied
- arbitrary root escalation by `kgmops`: denied

## SentinelX cleanup run

Workflow run: `34388121721`
Job: `102589453954`
Result: **SUCCESS**

Pre-removal audit gate:

```text
KGM_SENTINELX_CLEANUP_AUDIT=PASS
sentinelx_host_id=host_a2767ee5915c4cfe
sentinelx_core_sha=e1be3162b22a4b0c744e0443c9f9b62f8fdb21a4
kgm_tailscale_ip=100.102.136.23
```

Removal gate:

```text
KGM_SENTINELX_LOCAL_REMOVE=PASS
```

Post-removal gate:

```text
KGM_SENTINELX_CLEANUP=PASS
kgm_service=active
kgm_tailscale_ip=100.102.136.23
runtime_db_read=DENIED
kgmops_arbitrary_root=DENIED
```

## Removed KGM SentinelX footprint

- systemd unit `sentinelx-cloud-core.service`
- `/etc/sentinelx`
- `/opt/sentinelx-cloud-core`
- `/etc/sudoers.d/sentinelx-kgm`
- `/usr/local/sbin/sentinelx-kgm-journal`
- `/var/lib/sentinelx/uploads`
- local `sentinelx` user and group

The cleanup was fail-closed and required the exact KGM SentinelX host ID and pinned core SHA before mutation.

## Preserved controls

- `kgm-monitor.service` remains active and enabled.
- `tailscaled` remains active and enabled.
- KGM remains online as `100.102.136.23` with `tag:kgm`.
- `kgmops` least-privilege restrictions remain intact.
- owner SSH recovery/bootstrap path remains intact.
- K-Trader SentinelX was not touched.
- KRC-Cobalt was not touched.

## Hub state after cleanup

SentinelX host inventory after the KGM agent stopped shows one connected host only:

- `host_8c63c46648154724` / `k-trader-prod-vnic` — operational

KGM is no longer connected or parked.

## Repository cleanup

The retired KGM SentinelX bootstrap workflow and the one-shot cleanup workflow are removed after successful cleanup so normal repository activity cannot reinstall or rerun the retired path accidentally.

## Manual credential hygiene

Delete these obsolete KGM GitHub Actions secrets manually:

- `SENTINELX_ENROLL_TOKEN`
- `TS_KGM_AUTH_KEY`

Retain:

- `TS_OAUTH_CLIENT_ID`
- `TS_AUDIENCE`
- existing owner SSH recovery secrets while that recovery channel remains part of the design.
