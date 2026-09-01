# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.1
Status: APPROVED / IMPLEMENTED_BASELINE / P12_1_VALIDATED

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes:

- `sources` and raw source items;
- immutable versioned `source_portfolio_versions`;
- source collection attempts/audit and reproducibility metadata;
- translations as derived representations;
- append-only source reputation/status history;
- claims/evidence/events;
- monitoring watches/runs/findings and alerts;
- region/language attribution and coverage;
- geopolitical graph;
- forecasts/scenarios/outcomes/calibration;
- report snapshots/references;
- owner-only runtime-health state.

## P12.1 Source Portfolio Model

`source_portfolio_versions` is additive governance metadata over the existing canonical source identity.

It records source/publisher identity, class/role, region/language, access/cost/authentication, freshness/cadence, adapter identity/version, outbound host/protocol, fallback, availability, data classification, provenance/origin characteristics, independence constraints, terms, owner/reviewer/review state and paid-provider approval state.

Properties:

- immutable versions;
- monotonically increasing per-source version numbers;
- supersession links;
- current state derived from latest version;
- no new parallel source truth store;
- no collection activation semantics;
- no verification/independence/coverage promotion semantics.

## Boundaries

- translation remains derived and does not create independent origin;
- source reputation remains contextual and separate from portfolio governance;
- graph inference is analytical, not source evidence;
- forecast probability/confidence does not change factual verification;
- report rendering cannot strengthen evidence;
- coverage metrics cannot strengthen factual confidence;
- Phase 13 semantic verification v2 is not implemented by P12.1.

## Runtime Storage Boundary

- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- P12.1: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- P12.2: `NEXT / NOT_STARTED`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
