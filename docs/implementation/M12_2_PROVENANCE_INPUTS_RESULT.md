# M12.2 Provenance-Bound Forecast Inputs Result

Status: PASS
Date: 2026-08-26
Gate: M12_2_PROVENANCE_INPUTS_VALIDATED

## Implementation

Implementation commit:

- 44e37b950595b22db51472439602f17bbcd95096 - Implement M12.2 provenance-bound forecast inputs

Implemented:

- migration `012_forecast_provenance_inputs.sql`;
- project-local `forecast_version_inputs` table;
- typed forecast input kinds: SOURCE_EVIDENCE, CANONICAL_EVENT, GRAPH_RELATIONSHIP, OPERATIONAL_FINDING and ANALYST_ASSUMPTION;
- deterministic forecast input identity;
- immutable typed binding to an existing immutable M12.1 forecast version;
- canonical snapshot builder for typed inputs and explicit constraints;
- compatibility projection into existing `input_snapshot_json`, `provenance_refs_json` and `assumptions_json` fields;
- fail-closed durable reference validation against project-local raw items, canonical events, graph relationships and operational findings;
- analyst assumptions remain explicitly analytical and require no upstream canonical row;
- identical repeated binding is idempotent;
- changed input sets fail against the immutable forecast-version snapshot;
- restart-safe typed provenance retrieval.

## Validation

GitHub Actions run:

- run_id: 32975878963
- workflow: CI
- result: PASS
- tests: 131 passed
- execution time: 6.33s
- Python: 3.11

M12.2 acceptance coverage includes:

- typed provenance persistence and restart recovery;
- idempotent repeated binding;
- explicit constraints and analyst assumptions;
- fail-closed unknown SOURCE_EVIDENCE reference;
- fail-closed unknown CANONICAL_EVENT reference;
- fail-closed unknown GRAPH_RELATIONSHIP reference;
- fail-closed unknown OPERATIONAL_FINDING reference;
- immutable snapshot mismatch rejection;
- M8 claim verification status, confidence and independent-origin count remain unchanged;
- M11 graph relationship state remains unchanged.

## Architectural Boundaries

- Forecast inputs are analytical dependencies, not new evidence observations.
- GRAPH_RELATIONSHIP inputs do not become independent source evidence.
- ANALYST_ASSUMPTION inputs are never canonical evidence.
- Typed input binding cannot mutate M8 verification truth or M11 graph truth.
- Runtime storage remains PROJECT_LOCAL_ONLY.
- No external forecasting provider is introduced.

## Result

M12_2_PROVENANCE_INPUTS_VALIDATED = PASS

## Next

M12.3 Scenario Lifecycle and Updates.
