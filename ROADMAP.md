# ROADMAP

Version: 4.7
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
- media/domain/language/adapter/item/host count is not independent-origin count;
- operational source health and content freshness are not truth operators;
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
State: `VALIDATED_WITH_KNOWN_LIMITATIONS`
Gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`
Decision: `PASS_WITH_KNOWN_LIMITATIONS`
Validation matrix: `docs/implementation/P12_6_PHASE_12_VALIDATION_MATRIX.md`
Result: `docs/implementation/P12_6_PHASE_12_VALIDATION_MATRIX_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_6_PHASE_12_VALIDATED.md`
Validation anchor: `c6aca6a2fe3c0dc991b267efa82c5748bd6460e2`.

Phase 12 validation evidence:
- x64 run `33546794411`, job `99986187419`: `391 passed, 1 warning / SUCCESS`;
- native ARM64 run `33546794273`, job `99986186748`: native `aarch64`, `391 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

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

Governed P12.3 portfolio states remain:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED`;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

European Parliament remains degraded because its official endpoint returns non-feed/anti-bot content to unattended acquisition. No bypass or third-party canonical mirror is authorized. P12.5 later measured OSCE acquisition as healthy while observed publisher content was stale; this does not silently rewrite governance.

### P12.4 — Local-Language and Media Discovery Pack
State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

Governed first language slice remains:
- Ukrainian `uk` — Ukrainska Pravda — `ACTIVE`;
- Russian `ru` — Meduza — `ACTIVE`;
- Polish `pl` — RMF24 — `ACTIVE`;
- Turkish `tr` — Haberturk — `ACTIVE`.

P12.5 later measured one Haberturk item-URL validation failure and recorded the path `UNAVAILABLE` for that probe. The discrepancy is preserved for explicit remediation instead of silently rewriting governance. `uk/ru/pl/tr` is a prioritized initial slice, not global language coverage; translation remains derived.

### P12.5 — Source Health, Freshness and Egress Inventory
State: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`
Validation anchor: `92d0c0516351e2af7ba836d3ae711dd414d22023`.

Validation evidence:
- x64 run `33533313297`, job `99941475948`: `382 passed, 1 warning / SUCCESS`;
- native ARM64 run `33533313313`, job `99941475266`: `382 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live run `33533313654`, job `99941475574`: `10/10` source paths measured, `8 SUCCESS / 2 FAILED`.

Measured findings retained:
- European Parliament — governed `DEGRADED`, measured `UNAVAILABLE / PARSER`;
- Haberturk — governed `ACTIVE`, measured `UNAVAILABLE / UNKNOWN`;
- OSCE — acquisition `HEALTHY`, observed content `STALE`.

Ten required HTTPS hosts were inventoried. No outbound allowlist was deployed; broad outbound egress remains an explicit owner-approved candidate exception.

### P12.6 — Phase 12 Validation Matrix
State: `VALIDATED`
Gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`
Decision: `PASS_WITH_KNOWN_LIMITATIONS`
Validation anchor: `c6aca6a2fe3c0dc991b267efa82c5748bd6460e2`.

P12.6 reconciles P12.0-P12.5 evidence and explicitly retains external-source degradation/staleness, portfolio-vs-observation differences, limited language scope, security exceptions and production/runtime boundaries. It does not convert source availability into truth, coverage completeness or production acceptance.

## Phase 13 — Semantic Verification and Provenance Intelligence
State: `NEXT / NOT_STARTED`
Current activity: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE / NEXT_NOT_STARTED`
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
- state synchronization: `v4.7`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- P12.0-P12.6: validated;
- current/next engineering activity: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE / NEXT_NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: `BLOCKED`;
- production/live operational status: `NOT_OPERATIONAL`;
- private GPT Action: `NOT_CONNECTED`;
- backend HTTPS: `NOT_DEPLOYED`;
- admin dashboard: `NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`.

Next phase gate to evaluate:
`PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
