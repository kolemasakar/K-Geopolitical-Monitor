# Phase 19 — Runtime Candidate Verification and Convergence Runbook

Date: 2026-09-11
Status: `READ_ONLY_EVIDENCE_PREPARED / NO_DECISION_APPLIED`

This runbook supplements `PHASE_19_RUNTIME_CANDIDATE_DECISION_MEMO.md`.

## Verified historical facts for deployed `b31b2136...`

The exact deployed SHA exists in canonical Git history:

```text
SHA = b31b2136b5fe982d0b63b0135479b1549041906c
COMMIT_DATE = 2026-09-01T08:25:20Z
COMMIT_MESSAGE = Add E9A.6 state-preserving real-host validation
TREE = 7d097f988849b91bfe081307f61a6708ceb61e45
```

GitHub Actions history for that exact SHA contains two successful push runs:

```text
CI_RUN_ID = 33486945121
CI_CONCLUSION = success

E9A6_REAL_HOST_RUN_ID = 33486944907
E9A6_REAL_HOST_CONCLUSION = success
```

The historical E9A.6 real-host workflow used a pinned SSH trust pattern based on explicit `E4_SSH_KNOWN_HOSTS`, `StrictHostKeyChecking=yes`, and an owner-controlled SSH private key. That pattern is reusable as design precedent for the post-P19 Tailscale/Ansible host-key hardening work.

These facts improve Path A feasibility but do **not** by themselves establish that every current P19 regression/recovery requirement has been rerun against exact `b31b...` under today's test suite.

## Path A verification checklist — freeze deployed candidate

Before declaring `b31b...` the intended P19 candidate, collect or recreate evidence for:

```text
A0_COMMIT_AND_TREE_AVAILABLE = PASS  # already verified
A0_HISTORICAL_CI = PASS              # run 33486945121
A0_HISTORICAL_REAL_HOST = PASS       # run 33486944907
A1_EXACT_SOURCE_REPRODUCIBILITY = OPEN
A2_APPLICABLE_REGRESSION_COVERAGE = OPEN
A3_CURRENT_DEPLOYED_SHA_REVERIFY = OPEN
A4_NO_ATTEMPT_2_RUNTIME_MUTATION = CONTINUOUSLY_REQUIRED
A5_24H_72H_7D_TEMPORAL_GATES = IN_PROGRESS
A6_CANDIDATE_SCOPED_CLOSURE_WORDING = PREPARED_NOT_APPLIED
```

Recommended read-only evidence collection for A1/A2:

- enumerate exact dependency/constraints state at `b31b...`;
- determine which current tests existed and were applicable at that commit;
- classify later tests as candidate-independent control tests versus tests of code absent from `b31b...`;
- where safe, execute exact-commit CI in an isolated test environment without touching the owner-local runtime;
- record any tests that cannot meaningfully apply to the older candidate rather than back-projecting them.

Do not rewrite history or assert that current `main` tests were present at `b31b...`.

## Path B convergence runbook — selected canonical candidate

This path is **not authorized by this document**. When separately authorized:

1. Freeze an exact candidate SHA; never deploy floating `main`.
2. Require exact-main CI and architecture-specific validation for that SHA.
3. Create/verify state backup using the existing state-preserving deployment procedure.
4. Verify pre-deployment service/database state.
5. Deploy exact SHA through the bounded owner-local procedure.
6. Verify deployed `git rev-parse HEAD` equals selected SHA.
7. Verify service active, database integrity, security boundaries and read restrictions.
8. Record deployment evidence and rollback point.
9. Establish a **new P19 candidate-specific real-soak baseline** after deployment.
10. Do not carry any pre-deployment elapsed time into that new candidate's temporal gate.

Required fail-closed conditions:

```text
DEPLOYED_SHA != SELECTED_SHA -> ABORT / ROLLBACK
DB_INTEGRITY != PASS -> ABORT / ROLLBACK
SERVICE_ACTIVE != YES -> ABORT / ROLLBACK
SECURITY_BOUNDARY_REGRESSION -> ABORT / ROLLBACK
BACKUP_NOT_VERIFIED -> DO_NOT_DEPLOY
```

## Candidate-independent vs candidate-specific evidence

Candidate-independent examples may include:

- GitHub control-plane permission model;
- evidence-record format;
- audit/evaluator semantics proven independently of application runtime;
- owner-local access boundary design.

Candidate-specific evidence includes:

- deployed application behavior;
- runtime/database compatibility;
- application recovery behavior tied to code/schema;
- full elapsed stability of the selected build.

No candidate-independent evidence may be used to imply candidate-specific runtime stability.

## Current result

```text
B31B_COMMIT_AVAILABLE = PASS
B31B_HISTORICAL_CI = PASS
B31B_HISTORICAL_REAL_HOST_VALIDATION = PASS
PATH_A_FEASIBILITY = IMPROVED_BUT_NOT_YET_AUTHORIZED
PATH_B_RUNBOOK = PREPARED_NOT_EXECUTED
RUNTIME_MUTATION = NO
P19_BASELINE_MUTATION = NO
```
