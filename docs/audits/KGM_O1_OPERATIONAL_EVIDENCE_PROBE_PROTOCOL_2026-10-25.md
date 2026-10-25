# KGM O1 — Operational evidence probe (2026-10-25)

Status: **READY_FOR_MANUAL_OWNER_DISPATCH / NOT_YET_EXECUTED / PRODUCTION_NO_GO**.

## Basis and scope

PR #256 merged; its live read-only SQLite probe verified integrity_check=ok, zero foreign key violations, 51 tables, and 21 migrations, but did not validate worker cycles, source freshness or loaded code.

A separate narrower aggregate probe is supplied in `ops/o1_diag/kgm-o1-operational-aggregates.py`, with a manually dispatched workflow in `.github/workflows/o1-operational-evidence-readonly.yml`. It reuses the successful GitHub Actions -> pinned SSH -> ubuntu -> sudo -n /usr/bin/python3 - channel. The script must be launched only by the owner after CI.

## Evidence contract

Tables permitted: `monitoring_runs`, `live_analysis_runs`, `live_source_provenance`, `source_collection_runs`, `source_collection_attempts`, `source_freshness`, `owner_runtime_health`.

Output includes **column names (schema metadata), table row counts, conservative aggregate status buckets (SUCCESS, PARTIAL, FAIL, RUNNING, PENDING, OTHER), parseable MAX timestamp fields, and only exact GDACS/GDELT source row counts** where the table has a recognized direct source column.

Never output raw row values, secrets, raw logs, database files or source payloads. No DB writes, service restart, configuration changes, access grants or data export. The probe accesses SQLite via `mode=ro` and `PRAGMA query_only=ON`, in a read transaction with a time-bounded progress handler. Exceptions produce nonzero exit status. Tables or columns with unexpected schemas result in `UNVERIFIED` rather than invented evidence.

**Limitations:** Status buckets are lexical and cannot establish worker success without validating the meaning of the relevant status columns. A MAX timestamp is not proof of successful collection, nor is the existence of a `source_freshness` table. GDACS/GDELT may be encoded in normalized IDs or joined tables rather than matching a direct source text column. The script does not attest loaded-code SHA, does not demonstrate completeness of all cycles, and does not verify fresh external data independently. A success exit means aggregates were collected, not O1 Operational PASS.

## Acceptance steps

1. CI synthetic fixtures PASS and owner manual workflow dispatch.
2. Inspect full JSON: no raw data and recognized operational schema.
3. Derive documented worker-cycle and freshness metrics only after independent schema interpretation and source joins (if needed).
4. Record time-bounded evidence, limitations, reviewer findings and O1 decision in a separate audited PR.

Keep `FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO`. Historical Oct17 backup/export untouched. No production database upload to GitHub.
