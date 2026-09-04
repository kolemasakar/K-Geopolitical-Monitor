# Phase 13 — Semantic Verification and Provenance Intelligence

Date: 2026-09-04
Status: `ACTIVE_ENGINEERING_PHASE / P13.0-P13.5_VALIDATED / P13.6_CURRENT`
Project: K-Geopolitical Monitor
Strategic phase gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Current activity: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`

## Objective

Replace historical title/domain-count analytical shortcuts with a structured, provenance-bound and policy-controlled semantic verification layer while preserving backward compatibility with the validated Phase 12 acquisition/runtime stack.

Phase 13 improves analytical depth. It does not activate production/live operation, public ingress, shared runtime, paid providers or autonomous truth promotion.

## Audited Compatibility Baseline

The existing baseline remains historical compatibility state until P13.6:
- `claims` / `evidence` from migration 002 are minimal legacy objects;
- `live_analysis_claims` / `live_analysis_evidence` group evidence by normalized headline and store `origin_host` / `independent_origin_count`;
- historical `verification.py` uses an evidence-count threshold;
- historical live analysis uses distinct origin hosts for `PARTLY_VERIFIED` behavior;
- historical `confidence_engine.py` derives an independence term from source-ID count;
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

Contradiction state preserves unresolved/evolving/resolved history. A claim/denial pair is not automatically resolved by source reputation alone.

### Verification decision contract

Canonical semantic verification promotion is policy-controlled and auditable.

The engine must not promote a claim solely because:
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
Formal closure repair HEAD: `f771ce0154e24b2218b309d8b3e6b880b408a146`.

Implementation evidence:
- x64 `33594740585 / 100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 `33594740549 / 100135812546`: `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Formal closure evidence:
- x64 `33848458616 / 100945599309`: `463 passed, 2 warnings / SUCCESS`;
- native ARM64 `33848458681 / 100945599390`: `463 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `026_semantic_contradiction_model.sql` introduced append-only typed contradiction versions/evidence links. Resolution requires explicit reconciliation metadata but does not select a factual winner.

## P13.5 Verification Policy Engine and Multidimensional Confidence — VALIDATED

Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.
Validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.

Validation evidence:
- x64 run `33849149736`, job `100947736040`: `475 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33849149742`, job `100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

Migration `027_semantic_verification_policy_confidence.sql` introduced append-only verification policy versions, multidimensional factual-confidence versions and auditable semantic verification decisions.

Validated policy semantics:
- count-only, official-status-only, source-reputation-only and coverage-only promotion remain forbidden;
- `VERIFIED` requires an explicit current independent pair of current `SUPPORTS` evidence;
- current `CONTRADICTS` evidence or active P13.4 contradiction blocks `VERIFIED`;
- factual confidence is multidimensional before any optional presentation scalar and no canonical scalar is stored;
- coverage limitation remains separate and non-promotional;
- global-latest P13.3/P13.4 snapshots prevent stale/superseded evidence, independence or contradiction versions from acting as current inputs;
- legacy count-based verification and scalar confidence APIs remain compatibility state, not canonical P13.5 policy.

Minimum modeled factual-confidence dimensions:
- evidence sufficiency;
- provenance independence;
- proposition-specific authority/proximity;
- contradiction resolution;
- temporal freshness;
- extraction certainty;
- translation certainty;
- claim-specific certainty;
- coverage limitation remains separate.

## P13.6 Current Work Package — Live Compatibility Cutover and Phase 13 Validation Matrix

State: `CURRENT / NOT_STARTED`.
Expected strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.

Required scope:
- define a non-destructive compatibility/cutover path between historical `live_analysis_claims` / `live_analysis_evidence` and P13.1-P13.5 semantic state;
- preserve historical live rows and legacy read APIs;
- prevent historical `origin_host`, distinct-host counts, `independent_origin_count`, evidence-count thresholds or scalar confidence from being reinterpreted as canonical semantic independence/truth;
- bind semantic decisions to reproducibility/traceability records where instrumented evidence exists;
- prove deterministic restart/read compatibility and migration idempotence;
- validate that P13.5 decisions can be consumed without rewriting legacy records;
- produce a Phase 13 validation matrix covering P13.0-P13.6 boundaries and exact validation evidence;
- retain `PROJECT_LOCAL_ONLY` and `NOT_OPERATIONAL` runtime status.

P13.6 must not:
- silently promote old `PARTLY_VERIFIED`/`VERIFIED` values into P13.5 decisions;
- invent exact provenance or tool history that was not instrumented;
- use a compatibility view as proof of independent origin;
- activate production/live, public ingress, shared runtime or paid providers;
- advance Phase 14 without closing the Phase 13 strategic gate.

## Internal Phase 13 Sequencing

- `P13.0` — architecture contract — **VALIDATED**;
- `P13.1` — structured semantic claims — **VALIDATED**;
- `P13.2` — provenance / underlying origin — **VALIDATED**;
- `P13.3` — evidence relation / independence — **VALIDATED**;
- `P13.4` — typed contradiction lifecycle — **VALIDATED**;
- `P13.5` — verification policy / multidimensional confidence — **VALIDATED**;
- `P13.6` — live compatibility cutover, reproducibility and Phase 13 validation matrix — **CURRENT / NOT_STARTED**.

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

Next gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.

P13.6 must be implemented, validated and saved before Phase 13 is closed or Phase 14 engineering becomes current.