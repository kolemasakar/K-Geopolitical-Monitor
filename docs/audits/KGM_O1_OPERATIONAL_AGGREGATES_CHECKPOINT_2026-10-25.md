# O1 operational aggregates checkpoint — 2026-10-25

## Source

Owner-run manual GitHub Actions O1 Operational Evidence Readonly on `main` (merged PR #257). Output timestamp 2026-10-25T20:07:52.906131+00:00, euid=0, status=AGGREGATES_COLLECTED_REVIEW_REQUIRED. SQLite previously passed integrity_check=ok, foreign_key_violations=0, tables=51, migration_count=21 via manual O1 Live Readonly Attestation.

## Material observations (metadata/aggregates only)

- `monitoring_runs`: 4 records; lexical SUCCESS=2, FAIL=2; MAX completed_at/started_at 2026-09-01T08:32:14.331099Z.
- `source_collection_runs`: 2 records; lexical PARTIAL=2; MAX completed_at/started_at 2026-09-01T08:32:14.331099Z.
- `source_collection_attempts`: 4 records; lexical SUCCESS=2, FAIL=2; direct source_name exact-match counts GDACS=0, GDELT=0. This does NOT prove those sources absent from configuration or from any alternate tables.
- `live_analysis_runs` and `live_source_provenance`: zero rows.
- `source_freshness`: absent. This is not proof that there is no other freshness mechanism.
- `owner_runtime_health`: exactly one row. Crucial columns found: last_supervisor_tick_at, last_completed_tick_at, last_successful_execution_at, recovered_runs, execution_count, completed_execution_count, failed_execution_count, tick_status. The prior generic probe did not read these fields.

## Interpretation

The 2026-09-01 timestamp is last time in the *two queried run tables*, not necessarily the latest runner activity. A current active systemd service, sqlite integrity PASS and journal count do not demonstrate successful unattended cycles. No O1 Operational PASS is justified from these aggregates. No inferred GDACS/GDELT activity.

## Next bounded read

`ops/o1_diag/kgm-o1-health-detail.py` and `.github/workflows/o1-runtime-health-detail-readonly.yml` add a fixed, manual-only, read-only query of the singleton owner_runtime_health counters/three timestamps plus allowlisted source_name attempt aggregates. Never output raw error text, URLs, raw rows, payloads, identifiers, or secrets. Review these measurements for semantic mapping before concluding service activity. No permission changes, writes, service restart, or uploads.

**Current: O1_OPERATIONAL_SHORTFALL / REVIEW_REQUIRED / PRODUCTION_NO_GO. FREE_ONLY / NO_SEND / CLEANUP_HOLD.**
