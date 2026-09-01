# SOURCE_POLICY
Source management, onboarding and provenance rules.

Version: 2.5
Status: APPROVED / P12_5_VALIDATED

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
- `ACTIVE` and `DEGRADED` are governed operational availability states, not truth values;
- latest measured health/freshness is observation state and does not silently rewrite governance;
- paid provider approval requires separate explicit owner approval.

## P12.3 Authoritative Pack

European Commission, GOV.UK and OSCE remain governed `ACTIVE`. European Parliament remains governed `DEGRADED` for unattended RSS because the official endpoint returns non-feed/anti-bot content. The parser fails closed; no bypass or third-party canonical mirror is approved.

## P12.4 Local-Language / Media Discovery Pack

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

Governed first language slice:
- `uk` — Ukrainska Pravda — `ACTIVE`;
- `ru` — Meduza — `ACTIVE`;
- `pl` — RMF24 — `ACTIVE`;
- `tr` — Haberturk — `ACTIVE`.

P12.4 media sources are discovery inputs. A media publication may derive from the outlet's own reporting, an official statement, a wire service, another publisher, social content or unresolved/combined origins. Publisher identity therefore cannot be promoted to underlying-origin identity.

Original-language text is preserved. Translation remains a separate derived representation and does not create an independent source/origin.

The initial `uk/ru/pl/tr` slice is not global language coverage. Missing local languages, publishers, inaccessible/removed/closed sources and not-yet-indexed material remain explicit gaps.

## P12.5 Operational Measurement

Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`.

P12.5 measures governed source paths without converting availability into evidence truth.

Latest controlled observation:
- European Parliament — `UNAVAILABLE / PARSER`, while governed state remains `DEGRADED`;
- Haberturk — `UNAVAILABLE / UNKNOWN` due invalid item URL validation, while governed state remains `ACTIVE` pending review;
- OSCE — acquisition `HEALTHY` while observed publisher content is `STALE`.

These differences are deliberate: portfolio state describes approved governance; source-health state describes a measured observation. A single probe does not silently rewrite governance.

## Provenance / Independence

- same-origin duplicate observations do not increase corroboration;
- reposts, syndication, translations and citations do not create independent origins;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- discovery/index services do not corroborate claims merely by indexing them;
- media publication does not establish underlying-origin independence;
- source reputation/status changes context, not truth;
- portfolio governance changes governance, not truth;
- adapter availability/parser success/failure and content freshness change operational assessment, not verification;
- source/domain/adapter/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count.

## Coverage Boundary

Source portfolio/adapter/live-health/language metadata may inform configured coverage and source-health assessment, but does not itself change factual verification confidence or prove exhaustive coverage. `GLOBAL` remains scope, not proof of completeness.

Unavailable or stale sources are coverage limitations and must remain visible. They are not evidence that no event occurred.

## Egress Boundary

P12.5 inventories ten required HTTPS hosts. This inventory is not a firewall allowlist. Broad outbound egress remains an explicit owner-approved candidate exception pending a separate validated restriction decision.

## Activation Boundary

P12.4 validates governed media-discovery acquisition behavior; P12.5 validates operational measurement/inventory behavior. Neither declares system-wide production/live operation.

No source becomes evidentially independent solely because it is approved, active, in another language, parsed successfully or currently fresh.

## Current State

- source/provenance baseline: `VALIDATED`;
- P12.1 source portfolio: `VALIDATED`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 authoritative source pack: `VALIDATED`;
- P12.4 local-language/media discovery: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5 health/freshness/egress inventory: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- P12.6: `NEXT / NOT_STARTED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
