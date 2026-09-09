# ARCHITECTURE

Technical architecture definition for K-Geopolitical Monitor.

Version: 4.35
Status: APPROVED / ROADMAP_V4_34_SYNCHRONIZED / PHASE_18_P18_9_VALIDATED / A1_PREFLIGHT_VALIDATED / NOT_ACTIVATED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Current Architecture Position

Current strategic position: `PHASE_18_ACTIVATION_A1_VALIDATED_OWNER_ACTIVATION_GATE`.

Validated line:
- Phase 12 — intelligence/source-network foundation validated with known limitations;
- Phase 13 — semantic verification/provenance validated; P13.5/P13.6 remains canonical factual-verification authority;
- Phase 14 — owner operational intelligence `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 15 — forecast calibration/performance validated;
- Phase 16 — delivery/operator quality loop validated;
- Phase 17 — controlled external publication readiness `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 18 — architecture approved, implementation authorized, P18.0–P18.9 validated;
- A1 — concrete disposable Railway/PostgreSQL non-production preflight validated with live startup RLS isolation PASS.

Phase 18 remains `NOT_ACTIVATED` and requires an explicit owner decision plus fresh launch-time validation before any activation/cutover.

## Logical Architecture

`Public Sources -> Governed Acquisition -> Provenance / Semantic Claims -> P13.5 Verification Policy -> P13.6 Live Compatibility -> Analysis / Graph -> Forecasting -> Calibration / Performance -> Monitoring / Alerts -> Owner Read Model -> Delivery / Feedback -> Controlled Publication Readiness -> Optional Shared Runtime`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Canonical Truth / Provenance Boundary

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements establish what was stated, not automatically the underlying event;
- source reputation, portfolio state, availability, freshness and coverage are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- graph inference cannot promote factual verification;
- forecast probability/confidence/calibration metrics cannot promote factual verification;
- delivery state, feedback, publication eligibility, receipts and engagement cannot promote factual verification;
- count-only verification promotion is forbidden;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- canonical factual-verification authority remains P13.5/P13.6.

## Shared Runtime Architecture — Phase 18

P18.0–P18.9 validate the provider-neutral shared-runtime contracts for tenancy, RBAC, datastore schema/migration behavior, concurrency/idempotency, audit/outbox isolation, security controls, recovery/rollback and non-production shadow/canary readiness. Those gates validate architecture/readiness, not production deployment.

A1 adds concrete non-production infrastructure evidence without changing the canonical runtime boundary:

- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- candidate application: Railway `kgm-preflight-api-v3`;
- candidate database: Railway `kgm-preflight-postgres`;
- database has no public domain and no public TCP proxy;
- transaction-scoped execution role: `kgm_preflight_runtime`;
- role is `NOLOGIN / NOSUPERUSER / NOBYPASSRLS / NOCREATEDB / NOCREATEROLE / NOINHERIT` with minimal grants;
- startup is fail-closed unless RLS isolation is observed and alternate-tenant visible rows equal zero;
- live A1 startup acceptance: `rls_isolation_observed=true`, `alternate_tenant_visible_rows=0`, deployment and health PASS;
- no new runtime-role password, DSN or secret was introduced.

Railway's environment label `production` is provider metadata only. Under KGM governance this is a disposable non-production preflight candidate and does not constitute production/live activation.

## Runtime / Storage Boundary

- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- direct cross-project canonical-store mutation: forbidden;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- no canonical shared-store cutover;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

The disposable A1 candidate is an observation/preflight surface only and is not the canonical runtime datastore.

## Security / Exposure Boundary

- owner-only OCI remains the validated canonical runtime line;
- production KGM public API/dashboard ingress: not approved/deployed;
- disposable A1 API may use a provider-generated HTTPS domain solely for preflight;
- A1 PostgreSQL public domain: none;
- A1 PostgreSQL public TCP proxy: none;
- private GPT backend Action: `NOT_CONNECTED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`;
- secret values remain non-documentable; no new role credential was created for A1.

## Activation Rule

`IMPLEMENTED != VALIDATED != ACTIVATED != PRODUCTION_LIVE`.

A1 validation does not authorize migration `033`, provider spending, canonical-data migration, shared-runtime activation, public production ingress or production/live operation. Any such step requires a separate explicit owner decision and a fresh launch-time gate.

## Current State

- ROADMAP: `APPROVED / v4`, roadmap document version `4.34`;
- state synchronization: `4.35`;
- Phase 18 P18.0–P18.9: `VALIDATED`;
- A1 live non-production RLS preflight: `VALIDATED`;
- Phase 18 activation: `NO`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- production/live: `NOT_OPERATIONAL`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`.
