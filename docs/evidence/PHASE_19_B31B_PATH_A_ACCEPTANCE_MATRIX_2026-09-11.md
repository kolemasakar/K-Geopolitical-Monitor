# Phase 19 — `b31b2136...` Path A Acceptance Matrix

Date: 2026-09-11
Status: `CONDITIONAL_READINESS / NOT_AUTHORIZED`

## Purpose

Evaluate whether the already deployed owner-local runtime candidate
`b31b2136b5fe982d0b63b0135479b1549041906c` can remain the explicit Phase 19
candidate without resetting the active Attempt 2 temporal soak.

This document is evidence/decision preparation only. It does not deploy code,
restart services, change the canonical soak baseline, change GitHub Actions
cadence/workflows, change the Tailscale trust path, or authorize final P19
closure.

## Candidate identity

```text
CANDIDATE_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
TREE_SHA = 7d097f988849b91bfe081307f61a6708ceb61e45
COMMIT_DATE_UTC = 2026-09-01T08:25:20Z
COMMIT_MESSAGE = Add E9A.6 state-preserving real-host validation
```

The candidate exists in canonical Git history and is the build last observed as
deployed on `kgm-e4-owner-pilot` during the active P19 Attempt 2 health chain.

## Direct candidate evidence

| Gate | Evidence | Result |
| --- | --- | --- |
| Commit/tree available | canonical Git history | PASS |
| Historical exact-SHA CI | run `33486945121`, attempt 1 | PASS |
| Historical real-host validation | run `33486944907` | PASS |
| Current exact-source CI replay | run `33486945121`, attempt 2, job `103264025849` | PASS |
| Current replay test count | `317 passed in 39.36s` | PASS |
| Current deployed SHA | last qualifying owner-local health evidence reports `b31b2136...` | PASS_AT_LAST_OBSERVATION / REVERIFY_AT_CLOSURE |
| No Attempt 2 deployment/restart | active soak operating boundary | PASS / CONTINUOUS REQUIREMENT |
| 24h temporal gate | boundary `2026-09-12T07:38:44Z` | IN_PROGRESS |
| 72h temporal gate | boundary `2026-09-14T07:38:44Z` | IN_PROGRESS |
| 7d temporal gate | boundary `2026-09-18T07:38:44Z` | IN_PROGRESS |

## Dependency reproducibility comparison

### Candidate `b31b2136...`

Project metadata declared:

```text
runtime:
  fastapi >=0.116,<1
  uvicorn >=0.35,<1

test:
  pytest >=8.0
  httpx >=0.28,<1
```

The historical workflow used mutable `actions/checkout@v4` and
`actions/setup-python@v5` references and did not apply the later focused CI
constraints contract.

The 2026-09-11 replay therefore proves that the exact source tree still passes
its own suite in the contemporary GitHub runner environment, but it does not
prove byte-for-byte or package-for-package reconstruction of the 2026-09-01
environment.

### Current canonical repository

Current metadata additionally includes `psycopg[binary]>=3.3,<4`, uses
`httpx2>=2.12,<3`, explicitly constrains `anyio>=4.14.2,<4.15`, and treats
selected deprecations as test errors. Current CI also applies a focused
compatibility constraints file.

Therefore:

```text
EXACT_SOURCE_REPRODUCIBILITY = PASS
EXACT_HISTORICAL_DEPENDENCY_REPRODUCIBILITY = NOT_PROVEN
DEPENDENCY_COMPATIBILITY_IN_CURRENT_RUNNER = PASS
```

## Regression applicability classification

The current canonical suite contains substantially more tests than existed at
`b31b2136...`. Those tests must not be mechanically back-projected onto an older
candidate.

### A — candidate-native tests

Tests that existed in the exact `b31b2136...` source tree are candidate-specific
and authoritative for the source-level replay. The replay result is:

```text
B31B_NATIVE_SUITE = 317 PASSED
```

The tree already included runtime/deployment/security coverage such as:

- database runtime profile;
- E4 bootstrap/deployment/host validation;
- E4 real-host workflow contract;
- E9A security hardening;
- reproducibility instrumentation;
- runtime backup, health, lease and storage;
- unattended runner/service;
- application feature and persistence tests present at that revision.

### B — historical real-host candidate validation

Run `33486944907` executed the E9A.6 state-preserving real-host validation for
this exact candidate and concluded success. This is candidate-specific historical
runtime evidence.

### C — later candidate-independent control/evidence tests

Post-`b31b...` P19 soak evaluator, control-plane, evidence-retention and closure
mechanics validate the monitoring/control system around the candidate. They may
support P19 control semantics but must not be used to claim that current-main
application code is deployed or soak-tested.

Examples include later P19 soak-gate/control workflow tests and evidence tooling.

### D — later tests for code/features absent from `b31b...`

Tests for functionality, migrations or infrastructure introduced after the
candidate are `NOT_APPLICABLE_TO_B31B` as candidate-runtime acceptance tests.
They remain valid for the newer canonical repository, but cannot be required of
an older frozen candidate without first deploying that newer code.

### E — later regressions against code paths that already existed in `b31b...`

This is the only post-candidate class that could materially block Path A without
a deployment. Because the repository advanced by hundreds of commits, later
regression/security fixes touching pre-existing code must be reviewed for known
candidate-relevant defects before Path A can be fully authorized.

Current status:

```text
POST_B31B_EXISTING_PATH_REGRESSION_REVIEW = OPEN
```

The open status is intentional and fail-closed; absence of a discovered defect
has not yet been promoted to evidence that no such defect exists.

## Acceptance matrix

| Requirement | Status | Closure rule |
| --- | --- | --- |
| Exact candidate commit/tree available | PASS | none |
| Historical exact-SHA CI | PASS | none |
| Historical exact-SHA real-host validation | PASS | none |
| Current exact-source replay | PASS | none |
| Candidate-native suite | PASS (`317`) | none |
| Exact historical dependency reproduction | PARTIAL / NOT_PROVEN | may remain an explicit limitation if source replay and candidate-specific runtime evidence are accepted; must not be mislabeled as exact environment reproduction |
| Later candidate-independent P19 controls | PASS / SEPARATE SEMANTIC DOMAIN | may support control/evidence semantics only |
| Later new-feature tests | NOT_APPLICABLE_TO_B31B | no back-projection |
| Later regression review of pre-existing paths | OPEN | blocking for unconditional Path A authorization |
| Deployed SHA reverified at milestone/final closure | OPEN / REQUIRED | must equal `b31b2136...` |
| Attempt 2 runtime remained unmutated | CONTINUOUSLY_REQUIRED | any deployment/restart that changes candidate invalidates candidate-specific elapsed time |
| 24h/72h/7d gates | IN_PROGRESS | all must pass with terminal observations and continuity <=7h |

## Semantic boundaries

```text
317_PASS_CURRENT_REPLAY != EXACT_2026_09_01_DEPENDENCY_REPRODUCTION
P19_CONTROL_CHAIN_PASS != CURRENT_MAIN_RUNTIME_EQUIVALENCE
CURRENT_MAIN_TEST_COUNT != REQUIRED_B31B_TEST_COUNT
CANDIDATE_INDEPENDENT_CONTROL_EVIDENCE != CANDIDATE_SPECIFIC_RUNTIME_EVIDENCE
```

## Decision state

Path A remains the preferred low-disruption option because it preserves the
already accumulated candidate-specific temporal soak and now has both historical
real-host evidence and a successful contemporary exact-source replay.

It is not yet fully authorized because the later-regression review of code paths
that already existed at `b31b...` remains open and the elapsed 24h/72h/7d gates
are still in progress.

```text
PATH_A_READINESS = CONDITIONAL_PREFERRED
PATH_A_AUTHORIZED = NO
PATH_B = FALLBACK_PREPARED_NOT_EXECUTED
CURRENT_MAIN_RUNTIME_EQUIVALENCE = NOT_CLAIMED
P19_BASELINE_MUTATION = NO
RUNTIME_MUTATION = NO
```
