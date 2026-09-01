# EXTERNAL_INTEGRATIONS

Version: 0.8
Status: APPROVED / P12_2_VALIDATED

## Purpose

Define governance rules for public sources, external services, cross-project resources and non-canonical operator tools.

## P12.1 Source Portfolio Contract

Canonical governance:

- migration `022_source_portfolio_contract.sql`;
- table `source_portfolio_versions`;
- service `src/kgeopolitical_monitor/source_portfolio.py`.

Portfolio versions are immutable. Portfolio approval does not activate collection and does not establish evidence independence.

## P12.2 Live Adapter Framework v2

Validated implementation:

- `src/kgeopolitical_monitor/adapter_framework.py`;
- bounded read-only HTTPS GET transport;
- RSS/Atom parser;
- bounded JSON-list parser;
- reusable public feed and JSON adapter contracts;
- deterministic source/adapter/version/item identity;
- P12.1 review/access/adapter/outbound-host enforcement;
- canonical collection-attempt/provenance compatibility;
- E6 reproducibility compatibility;
- deterministic local fixtures and isolated source failures.

The public-anonymous P12.2 framework rejects non-HTTPS URLs, URL credentials and credential-bearing request headers.

A v2 adapter class does not activate a source. Runtime/source activation remains a separate explicit integration decision.

## Validated Starting Live Integrations

### Consilium Press Releases RSS

- class: Official sources;
- mode: public read-only RSS/HTTPS;
- authentication: none;
- controlled-live baseline: validated;
- P12.2 includes a reusable v2 adapter definition but does not automatically switch runtime configuration.

### GDELT DOC 2.0

- class: Structured data;
- role: discovery/index;
- mode: public read-only HTTPS API;
- authentication: none;
- controlled-live baseline: validated;
- P12.2 includes a reusable v2 JSON adapter definition but does not automatically switch runtime configuration.

GDELT indexing/discovery is not independent factual corroboration of linked publisher claims.

P12.2 activates no additional external live source.

## Phase 12 Integration Policy

- prefer public/free sources first;
- no paid provider is approved by Phase 12 alone;
- source/domain/adapter count is not underlying-origin count;
- repost/syndication/translation/citation does not create independent corroboration;
- deterministic CI must not depend on live source availability;
- live failures remain isolated and visible;
- exact outbound host/protocol requirements must be recorded;
- P12.3 source onboarding must use both P12.1 governance and a P12.2-compatible adapter path.

## Cross-Project Boundary

- architecture: HYBRID;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- no shared runtime database;
- no implicit mixed canonical storage;
- no direct writes to another project's canonical store;
- shared/team runtime requires a new architecture approval.

## Credentials / Paid Providers

Credentialed sources require explicit approval and external secret handling.

A paid source may be documented as planned, but APPROVED paid-provider state requires a separate explicit approval. P12.2 grants none.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me is non-canonical and limited to public, non-sensitive navigation/source material.

## Current State

- P12.1 source-portfolio governance: `VALIDATED`;
- P12.2 adapter framework: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- controlled-live source baseline: Consilium RSS + GDELT DOC 2.0;
- additional live sources activated by P12.2: `NONE`;
- paid providers: `NONE_APPROVED`;
- P12.3 authoritative source pack: `NEXT / NOT_STARTED`;
- public KGM ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
