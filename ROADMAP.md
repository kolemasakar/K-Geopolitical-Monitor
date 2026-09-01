# ROADMAP

Version: 4.8
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
- semantic extraction confidence is not factual verification confidence;
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
Final closure HEAD: `3211994450c11698a553f5249e3ecec94079b5ad`.

Final closure validation:
- x64 run `33552777066`, job `100006077954`: `391 passed, 1 warning / SUCCESS`;
- native ARM64 run `33552776997`, job `100006077747`: native `aarch64`, `391 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

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

European Commission, European Parliament, GOV.UK and OSCE governance remains canonical. European Parliament remains explicitly degraded for unattended acquisition; OSCE's later stale-content observation remains separate from acquisition health.

### P12.4 — Local-Language and Media Discovery Pack
State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

Validated initial slice remains `uk/ru/pl/tr`; this is not global language coverage. Translation remains derived and publisher identity is not underlying-origin identity.

### P12.5 — Source Health, Freshness and Egress Inventory
State: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

P12.5 retained European Parliament `UNAVAILABLE/PARSER`, Haberturk `UNAVAILABLE/UNKNOWN`, OSCE acquisition `HEALTHY` with observed content `STALE`, and ten measured HTTPS egress hosts without deploying an allowlist.

### P12.6 — Phase 12 Validation Matrix
State: `VALIDATED`
Gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`
Decision: `PASS_WITH_KNOWN_LIMITATIONS`

P12.6 reconciles P12.0-P12.5 evidence and explicitly retains external-source degradation/staleness, limited language scope, security exceptions and production/runtime boundaries. It does not convert source availability into truth, coverage completeness or production acceptance.

## Phase 13 — Semantic Verification and Provenance Intelligence
State: `APPROVED / ACTIVE_ENGINEERING_PHASE`
Current activity: `P13.0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT`
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Implementation plan: `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md`

Phase 13 replaces analytical shortcuts with structured, provenance-bound, policy-controlled semantic verification while preserving backward compatibility with the validated Phase 12 acquisition/runtime stack.

The P13.x labels below are internal implementation work packages derived from the approved Phase 13 architecture. They do not change strategic roadmap numbering.

### P13.0 — Semantic Verification Architecture Contract
State: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`

Required contract:
- semantic claim identity is not normalized-headline identity;
- provenance distinguishes publisher/publication, cited source and underlying origin;
- typed evidence relations are separate from final verification decisions;
- semantic independence is explicit and cannot be inferred from domain/source/language count;
- contradiction reasoning becomes typed and versionable;
- verification promotion is policy-controlled and cannot use `>=2 domains/hosts` as a sufficient rule;
- extraction confidence, factual confidence and coverage confidence remain separate;
- legacy `claims/evidence/live_analysis_*` remain readable and are not destructively rewritten.

P13.0 creates no database migration. The first additive semantic schema begins only after this contract is validated.

### P13.1 — Structured Semantic Claim Model
State: `PLANNED / NOT_STARTED`
Expected gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`

### P13.2 — Provenance / Underlying-Origin Relation Model
State: `PLANNED / NOT_STARTED`
Expected gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`

### P13.3 — Evidence Relation and Independence Assessment
State: `PLANNED / NOT_STARTED`
Expected gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`

### P13.4 — Typed Contradiction Model and Resolution Lifecycle
State: `PLANNED / NOT_STARTED`
Expected gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`

### P13.5 — Verification Policy Engine and Multidimensional Confidence
State: `PLANNED / NOT_STARTED`
Expected gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`

### P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix
State: `PLANNED / NOT_STARTED`
Expected gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`

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
- state synchronization: `v4.8`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- P12.0-P12.6 validated gates remain canonical;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- current engineering activity: `P13.0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT`;
- P13.1-P13.6: planned / not started;
- Phase 14+: not started;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: `BLOCKED`;
- production/live operational status: `NOT_OPERATIONAL`;
- private GPT Action: `NOT_CONNECTED`;
- backend HTTPS: `NOT_DEPLOYED`;
- admin dashboard: `NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`.

Next implementation gate to evaluate:
`P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`
