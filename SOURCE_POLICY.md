# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.1
Status: APPROVED / P12_1_VALIDATED

## Core Principle

Source quantity does not equal source independence.

Publisher/domain/adapter identity is not automatically underlying-origin identity.

## Source Classes

Approved baseline classes:

- Official sources;
- International media;
- Regional media;
- Social platforms;
- OSINT;
- Structured data;
- User-provided information.

P12.1 adds a separate source-role vocabulary without changing these canonical classes.

## Source Portfolio Governance

P12.1 establishes immutable versioned governance in `source_portfolio_versions`.

Required governance dimensions include source/publisher identity, class/role, region/language, access/cost/authentication, freshness/cadence, adapter identity/version, outbound host/protocol, fallback, availability, data classification, origin/provenance characteristics, independence constraints, terms and review state.

Rules:

- a portfolio record does not activate collection;
- portfolio approval does not establish independent corroboration;
- source identity conflicts fail closed;
- operational availability requires approved review state;
- approved sources require assigned adapter identity/version;
- paid provider approval requires separate explicit approval;
- P12.1 approves no paid provider.

## Provenance / Independence

- same-origin duplicate observations do not increase corroboration;
- reposts, syndication, translations and citations do not create independent origins;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- discovery/index services do not corroborate claims merely by indexing them;
- source reputation/status changes context, not truth;
- portfolio governance changes governance, not truth.

## Validated Starting Live Baseline

- Consilium press-release RSS — Official sources;
- GDELT DOC 2.0 — Structured discovery/index metadata.

P12.1 adds no new live source.

## Coverage Boundary

Source portfolio metadata may inform future configured coverage/source-health requirements, but it does not itself change coverage confidence or factual verification confidence. `GLOBAL` remains scope, not proof of exhaustive monitoring.

## Activation Boundary

P12.2 is the next gate and may link reusable adapters to P12.1 portfolio governance. No source becomes live solely because it exists in the portfolio.

## Current State

- source/provenance baseline: `VALIDATED`;
- P12.1 source portfolio: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- current controlled-live source network: 2 validated integrations;
- new live sources from P12.1: none;
- paid providers: none approved;
- P12.2: `NEXT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
