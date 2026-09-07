# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 3.0
Status: APPROVED / PHASE_12_VALIDATED / PHASE_13_VALIDATED / ROADMAP_V4_22_SYNCHRONIZED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Core Principle

Source quantity does not equal source independence. Publisher/domain/adapter/item/language/host identity is not automatically underlying-origin identity.

## Source Classes

Approved baseline classes remain Official sources, International media, Regional media, Social platforms, OSINT, Structured data and User-provided information. Source roles remain governance/provenance metadata, not truth operators.

## Phase 12 Source Governance

P12.1-P12.6 remain validated. Portfolio approval, adapter success, operational availability, freshness and source count do not establish factual truth or independent corroboration.

Validated Phase 12 gates remain canonical:
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

Known historical Phase 12 observations remain visible:
- European Parliament — governed `DEGRADED`, measured `UNAVAILABLE / PARSER`;
- Haberturk — governed `ACTIVE`, measured `UNAVAILABLE / UNKNOWN` for the P12.5 probe;
- OSCE — acquisition `HEALTHY`, observed publisher content `STALE`;
- `uk/ru/pl/tr` — initial language slice, not global coverage.

## Provenance / Independence — Phase 13 Validated Model

P13.0 semantic verification architecture contract: `VALIDATED`.
Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.

P13.1 structured semantic claim model: `VALIDATED`.
Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.

P13.2 provenance/origin relation model: `VALIDATED`.
Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

P13.3 evidence relation and independence assessment: `VALIDATED`.
Gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`.

P13.4 typed contradiction model: `VALIDATED`.
Gate: `P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED`.

P13.5 verification policy/confidence: `VALIDATED`.
Gate: `P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED`.

P13.6 live compatibility/validation matrix: `VALIDATED`.
Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.

The canonical provenance layer distinguishes publisher/publication, immediate acquired source, cited/quoted source, asserted underlying origin, official statement/document origin, wire/syndication origin, dataset/structured-data origin, social/user-provided origin, translation/repost/syndication/citation derivation and unresolved/mixed origin.

Publisher identity therefore cannot be promoted to underlying-origin identity. Unknown origin remains unresolved rather than being inferred from a different domain, publisher or language.

## Evidence Relations and Semantic Independence

Evidence relation vocabulary includes `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `CONTEXT_ONLY`, `ATTRIBUTION_ONLY`, `DUPLICATE_OR_SAME_ORIGIN`.

Independence vocabulary includes `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, `MIXED`.

Independence requires provenance/origin reasoning. It is not established solely by another publisher/domain/host, adapter/source ID, language/translation, repost/syndication/citation, source reputation, official status, parsing success, freshness or portfolio `ACTIVE` state.

Legacy `origin_host` and `independent_origin_count` remain historical compatibility observations, not sufficient semantic independence proof.

## Verification Promotion Boundary

Canonical factual verification is policy-controlled and auditable under P13.5/P13.6.

A claim cannot be promoted solely because evidence count is at least two; two domains/hosts/publishers differ; the same claim appears in multiple languages; a source is official/high-reputation/fresh/healthy; a graph model infers a relationship; a forecasting model assigns high probability; a delivery succeeds; or publication/engagement occurs.

Model/LLM-assisted extraction may propose structured claims/provenance/relations. It cannot directly promote canonical truth state.

## Contradiction / Coverage Boundary

Contradictions are typed/versioned analytical objects. Conflicting sources remain visible when unresolved; a claim/denial pair is not resolved automatically by source reputation or publisher count.

Source portfolio, language, source-health and semantic-provenance metadata may inform coverage assessment, but coverage confidence does not modify factual verification confidence. `GLOBAL` remains intended scope, not proof of exhaustive coverage.

Unavailable, stale, closed, inaccessible, deleted or unindexed sources remain coverage limitations, not evidence that an event did not occur.

## Downstream Non-Truth Boundaries

- Phase 15 forecast probability/calibration/performance metrics cannot promote factual verification;
- Phase 16 delivery state, receipts and operator feedback cannot promote factual verification or create independent event evidence by themselves;
- Phase 17 publication eligibility, publication receipts and engagement cannot promote factual verification;
- publisher/publication identity remains distinct from underlying-origin identity throughout publication.

## Runtime / Activation Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

- Phase 14 owner operational layer remains `VALIDATED_READY / NOT_ACTIVATED`; `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`;
- Phase 17 remains `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- Phase 18 remains `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- public backend/API/dashboard ingress, backend HTTPS, public GPT Action, shared runtime and paid providers remain unactivated.

## Current State

- source/provenance Phase 12 baseline: `VALIDATED`;
- Phase 13: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`;
- P13.0–P13.6: `VALIDATED`;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED / OWNER_DECISION_REQUIRED`;
- Phase 15: `VALIDATED`;
- Phase 16: `VALIDATED`;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- Phase 18: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
