# PROJECT CHECKPOINT — Phase 18 Activation A2.1 Network / TLS / Exposure Validated

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `VALIDATED / READ_ONLY_LIVE_OBSERVATION / NON_PRODUCTION / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED`
Parent A2 target: `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED`

## Scope

This checkpoint records the approved A2.1 live network/TLS/exposure validation against the existing disposable Railway A1 candidate. The validation is credential-free and read-only. It does not authorize Railway mutation, paid resources, canonical data movement, migration `033`, shared-runtime activation, or production/live operation.

## Canonical project anchor

- canonical `main` at A2.1 start: `be96b8bdccf594a869b768f41e136d44c3e0adbf`;
- approved beta strategy: single-owner only until beta completion;
- beta paid resources: `NOT_CONSIDERED / NOT_AUTHORIZED`;
- A1 gate already validated: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`.

The disposable Railway service itself remains pinned to the previously accepted A1 implementation anchor `8ac2c92c9351ac1bcea8818e52a819f81868ed92`. A2.1 intentionally did not redeploy or mutate the candidate.

## Railway live platform observations

Project:
- `kgm-shared-runtime-preflight`;
- project id: `6874bf36-79e7-4cfa-93d7-4da8109c9e5c`;
- environment id: `52bea49d-d122-4bed-85b5-217c45ddccfc`;
- provider environment name: `production`, while KGM classification remains disposable non-production preflight.

Canonical A1 API candidate:
- service: `kgm-preflight-api-v3`;
- service id: `987c9ab8-4642-4bbb-b0c2-aa86f236790c`;
- deployment id: `52c39935-9e89-4f12-82e3-82345c606426`;
- deployment status: `SUCCESS`;
- public service domain: `kgm-preflight-api-v3-production.up.railway.app`;
- custom domains: none;
- healthcheck path: `/health`;
- one replica in `iad`.

PostgreSQL candidate:
- service: `kgm-preflight-postgres`;
- service id: `7710abe9-942c-4e72-9eff-6a6ae26344cd`;
- deployment status: `SUCCESS`;
- service domains: none;
- custom domains: none;
- Railway service configuration exposes no public networking block for the database.

At observation time Railway reported staged platform changes in the environment. A2.1 did not apply, deploy, discard, or otherwise mutate those staged changes.

## External public-runner wire validation

Accepted live probe:
- workflow: `A2.1 Live Network TLS Exposure Probe`;
- run: `34368911806`;
- job: `102524751017`;
- probe branch head: `40ed67ad07e3a816a440a0af30c84412589f2917`;
- runner: GitHub-hosted Ubuntu 24.04 / Python 3.11.16;
- credentials supplied to probe: none.

Accepted observations:
- TLS handshake: `PASS`;
- negotiated protocol: `TLSv1.3`;
- cipher observed: `TLS_AES_256_GCM_SHA384`;
- HTTPS `GET /health`: `200`;
- public-safe health metadata confirms `canonical=false`, `production_live=false`, `shared_runtime_active=false`, `synthetic_data_only=true`, `database_network=railway_private`;
- existing live RLS startup evidence remains visible as `rls_isolation_observed=true`, `alternate_tenant_visible_rows=0`;
- plain HTTP `GET /health`: `301` redirect to the expected HTTPS host;
- `/docs`: `404`;
- `/redoc`: `404`;
- unauthenticated `GET /preflight/probes`: `401` with Bearer challenge;
- protected error response did not expose PostgreSQL/private-endpoint material;
- `kgm-preflight-postgres.railway.internal:5432` did not resolve from the public GitHub-hosted runner.

The first probe attempt was not accepted as closure evidence because the probe script itself raised a Python `AttributeError` after already observing TLS/HTTPS/redirect PASS. The script was corrected without changing Railway, then the full credential-free probe passed.

## Private app-to-database path evidence

The application source accepts only an approved private-network marker and the deployed `/health` reports `database_network=railway_private`. The application startup performs database initialization and live RLS isolation before becoming healthy. Since the same accepted candidate is healthy while the database has no public service/custom domain and its Railway-internal hostname is not publicly resolvable, the observed candidate path is consistent with and dependent on Railway private networking rather than a public database endpoint.

No `DATABASE_PUBLIC_URL` or public database endpoint was introduced by A2.1.

## Secret exposure inspection

A2.1 used no bearer or database credential in the external probe.

Observed Railway API configuration exposed variable names only, including `KGM_PREFLIGHT_BEARER_TOKEN` and `KGM_SHARED_DATABASE_URL`; no variable values were emitted through the connected OAuth path. The accepted A1 build/deploy logs and A2.1 public responses were inspected and no bearer token, database credential, PostgreSQL DSN, or Railway internal endpoint value was observed in the public API response or deployment output.

The application source loads bearer/database secrets from environment variables and its public `safe_metadata` intentionally excludes credentials, hosts, and endpoints.

## A2.1 verdict

`A2_1_TLS = PASS`

`A2_1_HTTPS_HEALTH = PASS`

`A2_1_HTTP_TO_HTTPS = PASS`

`A2_1_PUBLIC_API_SURFACE = PASS`

`A2_1_DB_PUBLIC_DOMAIN = ABSENT`

`A2_1_DB_PUBLIC_DNS = ABSENT_FROM_PUBLIC_RUNNER`

`A2_1_PRIVATE_DATABASE_PATH = OBSERVED_CONSISTENT_WITH_RAILWAY_PRIVATE`

`A2_1_SECRET_EXPOSURE_OBSERVED = NO`

`PHASE_18_ACTIVATION_A2_1_NETWORK_TLS_EXPOSURE_VALIDATED = YES`

## Preserved boundaries

- beta user model = `SINGLE_OWNER_ONLY`;
- beta paid resources = `NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- canonical runtime storage = `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime = `BLOCKED`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- no canonical cutover;
- no canonical data copied to the disposable candidate;
- no Railway staged changes applied by this validation.

## Decision consequence

A2.1 is complete. The parent A2 gate is **not** complete because A2.2 security negative-matrix and A2.3 recovery/rollback evidence remain outstanding.

Next executable stage: `A2.2 — Tenant / RBAC / Security Negative Matrix`.
