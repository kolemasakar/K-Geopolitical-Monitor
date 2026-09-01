# EXTERNAL_INTEGRATIONS

Version: 1.0
Status: APPROVED / P12_4_VALIDATED

## Purpose

Define governance rules for public sources, external services, cross-project resources and non-canonical operator tools.

## P12.1 / P12.2 Foundation

- immutable `source_portfolio_versions` govern source identity/access/adapter/outbound requirements;
- portfolio approval does not activate collection or establish evidence independence;
- P12.2 provides bounded read-only HTTPS, deterministic RSS/Atom/JSON parsing, exact adapter identity/version and governed outbound-host enforcement;
- deterministic CI remains independent of live source availability;
- one source failure remains isolated and visible.

## Validated Starting Integrations

- Consilium Press Releases RSS — official public read-only RSS/HTTPS;
- GDELT DOC 2.0 — public structured discovery/index metadata.

GDELT indexing/discovery is not independent factual corroboration.

## P12.3 Priority Authoritative Source Pack

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`.

Current governed source states:
- European Commission Press Corner — `ACTIVE`;
- European Parliament Press Releases — `DEGRADED` for unattended RSS acquisition because the official endpoint returns anti-bot HTML;
- UK Government News and Communications — `ACTIVE`;
- OSCE Latest News — `ACTIVE`.

The European Parliament official endpoint remains canonical. No anti-bot bypass or third-party mirror substitution is approved.

## P12.4 Local-Language and Media Discovery Pack

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

Validated first public/free media-discovery slice:
- Ukrainska Pravda — `uk` — `ACTIVE`;
- Meduza — `ru` — `ACTIVE`;
- RMF24 — `pl` — `ACTIVE`;
- Haberturk — `tr` — `ACTIVE`.

Controlled-live validation: run `33531518652`, job `99935565895`, `4 SUCCESS / 0 FAILED`.

The pack preserves original-language Unicode and source URL. Translation remains a separate derived representation. `uk/ru/pl/tr` is a prioritized first slice, not global language coverage.

## Phase 12 Integration Policy

- prefer public/free sources first;
- no paid provider is approved by Phase 12 alone;
- source/domain/adapter/item count is not underlying-origin count;
- media/domain/language/adapter/item count is not independent-origin count;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status confirms institutional publication/statement, not automatically the underlying event;
- media publication confirms publisher publication, not automatically the underlying origin or event;
- deterministic CI must not depend on live source availability;
- live failures/degradation remain isolated and visible;
- exact outbound host/protocol requirements must be recorded;
- P12.5 owns measured health/freshness and egress inventory before egress-restriction decisions.

## Cross-Project Boundary

- architecture: HYBRID;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- no shared runtime database;
- no implicit mixed canonical storage;
- no direct writes to another project's canonical store;
- shared/team runtime requires a new architecture approval.

## Credentials / Paid Providers

Credentialed sources require explicit approval and external secret handling. APPROVED paid-provider state requires separate explicit owner approval.

Paid providers: `NONE_APPROVED`.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me is non-canonical and limited to public, non-sensitive navigation/source material.

## Current State

- P12.1 source-portfolio governance: `VALIDATED`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 authoritative source pack: `VALIDATED`;
- P12.4 local-language/media discovery pack: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- public KGM ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
