# KGM O1 watch scheduler audit — 2026-10-25

## Source semantics

Deployed disk release `b31b2136b5fe982d0b63b0135479b1549041906c`:
- `OperationalMonitoringRuntime.due_watches()` enumerates enabled `monitoring_watches`. A watch with no prior run is due.
- A latest run in RUNNING state blocks scheduling; otherwise the watch becomes due at `latest.started_at + cadence_minutes`. Polling is independent (60 seconds).
- The runner obtains `execute_due(now)` each tick. The runtime health singleton counters describe one tick, not cumulative history.
- These are **disk-source semantics**, not proof of the actually loaded code.

## Proposed probe

`ops/o1_diag/kgm-o1-watch-due.py` queries only `monitoring_watches` and `monitoring_runs`, using SQLite mode=ro, query_only=ON, read transaction and deadline. Outputs totals enabled/disabled/due/not-due/never-run/running-blocked, cadence bounds, earliest computed next-due and maximum overdue minutes. No watch IDs, names, queries, raw rows or credentials. No writes, deployment or restart.

Schema unexpected / query errors are fail-closed. A successful probe run does **not** establish operational PASS.

## Interpretation

- Enabled=0: IDLE expected; separately assess whether pilot watches were intended to be enabled.
- Due>0 plus contemporaneous supervisor ticks and no executions: investigate scheduler/routing and loaded-code mismatch, but do not claim failure until timing samples and code identity reviewed.
- RUNNING blocked>0: review last-run state and recovery expectations; do not force recovery.
- No due watches: IDLE may be expected.
- Last success at 2026-09-01 is historic; no claim of current source freshness.
- GDACS/GDELT current adapter selection must be independently verified. Production source changes are not authorized.

Manual workflow `.github/workflows/o1-watch-schedule-readonly.yml` uses previously verified GitHub Actions -> SSH -> Ubuntu -> sudo admin path. No automatic dispatch.

Gate **O1_OPERATIONAL_SHORTFALL / PRODUCTION_NO_GO**, FREE_ONLY / NO_SEND / CLEANUP_HOLD.
