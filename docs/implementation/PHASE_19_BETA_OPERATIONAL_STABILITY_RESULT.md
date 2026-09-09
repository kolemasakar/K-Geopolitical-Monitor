# Phase 19 — Beta Operational Stability Result

Date: 2026-09-09  
Project: K-Geopolitical Monitor  
Status: `HARNESS_VALIDATED / REAL_ELAPSED_SOAK_PENDING / FULL_GATE_OPEN`  
Harness subgate: `PHASE_19_OPERATIONAL_STABILITY_HARNESS_VALIDATED = PASS`  
Target full gate: `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED`

## 1. Purpose and evidence boundary

Phase 19 proves that the owner-local canonical beta runtime can operate unattended for extended periods while making failures visible, classified, recoverable and non-corrupting.

The deterministic stability harness is now validated. This does **not** claim that a real 24-hour, 72-hour or 7-day owner-local soak has elapsed.

```text
P19_REAL_24H_SOAK = NOT_EVIDENCED
P19_REAL_72H_SOAK = NOT_EVIDENCED
P19_REAL_7D_SOAK = NOT_EVIDENCED
PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED = NOT_YET_CLOSED
```

## 2. Validated operational controls

`src/kgeopolitical_monitor/operational_stability.py` evaluates existing persisted owner-local facts without adding a canonical schema migration.

Deterministic findings cover:

- missing/stale supervisor health;
- late watches and historical missed-cycle gaps;
- stalled `RUNNING` executions;
- expected sources never observed or stale;
- repeated execution failures;
- retry recurrence;
- SQLite integrity and foreign-key violations.

Fail-closed status:

- `HEALTHY`
- `DEGRADED`
- `CRITICAL`

Default beta detection thresholds:

- supervisor stale: `180 seconds`;
- watch lateness grace: `15 minutes`;
- stalled run: `30 minutes`;
- source stale: `180 minutes`;
- repeated failure threshold: `3`;
- retry recurrence threshold: `3`.

These thresholds are beta operational health controls, not contractual uptime/SLA claims.

## 3. Structured error distribution

Persisted free-form failures are mapped into deterministic classes:

- `RECOVERED_INTERRUPTION`
- `TIMEOUT`
- `HTTP`
- `NETWORK`
- `PERMISSION`
- `DATABASE`
- `SOURCE_IDENTITY`
- `SOURCE`
- `OTHER`

Both snapshot and soak-window evidence expose structured error-class distributions.

## 4. Historical soak-window evaluator

`evaluate_soak_window(...)` reports, for a bounded persisted execution window:

- start/end and duration;
- completed/failed/running/recovered run counts;
- cadence-gap / missed-cycle count;
- error-class distribution;
- SQLite integrity;
- clean/non-clean result.

The evaluator never infers whether timestamps represent real elapsed wall-clock evidence. Simulated and real elapsed evidence must be labelled separately.

## 5. Operator-facing status

`scripts/p19_operational_status.py` evaluates the project-local canonical database and can evaluate a preceding `--window-hours` interval.

Exit semantics:

- `0`: healthy and requested window clean;
- `2`: degraded;
- `3`: critical or requested soak window non-clean.

`RuntimeStoragePolicy` continues to constrain the database to project-local `data/`.

## 6. Accelerated deterministic proof — PASS

Validated branch evidence anchor before this documentation-only closure update:

- branch head: `6365bdd4a5b7efb5876c03377601f3f1ea6f8908`;
- P19 workflow run: `34398358219`;
- P19 job: `102623755465`;
- focused tests: `8 passed in 2.01s`.

Proof result:

- logical window: `24h / 86400s`;
- logical executions: `25`;
- completed: `25`;
- failed: `0`;
- running: `0`;
- recovered: `0`;
- missed-cycle count: `0`;
- simulated soak-window status: `clean = true`;
- SQLite `integrity_check = ok`;
- foreign-key violations: `0`.

Injected fault scenario deterministically detected:

- `REPEATED_FAILURE`
- `RETRY_RECURRENCE`
- `RUN_STALLED`
- `SOURCE_NEVER_OBSERVED`
- `SOURCE_STALE`
- `SUPERVISOR_STALE`
- `WATCH_LATE`

The fault scenario produced `CRITICAL` while preserving SQLite integrity.

Restart/retry/idempotency evidence:

- interrupted runs recovered: `1`;
- retry progression: `retry_count = 1`;
- duplicate collection canonical raw-item count: `1`;
- post-fault integrity: `ok`.

Proof markers:

```text
P19_ACCELERATED_STABILITY_PROOF=PASS
P19_RESTART_RECOVERY=PASS
P19_RETRY_IDEMPOTENCY=PASS
P19_SQLITE_INTEGRITY=PASS
P19_OPERATOR_DIAGNOSTICS=PASS
P19_REAL_24H_SOAK=NOT_EVIDENCED
```

## 7. Full repository regression — PASS

Validation anchor:

- CI run: `34398358188`;
- CI job: `102623755396`;
- result: `1172 passed in 197.01s`.

The final PR head must still pass both standard CI and the P19 workflow after this documentation-only closure update before guarded merge.

## 8. Preserved strategic and beta boundaries

No migration, activation, provider or billing mutation is authorized or performed by this slice.

```text
OWNER_LOCAL_RUNTIME = CANONICAL
PHASE_18_SHARED_RUNTIME_ACTIVE = NO
CANONICAL_CUTOVER_AUTHORIZED = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
STRATEGIC_MACHINE_STATE = 4.34
```

## 9. Next Phase 19 evidence sequence

The harness subgate is validated; the full P19 gate remains open.

Next evidence sequence:

1. real owner-local 24-hour short soak;
2. real owner-local 72-hour extended soak after the short window is acceptable;
3. real 7-day candidate stability window once shorter windows are consistently clean;
4. only then consider `PHASE_19_BETA_OPERATIONAL_STABILITY_VALIDATED` for closure.

No simulated-time proof may substitute for those real elapsed windows.
