# EXTERNAL_INTEGRATIONS

Version: 0.6
Status: APPROVED / ROADMAP_V4_PHASE_12_BASELINE / P12_0_VALIDATED

## Purpose

Define rules for public sources, external services, cross-project resources and integrations.

## Required Integration Record

Each integration requires an explicit record covering, as applicable: purpose/owner, provider/source identity, source class/role, exchanged data and classification, region/language, public/free/credentialed access, authentication, freshness/cadence, adapter/parser identity/version, required outbound destination/protocol, licensing/terms, Source of Truth, provenance/origin characteristics and independence caveats, fallback/replacement, failure isolation, operational impact and approval state.

P12.1 will formalize this into a versioned source-portfolio contract. `P12.1 = NEXT / NOT_STARTED`.

## Cross-Project Rule

`ADR_M5_SHARED_INFRASTRUCTURE.md` remains approved and establishes HYBRID architecture with `PROJECT_LOCAL_ONLY` runtime storage.

- no shared runtime database;
- no implicit mixed canonical storage;
- no direct write access to another project's canonical store;
- cross-project exchange requires an explicit versioned contract/export/API;
- failures in one project must not corrupt another project's canonical state;
- shared/team runtime or cross-project canonical write capability requires a new architecture approval.

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

GDELT discovery/index metadata does not itself provide independent factual corroboration of linked publisher claims.

These two integrations remain the validated starting Phase 12 baseline; they are not evidence of broad/global source coverage.

## Phase 12 Integration Policy

- prefer public/free sources first;
- no paid provider is activated by Phase 12 alone;
- prefer read-only HTTPS/RSS/Atom/JSON/other explicitly approved public acquisition;
- source/adapter/domain count is not underlying-origin independence count;
- repost/syndication/translation/citation do not create independent corroboration;
- discovery/index providers are not factual corroboration merely by surfacing links;
- local-language gaps remain visible;
- timeouts, payload/pagination/record limits and parser identity must be explicit in the adapter framework;
- deterministic CI uses fixtures and does not depend on live source availability;
- controlled-live checks remain separate from deterministic regression;
- collection failures remain visible where the source framework provides such state.

P12.0 was documentation convergence only and activated no new source/integration.

## Failure Boundary

External-source failures fail closed at the affected adapter, remain visible and must not block/corrupt another source adapter or canonical state. Unavailable/stale/parser/network states must not silently become success. Provider availability does not strengthen verification or coverage confidence.

## Network / Egress Boundary

Broad outbound egress remains an explicit owner-approved candidate exception. P12.5 owns the real source/service destination/protocol inventory. No egress allowlist restriction is authorized merely by Phase 12 documentation.

Public KGM application ingress remains not approved/not deployed. Public SSH TCP/22 remains the separate owner administrative exception.

## Credential / Secret Boundary

Credentials are not stored in repository files. Credentialed sources require explicit approval and platform/environment secret handling. Phase 12 source expansion does not itself authorize credentials or paid services.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me may hold public URLs/RSS/source names/classes and public analytical/navigation resources only. It is non-canonical and cannot hold credentials, private endpoints, runtime state, private findings/alerts, sensitive data or canonical evidence/provenance/coverage authority.

## Current State

- controlled-live starting integrations: `2 / VALIDATED_BASELINE` — Consilium RSS and GDELT DOC 2.0;
- Phase 12 source-network expansion: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P12.0 canonical convergence: `VALIDATED`;
- P12.1 source-portfolio contract: `NEXT / NOT_STARTED`;
- additional Phase 12 sources activated by P12.0: `NONE`;
- paid providers: `NONE_APPROVED`;
- cross-project runtime sharing: `BLOCKED_BY_PROJECT_LOCAL_ONLY_BOUNDARY`;
- public KGM API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
