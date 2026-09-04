# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.13
Status: ACTIVE / PHASE_13_VALIDATED / PHASE_14_NOT_STARTED

## Validated Historical Baseline

Phases 0-11, owner-only private GPT pilot, E1-E7 and E9A remain validated as recorded in prior project checkpoints. E8 remains user-deferred and E9 shared production runtime remains not approved.

E9A final state remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`; `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — Phase 12

ROADMAP v4 owner-approved the sequential intelligence-quality/source-expansion/owner-value development line. Phase 12 closed at `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`.

Final Phase-12 closure HEAD `3211994450c11698a553f5249e3ecec94079b5ad`:
- x64 `33552777066 / 100006077954`: `391 passed, 1 warning / SUCCESS`;
- ARM64 `33552776997 / 100006077747`: native `aarch64`, `391 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P12.0-P12.6 gates remain historical validated state, including explicit European Parliament/Haberturk/OSCE source limitations and the non-global `uk/ru/pl/tr` initial local-language slice.

## 2026-09-01 — P13.0 Semantic Verification Architecture Contract

Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Validation anchor `4422fae5e2a4546585a43237d2124f466c457543`:
- x64 `33554568574 / 100012110127`: `399 passed, 1 warning / SUCCESS`;
- ARM64 `33554568570 / 100012110488`: native `aarch64`, `399 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.0 established structured semantic identity, explicit provenance, typed evidence, explicit independence, typed contradiction and policy-controlled verification as separate layers. Count-based domain/host shortcuts cannot become canonical truth rules.

## 2026-09-01 — P13.1 Structured Semantic Claim Model

Implementation/validation anchor `69c3282077ad8dd90ef239c0594be56f9363bfe5`:
- migration `023_structured_semantic_claim_model.sql`;
- append-only semantic claims and links;
- x64 `33555804493 / 100016206225`: `408 passed, 1 warning / SUCCESS`;
- ARM64 `33555804396 / 100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Extraction confidence remained separate from factual confidence. Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.

## 2026-09-02 — P13.2 Provenance / Underlying-Origin Relation Model

Implementation/validation anchor `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`:
- migration `024_semantic_provenance_origin_relation_model.sql`;
- explicit publication/publisher, immediate/cited/quoted source and underlying-origin concepts;
- x64 `33558425194 / 100024835794`: `420 passed, 1 warning / SUCCESS`;
- ARM64 `33558425252 / 100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Citation, syndication, repost, translation and derivation remained provenance relationships, not independent corroboration. Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

## 2026-09-02 — P13.3 Evidence Relation and Independence Assessment

Implementation anchor `639d6b2e64d618edfbe742636cb2ac0f663c68ee` added migration `025_semantic_evidence_relation_independence.sql`, typed evidence relations and explicit pairwise independence assessments.

Formal closure HEAD `9023dc22d36525b4dc9babbf21d97d184a1c110e`:
- x64 `33594299961 / 100134512548`: `438 passed, 1 warning / SUCCESS`;
- ARM64 `33594299979 / 100134512479`: native `aarch64`, `438 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Different publisher/source/host/domain/language never suffices for independence; absent derivation remains `UNKNOWN`, not automatically independent. Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.

## 2026-09-04 — P13.4 Typed Contradiction Model and Resolution Lifecycle

Implementation/validation anchor `d4dbb8a8098cef960194935bd94d4640fd719050` added migration `026_semantic_contradiction_model.sql`.

Formal closure repair HEAD `f771ce0154e24b2218b309d8b3e6b880b408a146`:
- x64 `33848458616 / 100945599309`: `463 passed, 2 warnings / SUCCESS`;
- ARM64 `33848458681 / 100945599390`: native `aarch64`, `463 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Contradiction lifecycle preserves disagreement history; resolution requires explicit reconciliation metadata and does not automatically select a factual winner. Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.

## 2026-09-04 — P13.5 Verification Policy Engine and Multidimensional Confidence

Implementation/validation anchor `0f0d746c538dc5ce8f010fb80f8afbe00685414a` added migration `027_semantic_verification_policy_confidence.sql`, versioned verification policies, multidimensional factual-confidence profiles and append-only auditable semantic verification decisions.

Implementation validation:
- x64 `33849149736 / 100947736040`: `475 passed, 2 warnings / SUCCESS`;
- ARM64 `33849149742 / 100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure HEAD `d2e80fe8a1bd998ca422be1e1001744be0e9e6e3`:
- x64 `33856550956 / 100971101911`: `480 passed, 2 warnings / SUCCESS`;
- ARM64 `33856550913 / 100971101835`: native `aarch64`, `480 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated policy semantics:
- count-only evidence/source/domain/host/publisher/language promotion is forbidden;
- official status, source reputation and coverage metadata are not standalone truth operators;
- `VERIFIED` requires an explicit current independent pair of current `SUPPORTS` evidence plus policy confidence floors;
- current `CONTRADICTS` evidence or active P13.4 contradiction blocks `VERIFIED`;
- factual confidence remains multidimensional and stores no canonical scalar;
- coverage limitation remains separate and non-promotional;
- legacy `verification.py` and `confidence_engine.py` remain readable compatibility APIs and are not the canonical P13.5 engine.

Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

## 2026-09-04 — P13.6 Live Compatibility Cutover and Validation Matrix

Implementation anchor `3b8d75d05168561898ba3fa592d0d7bdad5a5dd4` added read-only `semantic_live_compatibility.py`. No migration 028 was introduced.

Implementation validation:
- x64 `33857212159 / 100973174656`: `489 passed, 2 warnings / SUCCESS`;
- ARM64 `33857212157 / 100973174256`: native `aarch64`, `489 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Evidence-save HEAD `2a482eb85b118fa5ea46396fa92707733dad5159`:
- x64 `33857629735 / 100974493101`: `493 passed, 2 warnings / SUCCESS`;
- ARM64 `33857629714 / 100974493074`: native `aarch64`, `493 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.6 validated a non-destructive bridge from explicit P13.1 `LIVE_ANALYSIS_CLAIM` links to current P13.5 semantic decisions. Legacy `PARTLY_VERIFIED`, scalar confidence, URL-host counts and `independent_origin_count` remain historical compatibility metadata. Stale/ambiguous links fail closed. E6 reproducibility metadata appears only when actually persisted; `NOT_INSTRUMENTED` history is never reconstructed. Legacy and semantic rows are not rewritten by the projection.

## 2026-09-04 — Phase 13 Strategic Closure

Strategic closure validation anchor: `7e49f790a36f596cdb8ed3d7d6e17f5ace2787be`.
Validation:
- x64 `33861302915 / 100986128743`: `497 passed, 2 warnings / SUCCESS`;
- ARM64 `33861302926 / 100986128780`: native `aarch64`, `497 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Gate granted: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.

The closure preserves all Phase-13 permanent boundaries, retains migration 028 as `NONE`, and does not activate production/live or Phase 14.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- P13.5: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`;
- P13.6: `VALIDATED`;
- Phase 14: `APPROVED_SEQUENTIAL / NOT_STARTED`;
- operational activation: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- broad outbound egress: retained explicit owner-approved candidate exception;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY
