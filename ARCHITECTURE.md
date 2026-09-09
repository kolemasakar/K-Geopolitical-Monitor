# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 4.0
Status: APPROVED / ROADMAP_V4_22_SYNCHRONIZED / PHASE_17_VALIDATED_READY
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Current Architecture Position

Current strategic position: `POST_PHASE_17_PRE_PHASE_18_ARCHITECTURE_GATE`.

Validated line:
- Phase 12 — `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13 — `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- Phase 14 — `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY / VALIDATED_READY / NOT_ACTIVATED`;
- Phase 15 — `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`;
- Phase 16 — `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`;
- Phase 17 — `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED / VALIDATED_READY / NOT_ACTIVATED`;
- Phase 18 — `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED` under `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`.

Phase 18 is not activated or pre-approved by Phase 17 closure.

## Logical Architecture

`Public Sources -> Governed Acquisition -> Provenance / Semantic Claims -> P13.5 Verification Policy -> P13.6 Live Compatibility -> Analysis / Graph -> Forecasting -> P15 Calibration / Performance -> Monitoring / Alerts -> P14 Owner Read Model -> P16 Delivery / Feedback -> P17 Public-Safe Publication Readiness`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Canonical Truth / Provenance Boundary

- publisher/publication is not automatically underlying origin;
- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements establish what was stated, not automatically the underlying event;
- source reputation, portfolio state, availability and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- graph inference cannot promote factual verification;
- forecast probability/confidence, Brier/calibration/performance metrics and drift/bias cannot promote factual verification;
- delivery state, receipts, operator feedback and quality metrics cannot promote factual verification;
- publication eligibility, receipts and engagement cannot promote factual verification;
- count-only verification promotion is forbidden;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- canonical factual verification authority remains P13.5/P13.6 only.

## Source / Governance Historical Baseline

Phase 12 remains validated with known limitations. Historical gates remain:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

Known retained observations include European Parliament `UNAVAILABLE / PARSER` with governed `DEGRADED`, Haberturk `UNAVAILABLE / UNKNOWN` in the P12.5 probe, OSCE acquisition `HEALTHY` with observed content `STALE`, and the initial `uk/ru/pl/tr` slice as not global language coverage. These are historical/operational observations, not truth operators.

## Semantic / Forecast / Delivery / Publication Layers

- Phase 13 adds structured semantic claims, provenance/origin relations, typed evidence/independence, contradictions and policy-controlled multidimensional verification.
- Phase 14 projects persisted owner intelligence read-only and remains `NOT_ACTIVATED`; `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
- Phase 15 adds provenance-bound forecast outcome, calibration and performance intelligence without changing factual truth authority.
- Phase 16 adds auditable delivery intents, redaction, provider-neutral local/test transport, receipts and operator quality feedback; no real provider is activated.
- Phase 17 adds deterministic publication eligibility, public-safe redaction/projection, release manifests/packages and a local/test target only. Real publication is `NOT_ACTIVATED` and current account publication capability is `UNAVAILABLE`.

## Runtime / Storage Boundary

- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- no direct cross-project canonical-store mutation;
- shared/team runtime requires a new architecture approval under Phase 18;
- owner-only OCI remains the validated runtime line;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Runtime storage mode: PROJECT_LOCAL_ONLY
Production/live operational status: NOT_OPERATIONAL

## Security / Exposure Boundary

- E9A remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- explicit historical candidate networking exceptions remain public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress;
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- public Action/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me remains non-canonical.

## Current State

- ROADMAP: `APPROVED / v4`, synchronization `4.22`;
- Phase 12–16 strategic engineering gates: validated as recorded above;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- Phase 18: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- owner operational activation: `OWNER_DECISION_REQUIRED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime: `BLOCKED`;
- production/live: `NOT_OPERATIONAL`.

## Current-State Addendum — Phase 18 A1 (2026-09-09)

The pre-Phase-18 architecture-position text above is retained verbatim as historical regression evidence. It is superseded for current interpretation by the approved Phase 18 architecture and the additive A1 preflight record.

- Phase 18 architecture: approved by owner; implementation authorized;
- P18.0–P18.9: validated through `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`;
- A1 live preflight gate: `PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`;
- exact implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- restricted `kgm_preflight_runtime` role is non-login, non-superuser and non-BYPASSRLS with transaction-local role switching;
- live RLS isolation accepted with `rls_isolation_observed=true` and `alternate_tenant_visible_rows=0`;
- Railway API candidate deployed successfully; PostgreSQL remains private-only with no public TCP proxy;
- A1 is disposable non-production preflight, not canonical shared runtime;
- machine-readable strategic state deliberately remains at synchronization `4.34` / `PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE` until a formal activation synchronization gate;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- `PAID_PROVIDERS = NONE_APPROVED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.
