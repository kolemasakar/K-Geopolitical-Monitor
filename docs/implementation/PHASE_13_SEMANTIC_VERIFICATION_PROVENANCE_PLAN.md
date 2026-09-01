# Phase 13 — Semantic Verification and Provenance Intelligence

Date: 2026-09-01
Status: `ACTIVE_ENGINEERING_PHASE / P13.0_VALIDATED / P13.1_VALIDATED / P13.2_CURRENT`
Project: K-Geopolitical Monitor
Strategic phase gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`
Current activity: `P13.2_PROVENANCE_ORIGIN_RELATION_MODEL`

## Objective

Replace the current title/domain-count analytical shortcuts with a structured, provenance-bound and policy-controlled semantic verification layer while preserving backward compatibility with the validated Phase 12 acquisition/runtime stack.

Phase 13 improves analytical depth. It does not activate production/live operation, public ingress, shared runtime, paid providers or autonomous truth promotion.

## Audited Baseline

The existing baseline is intentionally retained as historical compatibility state:

- `claims` / `evidence` from migration 002 are minimal legacy objects;
- `live_analysis_claims` / `live_analysis_evidence` from migration 007 group evidence by normalized headline and store `origin_host` / `independent_origin_count`;
- `verification.py` currently promotes to `PARTLY_VERIFIED` when `evidence_count >= 2`;
- `live_end_to_end.py` currently uses two distinct origin hosts as the live `PARTLY_VERIFIED` threshold;
- `confidence_engine.py` currently derives an independence term from distinct source IDs;
- `contradictions.py` is a minimal container rather than a typed contradiction engine.

These behaviors remain supported until a later Phase 13 compatibility cutover. They are not the semantic rules for the new layer.

## P13.0 Architecture Contract — VALIDATED

Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Validation anchor: `4422fae5e2a4546585a43237d2124f466c457543`.

Validation evidence:
- x64 run `33554568574`, job `100012110127`: `399 passed, 1 warning / SUCCESS`;
- native ARM64 run `33554568570`, job `100012110488`: native `aarch64`, `399 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.0 is documentation/test contract work only. It intentionally creates **no database migration** and does not mutate legacy analytical tables.

### Semantic claim identity

A semantic claim is not identified solely by a headline or normalized headline.

The structured claim contract must be able to represent, where applicable:
- claimant / attributed actor;
- normalized proposition;
- subject / object or theme;
- event/action type;
- polarity / negation;
- modality and epistemic framing (`asserted`, `reported`, `alleged`, `denied`, `estimated`, etc.);
- time scope;
- location scope;
- quantity/value/unit and range when materially relevant;
- original language;
- extraction method/version;
- extraction confidence separated from factual verification confidence;
- canonical version/supersession metadata;
- linkage to legacy/live analytical objects and raw evidence.

Semantically equivalent claims may have different wording. Similar wording may encode materially different claims. One publication may contain multiple claims.

### Provenance / underlying-origin contract

The new provenance model must distinguish at minimum:
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

Publisher/domain identity is not automatically underlying-origin identity.

A provenance relationship must be explicit and auditable. Unknown origin remains `UNKNOWN/UNRESOLVED`; it is never inferred merely from a different hostname, language or publisher.

### Evidence relation contract

Evidence-to-claim relations must become typed. Planned relation vocabulary includes:
- `SUPPORTS`;
- `CONTRADICTS`;
- `QUALIFIES`;
- `CONTEXT_ONLY`;
- `ATTRIBUTION_ONLY`;
- `DUPLICATE_OR_SAME_ORIGIN`.

The relation describes how a piece of evidence bears on a claim; it does not itself determine final verification state.

### Independence contract

Independence must be assessed from provenance/origin relationships, not from domain/source/media/language/adapter/item count.

Planned independence states:
- `INDEPENDENT`;
- `NOT_INDEPENDENT`;
- `UNKNOWN`;
- `MIXED` where a record contains separable components with different origin relationships.

Unknown independence cannot be promoted to independent merely to satisfy a verification threshold.

### Contradiction contract

Contradictions become typed analytical objects. Planned contradiction dimensions include:
- occurrence/existence;
- attribution/responsibility;
- actor identity;
- quantity/value;
- time;
- location;
- status/outcome;
- scope/extent;
- causal interpretation where explicitly modeled.

Contradiction state must support unresolved/evolving information and later resolution without deleting the historical disagreement.

A claim/denial pair is not automatically resolved by source reputation alone.

### Verification decision contract

Canonical semantic verification promotion must be policy-controlled and auditable.

The new engine must not promote a claim solely because:
- evidence count is `>= 2`;
- two domains/hosts are different;
- two publishers are different;
- the same statement appears in multiple languages;
- an item is official, fresh, highly reputable or successfully parsed;
- a graph or forecast model assigns high probability.

The existing states `DETECTED`, `PARTLY_VERIFIED`, `VERIFIED`, `DISPUTED`, `UNVERIFIABLE` remain the compatibility vocabulary unless a later explicit migration expands them.

### Confidence contract

Confidence becomes multidimensional before any presentation scalar is calculated. Planned inspectable dimensions include:
- evidence sufficiency;
- provenance/independence confidence;
- source proximity/authority for the specific proposition;
- source reliability context;
- contradiction severity;
- temporal freshness;
- extraction uncertainty;
- translation uncertainty;
- claim-specific uncertainty;
- coverage limitation.

Coverage confidence remains separate and cannot promote factual verification confidence.

## Compatibility / Migration Rules

- Phase 13 uses additive migrations only unless a later explicit architecture decision authorizes otherwise.
- Existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` and their historical rows remain readable.
- P13 semantic objects must link to legacy/live objects rather than silently overwrite their historical meaning.
- Existing `independent_origin_count` and `origin_host` are retained as historical/observational fields, not accepted as sufficient semantic independence proof.
- A later cutover may change live output wording and verification behavior only after deterministic compatibility tests and stored migration evidence.
- No LLM/model extraction output may directly promote canonical factual truth state. Model output may propose structured objects; policy validates and records them.

## P13.1 Structured Semantic Claim Model — VALIDATED

Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.

Validation evidence:
- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.1 introduced additive migration `023_structured_semantic_claim_model.sql` with:
- append-only `semantic_claim_versions`;
- append-only `semantic_claim_links`;
- explicit caller-controlled semantic identity and version/supersession;
- structured proposition, actor/subject/object/action, polarity, modality, time/location/quantity, original-language and extraction metadata;
- non-evidentiary links to legacy claims, live-analysis claims and raw items;
- fail-closed validation of link targets and structured values;
- explicit separation of extraction confidence from factual/coverage confidence.

P13.1 intentionally contains no P13.2-P13.5 truth semantics: no underlying-origin field, independence state, evidence relation, contradiction state, verification state, factual confidence or coverage confidence.

## P13.2 Current Work Package — Provenance / Underlying-Origin Relation Model

State: `CURRENT / NOT_STARTED`.
Expected gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

P13.2 is responsible for additive, auditable provenance/origin persistence tied to semantic claims and acquired/raw evidence.

Required scope:
- distinguish publication/publisher, immediate acquired source, cited/quoted source and asserted underlying origin;
- represent official statement/document, wire/syndication, dataset/structured-data, social/user-provided and unresolved/mixed origins;
- represent derivation such as citation, syndication, repost and translation without creating another independent origin;
- retain explicit `UNKNOWN/UNRESOLVED` where origin cannot be established;
- preserve source/publication URL and identity traceability without conflating publisher with origin;
- use append-only/versionable persistence and deterministic validation;
- link to P13.1 semantic claim versions and existing raw/source objects without destructive rewrite.

P13.2 must not implement:
- evidentiary independence decision or evidence stance — P13.3;
- contradiction lifecycle — P13.4;
- verification promotion or multidimensional factual confidence — P13.5;
- live analytical cutover — P13.6.

## Internal Phase 13 Sequencing

- `P13.0` — Semantic Verification Architecture Contract — **VALIDATED**;
- `P13.1` — Structured Semantic Claim Model and additive persistence — **VALIDATED**;
- `P13.2` — Provenance / Underlying-Origin Relation Model — **CURRENT / NOT_STARTED**;
- `P13.3` — Evidence Relation and Independence Assessment;
- `P13.4` — Typed Contradiction Model and resolution lifecycle;
- `P13.5` — Verification Policy Engine and multidimensional confidence;
- `P13.6` — Live compatibility cutover, reproducibility and Phase 13 validation matrix.

Each work package requires its own validation before the next package becomes current.

## Permanent Boundaries

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statement establishes that an actor/institution made the statement, not automatically the substantive event claim;
- source reputation, portfolio approval, source health and freshness are not truth operators;
- semantic extraction confidence is not factual verification confidence;
- source/domain/media/language/adapter/item/host count is not independent-origin count;
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

Next gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

P13.3 must not start before P13.2 is implemented, validated and saved.