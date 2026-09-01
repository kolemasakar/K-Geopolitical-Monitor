# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.3
Status: APPROVED / P12_3_VALIDATED

## Core Principle

Source quantity does not equal source independence. Publisher/domain/adapter/item identity is not automatically underlying-origin identity.

## Source Classes

Approved baseline classes remain Official sources, International media, Regional media, Social platforms, OSINT, Structured data and User-provided information. P12.1 source roles are separate governance metadata.

## Source Portfolio / Adapter Governance

P12.1 immutable portfolio records and P12.2 governed adapters preserve:

- portfolio registration does not activate collection;
- portfolio approval does not establish independent corroboration;
- approved public sources require exact adapter identity/version and outbound HTTPS host;
- public-anonymous acquisition rejects credentials and non-HTTPS requests;
- `ACTIVE` and `DEGRADED` are operational availability states, not truth values;
- paid provider approval requires separate explicit owner approval.

## P12.3 Authoritative Pack

Validated governed sources:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

The European Parliament official RSS endpoint returns anti-bot HTML to the unattended runner. The P12.2 parser fails closed; no bypass or third-party canonical mirror is approved.

Controlled-live source-specific failure isolation is validated. A degraded endpoint remains visible rather than being removed from evidence about source health.

## Provenance / Independence

- same-origin duplicate observations do not increase corroboration;
- reposts, syndication, translations and citations do not create independent origins;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- discovery/index services do not corroborate claims merely by indexing them;
- source reputation/status changes context, not truth;
- portfolio governance changes governance, not truth;
- adapter availability/parser success changes operational state, not verification;
- source/domain/adapter/item count is not independent-origin count.

## Coverage Boundary

Source portfolio/adapter/live-health metadata may inform configured coverage and future P12.5 source-health assessment, but does not itself change factual verification confidence or prove exhaustive coverage. `GLOBAL` remains scope, not proof of completeness.

## Activation Boundary

P12.3 validates a governed pack and controlled-live acquisition behavior; it does not declare system-wide production/live operation. P12.4 discovery-source expansion must use the same P12.1/P12.2 governance path.

No source becomes evidentially independent solely because it is approved, active or parsed successfully.

## Current State

- source/provenance baseline: `VALIDATED`;
- P12.1 source portfolio: `VALIDATED`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 authoritative source pack: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.3 live state: 3 `ACTIVE`, European Parliament `DEGRADED`;
- paid providers: none approved;
- P12.4: `NEXT / NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
