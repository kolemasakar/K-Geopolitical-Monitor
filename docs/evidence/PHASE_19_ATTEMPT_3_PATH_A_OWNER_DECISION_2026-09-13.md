# Phase 19 Attempt 3 — Path A Owner Decision and Continuity Root Cause

Date: 2026-09-13
Status: `OWNER_APPROVED_PATH_A / ATTEMPT_3_BASELINE_PENDING`
Scope: K-Geopolitical Monitor Phase 19 owner-local real soak

## Owner decision

The owner explicitly approved **Path A** for the next Phase 19 real-soak attempt.

```text
OWNER_DECISION = APPROVE_PATH_A
P19_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
CANDIDATE_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
```

Path A freezes the already deployed owner-local runtime candidate `b31b2136b5fe982d0b63b0135479b1549041906c` as the candidate to be validated by the new temporal soak. It does **not** claim full repository equivalence with current `main`.

## Continuity root-cause classification

Attempt 2 failed closed because the maximum qualifying observation gap exceeded the accepted seven-hour bound:

```text
ATTEMPT_2_MAX_OBSERVED_GAP_HOURS = 8.337222222222222
MAX_ALLOWED_GAP_HOURS = 7.0
ATTEMPT_2_CONTROL_FAILED_RUNS = 0
ATTEMPT_2_QUALIFYING_OBSERVATIONS = 13
```

The accepted root-cause classification for preparation of Attempt 3 is:

```text
ROOT_CAUSE = GITHUB_ACTIONS_SCHEDULED_EVENT_DELIVERY_LATENCY_OR_JITTER
BOUNDED_HEALTH_FAILURE = NO
OWNER_LOCAL_VM_OR_SERVICE_FAILURE = NO_EVIDENCE
CANDIDATE_RUNTIME_FAILURE = NO_EVIDENCE
```

This classification is intentionally narrow: the observed failure is in evidence continuity / scheduled delivery, not a demonstrated failure of the bounded owner-local health operation. It does not convert GitHub scheduled delivery into a hard real-time guarantee.

## Pre-decision observation boundary

A fresh bounded health observation completed successfully before this owner decision:

```text
PRE_DECISION_OBSERVATION_UTC = 2026-09-13T08:32:01Z
P19_REAL_SOAK_OBSERVATION = PASS
REPOSITORY_SHA = 4c755410bce905c0b0e41cfcd321dc48d684b6fa
```

That observation is retained as valid runtime/control evidence but **must not** be used as the Attempt 3 baseline because it predates the explicit Path A owner decision.

```text
PRE_DECISION_OBSERVATION_AS_ATTEMPT_3_BASELINE = FORBIDDEN
ATTEMPT_1_ELAPSED_TIME_REUSE = NO
ATTEMPT_2_ELAPSED_TIME_REUSE = NO
```

## Attempt 3 baseline rule

Attempt 3 starts only from the exact UTC timestamp of the first successful **fresh post-decision** bounded `health` observation for the selected candidate.

Required sequence:

1. obtain a fresh bounded owner-local `health` observation through the accepted KGM control plane;
2. verify the deployed runtime candidate remains exactly `b31b2136b5fe982d0b63b0135479b1549041906c`;
3. verify service active, no restart, no runtime mutation, and bounded access controls preserved;
4. set `ops/p19/real_soak_baseline.txt` to that exact `observation_utc`;
5. obtain/retain qualifying post-baseline evidence and evaluate continuity fail-closed;
6. do not infer 24h, 72h or 7d PASS from a single observation.

## Preserved project boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL_AUTHORITY
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
A5 = DEFERRED / NOT_AUTHORIZED
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_AUTHORIZED
P20_OPERATIONAL_EXECUTION = NOT_STARTED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
```

Preparation PRs #78, #79, #80 and #81 remain draft/unmerged while the real soak is active. This decision record does not merge them and does not modify Tailscale trust, P19 evaluator semantics, runtime code, deployment state or service state.

## Current classification

```text
P19_REAL_SOAK_ATTEMPT_1 = FAILED_CONTINUITY
P19_REAL_SOAK_ATTEMPT_2 = FAILED_CONTINUITY
P19_PATH_A = OWNER_APPROVED
P19_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
P19_ATTEMPT_3 = BASELINE_PENDING
P19_FULL_GATE = OPEN
```
