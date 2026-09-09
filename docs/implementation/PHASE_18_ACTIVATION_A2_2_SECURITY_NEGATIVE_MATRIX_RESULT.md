# Phase 18 Activation A2.2 — Tenant / RBAC / Security Negative Matrix Result

Date: 2026-09-09
Project: K-Geopolitical Monitor
Status: `VALIDATED / NON-PRODUCTION PREFLIGHT / NOT_ACTIVATED`
Gate: `PHASE_18_ACTIVATION_A2_2_SECURITY_NEGATIVE_MATRIX_VALIDATED`
Parent A2 gate: `NOT_YET_SATISFIED / A2.3_REQUIRED`

## 1. Scope

A2.2 validates negative authorization, tenant-isolation and security-boundary behavior for the existing disposable Railway preflight candidate. It does not activate shared runtime and does not authorize production, paid resources, canonical-data migration, or migration `033`.

Evidence is intentionally split into:

- direct live observations against the already-deployed candidate; and
- exact-source structural/regression tests for boundaries that cannot be exercised credential-free without reading a secret.

No bearer token or database credential was read, printed, copied or added to GitHub Actions.

## 2. Live Candidate Anchor

- Railway project: `kgm-shared-runtime-preflight`
- candidate service: `kgm-preflight-api-v3`
- service id: `987c9ab8-4642-4bbb-b0c2-aa86f236790c`
- deployment id: `52c39935-9e89-4f12-82e3-82345c606426`
- deployment status: `SUCCESS`
- deployed source commit: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`
- Railway staged changes observed during A2.2: `31`
- A2.2 Railway mutations/redeploys: `NONE`

## 3. Direct Live Negative Matrix

Accepted workflow:

- workflow: `A2.2 Live Security Negative Matrix`
- run: `34373579763`
- job: `102540600589`
- runner: GitHub-hosted Ubuntu 24.04 / Python 3.11
- credential use: `NONE`
- result: `SUCCESS`

Observed gates:

- `LIVE_RLS_ISOLATION_PASS alternate_tenant_visible_rows=0`
- `AUTH_PRIV_ESC_NEGATIVE_MATRIX_PASS cases=7`
- `PROTECTED_MUTATION_AND_RLS_GATE_PASS`
- `IDOR_SSRF_PUBLIC_SURFACE_NEGATIVE_PASS`
- `A2_2_LIVE_SECURITY_NEGATIVE_MATRIX=PASS`

The seven authentication/privilege-escalation negative cases included:

- missing authorization;
- Basic authorization;
- wrong bearer;
- literal `admin` bearer;
- JWT-like admin-role bearer;
- SQL-injection-like bearer material;
- URL/metadata-endpoint-like bearer material.

All were rejected by the live candidate with the expected fail-closed bearer challenge and without private endpoint, tenant identifier, DSN, token or traceback disclosure.

Protected write and RLS-observation endpoints also remained inaccessible without a valid bearer. Guessed IDOR-style tenant/project routes and a generic SSRF-style fetch route were absent. Supplying alternate tenant/project query parameters did not bypass authentication.

## 4. Structural Security Evidence

`tests/test_a2_2_security_negative_matrix.py` validates the current candidate contract without changing runtime code:

- public API exposes no client-selected `workspace_id` or `project_id` route parameter;
- no generic `url`/fetch primitive is exposed by the preflight API;
- safe metadata excludes DB DSN, bearer token and tenant identifiers;
- SQL-injection-style `probe_id` values are rejected before database connection;
- adversarial payload text is SHA-256 hashed and never interpolated into SQL;
- SQL execution remains parameterized;
- tenant transactions switch to `SET LOCAL ROLE kgm_preflight_runtime`;
- runtime role remains `NOLOGIN`, `NOSUPERUSER`, `NOINHERIT`, `NOBYPASSRLS`;
- RLS remains forced;
- elevated grants such as ALL/DELETE/TRUNCATE/CREATE are absent.

## 5. Interpretation of RBAC / IDOR / SSRF Scope

The approved beta boundary is single-owner only. The disposable A2 candidate therefore has no multi-user role hierarchy to validate as if it were production RBAC. A2.2 validates the actual present boundary rather than inventing future roles:

- possession of the one configured bearer is the protected API authorization boundary;
- fake role/admin claims do not create privilege;
- tenant identity is server-side configuration, not client-selected input;
- no public resource-id route permits tenant switching;
- no generic outbound URL-fetch capability exists on this candidate.

Future multi-user/team RBAC remains outside beta scope and would require a separate implementation and security gate before activation.

## 6. Probe Correction Record

The first live workflow attempt (`34373478838`, job `102540251981`) stopped after live RLS PASS because the probe itself called `casefold()` on `bytes`. This was a probe implementation defect, not a candidate security failure. The probe was corrected to use byte-safe lowering and rerun successfully as `34373579763`.

## 7. Preserved Boundaries

A2.2 does not change:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- canonical runtime storage = `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime = `BLOCKED`;
- `MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `BETA_PAID_RESOURCES = NOT_CONSIDERED / NOT_AUTHORIZED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- strategic machine-state sync = `4.34`.

## 8. Next Stage

A2.2 closure advances the workstream to:

`A2.3 — Backup / Restore / Rollback`

The parent gate `PHASE_18_SHARED_RUNTIME_LIVE_CONTROLS_OBSERVED` remains unsatisfied until A2.3 is directly validated.