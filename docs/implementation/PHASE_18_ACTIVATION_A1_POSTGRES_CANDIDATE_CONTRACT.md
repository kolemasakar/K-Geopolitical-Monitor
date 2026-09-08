# Phase 18 Activation A1 — Disposable PostgreSQL Candidate Contract

Status: `A1_1_IMPLEMENTATION_CANDIDATE / NOT_DEPLOYED / NOT_ACTIVATED`
Date: 2026-09-08
Project: K-Geopolitical Monitor
Parent workstream: `docs/implementation/PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_PLAN.md`

## Purpose

Provide the smallest concrete PostgreSQL-backed application surface needed to create and directly observe a disposable Render Frankfurt non-production candidate.

This is not the canonical shared runtime, not migration `033`, not a production API, and not an activation or cutover mechanism.

## Runtime Boundary

The candidate is valid only when all of the following server-side settings are explicit:

- `KGM_SHARED_DATABASE_URL` — PostgreSQL DSN supplied through the provider environment, never committed;
- `KGM_PREFLIGHT_BEARER_TOKEN` — preflight-only secret supplied through the provider environment;
- `KGM_PREFLIGHT_WORKSPACE_ID` — synthetic workspace identifier;
- `KGM_PREFLIGHT_PROJECT_ID` — synthetic project identifier;
- `KGM_SHARED_PREFLIGHT_MODE=synthetic_nonprod`;
- `KGM_SHARED_DATABASE_NETWORK=render_private`.

Missing or different mode/network markers fail closed at application construction.

## Database Surface

Only the isolated PostgreSQL namespace is created:

`kgm_preflight.tenant_probe`

The table contains only:

- `workspace_id`;
- `project_id`;
- `probe_id`;
- SHA-256 of a synthetic probe payload;
- creation timestamp.

The raw synthetic payload is not persisted.

The adapter:

- enables PostgreSQL row-level security;
- forces row-level security for the table owner;
- scopes both `USING` and `WITH CHECK` to transaction-local `kgm.workspace_id` and `kgm.project_id` settings;
- uses parameterized SQL for tenant context and probe writes;
- does not access owner-local SQLite;
- does not create any repository migration file;
- does not expose a canonical shared repository API.

## HTTP Surface

Public candidate surface:

- `GET /health` — safe non-secret metadata only.

Bearer-protected preflight surface:

- `POST /preflight/probe` — write/update one synthetic probe marker;
- `GET /preflight/probes` — read markers visible to the configured synthetic tenant;
- `GET /preflight/rls-isolation` — direct alternate-tenant RLS observation.

The service does not accept workspace/project identifiers from client requests. Tenant context comes only from server-side candidate configuration.

Database/provider failures are returned as a generic `503 candidate database unavailable`; DSNs, credentials, private hosts and provider exception text are not returned.

## Render A1 Target

After exact-head CI is green, the intended disposable resources are:

- Render workspace: explicitly owner-confirmed `My Workspace`;
- region: Frankfurt;
- one free Render PostgreSQL instance dedicated to KGM preflight;
- one free Render Python web service dedicated to KGM preflight;
- application DB connection via Render internal/private connection string only;
- auto-deploy disabled during initial configuration/review;
- synthetic data only.

Existing non-KGM services and databases in the workspace are out of scope and must not be reused or modified.

## Evidence Boundary

Code/tests can validate configuration, query construction, RLS policy structure, API authentication and secret-redaction contracts.

They cannot establish any of the following until the Render candidate exists and is directly observed:

- real TLS/HTTPS behavior;
- real private app-to-Postgres connectivity;
- real public database non-reachability;
- actual PostgreSQL RLS execution;
- provider backup/recovery behavior;
- deployed secret/log behavior.

Those remain A1/A2 live evidence.

## Immutable Project State

This implementation does not change:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- `PROJECT_LOCAL_ONLY` canonical storage;
- mixed/shared canonical runtime `BLOCKED`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers `NONE_APPROVED`;
- production/live `NOT_OPERATIONAL`;
- P13.5/P13.6 factual-verification authority.
