# Phase 19 — Beta Operational Stability Result

Date: 2026-09-09  
Project: K-Geopolitical Monitor  
Status: `IMPLEMENTATION_CANDIDATE / VALIDATION_PENDING / REAL_ELAPSED_SOAK_PENDING`  
Target gate: `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED`

## 1. Purpose

Phase 19 proves that the owner-local canonical beta runtime can operate unattended for extended periods while making failures visible, classified, recoverable and non-corrupting.

This change establishes the deterministic evaluator and evidence harness. It does **not** claim that a real 24-hour, 72-hour or 7-day soak has already elapsed.

## 2. Implemented operational controls

### Deterministic health classification

`src/kgeopolitical_monitor/operational_stability.py` evaluates existing persisted owner-local facts without adding a new canonical schema migration.

It classifies:

- missing or stale supervisor health;
- late watches / missed expected cycles;
- stalled `RUNNING` executions;
- expected sources that have never been observed;
- stale source collection attempts;
- repeated failed executions;
- retry recurrence;
- SQLite integrity failures;
- SQLite foreign-key violations.

Status is fail-closed:

- `HEALTHY`
- `DEGRADED`
- `CRITICAL`

### Beta operational SLO thresholds

Default detection thresholds:

- supervisor stale: `180 seconds`;
- watch lateness grace: `15 minutes`;
- stalled run: `30 minutes`;
- source stale: `180 minutes`;
- repeated failure threshold: `3`;
- retry recurrence threshold: `3`.

These are beta health-detection thresholds, not a contractual uptime SLA.

### Structured failure classes

Persisted free-form errors are mapped deterministically into operator classes:

- `RECOVERED_INTERRUPTION`
- `TIMEOUT`
- `HTTP`
- `NETWORK`
- `PERMISSION`
- `DATABASE`
- `SOURCE_IDENTITY`
- `SOURCE`
- `OTHER`

This permits recurrence/distribution analysis without treating raw log text as the operational interface.

### Historical soak-window evaluator

`evaluate_soak_window(...)` evaluates a bounded persisted execution window and reports:

- elapsed window;
- completed/failed/running/recovered run counts;
- historical cadence-gap / missed-cycle count;
- error-class distribution;
- SQLite integrity;
- whether the evaluated window is clean.

The evaluator does not infer that timestamps represent real elapsed wall-clock evidence. The caller/evidence record must distinguish simulated time from real elapsed time.

### Operator-facing status

`scripts/p19_operational_status.py` prints a machine-readable summary for the project-local canonical database and can additionally evaluate a preceding `--window-hours` history window.

Exit semantics:

- `0`: healthy/clean;
- `2`: degraded;
- `3`: critical or non-clean requested soak window.

The command uses `RuntimeStoragePolicy`, so the database remains constrained to the project-local `data/` boundary.

## 3. Accelerated deterministic proof

`scripts/p19_operational_stability_proof.py` exercises, using synthetic/non-sensitive fixtures only:

- a logically simulated 24-hour sequence with 25 hourly executions;
- healthy deterministic schedule evaluation;
- historical soak-window gap detection;
- interrupted-run recovery after runtime reconstruction;
- retry-count progression;
- duplicate collection/idempotent raw-item persistence;
- injected repeated failures;
- stalled-run detection;
- stale and never-observed source detection;
- structured failure classification;
- SQLite integrity and foreign-key integrity after repeated/faulted operations.

Expected proof markers:

```text
P19_ACCELERATED_STABILITY_PROOF=PASS
P19_RESTART_RECOVERY=PASS
P19_RETRY_IDEMPOTENCY=PASS
P19_SQLITE_INTEGRITY=PASS
P19_OPERATOR_DIAGNOSTICS=PASS
P19_REAL_24H_SOAK=NOT_EVIDENCED
```

## 4. Evidence boundary

The accelerated harness is **not** elapsed soak evidence.

Current long-window state remains:

```text
P19_REAL_24H_SOAK = NOT_EVIDENCED
P19_REAL_72H_SOAK = NOT_EVIDENCED
P19_REAL_7D_SOAK = NOT_EVIDENCED
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NOT_YET_CLOSED
```

The final Phase 19 gate must not close until required real owner-local elapsed evidence is collected and evaluated.

## 5. No migration / activation / provider mutation

This work does not authorize or perform:

- Railway upgrade or paid-resource use;
- shared-runtime activation;
- canonical cutover;
- migration `033`;
- provider deployment mutation;
- strategic machine-state synchronization.

Preserved state:

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
STRATEGIC_MACHINE_STATE = 4.34
```

## 6. Validation plan

Before this implementation slice is considered validated:

- focused Phase 19 tests must pass;
- accelerated proof must pass;
- full repository CI must remain green;
- exact branch/head evidence must be recorded.

After harness validation, Phase 19 continues with real elapsed owner-local soak evidence:

- 24-hour short soak;
- 72-hour extended soak;
- 7-day candidate stability window once the shorter windows are consistently clean.

Only then may the target gate `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED` be considered for closure.
