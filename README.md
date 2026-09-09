# K-Geopolitical Monitor

Global geopolitical monitoring and intelligence platform.

Version: 4.35
Status: ACTIVE / ROADMAP_V4_34 / PHASE_18_P18_9_VALIDATED / A1_PREFLIGHT_VALIDATED / PHASE_18_NOT_ACTIVATED / OWNER_DECISION_REQUIRED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Purpose

K-Geopolitical Monitor is a geopolitical decision-support system for discovery, provenance-aware verification, causal and strategic analysis, probabilistic forecasting, reporting, operational monitoring and controlled delivery/publication readiness. It is not a generic news feed, scraper or dashboard.

Canonical processing line:

`Discovery -> Verification -> Analysis -> Relationships -> Forecasting -> Reports`

The project preserves explicit separation between implementation, validation, activation and production/live operation.

## Canonical documentation

- `PROJECT_CONCEPT_FOUNDATION.md` — approved product/mission foundation;
- `ROADMAP.md` — strategic sequence and validated phase line;
- `docs/state/CURRENT_PROJECT_STATE.json` — machine-readable current-state contract;
- `ARCHITECTURE.md` — architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — integration/source/delivery/publication boundaries;
- `SOURCE_POLICY.md` — source/provenance governance;
- `DATA_MODELS.md` — canonical data-model/migration summary;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md` — latest concrete A1 preflight evidence.

## Current strategic position

Strategic ROADMAP: `APPROVED / v4`, roadmap document version `4.34`.
State synchronization: `4.35`.
Current position: `PHASE_18_ACTIVATION_A1_VALIDATED_OWNER_ACTIVATION_GATE`.

Validated development line:

- Phases 0–11: validated historical engineering baseline;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`; P13.5/P13.6 remains the factual-verification authority;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED / OWNER_DECISION_REQUIRED`;
- Phase 15: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`;
- Phase 16: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- Phase 18: architecture approved, implementation authorized, P18.0–P18.9 validated at `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`;
- Phase 18 A1: concrete Railway/PostgreSQL non-production RLS preflight validated at `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`.

## Phase 18 A1 concrete evidence

Canonical implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`.

Validation evidence:

- PR #45 CI: `1149 passed / SUCCESS`;
- exact-SHA native ARM64: run `34357091433`, job `102484414159`, native `aarch64`, `1149 passed in 100.03s / SUCCESS`, bootstrap/unattended/systemd PASS;
- independent exact-SHA x64: run `34358136924`, job `102487942139`, exact `8ac2c92c9351ac1bcea8818e52a819f81868ed92`, `1149 passed in 202.48s / SUCCESS`;
- Railway candidate `kgm-preflight-api-v3` repinned to exact canonical SHA;
- Railway deployment `52c39935-9e89-4f12-82e3-82345c606426`: `SUCCESS`;
- application startup complete and `/health` returned HTTP 200;
- startup RLS acceptance: `rls_isolation_observed = true`, `alternate_tenant_visible_rows = 0`;
- PostgreSQL candidate has no public service domain and no public TCP proxy;
- runtime role `kgm_preflight_runtime` is non-login, non-superuser and non-BYPASSRLS;
- no new runtime-role password/DSN/secret was introduced.

Railway's provider environment is named `production`, but under the KGM architecture contract this remains a disposable **non-production preflight candidate**. That provider label does not make KGM production/live.

## Activation and runtime boundaries

The A1 PASS does not activate Phase 18.

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- P18.9 historical launch eligibility remains `FALSE`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- runtime storage = `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime = `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public production KGM API/dashboard ingress = not approved/deployed;
- database public TCP proxy = none;
- paid providers = `NONE_APPROVED`;
- no canonical shared-store cutover has occurred;
- no real external publication is activated;
- Phase 14 owner operation remains separately owner-gated.

Any transition beyond A1 requires a separate explicit owner decision and fresh launch-time validation. No validation gate auto-promotes into production/live operation.

## Permanent truth / epistemic boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves that a source made a statement, not automatically that the underlying event occurred;
- source reputation, health, freshness, coverage and adapter/domain/item counts are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- count-only verification promotion is forbidden;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- delivery state, receipts, publication eligibility and engagement cannot promote factual verification;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing/uninstrumented evidence remains explicit and is never reconstructed as exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state.

## Latest checkpoint

`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`
