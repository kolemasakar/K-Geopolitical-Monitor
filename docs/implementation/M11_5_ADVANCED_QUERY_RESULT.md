# M11.5 Advanced Intelligence Query Result

Status: PASS
Date: 2026-08-26
Gate: M11_5_ADVANCED_QUERY_VALIDATED

## Implementation

Implementation commits:

- 8f0e4fe67acea7cb24fdcb1e15b081229c3b093e - Implement M11.5 advanced intelligence query
- 0f64326e47df18efdfc08406b192607669190cab - Add M11.5 advanced intelligence query acceptance tests

Implemented by extending the existing IntelligenceQuery facade rather than replacing it.

Advanced durable graph queries now include:

- direct neighborhood;
- bounded directed multi-hop paths;
- actor-to-actor relationships;
- actor-to-event participation;
- current and historical relationship state;
- causal/influence paths;
- explainable AdvancedQueryResult output.

Every advanced result can expose:

- graph node and edge IDs;
- canonical references;
- edge evidence references;
- path count and path graph IDs.

The validated M4 constructor and legacy methods remain available.

## Validation

GitHub Actions run:

- run_id: 32973020068
- workflow: CI
- result: PASS
- tests: 114 passed
- execution time: 3.80s

M11.5 acceptance coverage includes:

- evidence-backed direct neighborhood output;
- bounded multi-hop query behavior;
- invalidated-edge exclusion from current paths;
- current vs historical actor relationship state;
- actor-to-event PARTICIPATION queries;
- cycle-safe causal query output;
- explicit durable-backend requirement for advanced methods.

## Architectural Boundaries

- IntelligenceQuery remains a facade; canonical truth remains outside the graph query layer.
- Query results do not modify graph state or upstream evidence state.
- Graph confidence is not promoted into canonical verification confidence.
- No automatic VERIFIED promotion is introduced.
- No external graph service or shared runtime database is used.

## Result

M11_5_ADVANCED_QUERY_VALIDATED = PASS

## Next

M11.6 Isolation and Regression Gate.
