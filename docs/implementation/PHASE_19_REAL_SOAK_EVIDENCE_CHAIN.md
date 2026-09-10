# Phase 19 Real-Soak Evidence Chain

Date: 2026-09-10
Status: `CANONICAL DESIGN / P19 REAL ELAPSED SOAK IN PROGRESS`
Parent gate: `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED`

## Purpose

Phase 19 requires real elapsed owner-local runtime evidence. Accelerated or simulated time is not accepted as a substitute for the 24h, 72h, or 7d milestones.

The canonical target remains:

```text
host = kgm-e4-owner-pilot
Tailscale IPv4 = 100.102.136.23
runtime service = kgm-monitor.service
control identity = kgmops
OWNER_LOCAL_RUNTIME = CANONICAL
```

The real-soak baseline is:

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-10T00:19:31Z
```

## Accepted live control boundary

Tailscale workload identity is intentionally constrained to the accepted `workflow_dispatch` execution path of `.github/workflows/tailscale-kgm-control.yml`.

The control workflow remains `workflow_dispatch`-only. The P19 scheduler never authenticates to Tailscale directly.

Canonical chain:

```text
p19-owner-local-real-soak-dispatch.yml
  schedule: 27 */6 * * * UTC
  -> workflow_dispatch(operation=health)
  -> tailscale-kgm-control.yml
  -> GitHub OIDC
  -> Tailscale
  -> kgmops / bounded Ansible
  -> kgm-e4-owner-pilot
  -> successful P19 health observation
  -> dispatcher verifies control conclusion == success
  -> workflow_dispatch
  -> p19-owner-local-soak-gate-audit.yml
  -> read-only GitHub Actions history
  -> scripts/p19_soak_gate.py
```

The dispatcher is fail-closed: it does not dispatch the elapsed audit until the newly dispatched KGM health control run completes successfully.

## Why the explicit audit dispatch exists

A `workflow_run` trigger is retained as a best-effort supplementary trigger, but it is not the sole immediate evidence path. In observed GitHub execution, the KGM control workflow can itself be created by a repository `GITHUB_TOKEN` workflow dispatch, and no downstream `workflow_run` audit execution was observed for that chain.

Therefore the authoritative six-hour cycle explicitly dispatches the read-only audit after the control run succeeds. A separate dead-man audit schedule remains at `47 */6 * * *` UTC so evidence evaluation is still attempted even if an immediate downstream event is absent.

No Tailscale trust expansion is required by this design.

## Elapsed gate semantics

`script/p19_soak_gate.py` is represented in the repository as `scripts/p19_soak_gate.py` and evaluates:

```text
24h
72h
168h / 7d
```

Requirements:

- real wall-clock elapsed time;
- a qualifying successful health observation at or after each milestone boundary;
- maximum evidence gap of 7 hours;
- no conversion of simulated/accelerated evidence into elapsed evidence;
- no automatic parent-gate closure.

Possible milestone/evidence states include:

```text
IN_PROGRESS
WAITING_TERMINAL_OBSERVATION
PASS
FAIL_CONTINUITY
```

The 7-hour gap is an evidence-continuity tolerance around the intended six-hour observation cadence. It is not a runtime availability SLA. `FAIL_CONTINUITY` means the interval is not adequately evidenced; it does not by itself prove a host outage.

## Boundary timing

The health dispatcher runs at minute 27 because the baseline is at minute 19:31. This makes the midnight cycle unambiguously later than the milestone boundaries:

```text
24h earliest = 2026-09-11T00:19:31Z
72h earliest = 2026-09-13T00:19:31Z
7d earliest  = 2026-09-17T00:19:31Z
```

The `00:27` dispatch can therefore provide the required terminal health observation. The audit is dispatched only after that control completes successfully.

## Evidence already established

Before this chain hardening:

- P19 accelerated deterministic harness: PASS;
- owner-local access: revalidated;
- accepted Tailscale `workflow_dispatch` control: PASS;
- dispatcher -> control chain: PASS;
- deterministic elapsed evaluator tests: PASS;
- PR #70 regression: `1178 passed`;
- canonical PR #70 merge SHA: `c57a8ac3321532d97b4308a5dc057957af45c29e`;
- post-merge health observation on that SHA: `2026-09-10T02:03:02Z`, PASS;
- service remained active;
- runtime DB read and arbitrary root escalation remained denied;
- restart was skipped;
- Ansible reported `changed=0 unreachable=0 failed=0`.

The elapsed milestones themselves remain open until their real time boundaries are reached with continuous evidence.

## Binding boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
A5 = DEFERRED / NOT AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34
```

No automated P19 soak action may authorize a restart, shared-runtime activation, paid resource, canonical cutover, migration 033, or strategic-state change.
