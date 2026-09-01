# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.4
Status: APPROVED / IMPLEMENTED_BASELINE / P12_4_VALIDATED

## Principle

Data provenance must be preserved from acquisition through analytical and operational outputs. Governance, adapter, language or analytical metadata must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The project-local model includes source identity/raw items, immutable source-portfolio versions, collection attempts/provenance, reproducibility audit metadata, translations, source reputation/status, claims/evidence/events, monitoring/alerts, region-language coverage, graph, forecasts/calibration, reporting and owner-only runtime-health state.

## P12.1 Source Portfolio Model

`source_portfolio_versions` remains immutable governance metadata over canonical source identity. It does not activate collection, establish independent-origin credit, promote verification or modify coverage confidence.

## P12.2–P12.4 Data Boundary

P12.2, P12.3 and P12.4 introduce no new canonical database table or migration beyond validated migration 022.

P12.4 intentionally reuses:
- `sources` for canonical media-source identity;
- `source_portfolio_versions` for region/language/access/adapter/outbound/availability governance;
- `source_collection_runs` / `source_collection_attempts` for collection audit;
- `raw_items` and `live_source_provenance` for original-language parsed acquisition;
- existing translation storage for later derived representations;
- E6 reproducibility tables for query/adapter/artifact audit.

P12.4 pack membership and `content_language` metadata are not parallel evidence stores and do not establish underlying-origin independence.

Original language is retained at acquisition. Translation remains derived and does not create another source, observation origin or verification promotion.

## Retained P12.3 Availability State

European Parliament `DEGRADED` remains operational portfolio state caused by anti-bot HTML returned by the official RSS endpoint to unattended acquisition. It cannot directly change claim truth or independent-origin count.

## P12.4 Availability State

At controlled-live validation, Ukrainska Pravda, Meduza, RMF24 and Haberturk acquisition/parser paths were `ACTIVE`. This records one operational observation rather than continuous uptime.

## Boundaries

- translation remains derived and does not create independent origin;
- source reputation remains contextual and separate from portfolio governance;
- adapter/parser/acquisition state is operational, not evidence truth;
- official-source status proves institutional publication/statement, not automatically the underlying event;
- media publisher identity does not prove underlying-origin identity;
- language/source/adapter count does not strengthen factual confidence;
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
- P12.4 local-language/media discovery: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`;
- P12.5: `NEXT / NOT_STARTED`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
