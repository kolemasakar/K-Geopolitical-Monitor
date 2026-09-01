# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.3
Status: APPROVED / IMPLEMENTED_BASELINE / P12_3_VALIDATED

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, claims/evidence/events, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## P12.1 Source Portfolio Model

`source_portfolio_versions` remains immutable governance metadata over canonical source identity. It does not activate collection, establish independent-origin credit, promote verification or modify coverage confidence.

## P12.2 / P12.3 Data Boundary

P12.2 and P12.3 introduce no new canonical database table or migration beyond validated migration 022.

P12.3 intentionally reuses:
- `sources` for canonical source identity;
- `source_portfolio_versions` for pack governance and availability state;
- `source_collection_runs` / `source_collection_attempts` for collection audit;
- `raw_items` and `live_source_provenance` for parsed acquisition;
- E6 reproducibility tables for query/adapter/artifact audit.

P12.3 pack membership is code/configuration governance, not a parallel evidence store.

European Parliament `DEGRADED` is operational portfolio state. It cannot directly change claim truth, verification confidence or independent-origin count.

## Boundaries

- translation remains derived and does not create independent origin;
- source reputation remains contextual and separate from portfolio governance;
- adapter/parser/acquisition state is operational, not evidence truth;
- official-source status proves institutional publication/statement, not automatically the underlying event;
- graph inference is analytical, not source evidence;
- forecast probability/confidence does not change factual verification;
- report rendering cannot strengthen evidence;
- coverage metrics cannot strengthen factual confidence;
- Phase 13 semantic verification v2 is not implemented by Phase 12.

## Runtime Storage Boundary

- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved.

## Current State

- migration 022/source portfolio: `VALIDATED`;
- P12.1: `VALIDATED`;
- P12.2 schema mutation: `NONE`;
- P12.2 adapter framework: `VALIDATED`;
- P12.3 schema mutation: `NONE`;
- P12.3 authoritative source pack: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`;
- P12.4: `NEXT / NOT_STARTED`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
