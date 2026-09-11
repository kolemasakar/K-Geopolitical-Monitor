# Phase 19 — `b31b2136...` Post-Candidate Regression Screening

Date: 2026-09-11
Status: `SCREENED_NO_BLOCKER_FOUND / EXHAUSTIVE_DIFF_REVIEW_OPEN`

## Scope

This is a read-only screening of post-candidate repository history for later
fix/regression/security/compatibility work that could invalidate Path A by
revealing a known defect in a code path already present in the deployed
`b31b2136b5fe982d0b63b0135479b1549041906c` candidate.

It is deliberately narrower than a full semantic review of all 522 commits
between the deployed candidate and canonical `5714a76...`; therefore it cannot
by itself promote Path A to unconditional PASS.

## Search classes reviewed

Repository commit history was screened for explicit commit-message markers:

- `fix`;
- `regression`;
- `security`;
- `compatibility`.

Representative results were inspected at file/patch level where they could
plausibly overlap candidate code.

## Findings

### P13 compatibility fixes

Commit `4422fae5e2a4546585a43237d2124f466c457543` (`Fix P13.0 compatibility regressions`)
modified `SOURCE_POLICY.md` and Phase 12 closure/regression tests. It did not
patch the deployed candidate application runtime.

Classification:

```text
CANDIDATE_RUNTIME_BLOCKER = NO
CLASS = POST_CANDIDATE_POLICY/CLOSURE_COMPATIBILITY
```

### P12 deterministic GDELT fixture fix

Commit `cb6866e82d5dc4a26042e0b9d08e9098aae10ecb` changed only a synthetic P12.2
GDELT fixture ordering value.

Classification:

```text
CANDIDATE_RUNTIME_BLOCKER = NO
CLASS = POST_CANDIDATE_TEST_FIXTURE
```

### P15 outcome-state integration fix

Commit `ef922301b99ebb4e7b9042fa3a88445ce26f5ad6` modified
`src/kgeopolitical_monitor/forecast_outcome_persistence.py`. That file is not
present in the exact `b31b...` tree and therefore the fix belongs to functionality
introduced after the candidate.

Classification:

```text
CANDIDATE_RUNTIME_BLOCKER = NO
CLASS = POST_CANDIDATE_NEW_FEATURE
```

### P18/P19, Railway and control-plane fixes

The screened history includes later fixes for:

- P19 dispatcher state parsing;
- `kgmops` Git `safe.directory` health probing;
- Tailscale/control workflow action-generation policy;
- Phase 18 live probe/assertion mechanics;
- Railway build/preflight ordering;
- shared-runtime PostgreSQL/RLS candidate validation.

These concern later control-plane/shared-runtime/activation infrastructure and
are not evidence of a defect in the unchanged owner-local `b31b...` application
candidate. They remain important canonical-main hardening work but are
semantically separate from Path A candidate-runtime acceptance.

## Evidence retained from candidate itself

```text
B31B_HISTORICAL_CI = PASS
B31B_HISTORICAL_REAL_HOST_VALIDATION = PASS
B31B_CURRENT_EXACT_SOURCE_REPLAY = PASS
B31B_CURRENT_EXACT_SOURCE_REPLAY_TESTS = 317
```

The exact-source replay is stronger evidence for candidate behavior than
back-projecting later feature/control tests onto code that did not yet exist.

## Limitation

Commit-message screening is not equivalent to semantic inspection of every
post-candidate code diff. A later commit can alter a pre-existing path without
using `fix`, `regression`, `security` or `compatibility` in its message.

Therefore the correct fail-closed status remains:

```text
KNOWN_POST_B31B_CANDIDATE_BLOCKER = NONE_FOUND_IN_SCREENING
POST_B31B_EXISTING_PATH_REGRESSION_SCREENING = PASS_WITH_LIMITATION
POST_B31B_EXISTING_PATH_EXHAUSTIVE_DIFF_REVIEW = OPEN
PATH_A_READINESS = CONDITIONAL_PREFERRED
PATH_A_AUTHORIZED = NO
```

This limitation must remain explicit until either an exhaustive candidate-path
diff review is completed or the owner formally accepts the older candidate with
that bounded evidence limitation after the temporal soak gates pass.
