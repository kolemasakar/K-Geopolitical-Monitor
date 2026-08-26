# M11 Advanced Geopolitical Graph Audit

Status: COMPLETE
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 8 - Advanced Geopolitical Graph

## Purpose

Audit the existing M2/M4 graph implementation and define the exact engineering delta required for M11 without creating a second competing graph subsystem.

## Audited Baseline

The current repository contains several graph-related fragments:

- `knowledge_graph.py` - in-memory KnowledgeNode/KnowledgeEdge graph baseline;
- `entity_graph.py` - older in-memory entity/relation graph baseline;
- `entity_graph_repository.py` - separate in-memory relation repository;
- `knowledge_repository.py` - in-memory snapshot repository;
- `relationship_engine.py` - relationship-strength clamping baseline;
- `causal_intelligence.py` - in-memory cause/effect links;
- `temporal_graph.py` - in-memory timestamped relations and simple influence delta;
- `intelligence_query.py` - deterministic graph/query/explanation facade;
- `tests/test_m4_validation.py` - functional M4 baseline acceptance contract.

The M4 plan explicitly defined its scope as baseline implementation only. The M4 validation report also records durable graph persistence and advanced semantic/scenario intelligence as known limitations.

## Findings

### 1. Multiple graph representations exist

M2/M4 currently expose overlapping models:

- EntityGraph / EntityRelation;
- KnowledgeGraph / KnowledgeEdge;
- EntityGraphRepository.EntityRelation;
- KnowledgeSnapshot edge dictionaries.

These structures do not share one canonical typed graph schema.

Risk:
Further Phase 8 development on top of a new independent model would create a fourth representation and increase divergence.

Decision:
M11 must converge these fragments around one canonical advanced graph contract while preserving compatibility with validated M4 public behavior where practical.

### 2. Graph persistence is not durable

KnowledgeRepository stores snapshots in a Python list. EntityGraphRepository stores relations in a Python list.

No current migration defines durable graph node/edge/lifecycle tables.

Decision:
M11 durable graph persistence must use the existing project-local SQLite migration system. The next graph schema migration is expected to follow migration `009_region_language_coverage.sql`.

### 3. Relationship intelligence is minimal

RelationshipEngine currently normalizes a supplied relationship strength to the range 0..1. It does not perform evidence aggregation, relation lifecycle handling, provenance preservation, conflict handling or temporal validity.

Decision:
M11 must add typed relationship state and evidence-backed lifecycle semantics. Graph relationship confidence must not become an independent verification source or inflate upstream evidence confidence.

### 4. Causal intelligence is a baseline link store

CausalEngine stores cause/effect links and supports outbound traversal. It has no persisted provenance, validity interval, invalidation state or evidence references.

Decision:
Causal relationships must become typed graph edges with provenance and lifecycle semantics. Existing bounded causal traversal can remain available through the intelligence-query facade.

### 5. Temporal analysis is insertion-order dependent

TemporalGraphAnalyzer stores timestamped relations in memory. `influence_change()` compares the first and last stored weights rather than a canonical persisted temporal series.

Decision:
M11 must persist `valid_from`, `valid_to` and observation timestamps and provide deterministic time-ordered history and snapshot queries.

### 6. IntelligenceQuery is the correct compatibility facade

IntelligenceQuery already provides:

- entity lookup;
- relation lookup;
- bounded causal-chain traversal;
- deterministic text query;
- explanation output.

Decision:
M11 should extend this facade with advanced graph queries instead of replacing it.

### 7. Current canonical runtime truth already exists outside the graph

Later milestones persist canonical project data including:

- events and claims;
- raw items and evidence/provenance;
- operational findings;
- strategic alerts;
- region/language attribution and coverage.

Decision:
The graph must reference canonical persisted project objects. It must not duplicate or redefine evidence truth, verification status, source independence, alert state or region/language attribution.

## Required M11 Delta

M11 requires the following new capabilities:

- one canonical typed graph node/edge model;
- durable project-local SQLite graph persistence;
- deterministic graph identities and idempotent projection;
- actor graph projection;
- event graph projection;
- evidence/provenance references for graph edges;
- relationship status and lifecycle history;
- temporal validity intervals and deterministic history;
- explicit causal/influence relation types;
- invalidation without destructive deletion;
- advanced path, neighborhood, actor-event, temporal and causal queries;
- explanation output retaining evidence references;
- backward-compatible M4 acceptance behavior;
- restart persistence and project-local storage isolation;
- regression proof that graph metadata cannot increase upstream verification confidence or independent-origin count.

## Explicit Non-Goals

M11 must not:

- create a second canonical project database;
- create shared or mixed runtime storage;
- replace M8 evidence independence rules;
- automatically promote claims to VERIFIED;
- treat graph inference as source evidence;
- add external graph databases or hosted graph providers;
- introduce a production/global operational status.

## Recommended Convergence Rule

The target architecture is:

Canonical project objects -> deterministic graph projection -> durable project-local graph store -> IntelligenceQuery facade

Dependency direction must remain one way:

Canonical evidence/event state -> Graph

The graph must never mutate canonical evidence truth merely because a relationship was inferred or queried.

## Audit Result

M11_DELTA_AUDIT_PASS

The repository is ready for an M11 implementation plan centered on graph convergence and durable project-local persistence, not graph subsystem duplication.
