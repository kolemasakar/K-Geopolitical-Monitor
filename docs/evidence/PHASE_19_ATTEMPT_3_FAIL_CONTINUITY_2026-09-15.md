# K-Geopolitical Monitor — Phase 19 Attempt 3 FAIL_CONTINUITY Evidence

Date: 2026-09-15
Scope: durable documentation of the canonical P19 Attempt 3 continuity failure. This document is evidence-only and does not authorize runtime, workflow, cadence, baseline, deployment, restart, Tailscale, privilege, migration, paid-resource, or P20 mutations.

## Canonical attempt identity

```text
CANONICAL_MAIN_SHA = 3bfe4c1021fe27a363463d3eb8ecc3018b0989a3
P19_ATTEMPT = 3
P19_BASELINE_UTC = 2026-09-13T08:51:24Z
P19_RUNTIME_CANDIDATE = b31b2136b5fe982d0b63b0135479b1549041906c
```

## Failing audit

```text
workflow = P19 Owner-Local Soak Gate Audit
run_id = 34932643766
job_id = 104263902641
event = schedule
conclusion = failure
artifact_id = 10381978328
evaluated_at_utc = 2026-09-15T06:50:50Z
```

Exact evaluator result preserved from the audit artifact/log:

```text
P19_SOAK_AUDIT=FAIL_CONTINUITY
P19_CONTINUITY_STATUS=FAIL
P19_REAL_24H_SOAK=FAIL_CONTINUITY
P19_REAL_72H_SOAK=IN_PROGRESS
P19_REAL_7D_SOAK=IN_PROGRESS
P19_CONTROL_COMPLETED_RUNS=10
P19_CONTROL_FAILED_RUNS=0
P19_QUALIFYING_HEALTH_OBSERVATIONS=10
current_max_gap_hours=7.9025
max_allowed_gap_hours=7.0
latest_observation_utc=2026-09-14T19:24:32Z
```

The evaluator's 72h/7d `IN_PROGRESS` fields do not make Attempt 3 recoverable. Once continuity is violated, Attempt 3 cannot later satisfy the full fail-closed soak contract.

## Qualifying observation timeline

The audit artifact preserved these timestamps:

```text
2026-09-13T08:51:24Z
2026-09-13T12:10:51Z
2026-09-13T15:10:38Z
2026-09-13T16:36:07Z
2026-09-13T18:11:12Z
2026-09-13T22:32:50Z
2026-09-14T01:43:48Z
2026-09-14T05:13:02Z
2026-09-14T13:07:11Z
2026-09-14T19:24:32Z
```

Fatal interval:

```text
previous_observation = 2026-09-14T05:13:02Z
next_observation = 2026-09-14T13:07:11Z
gap = 7h 54m 09s
gap_hours = 7.9025
allowed_gap_hours = 7.0
```

The Attempt 3 24-hour boundary was `2026-09-14T08:51:24Z`, which lies inside the fatal evidence gap. Therefore the 24-hour gate is `FAIL_CONTINUITY`.

## Failure classification

Observed facts:

```text
QUALIFYING_CONTROL_FAILURES = 0
RUNTIME_OUTAGE = NOT_ESTABLISHED
CONTINUITY_FAILURE = YES
FAILURE_CLASS = EVIDENCE_CONTINUITY/CADENCE
```

The safest current root-cause statement is:

```text
ROOT_CAUSE_CLASS = SCHEDULED_EVIDENCE_DELIVERY/CADENCE_FAILURE
PLATFORM_SCHEDULE_LATENCY_OR_JITTER = MOST_LIKELY / CONSISTENT_WITH EVIDENCE
GITHUB_PLATFORM_CAUSALITY = NOT_CONCLUSIVELY_PROVEN
```

This failure must not be represented as proof that the owner-local service itself failed. Conversely, later successful observations cannot retroactively repair the broken continuity interval.

## Project-state consequence

```text
P19_REAL_SOAK_ATTEMPT_1 = FAILED_CONTINUITY
P19_REAL_SOAK_ATTEMPT_2 = FAILED_CONTINUITY
P19_REAL_SOAK_ATTEMPT_3 = FAILED_CONTINUITY
P19_REAL_24H_SOAK = FAIL_CONTINUITY
P19_FULL_GATE = OPEN
P20_EXECUTION = NOT_STARTED
```

The existing Attempt 3 baseline remains historical evidence and must not be changed merely to hide or repair this failure. A new Attempt 4 baseline or revised continuity mechanism requires an explicit owner decision after root-cause review.

## Freeze/recovery posture

Recommended fail-closed posture as of this evidence record:

```text
DEVELOPMENT_FREEZE = EXTEND_PENDING_RCA_AND_OWNER_DECISION
DEPLOY = NO
RESTART = NO
BASELINE_CHANGE = NO
WORKFLOW_OR_CADENCE_CHANGE = NO
P20_START = NO
```

Read-only diagnosis, evidence preservation, and isolated documentation updates remain safe. Any Attempt 4 design should address the repeated scheduled-evidence continuity failure rather than simply restarting the same mechanism unchanged.
