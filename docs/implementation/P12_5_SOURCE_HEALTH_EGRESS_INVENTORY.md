# P12.5 — Source Health, Freshness and Egress Inventory

Date: 2026-09-01
State: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`
Depends on: P12.1-P12.4 validated.

## Objective

Measure the validated public-source network's operational availability, measurement freshness, observed publisher-content freshness and exact outbound host/protocol requirements before proposing any egress restriction.

P12.5 is operational measurement. It does not change factual verification, independent-origin credit, coverage confidence or production/live state.

## Measured Network Scope

The controlled P12.5 inventory covers ten paths:

- Consilium press releases RSS;
- GDELT DOC 2.0;
- European Commission Press Corner;
- European Parliament Press Releases;
- UK Government News and Communications;
- OSCE Latest News;
- Ukrainska Pravda;
- Meduza;
- RMF24;
- Haberturk.

The two pre-P12 baseline integrations are given explicit P12.1 governance inside the controlled ephemeral runtime so their P12.2 v2 path can be measured. This does not switch or activate an owner production runtime.

## Three Separate Operational Dimensions

P12.5 deliberately does not collapse health and freshness into one flag.

### Operational state

- `UNMEASURED` — no persisted attempt exists; no health inference is made;
- `HEALTHY` — current successful attempt for a normally active portfolio source;
- `DEGRADED` — current successful attempt but governed portfolio state is degraded;
- `UNAVAILABLE` — current latest attempt failed;
- `STALE` — latest measurement itself is too old to represent current health.

### Measurement freshness

- `UNMEASURED`;
- `CURRENT`;
- `STALE`.

The measurement staleness limit is tied to both portfolio collection cadence and expected freshness: `max(2 * collection_cadence, expected_freshness)`.

### Observed content freshness

- `FRESH` — a real publisher/content timestamp was observed and falls within `expected_freshness_minutes`;
- `STALE` — a real observed timestamp exceeds that expectation;
- `UNKNOWN` — no parseable publisher/content timestamp was captured.

`UNKNOWN` is not converted into an estimate from collection time.

Supported timestamp evidence includes explicit `published_at`, raw RSS/Atom publication timestamps and GDELT `seendate` when parseable.

## Error Classification

Latest failed attempts are classified separately:

- `TRANSPORT` — network/HTTP/timeout/connectivity failure;
- `PARSER` — response reached the adapter but payload/shape was not parseable;
- `GOVERNANCE` — portfolio/adapter/outbound-host contract mismatch;
- `UNKNOWN` — failure cannot be safely assigned to the above classes;
- `NONE` — no current error.

The class is operational diagnosis only.

## Egress Inventory

The inventory is derived from current `APPROVED` P12.1 portfolio records and records per source:

- exact hostname;
- protocol;
- adapter identity/version;
- access mode;
- data classification;
- portfolio availability state.

P12.5 does not broaden egress. It measures declared requirements and controlled live behavior before any restriction proposal.

## Persistence / Schema Boundary

P12.5 adds no canonical database migration.

It reuses:

- `source_portfolio_versions` for governance and expected freshness/cadence;
- `source_collection_attempts` for actual SUCCESS/FAILED state and attempt time;
- `raw_items` + `live_source_provenance` for captured publication metadata;
- P12.2 adapters for controlled read-only acquisition.

The assessment layer is read-only over this persisted state.

## Controlled-Live Probe

Workflow: `P12.5 Controlled Live Source Health Inventory`.

The workflow creates an ephemeral project-local runtime, installs exact governance for all ten measured paths, runs one bounded read-only collection and prints a complete JSON health/freshness/egress snapshot.

A source failure is measured data and does not by itself fail the workflow. The workflow fails if the measurement cannot persist one attempt for each of the ten governed paths or if governance/adapter construction itself is invalid.

## Epistemic / Coverage Boundary

- health state does not change claim truth;
- content freshness does not change verification confidence;
- source/host count does not create independent-origin count;
- source availability does not prove coverage completeness;
- unavailable sources remain coverage limitations, not evidence that no event occurred;
- `GLOBAL` remains scope, not proof of exhaustive monitoring.

## Security / Runtime Boundary

- public/free anonymous HTTPS only;
- no credentials;
- paid providers remain `NONE_APPROVED`;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- public KGM ingress remains not approved/deployed;
- production/live operational status remains `NOT_OPERATIONAL`;
- broad outbound egress remains the explicit owner-approved candidate exception until measured inventory is validated and a separate restriction decision is made.
