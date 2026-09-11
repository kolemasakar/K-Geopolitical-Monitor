# Project Checkpoint — 2026-09-11 — P19 Control-Plane Reconciliation

Status: `DOCUMENTATION_SYNC / P19_ATTEMPT_2_ACTIVE / OWNER_PAUSE_RECORDED`

## Purpose

Reconcile K-Geopolitical Monitor documentation with the current cross-project infrastructure inventory maintained in `kolemasakar/Sentinel-Remote` without mutating the KGM runtime, Phase 19 soak baseline, cadence, evaluator, workflows, Tailscale policy, service state, or deployed candidate.

## Canonical repository context

```text
KGM_MAIN_BEFORE_THIS_CHECKPOINT = ae677ea7b4c743fe5a7d30fd6491a2e2820f183c
SENTINEL_REMOTE_MAIN_REVALIDATED = ca15f4e6b66daa1eb047be742c4aee8fc6770d02
DOCUMENTATION_ONLY = YES
RUNTIME_MUTATION = NONE
```

The strategic machine-readable state remains intentionally frozen at synchronization `4.34`; `docs/state/CURRENT_PROJECT_STATE.json` is not advanced by this reconciliation.

## Accepted KGM access architecture

`kgm-e4-owner-pilot` is an active separate OCI VM and the owner-local canonical KGM runtime / Phase 19 real-soak target.

Primary operational path:

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

Canonical target identity:

```text
host = kgm-e4-owner-pilot
Tailscale IPv4 = 100.102.136.23
automation user = kgmops
service = kgm-monitor.service
project root = /opt/k-geopolitical-monitor
runtime DB = /opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db
```

## Recovery interpretation correction

The following are now explicit project rules:

```text
KGM_SENTINELX = RETIRED_BY_DESIGN
KGM_RDC_ACCESS = NOT_REQUIRED
KGM_PRIMARY_CONTROL_PLANE = GITHUB_OIDC_TAILSCALE_ANSIBLE
RECOVERY_ACCESS_GAP_FROM_SENTINELX_OR_RDC_ABSENCE = NONE
```

Therefore, the absence of `kgm-e4-owner-pilot` from SentinelX or Remote Desktop Commander must not be reported as an unresolved KGM recovery issue.

SentinelX retirement is complete and verified. Re-enrollment is prohibited unless a later explicit owner-approved architecture decision reverses that boundary.

Owner SSH remains recovery/bootstrap/break-glass only and is not the normal automation path.

## Security invariants

- runtime DB read as `kgmops`: denied;
- arbitrary root escalation as `kgmops`: denied;
- automation reachability remains bounded to KGM TCP/22 over accepted Tailscale policy;
- KGM identities, tags, trust credentials and privileges are project-scoped and must not be reused by K-Trader or KRC;
- new privileged operations require a fresh explicit authorization boundary.

## Source-of-truth split

For infrastructure topology and cross-project host/control-plane inventory:

```text
kolemasakar/Sentinel-Remote
```

For executable KGM operational-control semantics:

```text
.github/workflows/tailscale-kgm-control.yml
ops/ansible/kgm_control.yml
```

For P19 temporal state and milestone evidence:

```text
ops/p19/real_soak_baseline.txt
scripts/p19_soak_gate.py
docs/evidence/PHASE_19_PRE_24H_RUNTIME_REVALIDATION_2026-09-11.md
docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_PHASE_19_PRE_24H_FINAL_SYNC.md
```

## Phase 19 state preserved

```text
PHASE = PHASE_19
ATTEMPT = OWNER_LOCAL_REAL_SOAK_ATTEMPT_2
BASELINE_UTC = 2026-09-11T07:38:44Z
DEPLOYED_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
MAX_ALLOWED_EVIDENCE_GAP_HOURS = 7
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
MIGRATION_033 = NOT_CREATED_NOT_PREAUTHORIZED
BETA_PAID_RESOURCES_AUTHORIZED = NO
```

This documentation sync does not reset or replace the P19 baseline and does not create a new soak attempt.

## Owner pause

Owner instruction recorded on 2026-09-11:

```text
MANUAL_PROJECT_WORK = PAUSED
PAUSE_UNTIL = 2026-09-13 07:00 Europe/Kyiv
```

During the pause:

- no manual deploy;
- no manual restart;
- no preparation-PR merge;
- no baseline/cadence/evaluator/workflow/Tailscale mutation;
- no SentinelX re-enrollment;
- no P20 operational activation.

Existing already-authorized safeguards and evidence collection are not broadened by this checkpoint.

## Documentation synchronized

Updated records:

- `docs/ops/KGM_TAILSCALE_ANSIBLE_CONTROL_PLANE.md`
- `ARCHITECTURE.md`
- this checkpoint

Historical acceptance records remain unchanged.

## Resume rule

At or after `2026-09-13 07:00 Europe/Kyiv`, resume with a fresh read-only P19 control slice using the accepted KGM control plane, then evaluate the latest qualifying observations, continuity status and actual 24h milestone state before any further project action.
