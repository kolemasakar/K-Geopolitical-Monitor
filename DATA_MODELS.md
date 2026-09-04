# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.11
Status: APPROVED / PHASE_12_VALIDATED / P13.0-P13.4_VALIDATED / P13.5_CURRENT

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language, health, freshness, extraction, independence, contradiction or other analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, legacy claims/evidence/events, live-analysis claims/evidence, additive structured semantic-claim versions/links, semantic provenance/origin entities and relations, typed semantic evidence relations, pairwise independence assessments, typed contradiction versions/evidence links, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## Phase 12 Validated Boundary

Phase 12 source-governance/acquisition/health layers are validated. Governed source state and measured operational state remain separate. Health/freshness does not modify truth. Translation is derived. Source/domain/language/adapter/item/host counts are not semantic independence.

Phase 12 final gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

## Phase 13 Baseline Audit

The pre-Phase-13 analytical persistence remains historical compatibility state:
- migration 002 `claims(id,event_id,text,confidence)`;
- migration 002 `evidence(id,claim_id,source_id,provenance,verification_status)`;
- migration 007 `live_analysis_claims`, including normalized `claim_key`, verification status, scalar confidence and historical `independent_origin_count`;
- migration 007 `live_analysis_evidence`, including `original_url` and `origin_host`.

These tables remain readable. Their headline/host-based semantics are not promoted into the new Phase 13 semantic model.

## P13.0 Semantic Verification Architecture Contract

Phase 13 semantic model v2 architecture: `P13.0_VALIDATED`.
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.

P13.0 creates no database migration. It validates the compatibility and schema requirements implemented additively by P13.1+.

A single publication may contain multiple semantic claims. Different wording may represent the same proposition; similar wording may represent different propositions. Publisher/publication, cited source and underlying origin are distinct. Evidence relation, independence, contradiction and final verification remain separate layers.

## P13.1 Structured Semantic Claim Model

State: `VALIDATED`.
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.
Migration: `023_structured_semantic_claim_model.sql`.

P13.1 adds append-only `semantic_claim_versions` and `semantic_claim_links`. Semantic identity is explicit/caller-controlled; links to legacy claims, live-analysis claims and raw items are association records only and carry no evidentiary meaning.

`extraction_confidence` is extraction-only. P13.1 contains no `underlying_origin`, `independence_state`, `evidence_relation`, `contradiction_state`, `verification_state`, `factual_confidence` or `coverage_confidence` fields.

Validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.
- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

## P13.2 Provenance / Underlying-Origin Relation Model

State: `VALIDATED`.
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.
Migration: `024_semantic_provenance_origin_relation_model.sql`.

P13.2 adds append-only `semantic_provenance_entity_versions`, `semantic_claim_provenance_role_versions` and `semantic_provenance_relation_versions`.

Publication, publisher, immediate acquired source, cited/quoted source and underlying origin are explicit separate concepts. Official statement/document, wire, dataset, social/user-provided, `UNKNOWN` and `MIXED` origins are representable. Citation, syndication, repost, translation and derivation remain provenance relationships, not independent corroboration.

Validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.
- x64 run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`;
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

## P13.3 Evidence Relation and Independence Assessment

State: `VALIDATED`.
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.
Migration: `025_semantic_evidence_relation_independence.sql`.

P13.3 adds append-only `semantic_evidence_relation_versions` and `semantic_independence_assessment_versions`.

Evidence relation vocabulary: `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`.

Independence vocabulary: `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`.

Independence is explicitly assessed from P13.2 provenance/origin relations rather than domain/source/publisher/language counts. Automated fail-closed inference can establish non-independence or uncertainty but never infers `INDEPENDENT` merely because no known derivation path exists. Current inference uses only the latest version of each P13.2 provenance relation identity; superseded edges remain audit history.

Formal closure HEAD: `9023dc22d36525b4dc9babbf21d97d184a1c110e`.
- x64 closure run `33594299961`, job `100134512548`: `438 passed, 1 warning / SUCCESS`;
- native ARM64 closure run `33594299979`, job `100134512479`: native `aarch64`, `438 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

## P13.4 Typed Contradiction Model and Resolution Lifecycle

State: `VALIDATED`.
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.
Migration: `026_semantic_contradiction_model.sql`.

P13.4 adds append-only:
- `semantic_contradiction_versions`;
- `semantic_contradiction_evidence_links`.

Contradiction identity binds two distinct immutable semantic claim version IDs plus one typed dimension. Later lifecycle versions cannot silently change that pair or dimension.

Dimensions include `OCCURRENCE_EXISTENCE`, `ATTRIBUTION_RESPONSIBILITY`, `ACTOR_IDENTITY`, `QUANTITY_VALUE`, `TIME`, `LOCATION`, `STATUS_OUTCOME`, `SCOPE_EXTENT`, `CAUSAL_INTERPRETATION`, `OTHER`.

Lifecycle states are `DETECTED`, `UNRESOLVED`, `EVOLVING`, `RESOLVED`. A resolved version requires an explicit reconciliation code and explanatory note. Prior disagreement remains append-only history. Reconciliation is not equivalent to selecting which claim is factually true.

Evidence links are side-scoped and require a current P13.3 evidence relation version at link time. A P13.3 `CONTRADICTS` relation does not automatically create or resolve P13.4 contradiction state.

Validation anchor: `d4dbb8a8098cef960194935bd94d4640fd719050`.
- x64 run `33594740585`, job `100135812629`: `447 passed, 1 warning / SUCCESS`;
- native ARM64 run `33594740549`, job `100135812546`: native `aarch64`, `447 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.4 contains no canonical `verification_state`, `factual_confidence`, `coverage_confidence`, verification-policy field or truth-selection shortcut.

## P13.5 Verification / Confidence Contract

State: `CURRENT / NOT_STARTED`.
Expected gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

Verification promotion must be policy-controlled and auditable. Evidence count, domain/host count, publisher count, language count, official status, freshness, source reputation, independence state, graph inference, forecast probability or contradiction reconciliation cannot alone promote canonical factual truth state.

Existing compatibility states remain `DETECTED`, `PARTLY_VERIFIED`, `VERIFIED`, `DISPUTED`, `UNVERIFIABLE` unless a later explicit migration changes the vocabulary.

P13.5 factual confidence must be multidimensional before any presentation scalar. Extraction confidence and coverage confidence remain separate and cannot silently become factual verification confidence.

## Migration / Compatibility Boundary

- Phase 13 uses additive migrations unless a later explicit architecture decision authorizes otherwise;
- existing `claims`, `evidence`, `live_analysis_claims`, `live_analysis_evidence` rows are not destructively rewritten;
- P13.1 semantic objects link to historical/raw objects rather than replacing them;
- P13.2 provenance is referenced rather than duplicated by P13.3;
- P13.4 references P13.3 evidence instead of duplicating evidence/provenance state;
- legacy `origin_host` and `independent_origin_count` remain historical fields and are not sufficient proof of semantic independence;
- legacy `contradictions.py` remains compatibility state;
- model/LLM extraction may propose structured objects but cannot directly promote canonical truth state;
- no live analytical cutover has occurred.

## Runtime Storage Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Shared/mixed canonical runtime storage remains not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- migration 023/structured semantic claim model: `VALIDATED`;
- migration 024/provenance-origin relation model: `VALIDATED`;
- migration 025/evidence relation and independence: `VALIDATED`;
- migration 026/typed contradiction model: `VALIDATED`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13 P13.0 gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- Phase 13 P13.1 gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- Phase 13 P13.2 gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- Phase 13 P13.3 gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- Phase 13 P13.4 gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`;
- P13.5 verification/confidence: `CURRENT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.