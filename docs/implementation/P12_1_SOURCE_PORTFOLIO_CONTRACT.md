# P12.1 — Source Portfolio Contract and Governance

Date: 2026-09-01
Status: `BASELINE_VALIDATED`
Project: K-Geopolitical Monitor
Roadmap: `ROADMAP.md / v4.0`
Parent gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`

## Objective

Define a durable, versioned source-portfolio governance contract without activating new external sources, changing canonical runtime storage, or weakening provenance/verification/coverage boundaries.

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## Architecture

P12.1 is additive.

- `sources` remains the canonical minimal source-identity table.
- `source_portfolio_versions` stores immutable versioned governance metadata for a source.
- The portfolio does not replace source reputation history.
- The portfolio does not replace collection-attempt, provenance, coverage or verification state.
- A portfolio record does not activate collection.
- A separate adapter/integration step is still required before a source becomes live.

Migration:
`migrations/022_source_portfolio_contract.sql`

Service:
`src/kgeopolitical_monitor/source_portfolio.py`

## Contract Fields

Each portfolio version records:

- canonical `source_id` and source name;
- publisher/organization identity;
- source class and source role;
- region and language scope;
- access mode;
- free/paid/unknown cost mode;
- authentication mode;
- expected freshness and collection cadence;
- adapter/parser identity and version;
- required outbound hostnames and protocols;
- fallback/replacement source IDs;
- availability/degradation state;
- data classification;
- underlying-origin characteristics;
- independence constraints;
- licensing/terms notes;
- owner and reviewer;
- review status;
- explicit paid-provider approval state;
- version/supersession timestamps.

## Versioning / Immutability

- Portfolio versions are positive monotonically increasing integers per `source_id`.
- Every later version points to the prior `portfolio_entry_id`.
- SQL `UPDATE` and `DELETE` are rejected by database triggers.
- Current state is derived from the latest version; history remains queryable.
- Source identity conflicts fail closed.

## Controlled Vocabularies

Source roles:
`PRIMARY`, `OFFICIAL`, `MEDIA`, `DISCOVERY`, `STRUCTURED_DATA`, `OSINT`, `SOCIAL`, `USER_PROVIDED`, `OTHER_APPROVED`.

Access modes:
`PUBLIC_ANONYMOUS`, `PUBLIC_CREDENTIALED`, `RESTRICTED`, `USER_PROVIDED`.

Cost modes:
`FREE`, `PAID`, `UNKNOWN`.

Availability:
`PLANNED`, `ACTIVE`, `DEGRADED`, `UNAVAILABLE`, `STALE`, `RETIRED`.

Review:
`PLANNED`, `APPROVED`, `REJECTED`, `RETIRED`.

Outbound source transport at this gate is constrained to explicit HTTPS hostnames. Adapter transport/framework expansion remains P12.2 scope.

## Fail-Closed Governance Rules

- Existing canonical source identity must match the portfolio version.
- Operational availability requires `APPROVED` review state.
- Approved sources require assigned adapter identity/version.
- Public anonymous access cannot require credentials.
- Credentialed/restricted access must identify an authentication mode.
- Restricted/sensitive data cannot be classified as public-anonymous access.
- Exact outbound hostnames are required for networked sources; URLs/paths are rejected.
- A source cannot list itself as fallback.
- A paid source may be documented as `PLANNED`, but `APPROVED` paid-provider state requires explicit separate `paid_provider_approved=True`.
- P12.1 itself approves no paid provider.

## Epistemic Isolation

Portfolio metadata:

- does not establish independent corroboration;
- does not change claim truth;
- does not change verification state;
- does not change factual/evidence confidence;
- does not change coverage confidence;
- does not make `GLOBAL` exhaustive;
- does not turn an official statement into proof of the underlying event;
- does not turn a discovery/index provider into factual corroboration.

## Activation Boundary

P12.1 seeds no new external source records and changes no live collectors.

Validated controlled-live baseline therefore remains:

- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

Integration of portfolio governance into reusable/live adapters belongs to P12.2.

## Security / Runtime Boundary

Unchanged:

- `Runtime storage mode: PROJECT_LOCAL_ONLY`;
- `Production/live operational status: NOT_OPERATIONAL`;
- no public KGM API/dashboard ingress;
- backend HTTPS not deployed;
- private GPT Action not connected;
- shared/team runtime not approved;
- public GPT sharing user-deferred;
- public SSH TCP/22 and broad outbound egress remain the explicit owner-approved candidate networking exceptions.

## Validation

New deterministic tests cover:

- migration/table presence;
- source identity consistency;
- versioning/current/history semantics;
- deterministic multi-value normalization;
- access/auth/data/egress fail-closed rules;
- paid-provider separate-approval rule;
- SQL immutability;
- truth/verification/coverage isolation;
- current-entry projection.

Full regression validation evidence:
- commit `905a727d85701bf43d18de2d5216b83ab9a2b8bd`;
- CI run `33520371480`;
- job `99897786494`;
- result `334 passed, 1 warning / SUCCESS`.

Gate state:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`
