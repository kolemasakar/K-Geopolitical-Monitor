# Phase 19 — Pre-24h Runtime Revalidation Evidence

Date: 2026-09-11
Status: `PASS / ATTEMPT_2_ACTIVE / PRE_24H`

This evidence records a fresh bounded owner-local health observation and the immediately following P19 soak-gate audit. It does not authorize deployment, restart, baseline/cadence/workflow/trust changes, P20 operational execution, or a final P19 runtime-candidate decision.

## Canonical attempt contract

```text
ATTEMPT = 2
BASELINE_UTC = 2026-09-11T07:38:44Z
MAX_ALLOWED_EVIDENCE_GAP_HOURS = 7
24H_BOUNDARY_UTC = 2026-09-12T07:38:44Z
72H_BOUNDARY_UTC = 2026-09-14T07:38:44Z
7D_BOUNDARY_UTC = 2026-09-18T07:38:44Z
```

## Fresh bounded health control

```text
CONTROL_RUN_ID = 34602912625
CONTROL_JOB_ID = 103274318511
CONTROL_EVENT = workflow_dispatch
CONTROL_OPERATION = health
REPOSITORY_SHA = 4a1a3e1f4c7d44d9c1821e55d7f7aa98f438015f
TARGET = kgm-e4-owner-pilot
TAILSCALE_IP = 100.102.136.23
OBSERVATION_UTC = 2026-09-11T13:12:17Z
```

Observed runtime result:

```text
DEPLOYED_RUNTIME_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
SERVICE_BEFORE = active
SERVICE_AFTER = active
RUNTIME_DB_READ = denied
ARBITRARY_ROOT_ESCALATION = denied
RESTART = SKIPPED
ANSIBLE_OK = 10
ANSIBLE_CHANGED = 0
ANSIBLE_UNREACHABLE = 0
ANSIBLE_FAILED = 0
ANSIBLE_SKIPPED = 1
KGM_TAILSCALE_CONNECTIVITY = PASS
KGM_TAILSCALE_ANSIBLE_CONTROL = PASS
```

Therefore the deployed candidate identity was freshly reverified without runtime mutation:

```text
A3_CURRENT_DEPLOYED_SHA_REVERIFY = PASS
RUNTIME_MUTATION = NO
SERVICE_RESTART = NO
BASELINE_MUTATION = NO
```

## Immediate soak-gate audit

```text
AUDIT_RUN_ID = 34602993871
AUDIT_JOB_ID = 103274591934
AUDIT_EVENT = workflow_dispatch
AUDIT_REPOSITORY_SHA = 4a1a3e1f4c7d44d9c1821e55d7f7aa98f438015f
AUDIT_EVALUATED_AT_UTC = 2026-09-11T13:12:41Z
AUDIT_ARTIFACT_ID = 10265280733
AUDIT_ARTIFACT_SHA256 = 6836477d024f2be4a5b08c4910db6b656b999860d208397111012090179d5d77
AUDIT_ARTIFACT_RETENTION_DAYS = 30
```

Evaluator result:

```text
P19_SOAK_AUDIT = PASS
P19_CONTINUITY_STATUS = PASS
P19_CONTROL_COMPLETED_RUNS = 4
P19_CONTROL_FAILED_RUNS = 0
P19_QUALIFYING_HEALTH_OBSERVATIONS_RAW = 4
P19_QUALIFYING_OBSERVATIONS_AFTER_BASELINE = 3
LATEST_OBSERVATION_UTC = 2026-09-11T13:12:17Z
CURRENT_MAX_GAP_HOURS = 3.8152777777777778
MAX_ALLOWED_GAP_HOURS = 7.0
P19_REAL_24H_SOAK = IN_PROGRESS
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
```

The raw qualifying count includes the observation exactly equal to the canonical baseline; the evaluator's post-baseline count is strict `> baseline`. This is the previously verified counter semantics, not a discrepancy.

## Runtime-candidate interpretation

The fresh observation strengthens the conditional Path A case because the deployed SHA remains exactly the candidate already covered by:

- historical exact-candidate CI success;
- historical E9A.6 real-host validation success;
- current exact-source CI replay success (`317 passed in 39.36s`);
- inspected active-runtime-path blob equivalence and identical systemd execution contract;
- targeted post-candidate regression screening with no known candidate-runtime blocker found.

The semantic boundary remains fail-closed:

```text
PATH_A_READINESS = CONDITIONAL_PREFERRED_EVIDENCE_STRENGTHENED
PATH_A_AUTHORIZED = NO
FULL_REPOSITORY_EQUIVALENCE = NO
EXACT_HISTORICAL_DEPENDENCY_REPRODUCIBILITY = NOT_PROVEN
CURRENT_MAIN_RUNTIME_EQUIVALENCE = NOT_CLAIMED
P19_FULL_GATE = OPEN
```

No 24h PASS may be asserted before `2026-09-12T07:38:44Z` and a qualifying observation at or after that boundary.

## Safeguards

Two exact-time safeguards remain enabled outside the repository:

```text
P19_CONTINUITY_CHECK = 2026-09-11T20:30:00+03:00
P19_24H_GATE_CHECK = 2026-09-12T10:45:00+03:00
```

They are constrained to existing bounded health/audit actions and may not deploy, restart, mutate the baseline/cadence/workflows/trust path, or merge preparation PRs.