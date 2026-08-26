# M11.4 Temporal and Causal Graph Result

Status: PASS
Date: 2026-08-26
Gate: M11_4_TEMPORAL_CAUSAL_GRAPH_VALIDATED

## Implementation

Implementation commits:

- d6ee684d96b8e73efec60a33c552c02d94672e93 - Implement M11.4 temporal and causal graph
- 2eaf6e5f43eceec935d5f68dbb1d42b043417cb7 - Add M11.4 temporal and causal graph acceptance tests
- ee5341f56f4c91e742cf761c5c9c5b76f13a6318 - Fix M11.4 causal traversal semantic ordering

Implemented:

- deterministic relationship state reconstruction for requested timestamps;
- current and historical graph snapshots;
- validity interval enforcement through valid_from / valid_to;
- current-state filtering to ACTIVE / UPDATED relationships;
- invalidated and resolved relationships retained for historical queries;
- causal and influence traversal over durable M11 graph edges;
- bounded traversal through max_depth;
- cycle-safe traversal through path-local visited-node protection;
- deterministic semantic traversal ordering by canonical target reference;
- no separate temporal or causal persistence subsystem.

## Validation

Initial CI run:

- run_id: 32972607402
- result: FAIL
- result detail: 107 passed, 1 failed
- cause: causal traversal ordering used hashed node IDs rather than canonical semantic target identity.

The engine was corrected rather than weakening the acceptance test.

Final GitHub Actions run:

- run_id: 32972729712
- workflow: CI
- result: PASS
- tests: 108 passed
- execution time: 4.76s

M11.4 acceptance coverage includes:

- historical state reconstruction before and after material lifecycle changes;
- current snapshot exclusion of invalidated relationships;
- validity-window filtering;
- bounded deterministic causal traversal;
- cycle protection;
- exclusion of invalidated causal relations;
- max_depth validation.

## Architectural Boundaries

- Temporal state is reconstructed from the durable M11 relationship store and history.
- No external graph database or temporal service is introduced.
- Historical graph state does not modify canonical event or claim truth.
- Causal/influence graph edges remain graph-layer intelligence and do not create independent evidence.
- Runtime storage remains PROJECT_LOCAL_ONLY.

## Result

M11_4_TEMPORAL_CAUSAL_GRAPH_VALIDATED = PASS

## Next

M11.5 Advanced Intelligence Query.
