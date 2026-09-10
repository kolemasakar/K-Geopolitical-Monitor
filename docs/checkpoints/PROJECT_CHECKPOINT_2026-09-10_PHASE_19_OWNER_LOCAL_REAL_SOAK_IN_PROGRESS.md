# K-Geopolitical Monitor — Phase 19 Owner-Local Real Soak In Progress

Date: 2026-09-10
Status: `IN_PROGRESS / REAL_ELAPSED_SOAK_ACTIVE`
Parent gate: `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED`
Harness gate: `PHASE_19_OPERATIONAL_STABILITY_HARNESS_VALIDATED = PASS`

## Canonical owner-local target

The designated real beta runtime is the retained OCI VM:

```text
host = kgm-e4-owner-pilot
project = K-Geopolitical-Monitor
Tailscale IPv4 = 100.102.136.23
runtime service = kgm-monitor.service
control identity = kgmops
control plane = GitHub OIDC -> ephemeral Tailscale -> Tailscale SSH -> bounded Ansible
```

The VM was not deleted during Sentinel-Remote reorganization. KGM SentinelX was intentionally retired; the VM and accepted Tailscale/Ansible control plane were preserved.

## Fresh live access revalidation

Fresh read-only revalidation was completed before opening the elapsed-time window.

Evidence:

- parent workflow run: `34385314619`
- latest rerun health job: `102695438882`
- result: `SUCCESS`
- observation completed: `2026-09-10T00:19:31Z`
- tagged peer: `kgm-e4-owner-pilot`
- Tailscale IPv4: `100.102.136.23`
- tagged peer online: true
- Tailscale ping: PASS
- bounded Ansible operation: `health`
- `kgm-monitor.service` before: active
- `kgm-monitor.service` after: active
- runtime DB read as `kgmops`: DENIED
- arbitrary root escalation as `kgmops`: DENIED
- Ansible recap: `ok=10 changed=0 unreachable=0 failed=0`

This successful health observation is the conservative start anchor for the real elapsed soak. The host runtime is the object under observation; repository regression state remains independently covered by canonical GitHub CI.

## OIDC trust boundary discovered and preserved

Two fail-closed observations established that the Tailscale trust is narrower than repository/path authorization alone:

1. A second workflow path (`p19-owner-local-real-soak.yml`) was rejected with HTTP 403 before host access.
2. After moving live logic into the accepted `tailscale-kgm-control.yml` path, a `push` event on exact-main run `34422415082`, job `102700511669`, was also rejected with HTTP 403 before host access.

The accepted historical health proof used `workflow_dispatch`. The evidence therefore supports an event-bound workload-identity constraint: the control workflow must enter Tailscale through the existing `workflow_dispatch` path. No Tailscale trust expansion is authorized or required.

Remediation:

- `.github/workflows/tailscale-kgm-control.yml` is returned to `workflow_dispatch`-only live control;
- `.github/workflows/p19-owner-local-real-soak-dispatch.yml` owns the six-hour schedule and never touches Tailscale;
- the dispatcher uses the repository `GITHUB_TOKEN` with `actions: write` only to issue a `workflow_dispatch` request to `tailscale-kgm-control.yml` with `operation=health`;
- the dispatched control run then uses the already accepted GitHub OIDC -> Tailscale identity;
- `.github/workflows/p19-owner-local-real-soak.yml` is a static PR contract check and has no live Tailscale credentials.

Failed 403 runs are infrastructure-control evidence only. In both cases:

```text
remote Ansible operation = NOT STARTED
runtime mutation = NONE
service restart = NONE
runtime DB write = NONE
```

## Real elapsed soak baseline

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-10T00:19:31Z
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = PENDING
P19_REAL_7D_SOAK = PENDING
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NOT_YET_CLOSED
```

Earliest temporal eligibility, subject to clean observations through the interval and a fresh terminal observation at/after each boundary:

```text
24h earliest = 2026-09-11T00:19:31Z
72h earliest = 2026-09-13T00:19:31Z
7d earliest  = 2026-09-17T00:19:31Z
```

No gate may be closed from simulated time, accelerated test execution, a failed observation, or wall-clock arithmetic alone. Actual elapsed operation plus clean observable evidence is required.

## Observation mechanism

Live P19 observation is a two-stage chain:

```text
p19-owner-local-real-soak-dispatch.yml
  schedule: 17 */6 * * * UTC
  -> GitHub workflow_dispatch(operation=health)
  -> tailscale-kgm-control.yml
  -> GitHub OIDC
  -> Tailscale
  -> kgmops / bounded Ansible
  -> kgm-e4-owner-pilot
```

The dispatcher:

- schedules one health dispatch every six hours;
- can be manually dispatched for validation;
- performs no Tailscale login, SSH, service mutation, or database access;
- always requests `operation=health`.

The accepted control workflow:

- is live only for `workflow_dispatch`;
- requires exactly `kgm-e4-owner-pilot` at `100.102.136.23` and online;
- pings the host over Tailscale;
- invokes bounded Ansible with the requested `health|restart` operation;
- records a P19 observation only when the operation is `health`;
- verifies DB-read and arbitrary-root denial boundaries through `ops/ansible/kgm_control.yml`.

The P19 automated dispatcher cannot request `restart`. A single successful workflow run is only one observation and never substitutes for elapsed soak duration.

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

## Current Phase 19 state

```text
P19_ACCELERATED_DETERMINISTIC_HARNESS = PASS
P19_OWNER_LOCAL_ACCESS = REVALIDATED
P19_OWNER_LOCAL_REAL_SOAK = IN_PROGRESS
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = PENDING
P19_REAL_7D_SOAK = PENDING
P19_FULL_GATE = OPEN
```

Next evidence milestone: a clean observation at or after the 24-hour boundary, together with review of the intervening scheduled observation history.
