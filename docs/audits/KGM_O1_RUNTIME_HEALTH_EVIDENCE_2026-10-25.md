# O1 Runtime Health Detail — owner evidence checkpoint 2026-10-25

Status: **SUPERVISOR_ACTIVE / LAST_TICK_NO_EXECUTIONS / SUCCESS_STALE / O1_OPERATIONAL_SHORTFALL / PRODUCTION_NO_GO**

## Source and observations

Owner-run GitHub Actions `KGM O1 Runtime Health Detail Readonly`; summary timestamp `2026-10-25T20:18:06.065195+00:00`, euid 0, `SUMMARY_COLLECTED_REVIEW_REQUIRED`.

- `owner_runtime_health`: 1 row.
- `last_supervisor_tick_at = 2026-10-25T20:18:01.432185+00:00`
- `last_completed_tick_at = 2026-10-25T20:18:01.432185+00:00`
- `last_successful_execution_at = 2026-09-01T08:32:14.331099+00:00`
- `execution_count = 0`, `completed_execution_count = 0`, `failed_execution_count = 0`, `recovered_runs = 0`.
- The probe returned `tick_status_category=OTHER_OR_EMPTY`. This classification is incomplete: the deployed-source `runtime_health.py` permits exact statuses `IDLE`, `HEALTHY`, `DEGRADED`; the probe did not recognize `IDLE`. Do **not** assert the actual stored status without a bounded follow-up mapping.
- `source_collection_attempts`: 4 historical records categorized OTHER (2 success, 2 fail). The source names are not among the probe's allowlisted GDACS/GDELT/CONSILIUM/GCC exact labels. No source freshness conclusion follows.

## Source-level semantic verification

Read `src/kgeopolitical_monitor/runtime_health.py` and `src/kgeopolitical_monitor/unattended_runner.py` at **deployed disk SHA `b31b2136b5fe982d0b63b0135479b1549041906c`**.

- `RuntimeHealthStore.record_tick` UPSERTs the health singleton at every recorded tick. Its `execution_count`, completed and failed counts are scoped to the latest tick, **not cumulative historical totals**.
- No completed/failed executions in a tick yields `IDLE` under that source implementation. Thus a fresh tick and zero executions can coexist normally.
- `last_successful_execution_at` retains its previous value until the tick has at least one COMPLETED execution.
- `unattended_runner` runs a 60-second supervisor poll, while watch cadence is maintained separately.

The loaded in-memory Python release is **NOT ATTESTED**; disk source semantics are supportive but not definitive proof of the process's loaded code.

## Assessment and next gates

Supervisor heartbeat is contemporary and live SQLite integrity was previously PASS (PR #256 owner-run attestation). No verified successful execution since Sep 1 in the instrumented singleton, but this is not yet evidence of malfunction without evaluating active watch configuration/due scheduling, collection routes and possible alternate execution stores.

**Next read-only checks**: number of enabled watches, next-due times compared with current UTC, watch cadence, and sanitized status enum of last tick; confirm how current source adapters are selected and map historical attempts to source IDs without emitting raw fields or payloads. Then decide whether an absent due execution is expected IDLE or an operational defect. No restart, deployment, repair, rights changes, cleanup, unapproved source activation or raw data uploads.

FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
