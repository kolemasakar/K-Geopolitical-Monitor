# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.2
Status: APPROVED / IMPLEMENTED_BASELINE / P12_2_VALIDATED

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes:

- `sources` and raw source items;
- immutable versioned `source_portfolio_versions`;
- source collection attempts/audit and live-source provenance;
- reproducibility audit/query/artifact metadata;
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

`source_portfolio_versions` is additive immutable governance metadata over the existing canonical source identity.

It does not activate collection, establish independent-origin credit, promote verification or modify coverage confidence.

## P12.2 Adapter Framework Data Boundary

P12.2 introduces no new canonical database table or migration.

The framework intentionally reuses existing validated persistence:

- P12.1 `source_portfolio_versions` for governance;
- `source_collection_runs` and `source_collection_attempts` for collection audit;
- `raw_items` for ingested parsed items;
- `live_source_provenance` for collection-linked original URLs/metadata;
- E6 `research_audit_runs`, `research_query_executions` and artifact hashes for reproducibility.

Adapter identity/version is explicit in framework objects and is linked into existing reproducibility records. Exact remote request locator remains `NOT_INSTRUMENTED` where the existing schema did not actually capture it.

No parallel adapter-specific evidence store is created.

## Boundaries

- translation remains derived and does not create independent origin;
- source reputation remains contextual and separate from portfolio governance;
- adapter/parser success is operational state, not evidence truth;
- graph inference is analytical, not source evidence;
- forecast probability/confidence does not change factual verification;
- report rendering cannot strengthen evidence;
- coverage metrics cannot strengthen factual confidence;
- Phase 13 semantic verification v2 is not implemented by P12.2.

## Runtime Storage Boundary

- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- P12.1: `VALIDATED`;
- P12.2 schema mutation: `NONE`;
- P12.2 adapter framework: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`;
- P12.3: `NEXT / NOT_STARTED`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
