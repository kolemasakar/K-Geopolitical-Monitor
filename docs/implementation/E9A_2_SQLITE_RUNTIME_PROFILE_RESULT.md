# E9A.2 SQLite Runtime Profile Result

Status: BASELINE_VALIDATED
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — Owner-Only Production Runtime Hardening

## Scope

Make the canonical owner-only SQLite runtime connection behavior explicit and bounded without weakening `PROJECT_LOCAL_ONLY` or introducing an unvalidated WAL-based production assumption.

## Validated Runtime Profile

The E9A.2 baseline is deliberately conservative:
- `foreign_keys = ON`;
- `busy_timeout = 5000 ms`;
- `journal_mode = DELETE`;
- `synchronous = FULL`;
- transaction isolation level = `DEFERRED`.

WAL is not enabled by this gate. A future journal-mode change requires separate measured validation of checkpointing, online backup, restore, crash/reboot integrity and E3/E5 read-only compatibility.

## Implementation

Updated `src/kgeopolitical_monitor/database.py` with:
- centralized runtime connection constants;
- `connect_runtime_database()`;
- `runtime_database_connection()`;
- explicit initialization-time journal-mode establishment;
- fail-closed verification of the configured PRAGMA profile.

Updated `src/kgeopolitical_monitor/operational_monitoring.py` so canonical monitoring repository reads/writes use the profiled connection helper rather than independent default `sqlite3.connect()` behavior.

Added `tests/test_database_runtime_profile.py`.

## Validation Coverage

PASS:
- exact runtime PRAGMA profile is observable and asserted;
- concurrent reader sees the last committed state while a writer holds an uncommitted update;
- a second writer waits within the bounded busy timeout and completes after the first writer releases the lock;
- committed state survives close/reopen;
- `PRAGMA integrity_check` remains `ok` after reopen;
- existing migrations and monitoring semantics remain compatible;
- no shared/mixed runtime storage introduced;
- no public API/dashboard/GPT exposure introduced;
- production/live remains NOT_OPERATIONAL.

## Validation Evidence

Validated HEAD:
`e7429bfdfcf444a03be0ceb7ea8e92d6a3bdf9c2`

x64 GitHub Actions:
- workflow: CI;
- run: `33481683894`;
- job: `99772477806`;
- result: SUCCESS;
- regression: `303 passed, 1 warning in 41.57s`.

Native ARM64 GitHub Actions:
- workflow: E4 ARM64 Validation;
- run: `33481683925`;
- job: `99772477695`;
- architecture: `aarch64`;
- result: SUCCESS;
- full regression: `303 passed, 1 warning in 30.37s`;
- host bootstrap shell: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS.

## Gate Decision

`E9A.2_SQLITE_RUNTIME_PROFILE = BASELINE_VALIDATED`

Next step:
`E9A.3_BACKUP_AND_DISASTER_RECOVERY`
