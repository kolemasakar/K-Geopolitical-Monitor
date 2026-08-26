# M13.2 Common Report Assembly Result

Status: PASS
Date: 2026-08-26
Project: K-Geopolitical Monitor
Milestone: M13.2 Common Report Assembly and Provenance

## Implementation

Current validated implementation commit:
- `1849f4cc6cd39f8ba09162c93e5df3581217b833`

Implementation lineage:
- `6a3933d1fe3b19fc01618007f972a18d80e3c926` - common assembler and initial acceptance/isolation tests;
- `1849f4cc6cd39f8ba09162c93e5df3581217b833` - source-provenance hardening for alert-only and forecast-only reports.

Validation checkpoint commit:
- `15883e1c00032d115b29c6f47580b1ca16cf6799` - same M13.2 main tree plus manual `workflow_dispatch` support in CI.

## GitHub Actions Validation

Manual workflow-dispatch validation:
- run: `32989895962`;
- job: `98244742815`;
- Python: `3.11.16`;
- result: `170 passed in 12.00s`;
- conclusion: `success`.

The prior session diagnosis that connector-authored commits were not generating workflow runs was incorrect. The GitHub UI showed that push and pull-request runs had in fact been created; the connector/API reads used at that time returned a stale or incomplete run list. This was a validation-read-path issue, not a GitHub Actions trigger failure.

## Validated Contracts

- one common `ReportAssembler` interface;
- adapters for findings, strategic alerts, coverage, graph context and forecast versions;
- deterministic ordered report sections;
- typed durable provenance accumulation;
- source provenance aggregated from findings, alerts and forecast source evidence;
- explicit source evidence / graph inference / forecast scenario separation;
- forecast `RAW_ITEM` source evidence remains distinct from `GRAPH_EDGE` analytical context;
- graph relationships are excluded from `SOURCES` provenance;
- report assembly does not mutate upstream finding, alert, graph or forecast state;
- fail-closed unknown durable inputs;
- deterministic non-persisting preview mode;
- project-local report persistence only.

## Gate

`M13_2_REPORT_ASSEMBLY_VALIDATED = PASS`

## Boundary

This gate does not approve external publishing/delivery, shared runtime storage, report-driven verification changes, production dashboards or production/live OPERATIONAL status.
