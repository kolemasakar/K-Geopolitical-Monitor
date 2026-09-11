# Phase 19 Closure Preparation and Evidence Retention Plan

Date: 2026-09-11
Status: `PREPARED / NO LIVE-SOAK MUTATION`

## 1. Purpose

Prepare deterministic P19 closure steps while Attempt 2 continues to accumulate real elapsed evidence. This document does not change the active baseline, cadence, max-gap threshold, runtime, control plane, or strategic boundaries.

## 2. Current Attempt 2 boundaries

```text
BASELINE = 2026-09-11T07:38:44Z
24H_BOUNDARY = 2026-09-12T07:38:44Z
72H_BOUNDARY = 2026-09-14T07:38:44Z
7D_BOUNDARY = 2026-09-18T07:38:44Z
TARGET_CADENCE = 3h
MAX_ALLOWED_EVIDENCE_GAP = 7h
```

Attempt 1 remains `FAILED_CONTINUITY / CLOSED` and its elapsed time is not reusable.

## 3. Milestone acceptance checklist

For each milestone, all conditions are mandatory:

- canonical baseline file still equals the accepted Attempt 2 baseline;
- no failed qualifying `workflow_dispatch` control run after baseline;
- continuity evaluator returns `PASS`;
- maximum observed evidence gap is `<= 7h`;
- at least one qualifying health observation exists at or after the milestone boundary;
- terminal observation reports successful bounded control;
- no restart is silently inferred from a health observation;
- evidence artifact is successfully preserved;
- current-main CI remains green for any closure-documentation change;
- no A5/shared-runtime/cutover/paid-resource/migration-033 boundary changed.

Milestone outputs:

```text
P19_REAL_24H_SOAK = PASS | IN_PROGRESS | FAIL_CONTINUITY
P19_REAL_72H_SOAK = PASS | IN_PROGRESS | FAIL_CONTINUITY
P19_REAL_7D_SOAK = PASS | IN_PROGRESS | FAIL_CONTINUITY
```

## 4. 24h closure procedure

After `2026-09-12T07:38:44Z`:

1. Allow a post-boundary health observation to complete.
2. Run/read the P19 soak-gate audit.
3. Verify continuity and terminal observation.
4. Record run IDs, job IDs, observation UTC, max gap, failed-run count, artifact ID and exact `main` SHA.
5. Mark only `P19_REAL_24H_SOAK = PASS` if every criterion passes.
6. Keep 72h and 7d gates open.

A successful 24h gate does not by itself close P19.

## 5. 72h procedure

Repeat the same process after `2026-09-14T07:38:44Z` using the same baseline. Do not re-anchor solely because 24h passed.

## 6. 7d procedure

Repeat after `2026-09-18T07:38:44Z`. A 7d elapsed PASS is necessary but not sufficient for the full P19 gate: final closure must also resolve the runtime↔repo drift classification and reconcile the roadmap's broader 7/14/30-day stability objective.

## 7. Final P19 closure checklist

Before declaring `P19_BETA_OPERATIONAL_STABILITY_VALIDATED`, verify:

- accelerated deterministic harness: PASS;
- owner-local access/control plane: PASS;
- real soak Attempt 2 continuity: PASS through the chosen required duration;
- stale/missed/stalled/failure diagnostics: PASS;
- retry/idempotency behavior: PASS;
- database integrity checks: PASS;
- recovery behavior: evidenced;
- runtime↔repo drift decision: explicitly documented;
- no silent critical pipeline failure evidenced during accepted observation window;
- evidence package is durable enough for later audit;
- next-stage entry conditions are explicit.

## 8. Evidence retention audit

Current `p19-owner-local-soak-gate-audit.yml` uploads:

```text
p19-soak-audit.json
p19-soak-audit.log
p19-observations.txt
```

with:

```text
retention-days: 30
```

### Finding

Thirty-day artifact retention is sufficient for the current 24h/72h/7d milestones if GitHub retention behaves as configured, but it is weak for long-lived historical audit because:

- the roadmap references 7/14/30-day stability evidence;
- an artifact produced near the start of a 30-day study can expire around the time the study itself completes;
- closure evidence should not depend exclusively on expiring Actions artifacts.

### Required retention policy for closure

Use two layers:

- **ephemeral execution evidence** — Actions artifacts, currently 30 days;
- **durable canonical evidence** — concise, non-secret evidence summaries committed under `docs/evidence/` at accepted milestones/closure.

For a future non-soak-sensitive maintenance window, consider increasing P19 audit artifact retention to 90 days. This plan intentionally does **not** alter the active workflow during the current soak.

## 9. Evidence package schema

Each durable milestone record should contain at minimum:

```text
MILESTONE
BASELINE_UTC
BOUNDARY_UTC
EVALUATED_AT_UTC
TERMINAL_OBSERVATION_UTC
CANONICAL_MAIN_SHA
CONTROL_RUN_ID
CONTROL_JOB_ID
AUDIT_RUN_ID
AUDIT_JOB_ID
ARTIFACT_ID
QUALIFYING_OBSERVATION_COUNT
FAILED_CONTROL_COUNT
MAX_GAP_HOURS
MAX_ALLOWED_GAP_HOURS
CONTINUITY_STATUS
SERVICE_STATE
SECURITY_BOUNDARY_RESULT
RUNTIME_DEPLOYED_SHA
RUNTIME_REPO_DRIFT_CLASSIFICATION
```

## 10. Stop conditions

Do not close a milestone if any of the following occurs:

- gap `> 7h`;
- failed qualifying control run;
- service unavailable;
- exact peer contract fails;
- evidence timestamps are ambiguous or missing;
- baseline changes without explicit re-anchor;
- evidence artifact cannot be reconstructed;
- runtime is materially changed without a new accepted baseline.

## 11. Preserved project boundaries

```text
P20_IMPLEMENTATION = NOT_STARTED
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
A5 = DEFERRED / NOT_AUTHORIZED
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_AUTHORIZED
STRATEGIC_MACHINE_STATE = 4.34 / INTENTIONALLY_FROZEN
```
