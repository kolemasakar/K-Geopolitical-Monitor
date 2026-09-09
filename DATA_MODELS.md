# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 3.0
Status: APPROVED / PHASE_13_VALIDATED / PHASE_15_VALIDATED / PHASE_16_VALIDATED / PHASE_17_SYNCHRONIZED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Principle

Data provenance must be preserved from acquisition through analytical, forecast, delivery and publication-readiness outputs. Governance, adapter, language, health, freshness, extraction, independence, contradiction, confidence, forecast, delivery, feedback or publication metadata must not silently become source evidence or factual verification.

## Canonical Domain Summary

The project-local schema contains source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, semantic claim/provenance/evidence/independence/contradiction/verification histories, monitoring/alerts, coverage, graph, forecasts/outcomes/calibration/performance, reports, delivery audit, operator feedback and owner/runtime-health state.

Canonical factual-verification authority remains P13.5/P13.6. Phase 15 forecast metrics, Phase 16 delivery/feedback state and Phase 17 publication readiness do not create a second truth store.

## Phase 13 Semantic Model — Validated Historical Foundation

Phase 13 semantic model v2 architecture: `P13.0_VALIDATED`.
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.

Historical compatibility persistence remains readable (`claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence`) but is not promoted into canonical semantic truth.

### P13.1 Structured Semantic Claim Model

State: `VALIDATED`.
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Migration: `023_structured_semantic_claim_model.sql`.

P13.1 adds append-only `semantic_claim_versions` and `semantic_claim_links`. The schema boundary explicitly keeps `underlying_origin`, `independence_state`, `evidence_relation`, `contradiction_state`, `verification_state`, `factual_confidence` and `coverage_confidence` out of claim-identity persistence; those concepts belong to later semantic layers.

### P13.2 Provenance / Underlying-Origin Relation Model

State: `VALIDATED`.
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Migration: `024_semantic_provenance_origin_relation_model.sql`.

Publisher/publication, immediate source, cited/quoted source and underlying origin remain separate. Citation, syndication, repost, translation and derivation are provenance relations, not independent corroboration.

### P13.3 Evidence Relation and Independence Assessment

State: `VALIDATED`.
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Migration: `025_semantic_evidence_relation_independence.sql`.
Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.
Formal closure validation: `438 passed, 1 warning / SUCCESS` on x64 and native ARM64.

P13.3 adds append-only `semantic_evidence_relation_versions` and `semantic_independence_assessment_versions`. Evidence relation vocabulary includes `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`; independence states include `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`.

### P13.4 Typed Contradiction Model

State: `VALIDATED`.
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.
Migration: `026_semantic_contradiction_model.sql`.
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.
Implementation validation: `447 passed, 1 warning / SUCCESS`.

P13.4 adds append-only `semantic_contradiction_versions` and `semantic_contradiction_evidence_links`. Dimensions include `OCCURRENCE_EXISTENCE`, `ATTRIBUTION_RESPONSIBILITY`, `ACTOR_IDENTITY`, `QUANTITY_VALUE`, `TIME`, `LOCATION`, `STATUS_OUTCOME`, `SCOPE_EXTENT`, `CAUSAL_INTERPRETATION`; lifecycle states include `DETECTED`, `UNRESOLVED`, `EVOLVING`, `RESOLVED`. Evidence links require a current P13.3 evidence relation version. Contradiction resolution is not automatic factual truth selection.

### P13.5 Verification Policy and Multidimensional Confidence

State: `VALIDATED`.
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.
Migration: `027_semantic_verification_policy_confidence.sql`.
Validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.
Implementation validation: `475 passed, 2 warnings / SUCCESS`.

P13.5 adds append-only `semantic_verification_policy_versions`, `semantic_factual_confidence_versions` and `semantic_verification_decision_versions`. Count-only, official-status-only, source-reputation-only and coverage-only promotion are forbidden. `VERIFIED` requires current independent `SUPPORTS` evidence plus policy floors and no blocking contradiction/current `CONTRADICTS` state. Confidence is multidimensional; there is no canonical scalar. Coverage cannot promote factual verification.

### P13.6 Live Compatibility

State: `VALIDATED`.
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`.
Strategic closure anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`.
Strategic validation: `497 passed, 2 warnings / SUCCESS` on x64 and native ARM64.

P13.6 introduced no database migration. Historical Phase-13 statement: migration 028 = `NONE` for Phase 13. `semantic_live_compatibility.py` is read-only and uses explicit links/current P13.5 decisions only. Missing E6 instrumentation remains `NOT_INSTRUMENTED`.

## Phase 14 Read Model

Phase 14 is `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY / VALIDATED_READY / NOT_ACTIVATED` and introduced no migration `028`. It projects existing canonical monitoring/alert/semantic state read-only. `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

## Phase 15 Forecast Outcome / Calibration / Performance Models

State: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`.

Actual additive migration chain after Phase 14:
- `028_forecast_outcome_assessment_history.sql` — append-only provenance-bound forecast outcome assessment history;
- `029_forecast_calibration_observations.sql` — immutable calibration observations with separate raw/calibrated evidence;
- `030_forecast_performance_intelligence.sql` — exact-cohort aggregate membership and descriptive performance/drift intelligence.

This later Phase-15 migration `028` does not contradict the historical Phase-13/14 statement that those phases introduced no migration 028. Forecast probability, Brier/ECE, bias/drift, sample size and qualification remain non-truth operators.

## Phase 16 Delivery / Operator Feedback Models

State: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`.

Additive migrations:
- `031_delivery_intent_audit.sql` — stable delivery intents, append-only transport attempts/receipts and idempotency/audit state;
- `032_operator_quality_feedback.sql` — append-only typed operator quality feedback.

Delivery state, receipts, acknowledgements, ratings, feedback and quality metrics cannot write or promote P13 factual-verification state.

## Phase 17 Publication Readiness Model Boundary

State: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED / VALIDATED_READY / NOT_ACTIVATED`.

Phase 17 introduced no database migration. Migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`. Publication eligibility, public-safe projections, manifests/packages and local/test receipts are derived/readiness layers rather than a canonical truth store. Real external publication remains unactivated and current account capability is `UNAVAILABLE`.

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

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

- mixed/shared canonical runtime: `BLOCKED`;
- Phase 18 shared/team runtime: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- direct cross-project canonical-store mutation remains prohibited without a new architecture approval.

## Current State

- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- P13.0–P13.6: `VALIDATED`;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED / OWNER_DECISION_REQUIRED`;
- Phase 15: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`;
- Phase 16: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`;
- Phase 17: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED / VALIDATED_READY / NOT_ACTIVATED`;
- Phase 18: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- migration latest created: `032`;
- migration 033: `NOT_CREATED / NOT_PREAUTHORIZED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.

## Current-State Addendum — Phase 18 A1 (2026-09-09)

The historical Phase 18 model-boundary wording above is retained verbatim for regression/audit continuity. Phase 18 architecture and provider-neutral datastore contracts P18.0–P18.9 are now validated, but no canonical shared-store migration has been authorized.

A1 concrete Railway/PostgreSQL preflight adds infrastructure evidence only:

- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- restricted non-BYPASSRLS runtime role and transaction-local role switching validated;
- live startup RLS isolation passed with alternate-tenant visible rows `0`;
- no canonical owner data cutover occurred;
- no shared canonical datastore was activated;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Strategic machine state remains synchronization `4.34` until a separate formal activation synchronization gate; A1 evidence is recorded separately in its checkpoint/result/decision documents.
