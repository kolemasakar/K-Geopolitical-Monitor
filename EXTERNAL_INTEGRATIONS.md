# EXTERNAL_INTEGRATIONS

Version: 0.5
Status: APPROVED / ROADMAP_V4_PHASE_12_BASELINE

## Purpose

Define rules for public sources, external services, cross-project resources and integrations.

## Integration Categories

- public data/source feeds;
- external APIs;
- authentication services;
- AI services;
- storage services;
- monitoring/delivery services;
- cross-project repositories and shared-infrastructure resources;
- non-canonical operator/navigation tools.

## Required Integration Record

Each integration requires an explicit record containing, as applicable:
- purpose;
- owner/reviewer;
- provider/source and canonical identity;
- source/integration class and role;
- data exchanged and data classification;
- region/language scope when relevant;
- public/free/credentialed access mode;
- authentication mode;
- expected freshness/cadence;
- adapter/parser identity/version;
- required outbound destination/protocol;
- licensing/terms notes where relevant;
- Source of Truth;
- provenance/origin characteristics and independence caveats;
- fallback/replacement strategy;
- failure-isolation rule;
- operational impact;
- approval/review status.

P12.1 will formalize this into a versioned source-portfolio contract. This document does not claim that P12.1 is already implemented.

## Cross-Project Rule

`ADR_M5_SHARED_INFRASTRUCTURE.md` remains approved and establishes HYBRID architecture with `PROJECT_LOCAL_ONLY` runtime storage.

Current rules:
- no shared runtime database;
- no implicit mixed canonical storage;
- no direct write access to another project's canonical store;
- cross-project exchange requires an explicit versioned contract/export/API;
- cross-project reads remain external integrations unless a later architecture decision promotes them;
- failures in one project must not corrupt another project's canonical state.

Any future shared/team runtime or cross-project canonical write capability requires a new explicit architecture approval.

## Validated Starting Live Integrations

### Consilium Press Releases RSS

Status: `APPROVED_FOR_CONTROLLED_LIVE_BASELINE`
Class: Official sources
Mode: public read-only RSS; no authentication
Record: `docs/integrations/CONSILIUM_RSS_CONTROLLED_PILOT.md`
Live smoke: PASS

### GDELT DOC 2.0 API

Status: `APPROVED_FOR_CONTROLLED_LIVE_BASELINE`
Class: Structured discovery/index data
Mode: public read-only HTTPS API; no authentication
Record: `docs/integrations/GDELT_DOC2_CONTROLLED_PILOT.md`
Live smoke: PASS

GDELT is discovery/index metadata only. Discovering or indexing a publisher link does not create independent factual corroboration.

These two integrations are the validated starting baseline for Phase 12; they are not evidence of broad/global source coverage.

## Phase 12 Integration Policy

Phase 12 is approved to broaden the public-source network, but each source remains separately governed.

Rules:
- prefer public/free sources first;
- no paid provider is activated by ROADMAP v4 or Phase 12 alone;
- read-only HTTPS/RSS/Atom/JSON/other explicitly approved public acquisition is preferred;
- source/adaptor/domain count is not underlying-origin independence count;
- repost/syndication/translation/citation do not create independent corroboration;
- a discovery/index provider is not factual corroboration merely by surfacing a link;
- local-language gaps remain visible rather than being masked by translation;
- transport timeout, payload/pagination/record limits and parser identity must be explicit in the adapter framework;
- deterministic CI must use fixtures and must not depend on live source availability;
- controlled-live checks remain separate from deterministic regression;
- collection attempts/failures must remain persisted/visible where the source framework provides such state.

## Failure Boundary

- external-source failures fail closed at the affected adapter;
- failures remain visible in collection-attempt/audit state;
- one source failure must not block/corrupt another source adapter or canonical state;
- unavailable/stale/parser/network states must not be silently converted to success;
- external provider availability does not strengthen verification or coverage confidence.

## Network / Egress Boundary

The current owner-only candidate runtime retains broad outbound egress as an explicit owner-approved exception.

P12.5 owns creation of the real source/service destination and protocol inventory. No egress allowlist restriction is authorized merely by this document.

Public KGM application ingress remains not approved/not deployed. Public SSH TCP/22 remains the separate owner administrative exception.

## Credential / Secret Boundary

- credentials are not stored in repository files;
- credentialed sources require explicit approval and platform/environment secret handling;
- secret-bearing URLs/commands must not enter routine logs or integration records;
- Phase 12 source expansion does not itself authorize credentials or paid services.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me may hold public URLs/RSS/source names/classes and public analytical/navigation resources only. It is non-canonical and cannot hold credentials, private endpoints, runtime state, private findings/alerts, sensitive data, canonical evidence/provenance or coverage authority.

## Current State

- validated controlled-live starting integrations: `2` (Consilium RSS, GDELT DOC 2.0);
- controlled live-source acquisition: `VALIDATED_BASELINE`;
- ROADMAP v4 Phase 12 source-network expansion: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P12.0 canonical convergence: `IN_PROGRESS`;
- additional Phase 12 sources: `NOT_YET_APPROVED_BY_P12_0`;
- paid providers: `NONE_APPROVED`;
- cross-project runtime sharing: `BLOCKED_BY_PROJECT_LOCAL_ONLY_BOUNDARY`;
- public KGM API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
