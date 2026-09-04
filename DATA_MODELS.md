# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.12
Status: APPROVED / PHASE_12_VALIDATED / P13.0-P13.5_VALIDATED / P13.6_CURRENT

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language, health, freshness, extraction, independence, contradiction, confidence or other analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, additive semantic claim versions/links, semantic provenance/origin entities and relations, typed semantic evidence relations, pairwise independence assessments, typed contradiction versions/evidence links, versioned verification policies, multidimensional factual-confidence profiles, versioned semantic verification decisions, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## Phase 12 Validated Boundary

Phase 12 source-governance/acquisition/health layers are validated at `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`. Health/freshness does not modify truth. Translation is derived. Source/domain/language/adapter/item/host counts are not semantic independence.

## Phase 13 Baseline Compatibility

Historical compatibility persistence remains readable:
- migration 002 `claims(id,event_id,text,confidence)` and `evidence`;
- migration 007 `live_analysis_claims`, including normalized `claim_key`, verification status, scalar confidence and historical `independent_origin_count`;
- migration 007 `live_analysis_evidence`, including `original_url` and `origin_host`;
- legacy `verification.py`, `confidence_engine.py` and `contradictions.py` remain compatibility APIs.

These historical fields are not promoted into the canonical Phase 13 semantic truth model.

## P13.0 Semantic Verification Architecture Contract

State: `VALIDATED`.
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Phase 13 semantic model v2 architecture: `P13.0_VALIDATED`.

Semantic claim identity is not headline identity. Publisher/publication, cited source and underlying origin are distinct. Evidence relation, independence, contradiction and final verification remain separate layers.

## P13.1 Structured Semantic Claim Model

State: `VALIDATED`.
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Migration: `023_structured_semantic_claim_model.sql`.
Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.
- x64: `408 passed, 1 warning / SUCCESS`;
- native ARM64: `408 passed, 1 warning / SUCCESS`.

P13.1 adds append-only `semantic_claim_versions` and `semantic_claim_links`. Semantic identity is explicit/caller-controlled; association links carry no evidentiary meaning. `extraction_confidence` is extraction-only.

The P13.1 schema boundary remains explicit: it does not add `underlying_origin`, `independence_state`, `evidence_relation`, `contradiction_state`, `verification_state`, `factual_confidence` or `coverage_confidence` fields to semantic claim versions; those concepts belong to later Phase 13 layers.

## P13.2 Provenance / Underlying-Origin Relation Model

State: `VALIDATED`.
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Migration: `024_semantic_provenance_origin_relation_model.sql`.
Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.
- x64: `420 passed, 1 warning / SUCCESS`;
- native ARM64: `420 passed, 1 warning / SUCCESS`.

P13.2 adds append-only provenance entity, claim-role and provenance-relation versions. Publication, publisher, immediate acquired source, cited/quoted source and underlying origin are explicit separate concepts. Citation, syndication, repost, translation and derivation remain provenance relationships, not independent corroboration.

## P13.3 Evidence Relation and Independence Assessment

State: `VALIDATED`.
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Migration: `025_semantic_evidence_relation_independence.sql`.
Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.
- x64 closure: `438 passed, 1 warning / SUCCESS`;
- native ARM64 closure: `438 passed, 1 warning / SUCCESS`.

P13.3 adds append-only `semantic_evidence_relation_versions` and `semantic_independence_assessment_versions`.

Evidence relation vocabulary:
`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`.

Independence vocabulary:
`INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`.

Different publisher/source/host/domain/language never suffices for independence. Absence of a known derivation path remains `UNKNOWN` rather than automatically independent.

## P13.4 Typed Contradiction Model and Resolution Lifecycle

State: `VALIDATED`.
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.
Migration: `026_semantic_contradiction_model.sql`.
Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.
Formal closure repair HEAD: `f771ce0154e24b2218b309d8b3e6b880b408a146`.
- implementation x64/native ARM64: `447 passed, 1 warning / SUCCESS`;
- formal closure x64/native ARM64: `463 passed, 2 warnings / SUCCESS`.

P13.4 adds append-only `semantic_contradiction_versions` and `semantic_contradiction_evidence_links`.

Dimensions include `OCCURRENCE_EXISTENCE`, `ATTRIBUTION_RESPONSIBILITY`, `ACTOR_IDENTITY`, `QUANTITY_VALUE`, `TIME`, `LOCATION`, `STATUS_OUTCOME`, `SCOPE_EXTENT`, `CAUSAL_INTERPRETATION`, `OTHER`.

Lifecycle states are `DETECTED`, `UNRESOLVED`, `EVOLVING`, `RESOLVED`. Reconciliation is not equivalent to selecting which claim is factually true. Evidence links are side-scoped and require a current P13.3 evidence relation version at link time.

## P13.5 Verification Policy and Multidimensional Confidence

State: `VALIDATED`.
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.
Migration: `027_semantic_verification_policy_confidence.sql`.
Validation anchor: `0f0d746c538dc5ce8f010fb80f8afbe00685414a`.
- x64 run `33849149736`, job `100947736040`: `475 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33849149742`, job `100947736318`: native `aarch64`, `475 passed, 2 warnings / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.5 adds append-only:
- `semantic_verification_policy_versions`;
- `semantic_factual_confidence_versions`;
- `semantic_verification_decision_versions`.

Policy versions preserve permanent fail-closed invariants against count-only, official-status-only, source-reputation-only and coverage-only truth promotion.

Factual confidence is multidimensional:
- evidence sufficiency;
- provenance independence;
- authority/proximity;
- contradiction resolution;
- temporal freshness;
- extraction certainty;
- translation certainty;
- claim-specific certainty.

Each factual dimension is `UNKNOWN`, `LOW`, `MEDIUM` or `HIGH`. Coverage remains separate as `coverage_limitation = UNKNOWN | LIMITED | ADEQUATE`. There is no canonical factual-confidence scalar and no `coverage_confidence` field in the P13.5 confidence model.

`VERIFIED` requires an explicit current `INDEPENDENT` pair of current `SUPPORTS` evidence plus policy confidence floors; current `CONTRADICTS` evidence and any active P13.4 contradiction block `VERIFIED`.

Verification decisions snapshot global-latest P13.3 evidence identities, global-latest independence-assessment identities, current P13.4 contradiction identities, the current policy version and current confidence version. Superseded records therefore cannot silently act as current inputs.

Compatibility vocabulary remains `DETECTED`, `PARTLY_VERIFIED`, `VERIFIED`, `DISPUTED`, `UNVERIFIABLE`, but canonical promotion semantics are now policy-controlled rather than count-controlled.

## P13.6 Live Compatibility / Validation Matrix Contract

State: `CURRENT / NOT_STARTED`.
Expected gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.

P13.6 must provide a non-destructive compatibility/cutover path from historical `live_analysis_*` outputs to P13.1-P13.5 semantic decision state, maintain reproducibility/traceability, preserve historical rows/read APIs, and prove that legacy `origin_host`, `independent_origin_count` and scalar-confidence shortcuts are not silently treated as canonical semantic verification.

## Migration / Compatibility Boundary

- Phase 13 uses additive migrations unless a later explicit architecture decision authorizes otherwise;
- existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` rows are not destructively rewritten;
- P13.1 semantic objects link to historical/raw objects rather than replacing them;
- P13.2 provenance is referenced rather than duplicated by P13.3;
- P13.4 references P13.3 evidence instead of duplicating evidence/provenance state;
- P13.5 references current P13.3/P13.4 state and stores auditable snapshots rather than mutating them;
- legacy `origin_host`, `independent_origin_count`, scalar confidence and count-based verification remain historical fields, not sufficient proof of semantic independence or factual truth;
- no live analytical cutover has occurred yet.

## Runtime Storage Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Shared/mixed canonical runtime storage remains not approved.

## Current State

- migrations 022-027: validated through P13.5;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13 P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- Phase 13 P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- Phase 13 P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- Phase 13 P13.3: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- Phase 13 P13.4: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- Phase 13 P13.5: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`;
- P13.6: `CURRENT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.