# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.4
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_3_VALIDATED

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and public-source breadth.

Current numbered phase:
`Phase 12 — Intelligence Quality and Source Network Foundation`

Validated gates:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`.

Next activity:
`P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK / NEXT_NOT_STARTED`.

## Logical Architecture

`Public Sources -> Source Portfolio -> Governed Adapter Framework -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Source / Governance Boundary

- `sources` remains canonical source identity;
- immutable `source_portfolio_versions` carries P12.1 governance;
- P12.2 governed adapters enforce approved public access, adapter identity/version and outbound host;
- P12.3 authoritative source pack uses these existing layers and creates no parallel truth store;
- portfolio approval or pack membership does not establish evidence independence;
- acquisition availability does not determine factual truth.

## P12.3 Authoritative Source Pack

Governed source states:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

European Parliament degradation is caused by the official RSS endpoint returning anti-bot HTML to the unattended runner. The official endpoint is retained; no bypass or third-party canonical mirror is introduced.

Controlled-live failure isolation is validated: one degraded source does not invalidate the other source attempts or collection audit.

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

## External Integration Boundary

Validated starting integrations remain Consilium press-release RSS and GDELT DOC 2.0 discovery/index metadata. P12.3 additionally validates the governed authoritative pack above.

GDELT discovery is not independent factual corroboration.

Phase 12 rules:
- public/free first;
- explicit source-portfolio/integration governance;
- exact source/adapter identity;
- read-only/fail-closed acquisition;
- deterministic fixture testing independent of live networks;
- isolated and visible source failures/degradation;
- explicit outbound host/protocol inventory;
- no paid provider approval by Phase 12 alone.

## Truth Boundary

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements prove what was stated, not automatically the underlying event;
- source reputation, portfolio approval and adapter availability do not determine truth;
- adapter/source/domain/item count is not independent-origin count;
- graph inference cannot promote verification;
- forecast probability/confidence cannot promote factual verification;
- coverage metrics cannot promote factual confidence;
- report rendering cannot strengthen evidence;
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
- P12.0-P12.3: `VALIDATED`;
- P12.4: `NEXT / NOT_STARTED`;
- P12.3 controlled-live acquisition: 3 `ACTIVE`, 1 European Parliament `DEGRADED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
