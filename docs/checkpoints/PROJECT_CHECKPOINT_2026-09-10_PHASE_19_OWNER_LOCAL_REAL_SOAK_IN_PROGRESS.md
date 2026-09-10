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

This revalidation used the accepted historical control workflow and established the live host/access baseline. The current canonical repository revision remains tracked separately by normal GitHub CI and the new P19 soak workflow.

## Real elapsed soak baseline

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-10T00:31:24Z
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = PENDING
P19_REAL_7D_SOAK = PENDING
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NOT_YET_CLOSED
```

Earliest temporal eligibility, subject to clean observations through the interval and a fresh terminal observation at/after each boundary:

```text
24h earliest = 2026-09-11T00:31:24Z
72h earliest = 2026-09-13T00:31:24Z
7d earliest  = 2026-09-17T00:31:24Z
```

No gate may be closed from simulated time, accelerated test execution, or wall-clock arithmetic alone. Actual elapsed operation plus observable evidence is required.

## Observation mechanism

`.github/workflows/p19-owner-local-real-soak.yml` performs health-only observations through the already accepted least-privilege control plane.

The workflow:

- runs on a six-hour schedule after merge and supports manual execution;
- requires exactly the retained KGM host and expected Tailscale IPv4;
- pings the host over Tailscale;
- invokes only `operation=health` in `ops/ansible/kgm_control.yml`;
- verifies the existing DB-read and arbitrary-root denial boundaries;
- does not restart the service;
- does not write the runtime database;
- does not activate any shared runtime;
- records each observation in GitHub Actions evidence.

A single successful workflow run is only one observation and never substitutes for elapsed soak duration.

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
