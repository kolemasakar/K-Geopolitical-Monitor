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
- Ansible recap: `ok=10 changed=0 unreachable=0 failed=0 skipped=1`

This successful health observation is the conservative start anchor for the real elapsed soak. The host runtime is the object under observation; repository regression state remains independently covered by canonical GitHub CI.

## OIDC trust boundary discovered and preserved

The first implementation attempted to create a second live Tailscale path in `.github/workflows/p19-owner-local-real-soak.yml`.

Canonical push run `34421645389`, job `102698156654`, failed closed before reaching the host:

```text
Tailscale token exchange = HTTP 403 Unauthorized
remote Ansible operation = NOT STARTED
runtime mutation = NONE
```

This was not a KGM host/access outage. The accepted `.github/workflows/tailscale-kgm-control.yml` path had passed minutes earlier. The 403 demonstrated that the Tailscale workload-identity trust is intentionally bounded and does not automatically authorize a new workflow path.

Remediation preserves that boundary rather than broadening Tailscale trust:

- scheduled P19 observations are executed by the already accepted `tailscale-kgm-control.yml` workflow;
- scheduled and push-triggered executions are forced to `operation=health`;
- manual `workflow_dispatch` retains the pre-existing bounded `health|restart` choice;
- `.github/workflows/p19-owner-local-real-soak.yml` is now a static PR contract check only and creates no second OIDC/Tailscale path.

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

`.github/workflows/tailscale-kgm-control.yml` is the live observer because it is the already accepted and Tailscale-authorized workflow identity.

For P19 it:

- runs a health observation every six hours (`17 */6 * * *` UTC);
- performs an immediate health observation when the observer definition itself is merged to `main`;
- requires exactly `kgm-e4-owner-pilot` at `100.102.136.23` and online;
- pings the host over Tailscale;
- invokes bounded Ansible with `operation=health` for scheduled/push observations;
- verifies the existing DB-read and arbitrary-root denial boundaries through `ops/ansible/kgm_control.yml`;
- does not restart the service during P19 scheduled observations;
- does not write the runtime database;
- does not activate any shared runtime;
- records each successful observation in GitHub Actions evidence.

`.github/workflows/p19-owner-local-real-soak.yml` statically checks this contract on pull requests and has no live credentials or schedule of its own.

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
