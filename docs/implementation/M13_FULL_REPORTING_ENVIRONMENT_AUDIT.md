# M13 Full Reporting Environment Delta Audit

Status: M13_DELTA_AUDIT_PASS
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 10 - Full Reporting Environment

## Purpose

Determine the exact implementation delta between the approved reporting model and the validated M12 repository state without creating a parallel truth or output stack.

## Canonical Reporting Requirements

The approved REPORTING_MODEL defines these user-facing report classes:

- Strategic Alert;
- Global Geopolitical Brief;
- Regional / Country Brief;
- Storyline Report;
- Event Dossier;
- Forecast Report;
- Strategic Outlook.

Substantial reports begin with a short summary and may contain:

- critical events;
- changes;
- context;
- impact;
- forecast;
- confidence;
- sources.

Optional deeper detail includes timeline, evidence analysis, contradictions, scenarios and relationship analysis.

## Repository Audit Result

### 1. No canonical report runtime currently exists

The source tree contains no reporting module, report repository, report migration or report acceptance test.

This means M13 does not need to migrate or preserve a competing report engine. It can introduce the first canonical reporting assembly layer.

### 2. Operational findings are already report-ready inputs

`operational_output.py` persists:

- finding identity;
- watch/run identity;
- title and summary;
- importance;
- confidence;
- evidence references;
- explanation;
- creation time.

Reporting must reference these persisted findings rather than copy them into a new finding truth model.

### 3. Strategic alerts are already durable report inputs

`strategic_alerts.py` persists:

- alert identity and lifecycle status;
- watch/finding linkage;
- priority;
- evidence references;
- explanation;
- immutable alert events.

A Strategic Alert report is therefore a presentation snapshot of existing alert state and evidence, not a second alert implementation.

### 4. Region/language scope is already durable metadata

`region_language_coverage.py` provides canonical region/language definitions, watch scopes, observation attribution and coverage reports.

Regional/Country Brief assembly should use these existing scope contracts. Region/language metadata must not affect verification confidence or source independence.

### 5. Advanced graph queries are already explainable inputs

M11 `IntelligenceQuery` exposes:

- canonical node references;
- graph edge identities;
- evidence references;
- temporal `as_of` state;
- bounded relationship/causal paths.

Reporting must consume these query results as analytical context. It must not recalculate graph confidence or convert graph inference into source evidence.

### 6. Advanced forecast queries are already explainable inputs

M12 `AdvancedForecastQuery` exposes:

- current forecast and immutable version history;
- scenario comparison;
- typed provenance;
- outcome/evaluation history;
- calibration history.

Forecast reports must preserve the distinction between forecast probability, scenario confidence and evidence verification confidence.

### 7. Canonical events are minimal but durable

The `events` table currently provides canonical event identity, title, status and importance.

Event dossiers may enrich presentation through explicit linked findings, claims, graph projections and source references, but the reporting layer must not invent missing event truth or mutate the canonical event row.

### 8. No durable canonical storyline entity exists

No storyline table or approved durable storyline repository exists in the current migration set.

Therefore M13 must not introduce an implicit storyline Source of Truth inside reporting. A Storyline Report baseline may be assembled only from an explicit report scope plus validated canonical references. A future dedicated storyline domain store would require its own architecture/domain approval.

### 9. Current output surfaces are fragmented, not contradictory

The repository has validated output/query surfaces for findings, alerts, coverage, graph intelligence and forecasts. They are complementary and can be converged through one report assembly contract.

The missing capability is not analysis. The missing capability is reproducible, typed, immutable, provenance-preserving report assembly and rendering.

## Required M13 Delta

M13 should implement one reporting subsystem with these responsibilities:

1. Define canonical report types and subject/scope contracts.
2. Persist immutable report snapshots with deterministic identities.
3. Persist typed references to upstream project-local objects rather than copying truth state.
4. Persist ordered report sections as presentation snapshots.
5. Validate every durable upstream reference fail-closed.
6. Assemble Strategic Alert, Global, Regional/Country, Storyline, Event, Forecast and Strategic Outlook report forms through one common pipeline.
7. Preserve explicit labels for FACT/VERIFICATION/GRAPH_INFERENCE/FORECAST/ASSUMPTION presentation classes.
8. Preserve source/evidence/forecast provenance in every relevant section.
9. Provide deterministic text/structured rendering from the same report snapshot.
10. Prove reporting cannot mutate M8 verification, M11 graph state, M12 forecast state or source-independence counts.
11. Keep runtime storage PROJECT_LOCAL_ONLY.

## Canonical Reporting Principle

A report is a reproducible analytical presentation snapshot.

A report is not:

- a new canonical event store;
- a new claim/evidence store;
- a graph inference engine;
- a forecasting engine;
- a verification engine;
- a storyline truth store;
- an external publishing side effect.

## Recommended Durable Shape

Use one project-local reporting schema:

- `report_snapshots` - immutable report identity, type, scope, title, summary, as-of timestamp and creation metadata;
- `report_sections` - ordered immutable section payloads and presentation class;
- `report_references` - typed references to existing project-local objects and source/evidence identifiers.

Avoid report-type-specific storage tables unless a later validated requirement cannot be represented by the common contract.

## Audit Gate

`M13_FULL_REPORTING_DELTA_AUDIT_PASS = PASS`

## Boundary

This audit does not approve external publishing, email/chat delivery, production dashboards, shared runtime storage or any new truth store.
