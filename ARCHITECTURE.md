# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.6
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_5_VALIDATED

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and public-source breadth.

Current numbered phase: `Phase 12 — Intelligence Quality and Source Network Foundation`.

Validated gates:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`.

Next activity: `P12.6_PHASE_12_VALIDATION_MATRIX / NEXT_NOT_STARTED`.

## Logical Architecture

`Public Sources -> Source Portfolio -> Governed Adapter Framework -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Source / Governance Boundary

- `sources` remains canonical source identity;
- immutable `source_portfolio_versions` carries P12.1 governance;
- P12.2 governed adapters enforce approved access, adapter identity/version and outbound host;
- P12.3 authoritative and P12.4 media-discovery packs use the same existing layers;
- P12.5 is a read-only assessment layer over portfolio, collection attempts and provenance;
- pack membership does not create a parallel truth/evidence store;
- portfolio approval, language identity, acquisition availability or freshness does not establish evidence independence or factual truth.

## P12.3 Retained Authoritative Pack State

Governed portfolio state:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition because the official endpoint returns non-feed/anti-bot content;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

The European Parliament official endpoint is retained; no bypass or third-party canonical mirror is introduced.

## P12.4 Local-Language Discovery Boundary

P12.4 adds a governed first media/discovery slice:
- `uk` / Ukrainska Pravda;
- `ru` / Meduza;
- `pl` / RMF24;
- `tr` / Haberturk.

All four acquisition/parser paths succeeded in the bounded P12.4 validation probe and were governed `ACTIVE`. This remains historical validation evidence, not continuous-health proof.

P12.4 adapters preserve original Unicode and source URLs. They do not translate. Translation remains a separate derived representation and does not create another source or independent origin.

The initial `uk/ru/pl/tr` slice is not global language coverage. Missing languages, publishers, inaccessible/removed/closed sources and not-yet-indexed material remain explicit gaps.

## P12.5 Health / Freshness / Egress Layer

P12.5 separates:
- governed portfolio availability;
- latest acquisition/adapter operational state;
- measurement freshness;
- observed publisher-content freshness;
- exact governed outbound hostname/protocol requirements.

Validation anchor `92d0c0516351e2af7ba836d3ae711dd414d22023` measured all ten governed paths. Current controlled-live findings included:
- European Parliament: `UNAVAILABLE / PARSER`, governed `DEGRADED` retained;
- Haberturk: `UNAVAILABLE / UNKNOWN` because an item URL failed HTTP/HTTPS validation, governed `ACTIVE` retained pending review;
- OSCE: acquisition `HEALTHY`, observed content `STALE`.

A single observation does not silently mutate portfolio governance. Operational state and content freshness remain separate from truth and evidence independence.

P12.5 inventories ten HTTPS host requirements. The inventory is not a deployed firewall policy.

## Runtime / Storage Boundary

- runtime storage: `PROJECT_LOCAL_ONLY`;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- shared/mixed canonical runtime storage requires new architecture approval.

Runtime storage mode: PROJECT_LOCAL_ONLY
E9 Shared Production Runtime: `NOT_APPROVED`.

## Owner-Only Runtime Boundary

E9A remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Production/live operational status: NOT_OPERATIONAL

P12.5 measured outbound requirements but did not deploy egress restriction. Any restriction requires a separate validated decision.

## Truth Boundary

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements prove what was stated, not automatically the underlying event;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- source reputation, portfolio approval, language identity, adapter availability and freshness do not determine truth;
- adapter/source/domain/item count is not independent-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- graph inference cannot promote verification;
- forecast probability/confidence cannot promote factual verification;
- coverage metrics cannot promote factual confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage.

## Backend / Dashboard / GPT Boundary

- E3 backend API foundation: `BASELINE_VALIDATED / HTTPS_NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- E5 dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public Action/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- public GPT sharing: `USER_DEFERRED`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me remains non-canonical.

## Current State

- ROADMAP: `APPROVED / v4`;
- P12.0-P12.5: `VALIDATED`;
- P12.6: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
