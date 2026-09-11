# Phase 19 Closure Preparation and Evidence Retention Contract

Date: 2026-09-11
Status: `PREPARED / NO_LIVE_SOAK_LOGIC_CHANGE`

This document prepares P19 milestone and final closure while Attempt 2 continues. It does not close any elapsed-time gate and does not modify the live soak baseline, cadence, runtime, or trust path.

## Current Attempt 2 temporal contract

```text
BASELINE_UTC = 2026-09-11T07:38:44Z
24H_BOUNDARY = 2026-09-12T07:38:44Z
72H_BOUNDARY = 2026-09-14T07:38:44Z
7D_BOUNDARY  = 2026-09-18T07:38:44Z
MAX_ALLOWED_EVIDENCE_GAP = 7h
HEALTH_CADENCE = every 3h at minute 27 UTC
DEAD_MAN_AUDIT = every 3h at minute 47 UTC
```

Attempt 1 remains `FAILED_CONTINUITY / NOT_EVIDENCED` and contributes no elapsed time to Attempt 2.

## Milestone closure checklist

A temporal milestone may be recorded as PASS only when all of the following are true:

- canonical baseline exactly matches `ops/p19/real_soak_baseline.txt`;
- audit workflow completes successfully on canonical evidence logic;
- `P19_SOAK_AUDIT = PASS`;
- `P19_CONTINUITY_STATUS = PASS`;
- zero failed qualifying control runs are present after the baseline;
- no evidence gap exceeds 7 hours;
- at least one qualifying health observation exists **at or after** the milestone boundary;
- the terminal observation belongs to the current Attempt 2 chain;
- artifact ID and run IDs are recorded in the milestone evidence document;
- the owner-local service remains active before and after health observation;
- bounded-control security assertions remain intact: runtime DB read denied, arbitrary root denied, automatic restart not performed.

A temporal milestone PASS does not by itself close P19.

## Additional final P19 closure requirements

Before `P19_BETA_OPERATIONAL_STABILITY_VALIDATED` may be asserted:

- deterministic/accelerated harness remains PASS;
- real elapsed milestone evidence is preserved;
- representative recovery/restart/retry evidence remains valid;
- exact-main CI is green on the closure candidate;
- architecture-specific validation required by project policy is green;
- no known silent critical failure or canonical data-loss condition remains unresolved;
- the intended owner-local runtime candidate is explicitly identified;
- deployed runtime SHA is either the declared frozen P19 candidate or matches the selected convergence candidate;
- the runtime-drift finding in `docs/evidence/PHASE_19_OWNER_LOCAL_RUNTIME_DRIFT_AUDIT_2026-09-11.md` is resolved explicitly rather than ignored.

Recommended explicit gate field:

```text
P19_DEPLOYED_RUNTIME_SHA_MATCHES_INTENDED_CANDIDATE = PASS
```

If a deployment is required to satisfy this field, a new real-soak baseline must be established after that deployment; pre-deployment elapsed time cannot validate the new candidate.

## Evidence retention audit

The P19 elapsed-soak audit currently uploads:

```text
p19-soak-audit.json
p19-soak-audit.log
p19-observations.txt
```

with GitHub Actions artifact retention of **30 days**.

Assessment:

```text
LONGEST_CURRENT_SOAK_GATE = 7d
ARTIFACT_RETENTION = 30d
RETENTION_FOR_RUNNING_GATE = SUFFICIENT
ARTIFACT_AS_PERMANENT_CANONICAL_RECORD = INSUFFICIENT
```

Thirty days is adequate for executing and reviewing the 7-day gate. GitHub Actions artifacts remain ephemeral operational evidence and must not be the only permanent record of a completed milestone.

## Permanent evidence rule

After each accepted milestone (24h, 72h, 7d), commit a concise immutable evidence record under `docs/evidence/` containing at least:

```text
ATTEMPT_ID
BASELINE_UTC
BOUNDARY_UTC
TERMINAL_OBSERVATION_UTC
AUDIT_RUN_ID
AUDIT_JOB_ID
ARTIFACT_ID
QUALIFYING_OBSERVATION_COUNT
FAILED_CONTROL_COUNT
MAX_OBSERVED_GAP_HOURS
MAX_ALLOWED_GAP_HOURS
CONTROL_RUN_IDS or a stable reference to collected evidence
DEPLOYED_RUNTIME_SHA
CANONICAL_REPOSITORY_SHA_AT_CLOSURE
MILESTONE_RESULT
```

For final P19 closure, add/update a checkpoint under `docs/checkpoints/` that references the three milestone records plus the resolved runtime-candidate identity.

## Fail-closed rules

Do not close a milestone or P19 when any of these occurs:

- missing post-boundary terminal observation;
- failed qualifying control run;
- evidence gap over 7h;
- baseline ambiguity;
- Attempt 1 evidence reused for Attempt 2;
- artifact-only claim without a durable closure record;
- deployed runtime candidate identity unresolved at final P19 closure;
- a runtime deployment occurs but the old baseline remains in use.

## Pre-24h implementation preparation update

Draft PR #81 prepares an offline fail-closed milestone evidence generator and its pytest/runbook contract. It remains unmerged and is deliberately **not** wired into live GitHub Actions.

Prepared behavior includes rejecting evidence generation when any required condition is absent, including:

```text
P19_SOAK_AUDIT != PASS
P19_CONTINUITY_STATUS != PASS
milestone_status != PASS
terminal_observation < boundary
max_gap > 7h
failed_control_count != 0
service_before/after != active
runtime_db_read != denied
arbitrary_root_escalation != denied
restart_performed != false
invalid deployed/canonical SHA metadata
```

Validated preparation state:

```text
PR_81 = DRAFT / OPEN / UNMERGED
HEAD = 1c22011849b77ee370798cd9930bacdf1747ffc9
CI = PASS
LIVE_ACTIONS_WIRING = NO
AUTO_COMMIT_EVIDENCE = NO
```

The latest known pre-24h live evidence remains:

```text
CONTROL_RUN = 34596182532 / SUCCESS
LATEST_QUALIFYING_OBSERVATION_UTC = 2026-09-11T11:54:06Z
AUDIT_RUN = 34596259823 / SUCCESS
AUDIT_ARTIFACT_ID = 10262223231
P19_CONTINUITY_STATUS = PASS
```

Because scheduled-event delivery has shown multi-hour nondeterminism, two bounded future checks were scheduled outside repository workflow definitions:

```text
CONTINUITY_CHECK = 2026-09-11T20:30:00+03:00
24H_GATE_CHECK = 2026-09-12T10:45:00+03:00
```

The continuity check may use only the existing bounded `health` control and audit if the actual evidence gap approaches the 7h limit. The 24h check occurs only after the canonical boundary `2026-09-12T07:38:44Z`. Neither automation authorizes deployment, restart, workflow/cadence/baseline mutation, Tailscale trust change, or merge of preparation PRs.

The 24h evidence record must not be created as PASS before the evaluator has a qualifying observation at or after the boundary and reports the 24h milestone PASS.

## No-change assertion

Preparation of this document authorizes none of the following:

```text
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
SOAK_BASELINE_CHANGE = NO
SOAK_CADENCE_CHANGE = NO
TAILSCALE_TRUST_CHANGE = NO
P20_OPERATIONAL_START = NO
A5_ACTIVATION = NO
```
