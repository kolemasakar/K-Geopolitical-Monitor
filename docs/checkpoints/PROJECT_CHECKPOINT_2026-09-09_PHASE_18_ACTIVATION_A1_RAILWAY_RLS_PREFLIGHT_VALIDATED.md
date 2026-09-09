# PROJECT CHECKPOINT — Phase 18 Activation A1 Railway RLS Preflight Validated

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: VALIDATED / NON-PRODUCTION PREFLIGHT / NOT_ACTIVATED
Gate: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`

## Scope

This checkpoint records concrete non-production A1 infrastructure evidence after the already-validated P18.0–P18.9 readiness sequence. It does **not** authorize shared-runtime activation, canonical cutover, migration `033`, paid-provider use, or production/live operation.

## Canonical implementation anchor

- exact canonical `main`: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- PR #45: `Enforce non-BYPASSRLS runtime role for A1 preflight`;
- PR #45 branch validation: run `34356839990`, `1149 passed in 94.64s / SUCCESS`;
- exact-SHA native ARM64 validation: run `34357091433`, job `102484414159`, native `aarch64`, `1149 passed in 100.03s / SUCCESS`, bootstrap/unattended/systemd PASS;
- independent exact-SHA x64 fallback validation: run `34358136924`, job `102487942139`, Ubuntu 24.04 / Python 3.11.16 x64, exact `8ac2c92c9351ac1bcea8818e52a819f81868ed92`, `1149 passed in 202.48s / SUCCESS`.

The fallback x64 run is recorded explicitly as an independent exact-SHA validation because the original main-event x64 runner remained anomalously in progress during the acceptance chain; no weaker result is promoted.

## A1 runtime-role isolation

The A1 PostgreSQL candidate now uses `kgm_preflight_runtime` as a non-login, non-superuser, non-BYPASSRLS, non-createdb, non-createrole, non-inheriting execution role with minimal schema/table grants. Tenant operations enter the role using transaction-local role switching. No new runtime-role password, DSN, or secret was introduced.

## Railway candidate evidence

Railway project: `kgm-shared-runtime-preflight`.

Canonical A1 candidate service:
- service: `kgm-preflight-api-v3`;
- service id: `987c9ab8-4642-4bbb-b0c2-aa86f236790c`;
- source pin after validation: exact `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- deployment id: `52c39935-9e89-4f12-82e3-82345c606426`;
- deployment status: `SUCCESS`;
- healthcheck: `/health`, PASS / HTTP 200;
- application startup: complete.

PostgreSQL candidate:
- service: `kgm-preflight-postgres`;
- service id: `7710abe9-942c-4e72-9eff-6a6ae26344cd`;
- public service domain: none;
- public TCP proxy: none;
- database network exposure: private-only Railway internal network.

The Railway environment is named `production` by the provider. Under the KGM architecture contract this deployment remains a **disposable non-production preflight candidate**; the provider environment name does not change KGM operational status.

## Live startup RLS acceptance

Application startup executes the database initialization and then the candidate RLS isolation self-check. Startup fails closed unless:

- `rls_isolation_observed == true`; and
- `alternate_tenant_visible_rows == 0`.

The exact-SHA deployment reached `Application startup complete`, Railway deployment `SUCCESS`, and `/health` 200. No startup RLS exception was present. Therefore the A1 live RLS startup acceptance is recorded as:

- `rls_isolation_observed = true`;
- `alternate_tenant_visible_rows = 0`;
- `A1_LIVE_RLS_PREFLIGHT = PASS`.

## Preserved boundaries

The following remain unchanged and closed:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- canonical runtime storage = `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime = `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- `DB_PUBLIC_TCP_PROXY = NO`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- no canonical data cutover;
- no shared datastore activation;
- no owner production data imported into the disposable candidate;
- no production KGM public API/dashboard activation.

## Decision consequence

A1 has moved from implementation/infrastructure uncertainty to a concrete validated non-production preflight result. This does **not** auto-promote Phase 18. Any step beyond A1 still requires a separate explicit owner decision and a newly defined fresh launch-time validation/cutover gate.
