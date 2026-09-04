# K-Geopolitical Monitor
Global geopolitical monitoring and intelligence platform.

Version: 4.13
Status: ACTIVE / ROADMAP_V4 / PHASE_13_ACTIVE / P13.4_VALIDATED / P13.5_CURRENT

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
- `docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md` — active Phase 13 plan;
- `docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL_RESULT.md` — latest validated work-package result;
- `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED.md` — latest saved gate checkpoint.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- current engineering activity: `P13.5_VERIFICATION_POLICY_CONFIDENCE`;
- P13.5: `CURRENT / NOT_STARTED`;
- P13.6: `PLANNED / NOT_STARTED`;
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

- x64 run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `026_semantic_contradiction_model.sql` adds append-only typed contradiction versions and side-scoped links to current P13.3 evidence relation versions.

Validated contradiction dimensions include occurrence/existence, attribution/responsibility, actor identity, quantity/value, time, location, status/outcome, scope/extent and explicitly modeled causal interpretation.

Lifecycle is `DETECTED`, `UNRESOLVED`, `EVOLVING`, `RESOLVED`. Resolution requires explicit reconciliation metadata and preserves historical disagreement. It **does not automatically determine which semantic claim is factually true**. P13.3 `CONTRADICTS`, source reputation, official status or independence metadata cannot automatically create a truth decision.

Legacy `src/kgeopolitical_monitor/contradictions.py` remains compatibility state.

## P13.5 Current Package

`P13.5_VERIFICATION_POLICY_CONFIDENCE / CURRENT_NOT_STARTED`.
Expected gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

P13.5 must implement a policy-controlled, auditable verification decision layer and multidimensional confidence without reverting to historical shortcuts such as evidence count, distinct hosts/domains, publisher count, language count, official status or source reputation as sufficient truth rules.

Required confidence dimensions remain inspectable before any presentation scalar, including evidence sufficiency, provenance/independence confidence, proposition-specific authority/proximity, contradiction severity, temporal freshness, extraction/translation uncertainty and coverage limitation.

Coverage confidence remains separate and cannot promote factual verification confidence. P13.5 must not perform the P13.6 live analytical cutover.

## Truth / Epistemic Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status proves the source made a statement, not automatically the underlying event claim;
- source reputation/status, portfolio metadata, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
- contradiction resolution is analytical reconciliation, not automatic truth selection;
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
- Phase 13 — `APPROVED / ACTIVE_ENGINEERING_PHASE`; P13.0-P13.4 validated, P13.5 current/not started.
- Phase 14 — approved sequential / not started.
- Phase 15 — approved sequential / not started.
- Phase 16 — approved sequential / not started.
- Phase 17 — conditional / not activated.
- Phase 18 — conditional / new architecture approval required.

No production launch, public sharing, public backend exposure, shared runtime transition or paid-provider activation is implied by Phase 13 engineering work.