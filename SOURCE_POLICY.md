# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.4
Status: APPROVED / P12_4_VALIDATED

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

European Commission, GOV.UK and OSCE remain `ACTIVE`. European Parliament remains `DEGRADED` for unattended RSS because the official endpoint returns anti-bot HTML. The parser fails closed; no bypass or third-party canonical mirror is approved.

## P12.4 Local-Language / Media Discovery Pack

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

Validated first language slice:
- `uk` — Ukrainska Pravda — `ACTIVE`;
- `ru` — Meduza — `ACTIVE`;
- `pl` — RMF24 — `ACTIVE`;
- `tr` — Haberturk — `ACTIVE`.

P12.4 media sources are discovery inputs. A media publication may derive from the outlet's own reporting, an official statement, a wire service, another publisher, social content or unresolved/combined origins. Publisher identity therefore cannot be promoted to underlying-origin identity.

Original-language text is preserved. Translation remains a separate derived representation and does not create an independent source/origin.

The initial `uk/ru/pl/tr` slice is not global language coverage. Missing local languages, publishers, inaccessible/removed/closed sources and not-yet-indexed material remain explicit gaps.

## Provenance / Independence

- same-origin duplicate observations do not increase corroboration;
- reposts, syndication, translations and citations do not create independent origins;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- discovery/index services do not corroborate claims merely by indexing them;
- media publication does not establish underlying-origin independence;
- source reputation/status changes context, not truth;
- portfolio governance changes governance, not truth;
- adapter availability/parser success changes operational state, not verification;
- source/domain/adapter/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count.

## Coverage Boundary

Source portfolio/adapter/live-health/language metadata may inform configured coverage and P12.5 source-health assessment, but does not itself change factual verification confidence or prove exhaustive coverage. `GLOBAL` remains scope, not proof of completeness.

## Activation Boundary

P12.4 validates governed media-discovery acquisition behavior; it does not declare system-wide production/live operation. P12.5 measures source health/freshness and egress inventory before any egress restriction decision.

No source becomes evidentially independent solely because it is approved, active, in another language or parsed successfully.

## Current State

- source/provenance baseline: `VALIDATED`;
- P12.1 source portfolio: `VALIDATED`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 authoritative source pack: `VALIDATED`;
- P12.4 local-language/media discovery: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5: `NEXT / NOT_STARTED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
