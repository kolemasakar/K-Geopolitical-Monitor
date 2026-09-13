# Phase 19 — Runtime Candidate Decision Record

Date prepared: 2026-09-11
Decision applied: 2026-09-13
Status: `PATH_A_OWNER_APPROVED / ATTEMPT_3_ACTIVE / NO_RUNTIME_DEPLOYMENT`
Original base: `5714a76aaf12c77993ed5a02165c02a48d953758`
Current canonical main at audit: `3bfe4c1021fe27a363463d3eb8ecc3018b0989a3`

## Applied owner decision

The owner approved Path A: freeze the actually deployed owner-local runtime as the explicit Phase 19 runtime candidate.

```text
P19_RUNTIME_CANDIDATE_DECISION = PATH_A_FREEZE_DEPLOYED_B31B
P19_INTENDED_RUNTIME_CANDIDATE_SHA = b31b2136b5fe982d0b63b0135479b1549041906c
P19_DEPLOYED_RUNTIME_SHA_MATCHES_INTENDED_CANDIDATE = PASS
P19_ATTEMPT_3_BASELINE_UTC = 2026-09-13T08:51:24Z
P19_ATTEMPT_3 = ACTIVE
P19_FULL_GATE = OPEN
```

The decision does not claim that current repository `main` is covered by the runtime soak. The validated runtime candidate remains exactly `b31b2136b5fe982d0b63b0135479b1549041906c` unless a later explicit release/convergence decision changes it.

## Reason for Attempt 3

Attempts 1 and 2 were invalidated by continuity gaps exceeding the canonical maximum evidence gap. The bounded health controls themselves did not demonstrate a runtime/service failure; the observed failure mode was continuity/scheduling evidence, so a fresh non-backdated baseline was required.

No elapsed time from the failed attempts is reused for Attempt 3 temporal gates.

## Candidate-path record

### Path A — applied

Meaning:

- `b31b2136...` is the explicit P19 runtime candidate;
- Attempt 3 accrues fresh 24h/72h/7d evidence for this candidate;
- closure wording must remain candidate-scoped;
- newer canonical application code is not implicitly covered by the soak.

### Path B — not selected

Converge owner-local runtime to a selected canonical release candidate, then establish a fresh candidate-specific soak.

### Path C — not selected

Retain deployed-build evidence but keep full P19 open until later convergence.

## Current invariants

```text
DEPLOY_APPLICATION_CODE = NO
RESTART_SERVICE = NO
CHANGE_CADENCE = NO
CHANGE_P19_GATE_LOGIC = NO
CHANGE_TAILSCALE_TRUST = NO
MIGRATION_033 = NOT_CREATED_NOT_PREAUTHORIZED
PAID_OR_SHARED_RESOURCES = NOT_AUTHORIZED
```

The only baseline change associated with this decision is the explicit fresh Attempt 3 baseline already recorded on canonical `main`; this branch does not create or alter that baseline.

## Integration status

This PR branch predates Attempt 3 and is materially behind current `main`. The historical evidence files on the branch remain useful, but this decision memo is now a record of an already-applied owner decision rather than a pending choice.

Before any future merge consideration:

```text
REBASE_ON_THEN_CURRENT_MAIN = REQUIRED
CI_AFTER_REBASE = REQUIRED
NO_P19_RUNTIME_MUTATION = REQUIRED
NO_BASELINE_OR_CADENCE_CHANGE = REQUIRED
```

During active Attempt 3, this PR remains draft and unmerged. It may later be archived/closed as superseded if the canonical decision evidence already on `main` is sufficient.