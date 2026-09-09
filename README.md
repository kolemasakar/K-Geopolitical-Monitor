# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.20
Status: ACTIVE / ROADMAP_V4_22 / PHASE_15_VALIDATED / PHASE_17_VALIDATED_READY / PHASE_14_NOT_ACTIVATED / OWNER_ACTIVATION_REQUIRED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Purpose

K-Geopolitical Monitor supports discovery, provenance-aware verification, geopolitical analysis, forecasting, reporting, operational monitoring, delivery/quality feedback and controlled publication readiness while preserving explicit truth, storage, security and activation boundaries.

## Canonical Documentation

- `ROADMAP.md` — strategic sequence and authoritative phase state;
- `docs/state/CURRENT_PROJECT_STATE.json` — machine-readable current-state contract;
- `ARCHITECTURE.md` — architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — integration/source/delivery/publication rules;
- `SOURCE_POLICY.md` — source/provenance governance;
- `DATA_MODELS.md` — canonical data-model and migration summary;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md` — Phase 13 plan/closure record;
- `docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_PLAN.md` — Phase 14 validated readiness record;
- `docs/implementation/PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_PLAN.md` — Phase 15 validated record;
- `docs/implementation/PHASE_16_DELIVERY_OPERATOR_QUALITY_FEEDBACK_PLAN.md` — Phase 16 validated record;
- `docs/implementation/PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_PLAN.md` — Phase 17 validated readiness record;
- `docs/implementation/PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_RESULT.md` — Phase 17 final result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-05_PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED_READY.md` — Phase 17 checkpoint;
- `docs/decisions/PHASE_17_CURRENT_ACCOUNT_PUBLICATION_CAPABILITY_BOUNDARY_2026-09-05.md` — current account publication capability constraint.

## Current State

- strategic ROADMAP: `APPROVED / v4`, state synchronization `4.22`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- P13.5: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`;
- P13.6: `VALIDATED`;
- Phase 14: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY / VALIDATED_READY / NOT_ACTIVATED`;
- P14.0–P14.6: `VALIDATED`;
- Phase 15: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`;
- P15.0–P15.6: `VALIDATED`;
- Phase 16: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`;
- P16.0–P16.7: `VALIDATED`;
- Phase 17: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED / VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- P17.0–P17.6: `VALIDATED`;
- Phase 17 current account publication capability: `UNAVAILABLE`;
- Phase 17 activation: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`;
- Phase 18: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- Phase 18 gate: `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`;
- operational activation: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: `BLOCKED`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Phase 13 Strategic Closure

Gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.
P13.6 implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`.
Strategic closure validation anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`.
- x64 run `33861302915`, job `100986128743`: `497 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33861302926`, job `100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Historical Phase-13 package evidence retained for regression/audit:
- P13.3 formal closure HEAD `9023dc22d36525b4dc9babbf21d97d184a1c110e`: `438 passed, 1 warning / SUCCESS`;
- P13.4 validation anchor `d4dbb8a8098cef960194935bd94d4640fd719050`: `447 passed, 1 warning / SUCCESS`;
- P13.5 validation anchor `0f0d746c538dc5ce8f010fb80f8afbe00685414a`: `475 passed, 2 warnings / SUCCESS`.

Canonical P13.5/P13.6 factual verification remains policy-controlled, provenance-bound and multidimensional. Legacy `verification.py`, `confidence_engine.py`, scalar confidence, host/source counts and `independent_origin_count` remain compatibility state, not canonical truth. P13.6 is a read-only live compatibility cutover/projection; missing instrumentation remains `NOT_INSTRUMENTED`.

## Phase 14 Strategic Closure

Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`.
State: `VALIDATED_READY / NOT_ACTIVATED`.
Closure validation anchor: `43a26aee7ed677dafd46eb91c510d0e724d558c2`.
- x64 run `33873131265`, job `101023637949`: `510 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33873131300`, job `101023638027`: native `aarch64`, `510 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Phase 14 is readiness only. `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED` and owner execution remains disabled.

## Phase 15 Strategic Closure

Gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`.
Closure validation anchor: `77b444e2c89f763e56acc22183c74634ea993573`.
- x64 run `33906546408`, job `101132699703`: `576 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33906546431`, job `101132700003`: native `aarch64`, `576 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Phase 15 adds provenance-bound outcome resolution, calibration observations and exact-cohort performance intelligence. Forecast probability, Brier/ECE, bias/drift and sample metrics cannot promote factual verification.

## Phase 16 Strategic Closure

Gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`.
Closure validation anchor: `18c2d5eed4145500bf72bbeeb0b6bbc92e8c7553`.
- x64 run `33920882676`, job `101178676207`: `638 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33920882682`, job `101178676586`: native `aarch64`, `638 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Phase 16 validates deterministic delivery intent/audit, redaction, provider-neutral local/test transport, delivery receipts, operator feedback and advisory quality observations. No real external provider is activated. Delivery/feedback state cannot promote factual verification.

## Phase 17 Strategic Readiness Closure

Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`.
State: `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`.
Closure validation anchor: `daca1240cb1f99267795b39ddf7da32eb4fa9ec0`.
- x64 run `33937240088`, job `101227433133`: `716 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33937240097`, job `101227433249`: native `aarch64`, `716 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Phase 17 validates publication eligibility, public-safe projection/redaction, deterministic release manifests/packages and a provider-neutral local/test target only. Real publication is not activated. The current account capability is `UNAVAILABLE`; owner approval alone cannot bypass `PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`. If capability becomes available later, publication still requires `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION` and fresh launch-time validation. Migration `033` is `NOT_CREATED / NOT_PREAUTHORIZED`.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- count-only verification promotion is forbidden;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- delivery state, receipts and feedback cannot promote factual verification;
- publication eligibility, receipts and engagement cannot promote factual verification;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing/uninstrumented tool history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime remains the validated runtime line;
- public KGM HTTP/HTTPS/database/API/dashboard ingress: not approved/not deployed;
- backend HTTPS: not deployed;
- private GPT backend Action: not connected;
- public sharing: not active;
- production/live: not operational;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`.

## ROADMAP Position

Phase 17 engineering/readiness is closed. The next strategic boundary is Phase 18 — Shared / Team Runtime — `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`.

No Phase 18 implementation, shared runtime transition, production launch, public publication, owner operational activation or paid-provider activation is implied by this state. `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL` remains the next architecture gate.

## Current-State Addendum — Phase 18 A1 (2026-09-09)

The historical summary above is retained verbatim because canonical regression tests bind earlier gate evidence to this file. For current interpretation, the later validated Phase 18 records and this additive A1 preflight evidence take precedence.

- Phase 18 architecture: owner-approved; implementation authorized;
- P18.0–P18.9: validated through `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`;
- A1 live preflight: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`;
- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- exact-SHA validation: x64 `1149 passed`, native ARM64 `1149 passed`;
- Railway deployment `52c39935-9e89-4f12-82e3-82345c606426`: `SUCCESS`, health check HTTP 200;
- restricted runtime role `kgm_preflight_runtime`: `NOLOGIN / NOSUPERUSER / NOBYPASSRLS`;
- live RLS isolation accepted with `rls_isolation_observed=true` and `alternate_tenant_visible_rows=0`;
- PostgreSQL remains private-only; no public database TCP proxy/domain;
- no new runtime-role password, DSN or secret was introduced;
- A1 remains disposable non-production preflight only;
- strategic machine state intentionally remains at synchronization `4.34` / `PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE` until a separate formal synchronization gate;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `P18_9_LAUNCH_ELIGIBLE = FALSE`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- runtime storage remains `PROJECT_LOCAL_ONLY`; mixed/shared canonical runtime remains `BLOCKED`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

A1 evidence checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`.
