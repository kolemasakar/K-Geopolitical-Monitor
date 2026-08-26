# M13.2 Common Report Assembly Result

Status: VALIDATION_PENDING
Date: 2026-08-26
Project: K-Geopolitical Monitor
Milestone: M13.2 Common Report Assembly and Provenance

## Candidate Implementation

Current candidate commit:
- `1849f4cc6cd39f8ba09162c93e5df3581217b833`

Implementation lineage:
- `6a3933d1fe3b19fc01618007f972a18d80e3c926` - common assembler and initial acceptance/isolation tests;
- `1849f4cc6cd39f8ba09162c93e5df3581217b833` - source-provenance hardening for alert-only and forecast-only reports.

Implemented candidate contracts:
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

## Validation State

Executable regression evidence is still required before this artifact can be changed to PASS.

In the current session, connector-authored direct pushes, a Contents API write and a temporary pull-request event all failed to create a new GitHub Actions workflow run. The repository CI workflow remains configured for both push and pull_request on `main`; the absence of a run is recorded as a validation-transport block, not as a code PASS or FAIL.

A temporary validation pull request was opened and closed without merge after it also failed to generate a workflow run. It changed no runtime code and did not modify `main`.

Gate:
`M13_2_REPORT_ASSEMBLY_VALIDATED = PENDING`

## Boundary

This candidate does not approve external publishing/delivery, shared runtime storage, report-driven verification changes, production dashboards or production/live OPERATIONAL status.
