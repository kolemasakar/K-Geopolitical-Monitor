# Phase 19 Attempt 2 Continuity Failure — 2026-09-13

Status: `FAIL_CONTINUITY / TEMPORAL GATE INVALIDATED`
Scope: owner-local real-soak Attempt 2 on `kgm-e4-owner-pilot`

## Canonical evidence

Scheduled audit run `34740207402` on canonical `main` `ccf097ac55f480057cb8d450edfd29f392eb48e2` completed with failure at the elapsed-soak evaluator.

```text
P19_REAL_SOAK_BASELINE_UTC = 2026-09-11T07:38:44Z
P19_CONTROL_COMPLETED_RUNS = 13
P19_CONTROL_FAILED_RUNS = 0
P19_QUALIFYING_HEALTH_OBSERVATIONS = 13
AUDIT_STATUS = FAIL_CONTINUITY
CONTINUITY_STATUS = FAIL_CONTINUITY
MAX_OBSERVED_GAP_HOURS = 8.337222222222222
MAX_ALLOWED_GAP_HOURS = 7.0
LATEST_OBSERVATION_UTC = 2026-09-13T05:03:57Z
```

Milestone evaluation:

```text
24H_BOUNDARY = 2026-09-12T07:38:44Z
24H_TERMINAL_OBSERVATION = 2026-09-12T07:45:10Z
P19_REAL_24H_SOAK = FAIL_CONTINUITY
P19_REAL_72H_SOAK = IN_PROGRESS / NOT VALIDATED
P19_REAL_7D_SOAK = IN_PROGRESS / NOT VALIDATED
```

Audit artifact:

```text
AUDIT_RUN_ID = 34740207402
AUDIT_JOB_ID = 103678528070
ARTIFACT_ID = 10312358057
```

## Interpretation

No qualifying control run failed; this is an evidence-continuity failure, not evidence of VM outage or service failure. The observed maximum gap exceeded the accepted seven-hour bound. Therefore Attempt 2 cannot close the 24h gate and its elapsed time must not be promoted into P19 final validation.

This failure is independent of the already-documented runtime SHA drift between deployed `b31b2136b5fe982d0b63b0135479b1549041906c` and repository `main`.

## Fail-closed state

```text
P19_REAL_SOAK_ATTEMPT_2 = FAILED_CONTINUITY
P19_REAL_24H_SOAK = NOT_VALIDATED
P19_FULL_GATE = OPEN
P20_OPERATIONAL_EXECUTION = NOT_STARTED
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
BASELINE_CHANGE_BY_THIS_RECORD = NO
CADENCE_CHANGE_BY_THIS_RECORD = NO
TAILSCALE_TRUST_CHANGE = NO
A5_ACTIVATION = NO
```

Any future real-soak attempt must establish its own explicit baseline and must not reuse elapsed time from Attempts 1 or 2.
