# Phase 13 — Semantic Verification and Provenance Intelligence

Date: 2026-09-02
Status: `ACTIVE_ENGINEERING_PHASE / P13.0-P13.4_VALIDATED / P13.5_CURRENT`
Project: K-Geopolitical Monitor
Strategic phase gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Current activity: `P13.5_VERIFICATION_POLICY_CONFIDENCE`

## Objective

Replace historical title/domain-count analytical shortcuts with a structured, provenance-bound and policy-controlled semantic verification layer while preserving backward compatibility with the validated Phase 12 acquisition/runtime stack.

Phase 13 improves analytical depth. It does not activate production/live operation, public ingress, shared runtime, paid providers or autonomous truth promotion.

## Audited Compatibility Baseline

The existing baseline remains historical compatibility state until P13.6:
- `claims` / `evidence` from migration 002 are minimal legacy objects;
- `live_analysis_claims` / `live_analysis_evidence` group evidence by normalized headline and store `origin_host` / `independent_origin_count`;
- historical `verification.py` uses an evidence-count threshold;
- historical live analysis uses distinct origin hosts for `PARTLY_VERIFIED` behavior;
- historical confidence derives an independence term from source-ID count;
- legacy `contradictions.py` is a small compatibility container.

These behaviors remain readable; they are not the canonical semantic rules for the additive Phase 13 layer.

## P13.0 Architecture Contract — VALIDATED

Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Validation anchor: `4422fae5e2a4546585a43237d2124f466c457543`.

P13.0 creates **no database migration**. Phase 13 uses additive migrations only unless a later explicit architecture decision authorizes otherwise.

Existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` remain readable. New semantic objects must link to legacy/live objects rather than silently overwrite their historical meaning.

### Semantic claim identity

A semantic claim is not identified solely by a headline or normalized headline. One publication may contain multiple claims. Equivalent wording is not required for equivalent propositions, and similar wording may represent materially different propositions.

### Provenance / underlying-origin contract

The model distinguishes:
- publisher / publication;
- immediate acquired source;
- cited or quoted source;
- asserted underlying origin;
- official statement / document origin;
- wire/syndication origin;
- dataset/structured-data origin;
- social/user-provided origin;
- translation/repost/syndication/citation derivation;
- unresolved or mixed origin.

Publisher/domain identity is not automatically underlying-origin identity. Unknown origin remains explicit rather than inferred from hostname, language or publisher difference.

### Evidence relation contract

Typed evidence relation vocabulary includes:
- `SUPPORTS`;
- `CONTRADICTS`;
- `QUALIFIES`;
- `CONTEXT_ONLY`;
- `ATTRIBUTION_ONLY`;
- `DUPLICATE_OR_SAME_ORIGIN`.

Evidence relation does not itself determine final verification state.

### Independence contract

Independence states are `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`.

Unknown independence cannot be promoted to independent to satisfy a verification threshold. Different source, host, domain, publisher or language is not sufficient proof of independence.

### Contradiction contract

Typed contradiction dimensions include occurrence/existence, attribution/responsibility, actor identity, quantity/value, time, location, status/outcome, scope/extent and explicitly modeled causal interpretation.

Contradiction state must preserve unresolved/evolving/resolved history. A claim/denial pair is not automatically resolved by source reputation alone.

### Verification decision contract

Canonical semantic verification promotion must be policy-controlled and auditable.

The new engine must not promote a claim solely because:
- evidence count is `>= 2`;
- two domains/hosts are different;
- two publishers are different;
- the same statement appears in multiple languages;
- an item is official, fresh, highly reputable or successfully parsed;
- an independence assessment exists;
- a contradiction object is reconciled;
- a graph or forecast model assigns high probability.

### Confidence contract

Semantic extraction confidence is not factual verification confidence. Coverage confidence remains separate and cannot promote factual verification confidence. Model output may propose structured objects; policy validates and records them.

## P13.1 Structured Semantic Claim Model — VALIDATED

Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

Migration `023_structured_semantic_claim_model.sql` introduced append-only `semantic_claim_versions` and `semantic_claim_links`, explicit caller-controlled semantic identity, structured proposition dimensions and non-evidentiary links to legacy/live/raw state.

## P13.2 Provenance / Underlying-Origin Relation Model — VALIDATED

Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.

Migration `024_semantic_provenance_origin_relation_model.sql` introduced append-only provenance entities, semantic-claim provenance roles and provenance relations. Citation/syndication/repost/translation/derivation do not create independent corroboration.

## P13.3 Evidence Relation and Independence Assessment — VALIDATED

Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Implementation anchor: `639d6b2e64d618edfbe742636cb2ac0f663c68ee`.
Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.

Formal closure evidence:
- x64 run `33594299961`, job `100134512548`: `438 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594299979`, job `100134512479`: native `aarch64`, `438 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `025_semantic_evidence_relation_independence.sql` introduced append-only typed evidence relations and explicit pairwise independence assessments. Fail-closed inference does not infer `INDEPENDENT` merely from absence of a known derivation path.

## P13.4 Typed Contradiction Model and Resolution Lifecycle — VALIDATED

Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.

Validation evidence:
- x64 run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `026_semantic_contradiction_model.sql` introduced append-only:
- `semantic_contradiction_versions`;
- `semantic_contradiction_evidence_links`.

Validated behavior:
- contradiction identity binds two immutable semantic claim versions plus a typed dimension;
- identity drift across claim versions or dimensions fails closed;
- lifecycle is `DETECTED`, `UNRESOLVED`, `EVOLVING`, `RESOLVED` with preserved historical disagreement;
- resolution requires explicit reconciliation metadata but does not select a factual winner;
- evidence links are side-scoped and require current P13.3 evidence relation versions at link time;
- P13.3 `CONTRADICTS` does not automatically create or resolve a P13.4 contradiction;
- legacy `contradictions.py` remains compatibility state.

P13.4 intentionally contains no canonical verification promotion, factual confidence or coverage confidence.

## P13.5 Current Work Package — Verification Policy Engine and Multidimensional Confidence

State: `CURRENT / NOT_STARTED`.
Expected gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

P13.5 is responsible for a policy-controlled, versioned and auditable verification decision layer over P13.1-P13.4 semantic state.

Required scope:
- preserve compatibility verification vocabulary unless an explicit migration changes it: `DETECTED`, `PARTLY_VERIFIED`, `VERIFIED`, `DISPUTED`, `UNVERIFIABLE`;
- define explicit policy versions and decision records rather than hidden threshold logic;
- consume typed evidence relations, explicit independence assessments and contradiction lifecycle state without treating any single metadata field as sufficient truth proof;
- expose inspectable multidimensional confidence before any optional presentation scalar;
- keep extraction confidence and translation uncertainty separate from factual confidence;
- keep coverage limitation/confidence separate and non-promotional;
- retain proposition-specific source authority/proximity as context rather than global source truth score;
- fail closed when provenance/independence or contradiction state is unresolved;
- make every verification promotion/demotion auditable and reproducible from stored policy inputs.

Minimum confidence dimensions to model explicitly:
- evidence sufficiency;
- provenance/independence confidence;
- proposition-specific source authority/proximity;
- source reliability context;
- contradiction severity/resolution state;
- temporal freshness;
- extraction uncertainty;
- translation uncertainty;
- claim-specific uncertainty;
- coverage limitation.

P13.5 must not:
- use `>=2` evidence/domains/hosts as a sufficient promotion rule;
- equate different publishers or languages with independence;
- let official status or source reputation alone establish event truth;
- let graph inference or forecast probability promote verification;
- let coverage confidence promote factual confidence;
- perform the P13.6 live compatibility cutover.

## Internal Phase 13 Sequencing

- `P13.0` — architecture contract — **VALIDATED**;
- `P13.1` — structured semantic claims — **VALIDATED**;
- `P13.2` — provenance / underlying origin — **VALIDATED**;
- `P13.3` — evidence relation / independence — **VALIDATED**;
- `P13.4` — typed contradiction lifecycle — **VALIDATED**;
- `P13.5` — verification policy / multidimensional confidence — **CURRENT / NOT_STARTED**;
- `P13.6` — live compatibility cutover, reproducibility and Phase 13 validation matrix — **PLANNED / NOT_STARTED**.

Each work package requires its own validation before the next package becomes current.

## Permanent Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statement establishes that an actor/institution made the statement, not automatically the substantive event claim;
- source reputation, portfolio approval, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
- contradiction reconciliation is not automatic truth selection;
- graph inference and forecast probability cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` remains scope, not proof of exhaustive coverage;
- unavailable persisted state is not replaced by ad hoc web research;
- reconstructed/uninstrumented tool history is never labeled exact.

## Runtime / Security Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Public KGM API/dashboard ingress remains not approved/deployed. Backend HTTPS remains not deployed. Private GPT backend Action remains not connected. Paid providers remain `NONE_APPROVED`. Public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress remain explicit owner-approved candidate exceptions.

## Current Gate

Next gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

P13.6 must not start before P13.5 is implemented, validated and saved.