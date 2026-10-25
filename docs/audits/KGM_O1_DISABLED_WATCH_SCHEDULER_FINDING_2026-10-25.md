# KGM O1 owner-run watch scheduling evidence — 2026-10-25

**Gate: SUPERVISOR_TICK_CURRENT / ALL_WATCHES_DISABLED / O1_OPERATIONAL_SHORTFALL / PRODUCTION_NO_GO**

## Observed live read-only aggregates

Owner dispatched `.github/workflows/o1-watch-schedule-readonly.yml` on canonical main after PR #260. JSON observed_at: `2026-10-25T20:30:21.452189+00:00`, `state=AGGREGATES_COLLECTED_REVIEW_REQUIRED`.

- `watches_total=2`, `enabled=0`, `disabled=2`.
- `due=0`, `not_due=0`, `running_blocked=0`.
- `no_prior_run_due=0`, `latest_run_missing=0`, `invalid_cadence=0`, `invalid_run_timestamp=0`.
- `cadence_min_minutes=null`, `cadence_max_minutes=null`, `next_due_earliest_utc=null`: no enabled watches on which to calculate cadence.
- `loaded_code_sha=UNKNOWN`, `source_activation=NOT_CHECKED`.

These are aggregate facts, not disclosure of watch names, queries, identifiers or raw records.

## Explanation / limits

In source at deployed disk SHA `b31b2136b5fe982d0b63b0135479b1549041906c`, `OperationalMonitoringRuntime.due_watches()` only examines enabled watches. With no enabled watches, zero due executions and IDLE tick are expected. The observed owner_runtime_health heartbeat was current (2026-10-25T20:18:01Z), and its latest successful execution is historic (2026-09-01T08:32:14Z). Current data therefore provides a concrete configuration explanation for no new watch executions, without demonstrating a broken worker.

This does **not** attest loaded Python code, live external collection, actual source configuration or multi-source success. `O1_OPERATIONAL_PASS` remains unearned.

## Next gate before any activation

1. Inventory the two disabled watch specifications in a privacy-preserving owner-only channel, and verify intended source mapping, cadence and query scope (no raw secrets in CI).
2. Inspect whether the original P24 pilot deliberately disabled both watches, and reconcile with ROADMAP owner gate.
3. Propose a separately reviewed, explicit owner-authorized, reversible one-watch read-only collection pilot with NO_SEND and bounded traffic, only after a safety and provenance audit. Do not enable, restart, migrate, clean up, or switch sources by default.
4. Capture independent scheduled execution evidence and fresh source provenance before revisiting O1 acceptance.

**FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO remain.** No live state changed in this audit.
