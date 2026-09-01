# EXTERNAL_INTEGRATIONS

Version: 0.7
Status: APPROVED / P12_1_VALIDATED

## Purpose

Define governance rules for public sources, external services, cross-project resources and non-canonical operator tools.

## P12.1 Source Portfolio Contract

P12.1 is validated.

Canonical implementation:

- migration `022_source_portfolio_contract.sql`;
- table `source_portfolio_versions`;
- service `src/kgeopolitical_monitor/source_portfolio.py`.

Every governed source version can record:

- canonical source/publisher identity;
- source class/role;
- region/language scope;
- access/cost/authentication mode;
- freshness/cadence;
- adapter identity/version;
- exact required outbound hostnames/protocols;
- fallback/replacement sources;
- availability/degradation state;
- data classification;
- provenance/origin characteristics and independence constraints;
- licensing/terms notes;
- owner/reviewer/review state.

Portfolio versions are immutable. Portfolio approval does not activate collection and does not establish evidence independence.

## Validated Starting Live Integrations

### Consilium Press Releases RSS

- class: Official sources;
- mode: public read-only RSS/HTTPS;
- authentication: none;
- live baseline: validated.

### GDELT DOC 2.0

- class: Structured data;
- role: discovery/index;
- mode: public read-only HTTPS API;
- authentication: none;
- live baseline: validated.

GDELT indexing/discovery is not independent factual corroboration of linked publisher claims.

P12.1 activates no additional live source.

## Phase 12 Integration Policy

- prefer public/free sources first;
- no paid provider is approved by Phase 12 alone;
- source/domain/adapter count is not underlying-origin count;
- repost/syndication/translation/citation does not create independent corroboration;
- deterministic CI must not depend on live source availability;
- live failures remain isolated and visible;
- exact outbound host/protocol requirements must be recorded;
- new reusable adapter behavior belongs to P12.2;
- P12.2 must link adapter identity to P12.1 governance rather than bypassing it.

## Cross-Project Boundary

- architecture: HYBRID;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- no shared runtime database;
- no implicit mixed canonical storage;
- no direct writes to another project's canonical store;
- shared/team runtime requires a new architecture approval.

## Credentials / Paid Providers

Credentialed sources require explicit approval and external secret handling.

A paid source may be documented as planned, but APPROVED paid-provider state requires a separate explicit approval. P12.1 grants none.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me is non-canonical and limited to public, non-sensitive navigation/source material.

## Current State

- P12.1 source-portfolio governance: `VALIDATED`;
- controlled-live source baseline: Consilium RSS + GDELT DOC 2.0;
- additional live Phase 12 sources: `NONE_ACTIVATED_BY_P12_1`;
- paid providers: `NONE_APPROVED`;
- P12.2 adapter framework: `NEXT / NOT_STARTED`;
- public KGM ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
