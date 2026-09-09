# PHASE 18 ACTIVATION A1 — Railway/PostgreSQL RLS Preflight Result

Date: 2026-09-09
State: `VALIDATED`
Gate: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`
Classification: `DISPOSABLE_NONPRODUCTION_PREFLIGHT`

## Result

A1 concrete infrastructure preflight passed against exact canonical implementation `8ac2c92c9351ac1bcea8818e52a819f81868ed92`.

Acceptance evidence:

- PR #45 CI: `1149 passed / SUCCESS`;
- native ARM64 exact-SHA: run `34357091433`, job `102484414159`, `1149 passed in 100.03s / SUCCESS`;
- independent x64 exact-SHA: run `34358136924`, job `102487942139`, `1149 passed in 202.48s / SUCCESS`;
- Railway deployment `52c39935-9e89-4f12-82e3-82345c606426`: `SUCCESS`;
- `/health`: HTTP 200;
- `rls_isolation_observed = true`;
- `alternate_tenant_visible_rows = 0`;
- PostgreSQL public TCP proxy: none;
- PostgreSQL public domain: none;
- no new runtime-role password/DSN/secret.

## Runtime role

`kgm_preflight_runtime` is deliberately non-login, non-superuser and non-BYPASSRLS, with minimal privileges. Tenant operations use transaction-local role switching. Startup fails closed when RLS isolation is not observed or alternate-tenant rows are visible.

## Non-promotion boundary

This result validates A1 only. It does not authorize:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = YES`;
- migration `033`;
- canonical data migration/cutover;
- mixed/shared canonical storage;
- paid-provider approval;
- public database ingress;
- KGM production/live operation.

Current boundaries remain:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- runtime storage `PROJECT_LOCAL_ONLY`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Any transition beyond A1 requires a separate explicit owner decision and fresh launch-time validation.
