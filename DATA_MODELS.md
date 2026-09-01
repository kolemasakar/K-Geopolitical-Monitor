# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.5
Status: APPROVED / IMPLEMENTED_BASELINE / P12_5_VALIDATED

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language, health, freshness or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, claims/evidence/events, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## P12.1 Source Portfolio Model

`source_portfolio_versions` remains immutable governance metadata over canonical source identity. It does not activate collection, establish independent-origin credit, promote verification or modify coverage confidence.

## P12.2–P12.5 Data Boundary

P12.2, P12.3, P12.4 and P12.5 introduce no new canonical database table or migration beyond validated migration 022.

P12.4 reuses:
- `sources` for canonical media-source identity;
- `source_portfolio_versions` for region/language/access/adapter/outbound/availability governance;
- `source_collection_runs` / `source_collection_attempts` for collection audit;
- `raw_items` and `live_source_provenance` for original-language parsed acquisition;
- existing translation storage for later derived representations;
- E6 reproducibility tables for query/adapter/artifact audit.

P12.5 adds a read-only assessment layer over existing persisted state:
- current `source_portfolio_versions` for governance and expected freshness/cadence;
- `source_collection_attempts` for latest measured SUCCESS/FAILED and attempt time;
- `raw_items` + `live_source_provenance` for observed publication metadata;
- governed outbound-domain/protocol fields for egress inventory.

No P12.5 health snapshot is silently promoted into a new canonical truth table. Reassessment is derived from the persisted observations and current governance.

## Governed vs Measured Operational State

Governed portfolio state and latest measured source-health state are separate data concepts.

Examples from P12.5 controlled validation:
- European Parliament: governed `DEGRADED`, measured `UNAVAILABLE / PARSER`;
- Haberturk: governed `ACTIVE`, measured `UNAVAILABLE / UNKNOWN` for the probe;
- OSCE: governed `ACTIVE`, measured acquisition `HEALTHY`, observed content `STALE`.

A single controlled observation does not mutate immutable governance history.

## Freshness Model

P12.5 separates:
- measurement freshness — recency of the latest persisted attempt;
- content freshness — recency of an actually observed source/publisher timestamp.

When no parseable source timestamp exists, content freshness remains `UNKNOWN`; collection time is not substituted as a publisher timestamp.

## Boundaries

- translation remains derived and does not create independent origin;
- source reputation remains contextual and separate from portfolio governance;
- adapter/parser/acquisition health and content freshness are operational, not evidence truth;
- official-source status proves institutional publication/statement, not automatically the underlying event;
- media publisher identity does not prove underlying-origin identity;
- language/source/adapter/host count does not strengthen factual confidence;
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
- P12.3 schema mutation: `NONE`;
- P12.4 schema mutation: `NONE`;
- P12.5 schema mutation: `NONE`;
- P12.4 local-language/media discovery: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5 source-health/egress assessment: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`;
- P12.6: `NEXT / NOT_STARTED`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
