# Phase 19 — Real Soak Attempt 2 Reanchor Evidence

Date: 2026-09-11
Status: `ATTEMPT_2_REANCHOR_PROPOSED`

## Context

Attempt 1 is permanently classified as:

```text
P19_REAL_SOAK_ATTEMPT_1 = FAILED_CONTINUITY / NOT_EVIDENCED
P19_REAL_24H_SOAK_ATTEMPT_1 = NOT_VALIDATED
```

Its wall-clock duration is not reused or retroactively converted to PASS.

## Remediation anchor

Cadence remediation was merged to canonical `main` at:

`2cd911fa45d3a9ea94abc5979c1a2e109416a1d4`

The merge retained the seven-hour evidence-gap requirement and tightened nominal observation cadence to three hours.

A fresh exact-main owner-local health control then completed successfully:

```text
CONTROL_RUN = 34575282809
CONTROL_JOB = 103186235689
REPOSITORY_SHA = 2cd911fa45d3a9ea94abc5979c1a2e109416a1d4
OPERATION = health
OBSERVATION_UTC = 2026-09-11T07:38:44Z
TARGET = kgm-e4-owner-pilot
TAILSCALE_IP = 100.102.136.23
TAILSCALE_CONNECTIVITY = PASS
SERVICE_BEFORE = active
SERVICE_AFTER = active
RUNTIME_DB_READ_AS_KGMOPS = DENIED
ARBITRARY_ROOT_ESCALATION = DENIED
RESTART = SKIPPED
ANSIBLE = ok=10 changed=0 unreachable=0 failed=0 skipped=1
```

This verified observation is the only baseline used for Attempt 2.

## Attempt 2 baseline

```text
P19_REAL_SOAK_ATTEMPT_2_BASELINE_UTC = 2026-09-11T07:38:44Z
24H_BOUNDARY_UTC = 2026-09-12T07:38:44Z
72H_BOUNDARY_UTC = 2026-09-14T07:38:44Z
7D_BOUNDARY_UTC = 2026-09-18T07:38:44Z
```

Kyiv local equivalents at the observed UTC+03 offset:

```text
24H = 2026-09-12 10:38:44
72H = 2026-09-14 10:38:44
7D  = 2026-09-18 10:38:44
```

## Continuity contract

```text
TARGET_HEALTH_CADENCE = 3h
DEAD_MAN_AUDIT_CADENCE = 3h
MAX_ALLOWED_EVIDENCE_GAP = 7h
POST_BOUNDARY_TERMINAL_OBSERVATION = REQUIRED
SIMULATED_TIME = NOT_ACCEPTED
```

The three-hour nominal cadence gives margin for one missed nominal cycle while preserving the seven-hour maximum evidence-gap gate.

## Activation condition

This record proposes the reanchor. Attempt 2 becomes canonical active only after this baseline change is merged to `main` and a subsequent exact-main health/audit chain confirms the new baseline with `PASS / IN_PROGRESS` and no continuity failure.

## Binding boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
A5 = DEFERRED / NOT AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
P20 = NOT_STARTED
```
