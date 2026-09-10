# K-Geopolitical Monitor — Phase 19 Owner-Local Real Soak In Progress

Date: 2026-09-10
Status: `IN_PROGRESS / REAL_ELAPSED_SOAK_ACTIVE`
Parent gate: `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED`
Harness gate: `PHASE_19_OPERATIONAL_STABILITY_HARNESS_VALIDATED = PASS`
Explicit evidence chain: `P19_EXPLICIT_CONTROL_TO_AUDIT_CHAIN = PASS`

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

## Real elapsed soak baseline

The successful bounded health observation at `2026-09-10T00:19:31Z` remains the conservative real-time start anchor.

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-10T00:19:31Z
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NOT_YET_CLOSED
```

Earliest temporal eligibility, subject to clean observations through each interval and a fresh terminal observation at or after the boundary:

```text
24h earliest = 2026-09-11T00:19:31Z
72h earliest = 2026-09-13T00:19:31Z
7d earliest  = 2026-09-17T00:19:31Z
```

No gate may be closed from simulated time, accelerated test execution, a failed observation, or wall-clock arithmetic alone. Actual elapsed operation plus clean observable evidence is required.

## Preserved OIDC trust boundary

Fail-closed validation established that the Tailscale identity is narrower than repository/path authorization alone:

- a second workflow path attempting direct Tailscale entry was rejected with HTTP 403 before host access;
- a `push` event attempting direct entry through the accepted control workflow was also rejected with HTTP 403 before host access;
- the accepted live control path is therefore kept `workflow_dispatch`-only.

No Tailscale trust expansion was performed.

The accepted runtime control workflow is:

```text
.github/workflows/tailscale-kgm-control.yml
  event = workflow_dispatch only
  operation = health | restart
  exact host = kgm-e4-owner-pilot
  exact Tailscale IPv4 = 100.102.136.23
```

P19 automation always requests `operation=health`; it does not automate restart.

## Canonical real-soak evidence chain

The validated canonical six-hour chain is now explicit:

```text
p19-owner-local-real-soak-dispatch.yml
  schedule: 27 */6 * * * UTC
  -> GitHub workflow_dispatch(operation=health)
  -> tailscale-kgm-control.yml
  -> GitHub OIDC
  -> Tailscale
  -> kgmops / bounded Ansible
  -> kgm-e4-owner-pilot
  -> dispatcher waits for completed / success
  -> GitHub workflow_dispatch
  -> p19-owner-local-soak-gate-audit.yml
  -> read-only Actions history
  -> scripts/p19_soak_gate.py
```

The dispatcher has `actions: write` only for workflow dispatch. It does not log into Tailscale, SSH to the host, read or write the runtime database, or control systemd directly.

The control workflow remains the only Tailscale trust entry point. It verifies:

- exact peer identity and IP;
- peer online state and Tailscale reachability;
- dedicated `kgmops` identity;
- `kgm-monitor.service` active before and after the operation;
- runtime database unreadable to `kgmops`;
- arbitrary root escalation denied;
- bounded journal access;
- restart skipped unless explicitly requested.

The dispatcher fails closed unless the dispatched control run reaches `completed / success`. Only then does it dispatch the elapsed-soak audit.

## GitHub event behavior and hardening

An intermediate implementation expected GitHub `workflow_run` to fire the audit automatically after a control run created by the repository `GITHUB_TOKEN`. A real execution showed that the expected downstream audit did not fire in that path.

The canonical implementation therefore does not rely on that propagation. The dispatcher explicitly performs:

```text
health control -> wait for success -> audit dispatch
```

The audit workflow still retains:

- `workflow_dispatch` for explicit canonical dispatch;
- `workflow_run` as supplemental compatibility;
- dead-man schedule `47 */6 * * * UTC`;
- `actions: read` only.

A first exact-main dispatcher execution after that hardening exposed a fail-closed Bash parsing bug: while the control run was in progress, the empty `conclusion` field collapsed during whitespace-delimited parsing. The dispatcher stopped before audit dispatch while the separately created health control itself completed successfully.

PR #72 corrected this by using:

```text
conclusion sentinel = NONE
state delimiter = |
IFS = |
```

This preserves field positions for queued/in-progress control runs.

## Exact-main end-to-end validation

Canonical revision:

```text
main = 3b6ae49872ed4d88e3ba2e53ffecfdfdda51f4a0
GitHub verified = true
```

Repository regression:

```text
CI run = 34428832117
job = 102719738764
result = SUCCESS
1178 passed in 91.90s
```

Dispatcher:

```text
run = 34428832137
job = 102719739208
result = SUCCESS
P19_CONTROL_RUN_ID = 34428839423
P19_CONTROL_RESULT = PASS
P19_CONTROL_HEAD_SHA = 3b6ae49872ed4d88e3ba2e53ffecfdfdda51f4a0
P19_SOAK_AUDIT_DISPATCH = PASS
P19_AUDIT_TRIGGER_CONTROL_RUN_ID = 34428839423
P19_SOAK_DISPATCH_CHAIN = PASS
```

Dispatched owner-local health control:

```text
run = 34428839423
job = 102719764577
result = SUCCESS
operation = health
observation_utc = 2026-09-10T02:17:44Z
Tailscale connectivity = PASS
service before/after = active / active
runtime DB read as kgmops = denied
arbitrary root escalation = denied
restart = skipped
Ansible recap = ok=10 changed=0 unreachable=0 failed=0 skipped=1
P19_REAL_SOAK_OBSERVATION = PASS
```

The host-side deployed repository SHA reported by the bounded playbook remains:

```text
b31b2136b5fe982d0b63b0135479b1549041906c
```

This is host deployment evidence and is intentionally not conflated with the GitHub workflow repository SHA.

Explicit read-only elapsed audit:

```text
run = 34428891033
job = 102719925025
result = SUCCESS
P19_CONTROL_COMPLETED_RUNS = 4
P19_CONTROL_FAILED_RUNS = 0
P19_QUALIFYING_HEALTH_OBSERVATIONS = 4
P19_SOAK_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
latest_observation_utc = 2026-09-10T02:17:44Z
current_max_gap_hours = 0.9422222222222222
max_allowed_gap_hours = 7.0
```

Preserved audit artifact:

```text
artifact = p19-owner-local-soak-gate-audit-34428891033
artifact ID = 10133694818
zip SHA256 = a9e2913866552aa471acdedbdc552eb79e9f22bf7ce6601b7460fcbdcca3c0fd
size = 1153 bytes
retention = 30 days
```

Detailed evidence record:

```text
docs/evidence/PHASE_19_EXPLICIT_CONTROL_AUDIT_CHAIN_VALIDATION_2026-09-10.md
```

## Deterministic elapsed-soak gate audit

Qualifying evidence is a completed successful `workflow_dispatch` control run where the `Record P19 owner-local soak observation` step completed successfully. Manual `restart` runs do not qualify because that observation step is skipped.

The evaluator enforces:

```text
milestones = 24h / 72h / 168h
fresh terminal observation at or after each boundary = REQUIRED
maximum gap between verified observations = 7h
simulated or accelerated time = NOT ACCEPTED
```

The seven-hour value is an evidence-continuity tolerance around the intended six-hour cadence; it is not a runtime availability SLA. A gap greater than seven hours means `FAIL_CONTINUITY` for the current soak evidence and must not be silently converted into a pass. It does not by itself prove that the KGM host failed; it proves that continuous health was not adequately evidenced.

The audit emits states including:

```text
IN_PROGRESS
WAITING_TERMINAL_OBSERVATION
PASS
FAIL_CONTINUITY
```

Each audit preserves JSON/log/observation evidence as a GitHub artifact. The audit may identify milestone eligibility, but it does not automatically close the parent P19 gate or modify canonical runtime state.

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
P19_SCHEDULED_DISPATCH_CHAIN = PASS
P19_EXPLICIT_CONTROL_TO_AUDIT_CHAIN = PASS
P19_FAIL_CLOSED_CONTROL_WAIT = PASS
P19_READ_ONLY_ELAPSED_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
P19_OWNER_LOCAL_REAL_SOAK = IN_PROGRESS
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
P19_FULL_GATE = OPEN
```

Next evidence milestone: a clean observation at or after the 24-hour boundary (`2026-09-11T00:19:31Z`) together with deterministic audit confirmation that the intervening evidence chain remained continuous.
