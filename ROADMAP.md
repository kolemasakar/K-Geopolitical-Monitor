# ROADMAP

Version: 4.16
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
- contradiction resolution is analytical reconciliation, not automatic factual truth selection;
- count-only verification promotion is forbidden in the canonical semantic path;
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

European Parliament remains explicitly degraded for unattended acquisition; no third-party canonical bypass was introduced.

### P12.4 — Local-Language and Media Discovery Pack
State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

Validated initial slice remains `uk/ru/pl/tr`; this is not global language coverage. Translation remains derived and publisher identity is not underlying-origin identity.

### P12.5 — Source Health, Freshness and Egress Inventory
State: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

European Parliament `UNAVAILABLE/PARSER`, Haberturk `UNAVAILABLE/UNKNOWN`, OSCE acquisition `HEALTHY` with observed content `STALE`, and ten measured HTTPS egress hosts remain explicit measured state, not truth or firewall policy.

### P12.6 — Phase 12 Validation Matrix
State: `VALIDATED`
Gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`
Decision: `PASS_WITH_KNOWN_LIMITATIONS`

P12.6 closed Phase 12 without converting source availability into truth, coverage completeness or production acceptance.

## Phase 13 — Semantic Verification and Provenance Intelligence
State: `VALIDATED`
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Strategic closure validation anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`.
Implementation plan: `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md`
Final strategic result: `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_RESULT.md`
Final checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED.md`

Strategic closure validation:
- x64 run `33861302915`, job `100986128743`: `497 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33861302926`, job `100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Phase 13 replaces analytical shortcuts with structured, provenance-bound, policy-controlled semantic verification while preserving backward compatibility with the validated Phase 12 acquisition/runtime stack.

### P13.0 — Semantic Verification Architecture Contract
State: `VALIDATED`
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `4422fae5e2a4546585a43237d2124f466c457543`.
- x64 run `33554568574`, job `100012110127`: `399 passed, 1 warning / SUCCESS`;
- native ARM64 run `33554568570`, job `100012110488`: native `aarch64`, `399 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated contract: semantic claim identity is not headline identity; provenance, evidence relation, independence, contradiction and verification decisions remain separate layers; `>=2` domains/hosts cannot be a sufficient canonical truth rule.

### P13.1 — Structured Semantic Claim Model
State: `VALIDATED`
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.
- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `023_structured_semantic_claim_model.sql` is additive; extraction confidence remains non-factual.

### P13.2 — Provenance / Underlying-Origin Relation Model
State: `VALIDATED`
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.
- x64 run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`;
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `024_semantic_provenance_origin_relation_model.sql` distinguishes publisher/publication, immediate source, cited/quoted source and underlying origin. Citation/syndication/repost/translation/derivation do not create independent corroboration.

### P13.3 — Evidence Relation and Independence Assessment
State: `VALIDATED`
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`
Validation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`.
Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.

Implementation validation:
- x64 run `33575533714`, job `100078564552`: `434 passed, 1 warning / SUCCESS`;
- native ARM64 run `33575533657`, job `100078564729`: native `aarch64`, `434 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure validation:
- x64 run `33594299961`, job `100134512548`: `438 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594299979`, job `100134512479`: native `aarch64`, `438 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `025_semantic_evidence_relation_independence.sql` is append-only. Different publisher/source/host/domain/language never suffices for independence; absent derivation remains `UNKNOWN`, not automatically independent.

### P13.4 — Typed Contradiction Model and Resolution Lifecycle
State: `VALIDATED`
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.
Formal closure repair HEAD: `f771ce0154e24b2218b309d8b3e6b880b408a146`.

Implementation validation:
- x64 run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure validation:
- x64 run `33848458616`, job `100945599309`: `463 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33848458681`, job `100945599390`: native `aarch64`, `463 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `026_semantic_contradiction_model.sql` is additive and append-only. Contradiction resolution preserves disagreement history and does not select a factual winner.

### P13.5 — Verification Policy Engine and Multidimensional Confidence
State: `VALIDATED`
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`
Result: `docs/implementation/P13_5_VERIFICATION_POLICY_CONFIDENCE_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED.md`
Validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.

Implementation validation:
- x64 run `33849149736`, job `100947736040`: `475 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33849149742`, job `100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure HEAD: `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`.
Formal closure validation:
- x64 run `33856550956`, job `100971101911`: `480 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33856550913`, job `100971101835`: native `aarch64`, `480 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated model:
- migration `027_semantic_verification_policy_confidence.sql` adds append-only policy, multidimensional factual-confidence and decision histories;
- count-only, official-status-only, source-reputation-only and coverage-only promotion are explicitly forbidden;
- `VERIFIED` requires an explicit current independent `SUPPORTS` pair, confidence floors, no current `CONTRADICTS` evidence and no active P13.4 contradiction;
- confidence remains multidimensional; no canonical factual-confidence scalar is stored;
- coverage limitation remains separate and non-promotional;
- global-latest semantic snapshots prevent superseded evidence/independence/contradiction state from acting as current input;
- legacy count/scalar APIs remain readable compatibility state and are not the canonical policy engine.

### P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix
State: `VALIDATED`
Gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`.
Evidence-save HEAD: `2a482eb85b118fa5ea46396fa92707733dad5159`.
Closure-candidate HEAD: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`.

Implementation validation:
- x64 run `33857212159`, job `100973174656`: `489 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857212157`, job `100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Evidence-save validation:
- x64 run `33857629735`, job `100974493101`: `493 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857629714`, job `100974493074`: native `aarch64`, `493 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Strategic closure validation:
- x64 run `33861302915`, job `100986128743`: `497 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33861302926`, job `100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated compatibility behavior:
- `semantic_live_compatibility.py` is a read-only projection; migration 028 is `NONE`;
- explicit P13.1 `LIVE_ANALYSIS_CLAIM` links are the semantic/live bridge;
- only an unambiguous current P13.5 decision supplies semantic verification state;
- historical `origin_host`, distinct-host counts, `independent_origin_count`, legacy verification status and scalar confidence remain compatibility metadata and never become semantic independence/truth by fallback;
- stale and ambiguous current links fail closed;
- E6 reproducibility metadata is exposed only when persisted; uninstrumented history remains `NOT_INSTRUMENTED` and is not reconstructed;
- legacy and semantic rows remain readable and are not rewritten by the projection.

## Phase 14 — Owner Operational Intelligence Activation
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Required separate activation decision: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`

Phase 13 closure does not activate Phase 14, production/live, public ingress, shared runtime or paid providers.

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
- state synchronization: `v4.16`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- P13.5: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`;
- P13.6: `VALIDATED`;
- Phase 14: `APPROVED_SEQUENTIAL / NOT_STARTED / OWNER_DECISION_REQUIRED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared runtime storage: `BLOCKED`;
- production/live operational status: `NOT_OPERATIONAL`;
- private GPT Action: `NOT_CONNECTED`;
- backend HTTPS: `NOT_DEPLOYED`;
- admin dashboard: `NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- paid providers: `NONE_APPROVED`.

Next implementation gate is not activated automatically. Phase 14 requires the separate owner decision `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
