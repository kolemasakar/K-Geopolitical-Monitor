# Phase 12 — Intelligence Quality and Source Network Foundation Plan

Date: 2026-09-01
Status: `APPROVED_FOR_IMPLEMENTATION / P12_1_VALIDATED`
Project: K-Geopolitical Monitor
Roadmap: `ROADMAP.md / v4`

## Objective

Build a materially broader, measurable and maintainable public-source network without weakening provenance/verification/coverage boundaries or claiming exhaustive global monitoring.

Phase 12 does not activate production/live, public publication, shared runtime or paid providers by itself.

## Design Rules

- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- prefer public/free sources first;
- every external source requires explicit governance;
- source/domain/adapter identity is not evidentiary independence;
- publisher is not automatically underlying origin;
- translation remains derived;
- source failures remain isolated/visible;
- deterministic CI must not depend on live networks;
- coverage does not prove universal completeness;
- model/LLM assistance cannot directly promote verification;
- broad egress remains an explicit exception until P12.5 inventory is validated.

## P12.0 — Canonical Convergence

State: `VALIDATED`

Gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`

Result:
`docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md`

## P12.1 — Source Portfolio Contract and Governance

State: `VALIDATED`

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

Implementation:
`docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT.md`

Result:
`docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT_RESULT.md`

Validation:
commit `905a727d85701bf43d18de2d5216b83ab9a2b8bd`; CI `33520371480`; job `99897786494`; `334 passed, 1 warning / SUCCESS`.

Validated contract covers source identity/publisher, class/role, region/language, access/cost/authentication, freshness/cadence, adapter identity/version, outbound host/protocol, fallback, availability, data classification, provenance/origin characteristics, independence constraints, terms, owner/reviewer/review state and paid-provider approval state.

P12.1 activates no new live source and approves no paid provider.

## P12.2 — Live Adapter Framework v2

State: `NEXT / NOT_STARTED`

Required capabilities:

- reusable HTTPS read-only transport;
- bounded timeout/payload/pagination/record limits;
- RSS/Atom/JSON framework support;
- source-specific parsing extensions;
- deterministic source/adapter identity;
- linkage to P12.1 portfolio governance;
- collection-attempt and reproducibility linkage;
- no secret leakage;
- deterministic fixtures;
- source-failure isolation;
- live smoke separate from deterministic regression.

Gate:
`P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

## P12.3 — Priority Authoritative Source Pack

State: `PLANNED`

Select and validate a materially broader authoritative public-source pack across prioritized international organizations and official government/institutional sources.

Each source requires a P12.1 portfolio/integration record.

Gate:
`P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

## P12.4 — Local-Language and Media Discovery Pack

State: `PLANNED`

Expand priority region/language discovery while preserving local-language gaps, translation isolation and underlying-origin uncertainty.

Gate:
`P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

## P12.5 — Source Health and Egress Inventory

State: `PLANNED`

Measure availability, freshness/staleness, adapter/parser errors, drift and exact required outbound destinations/protocols.

Gate:
`P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

## P12.6 — Phase 12 Validation Matrix

State: `PLANNED`

Required evidence:

- full x64 regression;
- full native ARM64 regression;
- source-contract and adapter-fixture validation;
- controlled-live source matrix;
- provenance/origin invariants;
- translation/reputation/coverage isolation;
- reproducibility linkage;
- failure isolation;
- `PROJECT_LOCAL_ONLY`;
- no public ingress;
- no production/live activation.

Phase gate:
`PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## Explicit Non-Goals

Phase 12 does not:

- implement Phase 13 semantic verification v2;
- deploy public API/dashboard;
- connect public GPT Action;
- activate public sharing/Business migration;
- enable shared/team runtime;
- replace SQLite without measured need;
- activate a paid provider without separate approval;
- claim complete global coverage;
- set `PRODUCTION_LIVE = OPERATIONAL`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me remains non-canonical and may contain only public, non-sensitive navigation/source material.

## Exact Start Point

Next engineering activity:

`P12.2_LIVE_ADAPTER_FRAMEWORK_V2`

P12.3 does not begin until P12.2 is validated and saved to canonical state.
