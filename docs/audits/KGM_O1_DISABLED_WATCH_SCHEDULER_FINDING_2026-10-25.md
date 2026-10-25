# KGM O1 owner-run watch scheduling evidence — 2026-10-25

**Gate: ON_DEMAND_MODE_CONFIRMED_BY_OWNER / ALL_WATCHES_DISABLED_EXPECTED / ON_DEMAND_EXECUTION_UNVERIFIED / PRODUCTION_NO_GO**

## Observed live read-only aggregates

Owner dispatched `.github/workflows/o1-watch-schedule-readonly.yml` on canonical main after PR #260. JSON observed_at: `2026-10-25T20:30:21.452189+00:00`, `state=AGGREGATES_COLLECTED_REVIEW_REQUIRED`.

- `watches_total=2`, `enabled=0`, `disabled=2`.
- `due=0`, `not_due=0`, `running_blocked=0`.
- `no_prior_run_due=0`, `latest_run_missing=0`, `invalid_cadence=0`, `invalid_run_timestamp=0`.
- `cadence_min_minutes=null`, `cadence_max_minutes=null`, `next_due_earliest_utc=null`: no enabled watches on which to calculate cadence.
- `loaded_code_sha=UNKNOWN`, `source_activation=NOT_CHECKED`.

These are aggregate facts, not disclosure of watch names, queries, identifiers or raw records.

## Explanation / limits

In source at deployed disk SHA `b31b2136b5fe982d0b63b0135479b1549041906c`, `OperationalMonitoringRuntime.due_watches()` only examines enabled watches. With no enabled watches, zero due executions and IDLE tick are expected. The observed owner_runtime_health heartbeat was current (2026-10-25T20:18:01Z), and its latest successful execution is historic (2026-09-01T08:32:14Z). The owner explicitly confirmed on 2026-10-25 that this project performs research/collection on user request only and does **not** operate continuous scheduled monitoring. Therefore the disabled watches and zero due executions are intended configuration, not a scheduler incident. The September historical success timestamp is not a freshness SLA for an idle on-demand system.

This does **not** attest loaded Python code, any actual new user-requested execution, source selection, live collection or multi-source success. An on-demand request/response acceptance test remains open; a scheduled-watch acceptance test is explicitly not required for this deployment mode.

## Next gate for the approved request-driven mode

1. Inventory the two disabled watches' metadata without exposing queries, and confirm they are dormant legacy scheduling configuration, not the invocation route for user requests.
2. Reconcile this owner decision in the ROADMAP/hand-off: ON_DEMAND_ONLY, no continuous polling or scheduled source collection authorized. A still-running 60-second supervisor heartbeat is not evidence that network collection occurs, but its resource cost may merit later review.
3. Audit and test the **user-invoked, one-shot** collection-and-analysis route in an isolated disposable environment: explicit request input, bounded outbound collection, NO_SEND of generated reports, fail-closed source errors, no retained scheduler change, deterministic cleanup of test-owned temporary files only. Do not use live production DB, activate a watch, restart the service, or claim a live pilot from an offline fixture.
4. After independent test evidence and a separate owner acceptance decision, run a real one-time user-requested multi-source query through an already approved execution channel if one exists; otherwise retain SHORTFALL and document the required integration. No scheduled-execution evidence is required.

**FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO remain.** No live state changed in this audit.
