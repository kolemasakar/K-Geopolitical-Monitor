# E5 Admin Read-Only Dashboard

Status: BASELINE_VALIDATED
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E5 - unnumbered post-Phase-11 expansion
Validated code SHA: `4da27ac374c9832cbe189d178cf2e10fa0326bb5`

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains `NOT_OPERATIONAL`.
Dashboard deployment remains `NOT_DEPLOYED`.

## 1. Purpose

E5 adds an owner/admin-only read-only dashboard projection over the existing canonical persisted K-Geopolitical Monitor runtime state.

The dashboard is intentionally not a new backend or a parallel state store. It reuses the E3 `BackendStateReader`, opens the existing project-local SQLite database read-only/query-only, and preserves `PROJECT_LOCAL_ONLY` runtime storage.

## 2. Implemented Artifacts

- `src/kgeopolitical_monitor/admin_dashboard.py`
- `src/kgeopolitical_monitor/admin_dashboard_app.py`
- `tests/test_admin_dashboard.py`

## 3. Read-Only State Projection

Dashboard data includes:
- system state summary, last monitoring cycle and visible current errors;
- active watches with derived `DUE`, `RUNNING`, `FAILED_DUE`, `FAILED_WAITING` and `WAITING` states;
- source registry identity, latest collection availability and E2 reputation/status history;
- latest persisted coverage ratio/confidence and explicit GAP/UNAVAILABLE/STALE/UNKNOWN/UNMEASURED counts;
- recent operational findings;
- recent strategic alerts;
- active forecasts with latest immutable forecast version and calibrated scenario probabilities;
- recent per-source collection attempts.

System uptime is not inferred. Where no persisted uptime instrumentation exists the dashboard returns:
- `system_uptime_seconds: null`;
- `system_uptime_instrumentation: NOT_INSTRUMENTED`.

Finding/alert verification is not invented when the persisted claim relationship is unavailable.

## 4. Truth-Boundary Preservation

The dashboard explicitly preserves these semantics:
- coverage confidence measures assessment observability and cannot strengthen claim verification;
- forecast probability is analytical and is not factual confidence;
- report/dashboard presentation cannot strengthen evidence;
- source reputation status does not automatically determine claim truth;
- unavailable persisted backend state is not replaced by public-web research;
- dashboard reads do not mutate canonical runtime state.

## 5. Access and Rendering Security

Current local/protected baseline:
- protected dashboard routes require the runtime-injected owner bearer token;
- missing or invalid token returns HTTP 401;
- token comparison uses constant-time comparison;
- empty owner token fails closed;
- interactive FastAPI `/docs` and `/redoc` are disabled;
- HTML is static and script-free;
- persisted dynamic values are HTML-escaped before browser execution context;
- response policy includes `Cache-Control: no-store`, restrictive CSP, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY`.

Routes:
- `/health` - non-sensitive health metadata;
- `/admin/dashboard.json` - owner-protected read-only structured snapshot;
- `/admin/dashboard` - owner-protected server-rendered HTML snapshot.

## 6. Deployment Boundary

E5 validates the code foundation only.

The dashboard:
- is not launched by `kgm-monitor.service`;
- has not opened OCI TCP 80/443;
- is not exposed as a public unauthenticated service;
- is not connected to the private GPT;
- is not production deployed;
- does not change the E4 monitoring service or its project-local storage boundary.

Any later HTTPS/public-network exposure requires a separate deployment/security gate.

## 7. Validation

Initial E5 regression exposed one deterministic-test fixture issue: a fixed test timestamp was later than the executing GitHub runner clock, so one expected due-watch assertion was premature. Production watch semantics were unchanged; the fixture cut-off was corrected to a historical deterministic timestamp.

Canonical passing SHA:
`4da27ac374c9832cbe189d178cf2e10fa0326bb5`

Standard x64 CI:
- run ID: `33263584520`;
- job ID: `99129562037`;
- result: SUCCESS;
- regression: `282 passed, 1 warning in 30.29s`.

Native ARM64 CI:
- run ID: `33263584515`;
- job ID: `99129561992`;
- result: SUCCESS;
- native ARM64 confirmation: PASS;
- full ARM64 regression: PASS;
- E4 bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS.

The warning is the existing non-blocking Starlette `TestClient`/httpx deprecation warning.

## 8. E5 Gate

Validated:
- canonical project-local persisted state reused: PASS;
- no parallel dashboard database: PASS;
- SQLite read-only/query-only boundary inherited from E3: PASS;
- owner authentication: PASS;
- read-only request non-mutation: PASS;
- watch due/running/failed projection: PASS;
- source status/availability projection: PASS;
- coverage projection with visible limitations: PASS;
- findings/alerts projection without truth inflation: PASS;
- forecast version/scenario projection without forecast-to-fact promotion: PASS;
- collection-attempt visibility: PASS;
- HTML injection resistance for persisted text: PASS;
- restrictive response headers: PASS;
- x64 regression: PASS;
- native ARM64 regression: PASS.

E5 state:

`BASELINE_VALIDATED`

Supporting state:

`LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`

## 9. Explicit Non-Claims

E5 does not establish:
- a production dashboard;
- public dashboard availability;
- HTTPS deployment;
- shared production runtime;
- private GPT backend connectivity;
- complete global coverage;
- production/live operational status.

## 10. Next Engineering Activity

Continue the approved sequence with E6 Reproducibility Instrumentation while preserving all existing provenance, verification, coverage, forecasting and storage boundaries.
