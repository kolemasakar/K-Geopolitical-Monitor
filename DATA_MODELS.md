# DATA_MODELS
Canonical data concepts for K-Geopolitical Monitor.

Version: 2.0
Status: APPROVED / IMPLEMENTED_BASELINE

## Principle

Data provenance must be preserved from source acquisition through analytical and operational outputs. Persisted analytical context must not silently become source evidence or factual verification.

## Implemented Canonical Domains

The validated project-local data model includes persisted structures for major domains such as:
- source registry and raw source items;
- collection attempts/audit and reproducibility metadata;
- translations as derived representations;
- source reputation/status history;
- claims, evidence, entities, events, event updates and storylines;
- operational monitoring watches/runs and findings;
- strategic alerts/policies/state/events;
- region/language scope and attribution;
- coverage contracts, snapshots/results and source availability/freshness dimensions;
- geopolitical graph nodes/relationships, lifecycle/history and temporal snapshots;
- forecasts/scenarios, immutable versions, typed provenance, outcomes/evaluations and calibration history;
- report snapshots, sections and typed references;
- runtime lease and owner-only runtime-health instrumentation.

Detailed schema ownership remains in migrations and implementation-specific model/storage modules rather than this summary document.

## Source / Evidence Identity Boundary

Canonical source and publication identity does not automatically equal underlying origin. Evidence independence must preserve origin uncertainty and must not treat duplicate publishers/adapters as independent by default.

## Translation Boundary

Original source text remains immutable. Translations are separately persisted/versioned derived representations that retain origin lineage and cannot create independent-source credit.

## Graph Boundary

Graph state is a durable analytical projection over canonical project objects. Graph inference does not become independent evidence and cannot promote claim verification.

## Forecast Boundary

Forecast scenario probability/confidence objects are analytical state. They cannot modify factual verification or evidence independence.

## Reporting Boundary

Report snapshots/renderings are presentation artifacts over existing canonical state and cannot strengthen upstream truth.

## Coverage Boundary

Coverage objects measure configured monitoring requirements and known assessment state. Coverage confidence is not factual verification confidence and `GLOBAL` is scope, not proof of completeness.

## Runtime Storage Boundary

- canonical runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved;
- direct cross-project canonical mutation: prohibited absent a new explicit architecture decision.

## Phase 12 / Phase 13 Boundary

Phase 12 may add source-portfolio/source-health/adapter metadata under explicit migrations/contracts where required, but P12.0 is documentation convergence only.

The richer structured semantic claim/provenance/contradiction model planned for Phase 13 is not yet implemented and must not be back-claimed by this document.

## Current State

- canonical persisted model: `IMPLEMENTED / BASELINE_VALIDATED` through the existing Phase 0-11 + E1-E7 + E9A engineering line;
- P12.0 schema mutation: `NONE`;
- Phase 13 semantic model v2: `NOT_STARTED`;
- runtime storage: `PROJECT_LOCAL_ONLY`.
