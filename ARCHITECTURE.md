# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.5
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_4_VALIDATED

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and public-source breadth.

Current numbered phase: `Phase 12 — Intelligence Quality and Source Network Foundation`.

Validated gates:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

Next activity: `P12.5_SOURCE_HEALTH_EGRESS_INVENTORY / NEXT_NOT_STARTED`.

## Logical Architecture

`Public Sources -> Source Portfolio -> Governed Adapter Framework -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Source / Governance Boundary

- `sources` remains canonical source identity;
- immutable `source_portfolio_versions` carries P12.1 governance;
- P12.2 governed adapters enforce approved access, adapter identity/version and outbound host;
- P12.3 authoritative and P12.4 media-discovery packs use the same existing layers;
- pack membership does not create a parallel truth/evidence store;
- portfolio approval, language identity or acquisition availability does not establish evidence independence or factual truth.

## P12.3 Retained Authoritative Pack State

- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition because the official endpoint returns anti-bot HTML;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

The European Parliament official endpoint is retained; no bypass or third-party canonical mirror is introduced.

## P12.4 Local-Language Discovery Boundary

P12.4 adds a governed first media/discovery slice:
- `uk` / Ukrainska Pravda;
- `ru` / Meduza;
- `pl` / RMF24;
- `tr` / Haberturk.

All four current controlled-live acquisition/parser paths succeeded at validation and are governed `ACTIVE`. This is an acquisition observation, not continuous-health evidence.

P12.4 adapters preserve original Unicode and source URLs. They do not translate. Translation remains a separate derived representation and does not create another source or independent origin.

The initial `uk/ru/pl/tr` slice is not global language coverage. Missing languages, publishers, inaccessible/removed/closed sources and not-yet-indexed material remain explicit gaps.

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

P12.5 measures the actual source-health/freshness and outbound destination/protocol inventory before any egress-restriction proposal.

## Truth Boundary

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements prove what was stated, not automatically the underlying event;
- official sources are authoritative for their own statements, not automatically for the underlying event;
- source reputation, portfolio approval, language identity and adapter availability do not determine truth;
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
- P12.0-P12.4: `VALIDATED`;
- P12.5: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
