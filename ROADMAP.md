# ROADMAP

Version: 4.5
Status: APPROVED
Project: K-Geopolitical Monitor
Strategic roadmap: v4
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Development analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## Development Principle

K-Geopolitical Monitor advances through explicit implementation and validation gates.

Implementation does not equal validation. Validation does not equal production/live operation. Publication does not equal production runtime maturity.

Strategic sequence:
`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

No M14 engineering label is created by ROADMAP v4.

## Permanent Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- an official statement establishes `actor said X`, not automatically `X happened`;
- source reputation and source-portfolio metadata are context/governance, not truth operators;
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- translation remains derived and creates no independent origin;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive global coverage;
- missing local-language evidence remains explicit;
- reconstructed/uninstrumented tool history is never labeled exact;
- unavailable persisted backend state is never replaced by ad hoc web research.

## Storage / Runtime Boundary

- runtime storage remains `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage remains blocked;
- no direct cross-project canonical-store mutation is allowed;
- owner-only OCI remains the validated runtime line;
- public KGM API/dashboard ingress remains not approved/deployed;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

# Validated Historical Development Line

Phases 0-11 remain validated baselines. Post-Phase-11 E1-E7 remain validated; E8 is user-deferred; E9A is `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`; E9 shared production runtime remains `NOT_APPROVED`.

E9A retains explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

# ROADMAP v4 Development Line

## Phase 12 — Intelligence Quality and Source Network Foundation
State: `APPROVED / ACTIVE_ENGINEERING_PHASE`

### P12.0 — Canonical Architecture / Security / Integration Convergence
State: `VALIDATED`
Gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`

### P12.1 — Source Portfolio Contract and Governance
State: `VALIDATED`
Gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

### P12.2 — Live Adapter Framework v2
State: `VALIDATED`
Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

### P12.3 — Priority Authoritative Source Pack
State: `VALIDATED_WITH_EXPLICIT_DEGRADATION`
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`
Result: `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md`
Controlled-live matrix: `docs/implementation/P12_3_CONTROLLED_LIVE_SOURCE_MATRIX.md`

Validated P12.3 source states remain:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` because the official endpoint returns anti-bot HTML to the unattended runner;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

The European Parliament official endpoint remains canonical; no anti-bot bypass or third-party canonical mirror substitution is authorized.

### P12.4 — Local-Language and Media Discovery Pack
State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`
Implementation: `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK.md`
Result: `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md`
Controlled-live matrix: `docs/implementation/P12_4_CONTROLLED_LIVE_LANGUAGE_SOURCE_MATRIX.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED.md`
Validation anchor: `595d7f0f0e6316e95aca518bb9309e615f239479`.
Validation: x64 run `33531518780`, job `99935566406`, `370 passed, 1 warning / SUCCESS`; native ARM64 run `33531518525`, job `99935564828`, real `aarch64`, `370 passed, 1 warning / SUCCESS` plus bootstrap/unattended/systemd PASS.
Controlled-live: run `33531518652`, job `99935565895`, `4 SUCCESS / 0 FAILED`.

Validated first language slice:
- Ukrainian `uk` — Ukrainska Pravda — `ACTIVE`;
- Russian `ru` — Meduza — `ACTIVE`;
- Polish `pl` — RMF24 — `ACTIVE`;
- Turkish `tr` — Haberturk — `ACTIVE`.

This is a prioritized initial slice, not global language coverage or continuous-uptime proof. Original-language text is preserved; translation remains a separate derived representation.

### P12.5 — Source Health, Freshness and Egress Inventory
State: `NEXT / NOT_STARTED`
Measure availability, freshness/staleness, adapter/parser errors, source drift and the actual outbound host/protocol inventory before any egress-restriction decision.
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

### P12.6 — Phase 12 Validation Matrix
State: `PLANNED`
Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## Phase 13 — Semantic Verification and Provenance Intelligence
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`

## Phase 14 — Owner Operational Intelligence Activation
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Required separate activation decision: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`

## Phase 15 — Forecast Calibration and Performance Intelligence
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

## Phase 16 — Delivery, Operator Experience and Quality Feedback
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`

## Phase 17 — Controlled External Publication Readiness
State: `CONDITIONAL / NOT_ACTIVATED`
Gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

## Phase 18 — Shared / Team Runtime
State: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`
Gate: `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`

# Current Implementation Checkpoint

- Strategic ROADMAP: `APPROVED / v4`;
- state synchronization: `v4.5`;
- P12.0: `VALIDATED`;
- P12.1: `VALIDATED`;
- P12.2: `VALIDATED`;
- P12.3: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.4: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- current/next engineering activity: `P12.5_SOURCE_HEALTH_EGRESS_INVENTORY / NEXT_NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: `BLOCKED`;
- production/live operational status: `NOT_OPERATIONAL`;
- private GPT Action: `NOT_CONNECTED`;
- backend HTTPS: `NOT_DEPLOYED`;
- admin dashboard: `NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`.

Next gate:
`P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`
