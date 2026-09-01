# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.6
Status: APPROVED / PHASE_12_VALIDATED / PHASE_13_P13.0_CURRENT

## Core Principle

Source quantity does not equal source independence. Publisher/domain/adapter/item/language/host identity is not automatically underlying-origin identity.

## Source Classes

Approved baseline classes remain Official sources, International media, Regional media, Social platforms, OSINT, Structured data and User-provided information. P12.1 source roles remain separate governance metadata.

## Phase 12 Source Governance

P12.1-P12.6 remain validated. Portfolio approval, adapter success, operational availability, freshness and source count do not establish factual truth or independent corroboration.

Validated Phase 12 gates remain canonical:
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

Known Phase 12 observations remain visible:
- European Parliament — governed `DEGRADED`, measured `UNAVAILABLE / PARSER`;
- Haberturk — governed `ACTIVE`, measured `UNAVAILABLE / UNKNOWN` for the P12.5 probe;
- OSCE — acquisition `HEALTHY`, observed publisher content `STALE`;
- `uk/ru/pl/tr` — initial language slice, not global coverage.

## Provenance / Independence — Phase 13 Contract

P13.0 semantic verification architecture contract: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`.

Phase 13 makes provenance/origin relationships executable rather than relying on host/domain counts.

The semantic provenance layer must distinguish:
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

Publisher identity therefore cannot be promoted to underlying-origin identity. Unknown origin remains unresolved rather than being inferred from a different domain, publisher or language.

## Evidence Relations

Phase 13 evidence-to-claim relations are planned as typed analytical relationships:
- `SUPPORTS`;
- `CONTRADICTS`;
- `QUALIFIES`;
- `CONTEXT_ONLY`;
- `ATTRIBUTION_ONLY`;
- `DUPLICATE_OR_SAME_ORIGIN`.

A relation describes how evidence bears on a claim. It does not itself determine final verification state.

## Semantic Independence

Planned states: `INDEPENDENT`, `NOT_INDEPENDENT`, `UNKNOWN`, and where appropriate `MIXED`.

Independence requires provenance/origin reasoning. It is not established solely by:
- another publisher/domain/host;
- another adapter/source ID;
- another language/translation;
- another repost/syndication/citation;
- source reputation or official status;
- successful parsing, freshness or portfolio `ACTIVE` state.

Legacy `origin_host` and `independent_origin_count` remain historical observations, not sufficient semantic independence proof.

## Official / Media / Discovery Semantics

- official sources are authoritative for their own statements, not automatically for the underlying event;
- official sources are authoritative for what the institution published or stated, not automatically for the substantive event;
- media publication may derive from own reporting, official statements, wire services, other publishers, social content, datasets or mixed/unresolved origins;
- discovery/index services such as GDELT do not corroborate a claim merely by indexing it;
- translation remains a separate derived representation and creates no new underlying origin.

Historical Phase 12 invariants remain explicit:
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- media/domain/language/adapter/item/host count is not independent-origin count.

## Verification Promotion Boundary

Canonical Phase 13 factual verification is policy-controlled and auditable.

A claim cannot be promoted solely because:
- evidence count is at least two;
- two domains/hosts/publishers differ;
- the same claim appears in multiple languages;
- a source is official/high-reputation/fresh/healthy;
- a graph model infers a relationship;
- a forecasting model assigns high probability.

Model/LLM-assisted extraction may propose structured claims/provenance/relations. It cannot directly promote canonical truth state.

## Contradiction Boundary

Contradictions are planned as typed/versioned analytical objects. Conflicting sources must remain visible when unresolved. A claim/denial pair is not resolved automatically by source reputation or publisher count.

## Coverage Boundary

Source portfolio, language, source-health and semantic-provenance metadata may inform coverage assessment, but coverage confidence does not modify factual verification confidence. `GLOBAL` remains intended scope, not proof of exhaustive coverage.

Unavailable, stale, closed, inaccessible, deleted or unindexed sources remain coverage limitations, not evidence that an event did not occur.

## Runtime / Activation Boundary

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Phase 13 does not activate public backend/API/dashboard ingress, backend HTTPS, GPT Action connection, shared runtime or paid providers.

## Current State

- source/provenance Phase 12 baseline: `VALIDATED`;
- Phase 12 gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P13.0 semantic verification architecture contract: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`;
- P13.1 structured semantic claim model: `PLANNED / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
