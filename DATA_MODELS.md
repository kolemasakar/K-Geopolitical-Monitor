# DATA_MODELS

Canonical data concepts for K-Geopolitical Monitor.

Version: 3.1
Status: APPROVED / PHASE_13_VALIDATED / PHASE_15_VALIDATED / PHASE_16_VALIDATED / PHASE_17_VALIDATED / PHASE_18_A1_SYNCHRONIZED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Principle

Data provenance must be preserved from acquisition through analytical, forecast, delivery, publication-readiness and optional shared-runtime outputs. Governance, adapter, language, health, freshness, extraction, independence, contradiction, confidence, forecast, delivery, feedback, publication or infrastructure metadata must not silently become source evidence or factual verification.

Canonical factual-verification authority remains P13.5/P13.6. Later phases do not create a second truth store.

## Canonical Domain Summary

The canonical project-local schema contains source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, semantic claim/provenance/evidence/independence/contradiction/verification histories, monitoring/alerts, coverage, graph, forecasts/outcomes/calibration/performance, reports, delivery audit, operator feedback and owner/runtime-health state.

Canonical runtime storage remains `PROJECT_LOCAL_ONLY`.

## Phase 13 Semantic Model

Validated additive migration chain:

- `023_structured_semantic_claim_model.sql` — append-only semantic claim versions/links;
- `024_semantic_provenance_origin_relation_model.sql` — publisher/immediate/cited/underlying-origin relations;
- `025_semantic_evidence_relation_independence.sql` — typed evidence relations and independence assessments;
- `026_semantic_contradiction_model.sql` — typed contradiction lifecycle/history;
- `027_semantic_verification_policy_confidence.sql` — verification policy, multidimensional factual confidence and decision history.

P13.5/P13.6 remains the canonical factual-verification authority. Count-only, official-status-only, source-reputation-only and coverage-only promotion are forbidden.

## Phase 14 Read Model

Phase 14 is `VALIDATED_READY / NOT_ACTIVATED` and projects existing canonical monitoring/alert/semantic state read-only. It introduced no new canonical migration.

## Phase 15 Forecast Models

Validated additive migrations:

- `028_forecast_outcome_assessment_history.sql`;
- `029_forecast_calibration_observations.sql`;
- `030_forecast_performance_intelligence.sql`.

Forecast probability, calibration/performance metrics, sample size and drift remain non-truth operators.

## Phase 16 Delivery / Operator Feedback Models

Validated additive migrations:

- `031_delivery_intent_audit.sql`;
- `032_operator_quality_feedback.sql`.

Delivery state, receipts, acknowledgements, ratings, feedback and quality metrics cannot write or promote P13 factual-verification state.

## Phase 17 Publication Readiness Boundary

Phase 17 introduced no canonical database migration. Publication eligibility, public-safe projections, manifests/packages and local/test receipts are derived/readiness layers rather than a canonical truth store.

## Phase 18 Shared-Runtime Model Boundary

Phase 18 architecture and implementation contracts P18.0–P18.9 are validated. They define shared-runtime tenancy, RBAC, schema/migration compatibility, concurrency/idempotency, audit/outbox, security, recovery/rollback and non-production shadow/canary behavior.

These contracts do **not** allocate or create a canonical migration.

Migration `033` remains:

`NOT_CREATED / NOT_PREAUTHORIZED`.

The A1 Railway/PostgreSQL candidate is a disposable non-production preflight store. It is not the canonical datastore and its live RLS acceptance does not change the canonical migration chain.

A1 data/storage evidence:

- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- PostgreSQL candidate uses a restricted non-BYPASSRLS execution role;
- startup isolation acceptance observed alternate-tenant visible rows = `0`;
- no canonical owner data cutover occurred;
- no shared canonical datastore was activated;
- no migration `033` was created;
- no mixed/shared canonical runtime was enabled.

## Migration Chain — Current

Canonical created migration sequence currently extends through `032_operator_quality_feedback.sql`.

- 023 — structured semantic claims;
- 024 — semantic provenance/origin relations;
- 025 — semantic evidence relation/independence;
- 026 — semantic contradiction model;
- 027 — semantic verification policy/confidence;
- 028 — forecast outcome assessment history;
- 029 — forecast calibration observations;
- 030 — forecast performance intelligence;
- 031 — delivery intent/audit;
- 032 — operator quality feedback;
- 033 — `NOT_CREATED / NOT_PREAUTHORIZED`.

## Runtime / Storage Boundary

Production/live operational status: `NOT_OPERATIONAL`.
Runtime storage mode: `PROJECT_LOCAL_ONLY`.

- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- no direct cross-project canonical-store mutation;
- A1 is observation/preflight only;
- any canonical shared-store migration/cutover requires a separate explicit owner decision and fresh launch-time validation.

## Current State

- state synchronization: `4.35`;
- Phase 12: validated with known limitations;
- Phase 13: validated;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 15: validated;
- Phase 16: validated;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 18 P18.0–P18.9: validated;
- Phase 18 A1 non-production RLS preflight: validated;
- latest created migration: `032`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared runtime: `NOT_ACTIVATED`;
- production/live: `NOT_OPERATIONAL`.
