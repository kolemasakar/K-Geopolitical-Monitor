# M11 Advanced Geopolitical Graph Plan

Status: COMPLETED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 8 - Advanced Geopolitical Graph

## Goal

Extend the validated M4 knowledge-graph baseline into one durable, explainable, project-local geopolitical graph that connects actors, events and evidence-backed relationships without duplicating canonical project truth.

## Architecture Rule

M11 is an extension and convergence milestone, not a replacement graph subsystem.

Canonical project objects remain the Source of Truth. The graph is a deterministic projection and intelligence layer.

Runtime storage remains PROJECT_LOCAL_ONLY.

## Mandatory Boundaries

- No shared or mixed runtime database.
- No external graph database or hosted graph provider in the M11 baseline.
- Graph inference is not source evidence.
- Graph confidence must not increase M8 claim confidence or independent-origin count.
- Graph operations must not automatically assign VERIFIED status.
- Existing M4 public behavior remains compatible.
- Persisted analytical relationships retain evidence/provenance references and explanations.
- Invalidation preserves history rather than destructively deleting the relationship.

## Completed Gates

### M11.1 Graph Convergence and Durable Schema

Result: PASS

Delivered:
- migration `010_advanced_geopolitical_graph.sql`;
- durable graph node, edge, edge-evidence and edge-history tables;
- deterministic graph identities;
- M4 compatibility projection;
- project-local SQLite graph repository.

Gate:
M11_1_GRAPH_CONVERGENCE_VALIDATED = PASS

### M11.2 Actor and Event Projection

Result: PASS

Delivered:
- explicit canonical actor-reference projection;
- canonical event projection;
- explicit M8 claim and operational finding reference nodes;
- restart persistence and repeated-projection idempotence;
- same-project database enforcement.

Gate:
M11_2_ACTOR_EVENT_PROJECTION_VALIDATED = PASS

### M11.3 Evidence-Backed Relationship Lifecycle

Result: PASS

Delivered:
- typed relationship classes;
- SUPPORTS / CONTRADICTS / CONTEXT evidence roles;
- ACTIVE / UPDATED / INVALIDATED / RESOLVED lifecycle;
- material change history;
- evidence accumulation without duplicate logical edges;
- graph-local confidence semantics.

Gate:
M11_3_RELATIONSHIP_LIFECYCLE_VALIDATED = PASS

### M11.4 Temporal and Causal Graph

Result: PASS

Delivered:
- historical state reconstruction;
- valid_from / valid_to filtering;
- current and historical snapshots;
- bounded cycle-safe CAUSAL / INFLUENCE traversal;
- deterministic semantic ordering;
- current-state exclusion of invalidated/resolved relationships.

Gate:
M11_4_TEMPORAL_CAUSAL_GRAPH_VALIDATED = PASS

### M11.5 Advanced Intelligence Query

Result: PASS

Delivered by extending `IntelligenceQuery` rather than replacing it:
- direct neighborhood;
- bounded multi-hop paths;
- actor-to-actor relationships;
- actor-to-event participation;
- current vs historical relationship state;
- causal/influence paths;
- graph-ID, canonical-reference and evidence-reference explanations.

Gate:
M11_5_ADVANCED_QUERY_VALIDATED = PASS

### M11.6 Isolation and Regression Gate

Result: PASS

Validated:
- M4 acceptance compatibility;
- migration idempotence;
- graph restart persistence;
- repeated projection idempotence;
- lifecycle history persistence;
- graph operations do not change M8 claim confidence;
- graph operations do not change independent-origin count;
- M10 region/language and translation metadata does not create source independence;
- runtime storage remains project-local;
- no external graph provider is required;
- full deterministic repository regression passes.

Final gate evidence:
- GitHub Actions run 32973378757;
- 118 passed in 4.24s.

Gate:
M11_ADVANCED_GEOPOLITICAL_GRAPH_BASELINE_PASS = PASS

## Completion Boundary

M11 is complete.

ROADMAP Phase 8 Advanced Geopolitical Graph engineering baseline: BASELINE_VALIDATED.

M11 completion does not approve production/global operational status, shared runtime storage, external graph providers, automatic verification promotion, external notification providers or automatic translation providers.

## Next

ROADMAP Phase 9 - Advanced Forecasting.

Next engineering work package: M12 Advanced Forecasting preparation and delta audit.
