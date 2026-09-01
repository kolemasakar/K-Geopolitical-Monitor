# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.6
Status: APPROVED / PHASE_12_VALIDATED / PHASE_13_P13.0_CURRENT

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language, health, freshness, extraction or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

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

Phase 13 semantic model v2: `P13.0_CURRENT`.

P13.0 creates no database migration. It defines the compatibility and schema requirements that P13.1+ must implement additively.

Future semantic claim objects must support explicit structured identity rather than normalized headline identity, including where applicable claimant/actor, proposition, subject/object/theme, event/action type, negation/polarity, modality, time, location, quantitative values/units, original language, extraction method/version, extraction confidence, version/supersession and links to legacy/live/raw objects.

A single publication may contain multiple semantic claims. Different wording may represent the same proposition; similar wording may represent different propositions.

## Provenance / Origin Model Contract

Future provenance must distinguish:
- publisher/publication;
- immediate acquired source;
- cited/quoted source;
- asserted underlying origin;
- official statement/document origin;
- wire/syndication origin;
- dataset/structured-data origin;
- social/user-provided origin;
- translation/repost/syndication/citation derivation;
- unresolved/mixed origin.

Unknown underlying origin remains unknown; another hostname or language is not proof of a new origin.

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
- new semantic objects must link to historical/raw objects;
- model/LLM extraction may propose structured objects but cannot directly promote canonical truth state;
- P13.1 is the first planned schema-bearing work package and remains `NOT_STARTED` until P13.0 validation.

## Runtime Storage Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Shared/mixed canonical runtime storage remains not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13 semantic model v2: `P13.0_CURRENT`;
- P13.0 architecture contract: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`;
- P13.1 semantic schema: `PLANNED / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
