# Phase 19 — Attempt 2 — 24h Milestone Failure Evidence

Date: `2026-09-12`
Status: `FAIL_CONTINUITY`

This document records the fail-closed result of the Phase 19 Attempt 2 24-hour milestone evaluation. It does not authorize a new baseline, a new attempt, deployment, restart, runtime mutation, workflow/cadence changes, Tailscale trust changes, P20 activation, or merge of preparation PRs.

## Canonical contract

```text
BASELINE_UTC = 2026-09-11T07:38:44Z
24H_BOUNDARY_UTC = 2026-09-12T07:38:44Z
MAX_ALLOWED_EVIDENCE_GAP_HOURS = 7.0
CANONICAL_REPOSITORY_SHA_AT_GATE = ccf097ac55f480057cb8d450edfd29f392eb48e2
EXPECTED_DEPLOYED_RUNTIME_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
```

## Post-boundary bounded health observation

The existing bounded KGM health control was re-run after the 24h boundary without altering its operation.

```text
CONTROL_RUN_ID = 34673955916
CONTROL_RUN_ATTEMPT = 2
CONTROL_JOB_ID = 103520886824
CONTROL_OPERATION = health
CONTROL_RESULT = SUCCESS
OBSERVATION_UTC = 2026-09-12T07:45:10Z
REPOSITORY_SHA = ccf097ac55f480057cb8d450edfd29f392eb48e2
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
```

The terminal observation is after the 24h boundary by 6 minutes 26 seconds and therefore satisfies the terminal-observation timing requirement. Candidate identity and bounded runtime/security assertions remained valid.

## 24h soak-gate audit

The existing P19 owner-local soak-gate audit was then re-run against the unchanged canonical baseline.

```text
AUDIT_RUN_ID = 34674788045
AUDIT_RUN_ATTEMPT = 2
AUDIT_JOB_ID = 103521055076
AUDIT_REPOSITORY_SHA = ccf097ac55f480057cb8d450edfd29f392eb48e2
AUDIT_EVALUATED_AT_UTC = 2026-09-12T07:46:59Z
AUDIT_ARTIFACT_ID = 10293909700
AUDIT_ARTIFACT_SHA256 = f962db16c853879c391f02262f075778f6a6e2256b83814ac9e3057b04dce4a6
```

Evaluator output:

```text
P19_CONTROL_COMPLETED_RUNS = 8
P19_CONTROL_FAILED_RUNS = 0
P19_QUALIFYING_HEALTH_OBSERVATIONS = 8
QUALIFYING_OBSERVATION_COUNT_AFTER_BASELINE = 7
LATEST_OBSERVATION_UTC = 2026-09-12T07:45:10Z
CURRENT_MAX_GAP_HOURS = 8.337222222222222
MAX_ALLOWED_GAP_HOURS = 7.0
P19_SOAK_AUDIT = FAIL_CONTINUITY
P19_CONTINUITY_STATUS = FAIL_CONTINUITY
P19_REAL_24H_SOAK = FAIL_CONTINUITY
P19_REAL_72H_SOAK = IN_PROGRESS
P19_REAL_7D_SOAK = IN_PROGRESS
```

## Fail-closed conclusion

```text
BASELINE_UNCHANGED = PASS
POST_BOUNDARY_TERMINAL_OBSERVATION = PASS
DEPLOYED_RUNTIME_SHA = PASS
SERVICE_AND_SECURITY_ASSERTIONS = PASS
FAILED_QUALIFYING_CONTROLS = 0
CONTINUITY_MAX_GAP_REQUIREMENT = FAIL
P19_24H_MILESTONE = FAIL_CONTINUITY
P19_24H_PASS = NOT_ASSERTED
```

The decisive failure is historical continuity: the evaluator measured a maximum qualifying-observation gap of `8.337222222222222h`, which exceeds the contractual `7.0h` maximum. A later healthy terminal observation cannot retroactively repair that gap.

Attempt 2 therefore must not be represented as having passed the 24h milestone under the current contract. Any decision to establish another attempt, change the operational cadence, or adopt another candidate path requires a separate explicit project decision.

## Safety boundary preserved

During this gate evaluation:

- no deployment was performed;
- no service restart was requested or executed;
- no runtime mutation was performed by the bounded health control;
- the P19 baseline was not changed;
- workflows, cadence, evaluator and Tailscale trust were not changed;
- preparation PRs were not merged;
- P20 was not operationally started.
