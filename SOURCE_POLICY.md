# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.2
Status: APPROVED / P12_2_VALIDATED

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

Rules:

- a portfolio record does not activate collection;
- portfolio approval does not establish independent corroboration;
- source identity conflicts fail closed;
- operational availability requires approved review state;
- approved sources require assigned adapter identity/version;
- paid provider approval requires separate explicit approval;
- no Phase 12 gate approves a paid provider by itself.

## P12.2 Adapter Governance

P12.2 validates a reusable governed public-adapter layer.

A framework adapter may collect only when its current portfolio record:

- exists and is `APPROVED`;
- is operational (`ACTIVE` or `DEGRADED`);
- matches canonical source name/class;
- is `PUBLIC_ANONYMOUS` with authentication `NONE` and data classification `PUBLIC`;
- matches the exact declared adapter ID/version;
- approves HTTPS;
- explicitly allows the adapter request hostname.

Public-anonymous acquisition rejects non-HTTPS URLs, URL credentials and credential-bearing headers.

Adapter/source/domain count remains operational metadata, not independent-origin count.

## Provenance / Independence

- same-origin duplicate observations do not increase corroboration;
- reposts, syndication, translations and citations do not create independent origins;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- discovery/index services do not corroborate claims merely by indexing them;
- source reputation/status changes context, not truth;
- portfolio governance changes governance, not truth;
- adapter availability or parser success does not promote verification.

## Validated Starting Live Baseline

- Consilium press-release RSS — Official sources;
- GDELT DOC 2.0 — Structured discovery/index metadata.

P12.2 adds reusable v2 adapter definitions for these known shapes but does not automatically switch or activate runtime integrations.

## Coverage Boundary

Source portfolio/adapter metadata may inform future configured coverage/source-health requirements, but it does not itself change coverage confidence or factual verification confidence. `GLOBAL` remains scope, not proof of exhaustive monitoring.

## Activation Boundary

P12.3 is the next gate. Each authoritative source must have an explicit portfolio/integration record and a P12.2-compatible adapter path before any controlled activation.

No source becomes live solely because it exists in the portfolio or because an adapter class exists.

## Current State

- source/provenance baseline: `VALIDATED`;
- P12.1 source portfolio: `VALIDATED`;
- P12.2 adapter framework: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- current controlled-live source network: 2 validated integrations;
- new external live sources from P12.2: none;
- paid providers: none approved;
- P12.3: `NEXT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
