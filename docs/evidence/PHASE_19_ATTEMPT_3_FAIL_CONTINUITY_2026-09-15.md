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
run_number = 64
run_id = 34932643766
job_id = 104263902641
event = schedule
conclusion = failure
artifact_id = 10381978328
artifact_digest = sha256:5b37a0ef02fd065b5faed2c9cb97836b167fe86b81cc431d73a04742084a5bee
evaluated_at_utc = 2026-09-15T05:25:20Z
```

Exact evaluator result preserved from run #64 job logs and its artifact:

```text
P19_SOAK_AUDIT=FAIL_CONTINUITY
P19_CONTINUITY_STATUS=FAIL_CONTINUITY
P19_REAL_24H_SOAK=FAIL_CONTINUITY
P19_REAL_72H_SOAK=IN_PROGRESS
P19_REAL_7D_SOAK=IN_PROGRESS
P19_CONTROL_COMPLETED_RUNS=10
P19_CONTROL_FAILED_RUNS=0
P19_QUALIFYING_HEALTH_OBSERVATIONS=10
current_max_gap_hours=7.9025
max_allowed_gap_hours=7.0
latest_observation_utc=2026-09-15T05:06:05Z
qualifying_observation_count_after_baseline=9
```

The evaluator's 72h/7d `IN_PROGRESS` fields do not make Attempt 3 recoverable. Once continuity is violated, Attempt 3 cannot later satisfy the full fail-closed soak contract.

## Qualifying observation timeline

The run #64 artifact preserved these timestamps:

```text
2026-09-13T08:51:24Z
2026-09-13T12:10:51Z
2026-09-13T16:32:18Z
2026-09-13T20:59:41Z
2026-09-13T23:17:00Z
2026-09-14T05:13:02Z
2026-09-14T13:07:11Z
2026-09-14T19:53:53Z
2026-09-14T23:56:28Z
2026-09-15T05:06:05Z
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

## Dispatcher schedule evidence / RCA refinement

Canonical dispatcher configuration at `3bfe4c102...` is:

```text
cron = 27 */3 * * *
target_observation_cadence_hours = 3
max_evidence_gap_hours = 7
```

The repository's scheduled-run history for 2026-09-14 contains only four scheduled dispatcher runs in the UTC day. Relevant dispatcher records are:

```text
run #25 / 34808756269
created_at = 2026-09-14T05:12:14Z
conclusion = success
qualifying observation = 2026-09-14T05:13:02Z

run #26 / 34847185678
created_at = 2026-09-14T13:06:30Z
conclusion = success
qualifying observation = 2026-09-14T13:07:11Z

run #27 / 34889570586
created_at = 2026-09-14T19:52:59Z
conclusion = success
qualifying observation = 2026-09-14T19:53:53Z

run #28 / 34910963516
created_at = 2026-09-14T23:55:07Z
conclusion = success
qualifying observation = 2026-09-14T23:56:28Z
```

The fatal health-evidence gap aligns directly with an approximately `7h54m` interval between two successful scheduled dispatcher deliveries (#25 -> #26), despite the workflow's intended 3-hour cron cadence. No failed qualifying bounded control explains the interval.

This supports the orchestration-layer conclusion:

```text
SCHEDULE_DEPENDENT_DISPATCH_CONTINUITY = FAILED
EXPECTED_3H_SCHEDULE_DELIVERY = NOT_OBSERVED_RELIABLY
QUALIFYING_CONTROL_FAILURES = 0
RUNTIME_OUTAGE = NOT_ESTABLISHED
```

The repository evidence is sufficient to attribute the P19 gate failure to the schedule-dependent evidence-delivery mechanism. It is not sufficient to distinguish conclusively among GitHub-internal delayed scheduling, omitted scheduled events, queue/service behavior, or another platform-side scheduling mechanism detail. Do not claim a specific undocumented GitHub internal cause.

## Failure classification

```text
ROOT_CAUSE_CLASS = SCHEDULE_DEPENDENT_EVIDENCE_DELIVERY_FAILURE
RUNTIME_OUTAGE = NOT_ESTABLISHED
BOUNDED_CONTROL_FAILURE = NO
GITHUB_SCHEDULE_DELIVERY_RELIABILITY = INSUFFICIENT_FOR_CURRENT_P19_CONTRACT
SPECIFIC_GITHUB_INTERNAL_CAUSE = NOT_CONCLUSIVELY_PROVEN
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

Read-only diagnosis, evidence preservation, and isolated documentation updates remain safe. Any Attempt 4 design should remove GitHub scheduled-event delivery as the sole continuity anchor rather than simply restarting the same mechanism unchanged.
