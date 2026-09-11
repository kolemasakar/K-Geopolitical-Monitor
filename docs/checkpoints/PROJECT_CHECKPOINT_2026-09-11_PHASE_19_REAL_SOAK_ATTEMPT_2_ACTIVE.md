# K-Geopolitical Monitor — Phase 19 Real Soak Attempt 2

Date: 2026-09-11
Status: `ATTEMPT_2_ACTIVE / TEMPORAL_SOAK_IN_PROGRESS / RUNTIME_CANDIDATE_IDENTITY_OPEN`
Strategic machine state: `4.34 / INTENTIONALLY_FROZEN`

## Attempt history

```text
ATTEMPT_1 = FAILED_CONTINUITY / NOT_EVIDENCED / CLOSED
ATTEMPT_1_MAX_GAP = 9.280277777777778h
MAX_ALLOWED_GAP = 7h
ATTEMPT_1_24H = NOT_VALIDATED
```

No Attempt 1 elapsed time carries forward.

## Canonical Attempt 2 baseline

Cadence remediation canonical commit:

`2cd911fa45d3a9ea94abc5979c1a2e109416a1d4`

Attempt 2 reanchor merged through PR #76. Post-merge canonical SHA at activation:

`b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f`

```text
BASELINE_UTC = 2026-09-11T07:38:44Z
HEALTH_DISPATCHER = every 3h at minute 27 UTC
DEAD_MAN_AUDIT = every 3h at minute 47 UTC
MAX_ALLOWED_EVIDENCE_GAP = 7h
TAILSCALE_TRUST_PATH = unchanged
```

Temporal boundaries:

```text
24h = 2026-09-12T07:38:44Z
72h = 2026-09-14T07:38:44Z
7d  = 2026-09-18T07:38:44Z
```

## Post-merge exact-main validation

```text
DISPATCHER_RUN = 34577383874 / SUCCESS
CONTROL_RUN = 34577394775 / SUCCESS
CONTROL_JOB = 103192880010
AUDIT_RUN = 34577455069 / SUCCESS
AUDIT_JOB = 103193065140
EXACT_MAIN_CI_RUN = 34577383894 / SUCCESS
EXACT_MAIN_TESTS = 1179 passed in 119.33s
```

Live owner-local health observation:

```text
OBSERVATION_UTC = 2026-09-11T08:05:11Z
KGM_TARGET = kgm-e4-owner-pilot
TAILSCALE_IP = 100.102.136.23
TAILSCALE_CONNECTIVITY = PASS
KGM_MONITOR_SERVICE = active -> active
RUNTIME_DB_READ_AS_KGMOPS = DENIED
ARBITRARY_ROOT_ESCALATION = DENIED
RESTART = SKIPPED
ANSIBLE = ok=10 changed=0 unreachable=0 failed=0 skipped=1
```

Post-merge audit:

```text
P19_SOAK_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
CONTROL_COMPLETED_RUNS = 2
CONTROL_FAILED_RUNS = 0
QUALIFYING_HEALTH_OBSERVATIONS = 2
CURRENT_MAX_GAP_HOURS = 0.44083333333333335
MAX_ALLOWED_GAP_HOURS = 7.0
ARTIFACT_ID = 10190201003
ARTIFACT_RETENTION = 30d
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
```

## Runtime drift finding

A read-only VM↔repository audit performed while Attempt 2 was running established:

```text
OBSERVED_DEPLOYED_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
AUDIT_BASE_REPOSITORY_SHA = b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f
REPOSITORY_COMMITS_AHEAD_OF_DEPLOYED = 516
RUNTIME_CODE_DRIFT = MATERIAL
P19_RUNTIME_CANDIDATE_IDENTITY = UNRESOLVED
```

The temporal soak remains valid evidence for the build actually deployed on `kgm-e4-owner-pilot`, but final P19 closure must not imply that current repository application code was soak-tested unless the intended candidate is explicitly resolved.

No deployment or restart was performed during the audit. See:

`docs/evidence/PHASE_19_OWNER_LOCAL_RUNTIME_DRIFT_AUDIT_2026-09-11.md`

## Closure preparation

P19 milestone/retention requirements are prepared in:

`docs/implementation/PHASE_19_CLOSURE_PREP_AND_EVIDENCE_RETENTION.md`

Thirty-day Actions artifact retention is sufficient for the running 7-day gate, but accepted milestones must also receive durable evidence records under `docs/evidence/`.

## P20 preparation status

P20 design is prepared only; operational execution remains blocked:

```text
P20_DESIGN = PREPARED
P20_EXECUTION = NOT_STARTED
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
```

Design record:

`docs/implementation/PHASE_20_SOURCE_COVERAGE_COLLECTION_QUALITY_DESIGN_SPEC.md`

## 2026-09-11 pre-24h supplemental state

A later read-only control/audit cycle and parallel preparation work strengthened the Attempt 2 evidence without changing the canonical baseline or owner-local runtime.

Latest qualifying evidence:

```text
CONTROL_RUN = 34596182532 / SUCCESS
CONTROL_JOB = 103252358278
LATEST_QUALIFYING_OBSERVATION_UTC = 2026-09-11T11:54:06Z
AUDIT_RUN = 34596259823 / SUCCESS
AUDIT_JOB = 103252600665
AUDIT_ARTIFACT_ID = 10262223231
AUDIT_EVALUATED_AT_UTC = 2026-09-11T11:54:37Z
P19_SOAK_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
CONTROL_FAILED_RUNS = 0
CURRENT_MAX_GAP_HOURS = 3.8152777777777778
```

The 24h/72h/7d gates remain `IN_PROGRESS`.

GitHub scheduled delivery is not being treated as a deterministic clock. At the pre-24h inspection, only the eight historical pre-Attempt-2 `schedule` runs were present, while historical scheduled-event delivery had shown multi-hour delay before run creation. The evaluator's actual evidence gap remains the source of truth.

Two safety checks were scheduled outside the repository:

```text
CONTINUITY_CHECK = 2026-09-11T20:30:00+03:00
24H_GATE_CHECK = 2026-09-12T10:45:00+03:00
```

Both are restricted to read-only inspection plus the already-authorized bounded health/audit chain when required; they cannot deploy, restart, change the baseline/cadence/workflows or merge preparation PRs.

### Candidate evidence update

Pre-sync canonical repository SHA:

`5714a76aaf12c77993ed5a02165c02a48d953758`

Supplemental compare against deployed `b31b2136...`:

```text
REPOSITORY_COMMITS_AHEAD_OF_DEPLOYED = 522
FULL_REPOSITORY_DRIFT = MATERIAL
```

The original `516` value above remains the correct historical count against the earlier audit-base `b4c0f6...`.

Exact-candidate validation performed in isolation:

```text
B31B_HISTORICAL_CI = PASS
B31B_HISTORICAL_REAL_HOST_VALIDATION = PASS
B31B_CURRENT_EXACT_SOURCE_REPLAY = PASS
B31B_CURRENT_EXACT_SOURCE_REPLAY_RESULT = 317 passed in 39.36s
EXACT_HISTORICAL_DEPENDENCY_REPRODUCIBILITY = NOT_PROVEN
```

A blob-level comparison also established that the inspected active owner-local monitoring path is unchanged between deployed `b31b...` and canonical `5714a76...`: fifteen application files and `deployment/systemd/kgm-monitor.service` are blob-identical. The bootstrap script and broader repository/dependency environment are not identical.

Therefore:

```text
OWNER_LOCAL_ACTIVE_RUNTIME_CODE_PATH_EQUIVALENCE = PASS_FOR_INSPECTED_BLOBS
OWNER_LOCAL_SYSTEMD_EXECUTION_CONTRACT_EQUIVALENCE = PASS
FULL_REPOSITORY_EQUIVALENCE = NO
FULL_DEPLOYMENT_TOOLING_EQUIVALENCE = NO
CURRENT_MAIN_RUNTIME_EQUIVALENCE = NOT_CLAIMED
PATH_A_READINESS = CONDITIONAL_PREFERRED_EVIDENCE_STRENGTHENED
PATH_A_AUTHORIZED = NO
```

Targeted post-candidate regression screening found no known candidate-runtime blocker, but exhaustive semantic diff review remains open/fail-closed.

### Parallel draft preparation

```text
PR_78_P20_IMPLEMENTATION_READY = DRAFT / CI_PASS / UNMERGED
PR_79_RUNTIME_CANDIDATE_DECISION = DRAFT / UNMERGED / REVALIDATING_AFTER_EVIDENCE_UPDATES
PR_80_SECURITY_HARDENING = DRAFT / CI_PASS / P19_CONTRACT_PASS / UNMERGED
PR_81_MILESTONE_EVIDENCE_AUTOMATION = DRAFT / CI_PASS / UNMERGED
```

None of these preparation PRs changes canonical `main` while Attempt 2 is active.

Detailed synchronized pre-24h checkpoint:

`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-11_PHASE_19_PRE_24H_PARALLEL_PREP_COMPLETE.md`

## Current roadmap position

```text
P19_DETERMINISTIC_HARNESS = PASS
P19_OWNER_LOCAL_ACCESS = REVALIDATED
P19_CONTROL_CHAIN = PASS
P19_ATTEMPT_1 = FAILED_CONTINUITY / CLOSED
P19_ATTEMPT_2 = ACTIVE
P19_CONTINUITY_STATUS = PASS
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
P19_RUNTIME_CANDIDATE_IDENTITY = CONDITIONAL_B31B_PENDING_FORMAL_DECISION
P19_FULL_GATE = OPEN
P20_EXECUTION = NOT_STARTED
```

## Binding boundaries

```text
OWNER_LOCAL_RUNTIME = CANONICAL
CANONICAL_STORAGE = PROJECT_LOCAL_ONLY
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
RAILWAY_PAID_UPGRADE_AUTHORIZED = NO
RAILWAY_PAYMENT_METHOD_ADD_AUTHORIZED = NO
RAILWAY_CREDIT_PURCHASE_AUTHORIZED = NO
RAILWAY_POST_TRIAL_SPEND_AUTHORIZED = NO
A5 = DEFERRED / NOT AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
```
