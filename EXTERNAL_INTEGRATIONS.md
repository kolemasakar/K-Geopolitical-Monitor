# EXTERNAL_INTEGRATIONS

Version: 0.9
Status: APPROVED / P12_3_VALIDATED

## Purpose

Define governance rules for public sources, external services, cross-project resources and non-canonical operator tools.

## P12.1 / P12.2 Foundation

- immutable `source_portfolio_versions` govern source identity/access/adapter/outbound requirements;
- portfolio approval does not activate collection or establish evidence independence;
- P12.2 provides bounded read-only HTTPS, deterministic RSS/Atom/JSON parsing, exact adapter identity/version and governed outbound-host enforcement;
- deterministic CI remains independent of live source availability;
- one source failure remains isolated and visible.

## Validated Starting Live Integrations

### Consilium Press Releases RSS
- Official sources;
- public read-only RSS/HTTPS;
- authentication none;
- controlled-live baseline validated.

### GDELT DOC 2.0
- Structured data / discovery-index role;
- public read-only HTTPS API;
- authentication none;
- controlled-live baseline validated.

GDELT indexing/discovery is not independent factual corroboration.

## P12.3 Priority Authoritative Source Pack

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`.

Governed source states after deterministic and controlled-live validation:

- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

Controlled-live validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`:
- repeat live run `33527433106`, job `99921745640`;
- 3 source acquisitions succeeded;
- European Parliament failed closed because the official endpoint returned anti-bot HTML rather than valid XML;
- source-specific failure isolation passed.

The European Parliament official endpoint remains canonical. No anti-bot bypass or third-party mirror substitution is approved.

## Phase 12 Integration Policy

- prefer public/free sources first;
- no paid provider is approved by Phase 12 alone;
- source/domain/adapter/item count is not underlying-origin count;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status confirms institutional publication/statement, not automatically the underlying event;
- deterministic CI must not depend on live source availability;
- live failures/degradation remain isolated and visible;
- exact outbound host/protocol requirements must be recorded;
- P12.4 discovery-source onboarding must continue to use P12.1 governance and P12.2-compatible adapter paths.

## Cross-Project Boundary

- architecture: HYBRID;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- no shared runtime database;
- no implicit mixed canonical storage;
- no direct writes to another project's canonical store;
- shared/team runtime requires a new architecture approval.

## Credentials / Paid Providers

Credentialed sources require explicit approval and external secret handling. A paid source may be planned, but APPROVED paid-provider state requires a separate explicit owner approval.

Paid providers: `NONE_APPROVED`.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me is non-canonical and limited to public, non-sensitive navigation/source material.

## Current State

- P12.1 source-portfolio governance: `VALIDATED`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 authoritative source pack: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.3 live availability: 3 `ACTIVE`, European Parliament `DEGRADED`;
- P12.4: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- public KGM ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
