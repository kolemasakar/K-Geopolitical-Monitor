# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.15
Status: ACTIVE / ROADMAP_V4 / PHASE_13_CLOSURE_CANDIDATE / P13.6_IMPLEMENTATION_VALIDATED

## Purpose

K-Geopolitical Monitor supports discovery, provenance-aware verification, geopolitical analysis, forecasting, reporting, operational monitoring and explicit coverage assessment of significant developments.

## Canonical Documentation

- `ROADMAP.md` — ROADMAP v4 and current phase state;
- `ARCHITECTURE.md` — architecture/truth/storage/runtime boundaries;
- `SECURITY_AND_DATA_POLICY.md` — security/data policy;
- `EXTERNAL_INTEGRATIONS.md` — integration/source rules;
- `SOURCE_POLICY.md` — source/provenance governance;
- `DATA_MODELS.md` — canonical data-model summary;
- `PROJECT_HISTORY.md` — chronological project record;
- `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md` — Phase 13 implementation/closure plan;
- `docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md` — P13.6/Phase-13 validation matrix;
- `docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_RESULT.md` — P13.6 validated implementation result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_P13_6_IMPLEMENTATION_VALIDATED.md` — P13.6 saved evidence checkpoint.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `CLOSURE_CANDIDATE / AWAITING_EXACT_HEAD_REGRESSION`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- P13.5: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`;
- P13.6: `IMPLEMENTATION_VALIDATED / CLOSURE_CANDIDATE`;
- current engineering activity: `PHASE_13_CANONICAL_CLOSURE_VALIDATION`;
- strategic Phase-13 gate: `PENDING_EXACT_HEAD_CLOSURE_REGRESSION`;
- Phase 14: `APPROVED_SEQUENTIAL / NOT_STARTED`;
- operational activation: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

## Phase 13 Validated Packages

### P13.0 — Architecture Contract
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.

Semantic claim identity is not headline identity; provenance, evidence relation, independence, contradiction and verification policy are distinct layers. Count-based host/domain/source/language shortcuts cannot become canonical truth rules.

### P13.1 — Structured Semantic Claims
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

Migration `023_structured_semantic_claim_model.sql` provides append-only structured semantic claim versions and non-evidentiary links to legacy/live/raw objects. Extraction confidence remains extraction-only.

### P13.2 — Provenance / Underlying Origin
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.

Migration `024_semantic_provenance_origin_relation_model.sql` separates publication/publisher, immediate source, cited/quoted source and underlying origin. Citation/syndication/repost/translation/derivation do not create independent corroboration.

### P13.3 — Evidence Relation / Independence
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Implementation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`.
Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.

Final closure validation:
- x64 run `33594299961`, job `100134512548`: `438 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594299979`, job `100134512479`: native `aarch64`, `438 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `025_semantic_evidence_relation_independence.sql` provides typed evidence relations and explicit pairwise independence states. Different publisher/source/host/domain/language is never sufficient proof of independence; absent known derivation remains `UNKNOWN` rather than automatically independent.

### P13.4 — Typed Contradictions
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.
Formal closure repair HEAD: `f771ce0154e24b2218b309d8b3e6b880b408a146`.

Implementation validation:
- x64 `33594740585 / 100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 `33594740549 / 100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure validation:
- x64 `33848458616 / 100945599309`: `463 passed, 2 warnings / SUCCESS`;
- native ARM64 `33848458681 / 100945599390`: native `aarch64`, `463 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `026_semantic_contradiction_model.sql` adds append-only typed contradiction versions and side-scoped links to current P13.3 evidence relation versions. Reconciliation does not automatically determine which semantic claim is factually true. Legacy `src/kgeopolitical_monitor/contradictions.py` remains compatibility state.

### P13.5 — Verification Policy / Multidimensional Confidence
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.
Validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.

Implementation validation:
- x64 run `33849149736`, job `100947736040`: `475 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33849149742`, job `100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure HEAD: `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`.
Formal closure validation:
- x64 run `33856550956`, job `100971101911`: `480 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33856550913`, job `100971101835`: native `aarch64`, `480 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `027_semantic_verification_policy_confidence.sql` adds append-only policy versions, multidimensional factual-confidence versions and auditable decision versions.

Canonical rules reject historical shortcuts as sufficient truth rules:
- evidence/source/domain/host/publisher/language count alone cannot promote verification;
- official status and source reputation alone cannot establish substantive event truth;
- coverage limitation/confidence cannot promote factual verification;
- `VERIFIED` requires an explicit current `INDEPENDENT` pair of current `SUPPORTS` evidence, policy confidence floors, no current `CONTRADICTS` evidence and no active contradiction;
- factual confidence is multidimensional and stores no canonical presentation scalar;
- global-latest semantic snapshots prevent superseded evidence/independence/contradiction records from acting as current inputs.

Legacy `verification.py` and `confidence_engine.py` remain readable compatibility APIs. Their historical count/scalar behavior is not imported into the canonical P13.5 service.

### P13.6 — Live Compatibility Cutover / Validation Matrix

Package: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`.
State: `IMPLEMENTATION_VALIDATED / CLOSURE_CANDIDATE`.
Implementation / validation anchor: `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4`.
Evidence-save HEAD: `2a482eb85b118fa5ea46396fa92707733dad5159`.

Implementation validation:
- x64 run `33857212159`, job `100973174656`: `489 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857212157`, job `100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Evidence-save validation:
- x64 run `33857629735`, job `100974493101`: `493 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33857629714`, job `100974493074`: native `aarch64`, `493 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.6 implements a read-only semantic/live projection with no migration 028. Explicit P13.1 `LIVE_ANALYSIS_CLAIM` links are the only bridge; current P13.5 decisions are the only semantic verification source. Historical `origin_host`, `independent_origin_count`, legacy status and scalar confidence remain compatibility metadata and cannot silently become canonical semantic truth or independence. Missing E6 instrumentation remains `NOT_INSTRUMENTED`; exact history is never reconstructed.

The strategic Phase-13 gate remains pending until this synchronized closure candidate passes exact-head x64 and native ARM64 regression.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status, portfolio metadata, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
- contradiction resolution is analytical reconciliation, not automatic truth selection;
- count-only verification promotion is forbidden in the canonical semantic path;
- graph inference is analytical context, not source evidence;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- missing/uninstrumented tool history is never reconstructed and labeled exact;
- public-web research is not a substitute for unavailable persisted backend/runtime state.

## Runtime / Security State

- owner-only OCI Ubuntu 24.04 ARM64 runtime remains candidate-ready;
- public KGM HTTP/HTTPS/database/API/dashboard ingress: not approved/not deployed;
- backend HTTPS: not deployed;
- private GPT backend Action: not connected;
- dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public GPT sharing: user-deferred;
- production/live: not operational;
- paid providers: `NONE_APPROVED`.

Remaining explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

## ROADMAP v4

- Phase 12 — validated with known limitations.
- Phase 13 — `CLOSURE_CANDIDATE / AWAITING_EXACT_HEAD_REGRESSION`.
- Phase 14 — `APPROVED_SEQUENTIAL / NOT_STARTED`; operational activation requires `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, public sharing, public backend exposure, shared runtime transition or paid-provider activation is implied by Phase 13 closure engineering.
