# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.8
Status: APPROVED / PHASE_12_VALIDATED / P13.1_VALIDATED / P13.2_CURRENT

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language, health, freshness, extraction or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, additive structured semantic-claim versions/links, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## Phase 12 Validated Boundary

Phase 12 source-governance/acquisition/health layers are validated. Governed source state and measured operational state remain separate. Health/freshness does not modify truth. Translation is derived. Source/domain/language/adapter/item/host counts are not semantic independence.

Phase 12 final gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

## Phase 13 Baseline Audit

The pre-Phase-13 analytical persistence remains historical compatibility state:
- migration 002 `claims(id,event_id,text,confidence)`;
- migration 002 `evidence(id,claim_id,source_id,provenance,verification_status)`;
- migration 007 `live_analysis_claims`, including normalized `claim_key`, verification status, scalar confidence and historical `independent_origin_count`;
- migration 007 `live_analysis_evidence`, including `original_url` and `origin_host`.

These tables remain readable. Their current headline/host-based semantics are not promoted into the new Phase 13 semantic model.

## P13.0 Semantic Verification Architecture Contract

Phase 13 semantic model v2 architecture: `P13.0_VALIDATED`.
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.

P13.0 creates no database migration. It validates the compatibility and schema requirements that P13.1+ implement additively.

Validated semantic claim requirements include claimant/actor, normalized proposition, subject/object/theme, event/action type, negation/polarity, modality, time, location, quantitative values/units, original language, extraction method/version, extraction confidence, version/supersession and links to legacy/live/raw objects.

A single publication may contain multiple semantic claims. Different wording may represent the same proposition; similar wording may represent different propositions.

## P13.1 Structured Semantic Claim Model

State: `VALIDATED`.
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Migration: `023_structured_semantic_claim_model.sql`.

P13.1 adds two append-only tables:
- `semantic_claim_versions`;
- `semantic_claim_links`.

`semantic_claim_versions` stores explicit caller-controlled semantic identity, monotonic version number, normalized proposition, claimant/actor, subject, object/theme, event/action type, polarity, modality, structured time/location/quantity JSON, original language, extraction method/version/confidence, supersession and creation metadata.

`semantic_claim_links` stores non-evidentiary links from a semantic claim version to `LEGACY_CLAIM`, `LIVE_ANALYSIS_CLAIM` or `RAW_ITEM` targets. Link existence means association only; it does not mean `SUPPORTS`, `CONTRADICTS`, provenance identity or evidentiary independence.

Both tables are append-only through SQL triggers. Semantic identity is not auto-merged from identical proposition text, normalized headlines, publishers, embeddings or storage hashes.

`extraction_confidence` is explicitly extraction-only. P13.1 contains no `underlying_origin`, `independence_state`, `evidence_relation`, `contradiction_state`, `verification_state`, `factual_confidence` or `coverage_confidence` fields.

Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.
- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

## P13.2 Provenance / Underlying-Origin Relation Model

State: `CURRENT / NOT_STARTED`.
Expected gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

P13.2 is responsible for explicit provenance/origin relations. It must distinguish publisher/publication, immediate acquired source, cited/quoted source, asserted underlying origin, official statement/document origin, wire/syndication origin, dataset/structured-data origin, social/user-provided origin, derivation relations and unresolved/mixed origin.

P13.2 must not infer origin identity from a different hostname, publisher or language. Unknown origin remains explicit. P13.2 must not yet decide evidentiary independence, contradiction resolution or verification promotion.

## Evidence Relation / Independence Contract

Future evidence relations are typed separately from verification decisions. Planned relation vocabulary: `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`.

Semantic independence is an explicit provenance assessment with planned states `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, and where appropriate `MIXED`.

Legacy `origin_host` and `independent_origin_count` remain historical fields; they are not sufficient proof of semantic/evidentiary independence.

## Contradiction / Verification Contract

Contradictions must become typed/versioned analytical objects with dimensions such as occurrence, attribution, actor, quantity, time, location, status/outcome and scope.

Verification promotion must be policy-controlled. Evidence count, domain/host count, publisher count, language count, official status, freshness, source reputation, graph inference or forecast probability cannot alone promote canonical factual truth state.

Existing compatibility states remain `DETECTED`, `PARTLY_VERIFIED`, `VERIFIED`, `DISPUTED`, `UNVERIFIABLE` unless a later explicit migration changes the vocabulary.

## Confidence Separation

Future confidence is multidimensional before any presentation scalar:
- evidence sufficiency;
- provenance/independence confidence;
- proposition-specific source authority/proximity;
- source reliability context;
- contradiction severity;
- temporal freshness;
- extraction uncertainty;
- translation uncertainty;
- claim-specific uncertainty;
- coverage limitation.

Semantic extraction confidence is not factual verification confidence. Coverage confidence remains separate and cannot promote factual verification confidence.

## Migration / Compatibility Boundary

- Phase 13 uses additive migrations unless a later explicit architecture decision authorizes otherwise;
- existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` rows are not destructively rewritten;
- P13.1 semantic objects link to historical/raw objects rather than replacing them;
- model/LLM extraction may propose structured objects but cannot directly promote canonical truth state;
- P13.2 is the current provenance/origin package and must remain separate from later independence/verification packages.

## Runtime Storage Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Shared/mixed canonical runtime storage remains not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- migration 023/structured semantic claim model: `VALIDATED`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13 P13.0 gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- Phase 13 P13.1 gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.1 semantic schema: `VALIDATED`;
- P13.2 provenance/origin model: `CURRENT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.