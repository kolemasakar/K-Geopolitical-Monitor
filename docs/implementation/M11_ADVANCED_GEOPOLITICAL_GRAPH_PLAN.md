# M11 Advanced Geopolitical Graph Plan

Status: ACTIVE
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
- Existing M4 public behavior must remain compatible unless a migration is explicitly documented and tested.
- Every persisted edge that represents an observed or inferred geopolitical relationship must retain provenance/evidence references and an explanation.
- Invalidation must preserve history; destructive deletion is not the baseline lifecycle mechanism.

## Canonical Graph Model

### Graph Node

Required fields:

- node_id;
- node_kind;
- canonical_ref_type;
- canonical_ref_id;
- label;
- attributes_json;
- created_at;
- updated_at.

Baseline node kinds:

- ACTOR;
- EVENT;
- CLAIM;
- FINDING;
- SOURCE;
- REGION.

Actor specialization should use explicit actor metadata rather than a second actor graph store.

### Graph Edge

Required fields:

- edge_id;
- source_node_id;
- target_node_id;
- relation_type;
- relation_class;
- confidence;
- status;
- valid_from;
- valid_to;
- first_observed_at;
- last_observed_at;
- explanation;
- created_at;
- updated_at.

Baseline relation classes:

- STRUCTURAL;
- PARTICIPATION;
- POLITICAL;
- SECURITY;
- ECONOMIC;
- CAUSAL;
- INFLUENCE;
- TEMPORAL;
- CONTEXTUAL.

Baseline edge statuses:

- ACTIVE;
- UPDATED;
- INVALIDATED;
- RESOLVED.

### Edge Evidence

Graph evidence references must be persisted separately from relation identity so that the same relation can accumulate multiple traceable support records without creating duplicate edges.

Required fields:

- edge_id;
- evidence_ref;
- evidence_role;
- added_at.

Baseline evidence roles:

- SUPPORTS;
- CONTRADICTS;
- CONTEXT;

## Deterministic Identity

Graph projection must be idempotent.

- Node identity is deterministic from canonical reference type and canonical reference ID.
- Edge identity is deterministic from source node, target node, relation type and the relation identity contract.
- Reprocessing the same canonical object must not create duplicate nodes or duplicate logical edges.
- New supporting evidence may update the existing edge and its evidence set.

## M11.1 Graph Convergence and Durable Schema

Implement:

- canonical graph dataclasses/contracts;
- migration `010_advanced_geopolitical_graph.sql`;
- durable graph node, edge, edge-evidence and edge-history tables;
- compatibility adapters for validated M4 KnowledgeGraph behavior;
- explicit deprecation path for duplicate M2/M4 in-memory repository fragments without breaking current acceptance tests.

Gate:
M11_1_GRAPH_CONVERGENCE_VALIDATED

## M11.2 Actor and Event Projection

Implement deterministic projection from canonical project objects into graph nodes.

Actor baseline:

- countries;
- governments/organizations;
- persons when explicitly represented;
- other actor types through typed metadata.

Event baseline:

- canonical events;
- M8 live-analysis claims/findings only through explicit reference nodes when required for traceability;
- no graph-generated event may silently become a canonical verified event.

Requirements:

- restart persistence;
- idempotent repeated projection;
- canonical references retained;
- no cross-watch or cross-project leakage.

Gate:
M11_2_ACTOR_EVENT_PROJECTION_VALIDATED

## M11.3 Evidence-Backed Relationship Lifecycle

Extend relationship intelligence with:

- typed geopolitical relation classes;
- provenance/evidence references;
- confidence bounded to 0..1;
- ACTIVE/UPDATED/INVALIDATED/RESOLVED lifecycle;
- evidence accumulation without duplicate edge creation;
- contradiction/context evidence roles;
- preserved history for every material state transition.

Relationship confidence is graph-layer confidence only and must not modify upstream evidence confidence.

Gate:
M11_3_RELATIONSHIP_LIFECYCLE_VALIDATED

## M11.4 Temporal and Causal Graph

Implement:

- valid_from / valid_to intervals;
- first_observed_at / last_observed_at;
- deterministic time-ordered relationship history;
- graph snapshot queries for a requested time;
- causal/influence edge classes;
- bounded causal traversal;
- cycle-safe traversal;
- invalidated relations excluded from current-state queries but retained historically.

Gate:
M11_4_TEMPORAL_CAUSAL_GRAPH_VALIDATED

## M11.5 Advanced Intelligence Query

Extend `IntelligenceQuery` rather than replacing it.

Add deterministic queries for:

- direct neighborhood;
- bounded multi-hop paths;
- actor-to-actor relationships;
- actor-to-event participation;
- current vs historical relation state;
- causal/influence chains;
- evidence-backed explanations.

Every advanced query result must be explainable through graph IDs, canonical references and evidence references.

Gate:
M11_5_ADVANCED_QUERY_VALIDATED

## M11.6 Isolation and Regression Gate

Validate:

- all existing M4 acceptance tests remain green;
- migration execution is idempotent;
- graph state survives runtime restart;
- repeated projection is idempotent;
- graph history survives invalidation/update cycles;
- graph inference does not change M8 claim confidence;
- graph inference does not change independent-origin count;
- M10 region/language metadata does not create source independence;
- runtime database remains project-local;
- no external graph service is required;
- full deterministic repository regression CI passes.

Gate:
M11_ADVANCED_GEOPOLITICAL_GRAPH_BASELINE_PASS

## Initial Implementation Order

1. Add migration 010 and graph persistence contracts.
2. Add durable graph repository while preserving M4 interfaces.
3. Add deterministic node/edge projection helpers.
4. Add actor/event projection acceptance tests.
5. Add relationship evidence and lifecycle semantics.
6. Add temporal/causal history semantics.
7. Extend IntelligenceQuery.
8. Add isolation and confidence-non-inflation regressions.
9. Run full CI and record completion/validation artifacts.

## Completion Boundary

M11 is complete only when all M11 gates pass and the full deterministic regression suite succeeds.

M11 completion may validate the ROADMAP Phase 8 engineering baseline. It does not approve production/global operational status, shared runtime storage, external graph providers or automatic verification promotion.
