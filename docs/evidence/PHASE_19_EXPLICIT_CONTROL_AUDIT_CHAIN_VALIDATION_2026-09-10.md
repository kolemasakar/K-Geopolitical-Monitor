# Phase 19 — Explicit Control-to-Audit Chain Validation

Date: 2026-09-10
Status: `VALIDATED / REAL_SOAK_STILL_IN_PROGRESS`

## Purpose

This evidence record closes the implementation-validation gap in the P19 real-soak observation mechanism. It does **not** close any elapsed-time milestone.

The accepted canonical chain is now explicit and fail-closed:

```text
p19-owner-local-real-soak-dispatch.yml
  -> workflow_dispatch(operation=health)
  -> tailscale-kgm-control.yml
  -> wait for completed / success
  -> workflow_dispatch
  -> p19-owner-local-soak-gate-audit.yml
  -> read-only GitHub Actions history
  -> scripts/p19_soak_gate.py
```

The audit no longer depends solely on GitHub `workflow_run` propagation from a control run that was itself created with the repository `GITHUB_TOKEN`. The `workflow_run` trigger remains present as supplemental compatibility, and the `47 */6 * * *` dead-man schedule remains present. The canonical six-hour evidence chain is the explicit dispatcher-controlled sequence above.

## Canonical revision under validation

```text
main = 3b6ae49872ed4d88e3ba2e53ffecfdfdda51f4a0
```

GitHub commit verification: `verified = true`.

## Exact-main repository regression

Workflow run:

```text
CI run = 34428832117
job = 102719738764
result = SUCCESS
Python = 3.11.16 x64
pytest = 1178 passed in 91.90s
```

## Exact-main dispatcher proof

Workflow run:

```text
dispatcher run = 34428832137
job = 102719739208
result = SUCCESS
```

Observed dispatcher evidence:

```text
P19_CONTROL_RUN_ID=34428839423
P19_CONTROL_RESULT=PASS
P19_CONTROL_HEAD_SHA=3b6ae49872ed4d88e3ba2e53ffecfdfdda51f4a0
P19_SOAK_AUDIT_DISPATCH=PASS
P19_AUDIT_TRIGGER_CONTROL_RUN_ID=34428839423
P19_SOAK_DISPATCH_CHAIN=PASS
P19_CONTROL_EVENT=workflow_dispatch
P19_CONTROL_OPERATION=health
P19_AUDIT_EVENT=workflow_dispatch
P19_REAL_SOAK_ELAPSED_GATE=NOT_INFERRED_FROM_DISPATCH
PHASE_18_SHARED_RUNTIME_ACTIVE=NO
CANONICAL_CUTOVER_AUTHORIZED=NO
BETA_PAID_RESOURCES_AUTHORIZED=NO
```

The dispatcher waits for the control workflow to finish and fails closed unless its conclusion is `success`. The in-progress-state parsing defect observed immediately after PR #71 was fixed in PR #72 by using a non-empty `NONE` conclusion sentinel and a non-whitespace `|` delimiter.

## Exact-main owner-local health proof

Dispatched control run:

```text
control run = 34428839423
job = 102719764577
result = SUCCESS
repository_sha = 3b6ae49872ed4d88e3ba2e53ffecfdfdda51f4a0
operation = health
observation_utc = 2026-09-10T02:17:44Z
```

Observed runtime properties:

```text
owner-local target = kgm-e4-owner-pilot
Tailscale IPv4 = 100.102.136.23
Tailscale connectivity = PASS
service before = active
service after = active
runtime DB read as kgmops = denied
arbitrary root escalation as kgmops = denied
restart task = skipped
Ansible recap = ok=10 changed=0 unreachable=0 failed=0 skipped=1
P19_REAL_SOAK_OBSERVATION = PASS
```

The deployed host repository SHA reported by the bounded control playbook remains:

```text
b31b2136b5fe982d0b63b0135479b1549041906c
```

This value is recorded as host deployment evidence and is not confused with the GitHub control-workflow repository SHA.

## Explicit read-only audit proof

The dispatcher then started:

```text
audit run = 34428891033
job = 102719925025
result = SUCCESS
```

Audit result:

```text
P19_CONTROL_COMPLETED_RUNS=4
P19_CONTROL_FAILED_RUNS=0
P19_QUALIFYING_HEALTH_OBSERVATIONS=4
P19_SOAK_AUDIT=PASS
P19_CONTINUITY_STATUS=PASS
latest_observation_utc=2026-09-10T02:17:44Z
current_max_gap_hours=0.9422222222222222
max_allowed_gap_hours=7.0
P19_REAL_24H_SOAK=IN_PROGRESS
P19_REAL_72H_SOAK=IN_PROGRESS
P19_REAL_7D_SOAK=IN_PROGRESS
```

Preserved audit artifact:

```text
artifact name = p19-owner-local-soak-gate-audit-34428891033
artifact ID = 10133694818
artifact zip SHA256 = a9e2913866552aa471acdedbdc552eb79e9f22bf7ce6601b7460fcbdcca3c0fd
artifact size = 1153 bytes
retention = 30 days
```

## Elapsed-time status

The real-soak baseline remains unchanged:

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-10T00:19:31Z
24h boundary = 2026-09-11T00:19:31Z
72h boundary = 2026-09-13T00:19:31Z
7d boundary = 2026-09-17T00:19:31Z
```

No elapsed milestone is inferred from this implementation validation. Real wall-clock time plus continuous qualifying observations and a terminal observation at or after the relevant boundary remain required.

## Binding boundaries preserved

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

## Validation conclusion

```text
P19_EXPLICIT_CONTROL_TO_AUDIT_CHAIN = PASS
P19_FAIL_CLOSED_CONTROL_WAIT = PASS
P19_READ_ONLY_ELAPSED_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
P19_OWNER_LOCAL_REAL_SOAK = IN_PROGRESS
P19_FULL_GATE = OPEN
```
