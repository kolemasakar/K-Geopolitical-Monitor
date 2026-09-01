# E9A.4 Owner-Only Runtime Health Result

Status: IMPLEMENTATION_REGRESSION_VALIDATED
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — Owner-Only Production Runtime Hardening

## Scope

Add persisted, directly instrumented runtime-health facts for the owner-only unattended supervisor without inferring global coverage, source health, process uptime or production availability from unrelated timestamps.

## Implementation

Added:
- `migrations/021_owner_runtime_health.sql`;
- `src/kgeopolitical_monitor/runtime_health.py`;
- dedicated runtime-health tests.

Updated:
- `src/kgeopolitical_monitor/unattended_service.py`;
- `src/kgeopolitical_monitor/unattended_runner.py`;
- canonical migration/database contract tests.

Instrumentation version:
`KGM_OWNER_RUNTIME_HEALTH_V1`

Persisted singleton facts include:
- last supervisor tick timestamp;
- last completed tick timestamp;
- last successful execution timestamp, when directly observed;
- recovered-run count for the tick;
- total execution count;
- completed execution count;
- failed execution count;
- tick-local status;
- last directly instrumented execution error, when present.

## Status Semantics

- `IDLE` — supervisor tick completed and no due execution completed or failed in that tick.
- `HEALTHY` — at least one execution completed successfully in that tick and no execution failed.
- `DEGRADED` — at least one execution failed in that tick.

These labels are deliberately local to the supervisor tick. They do **not** establish or imply:
- global/source coverage completeness;
- factual verification state;
- source availability outside the executions actually observed;
- process uptime before the recorded tick;
- end-to-end public service availability;
- production/live readiness.

## Validation and Repair Evidence

The first x64 regression run correctly failed because the pre-existing canonical database test still expected migrations only through `020_reproducibility_instrumentation.sql`.

Observed first-run result:
- x64: `312 passed, 1 failed, 1 warning`;
- failing test: `tests/test_database.py::test_database_initialization_applies_canonical_migrations`;
- cause: new canonical migration `021_owner_runtime_health.sql` was absent from the old expected migration set.

Repair policy:
- production runtime-health behavior was not weakened;
- the canonical migration/database test was updated to require the new migration and table.

Repair commit:
`6db189a2ad672e4bc8099be378e2e2a0044de1ed`

Commit message:
`Include E9A runtime health migration in database contract test`

x64 GitHub Actions after repair:
- workflow: CI;
- run: `33482602853`;
- job: `99775349951`;
- result: SUCCESS;
- regression: `313 passed, 1 warning`.

Native ARM64 GitHub Actions after repair:
- workflow: E4 ARM64 Validation;
- run: `33482602833`;
- job: `99775350013`;
- result: SUCCESS;
- full regression: `313 passed, 1 warning`;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS;
- bootstrap/architecture validation: PASS.

## Policy Boundaries

PASS:
- runtime state remains `PROJECT_LOCAL_ONLY`;
- no inbound API/dashboard/public listener was enabled;
- no Business migration was performed;
- no public sharing/publication was activated;
- E9 Shared Production Runtime remains not approved;
- `production_live` remains `NOT_OPERATIONAL`.

## Gate Decision

`E9A.4_OWNER_ONLY_RUNTIME_HEALTH = IMPLEMENTATION_REGRESSION_VALIDATED`

The instrumented runtime-health baseline is green on x64 and ARM64. This does not close E9A as a whole and does not constitute a production/live claim.

Next engineering subgate:
`E9A.5_DEPLOYMENT_SECURITY_HARDENING`
