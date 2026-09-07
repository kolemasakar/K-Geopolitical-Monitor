# P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness Contract

Status: `IMPLEMENTATION_CANDIDATE / NOT_VALIDATED`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Target gate: `P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED`
Implementation base: `8d33090402a5aec4aac1ec3ba450718af761cd47`

## Purpose

P18.8 introduces an isolated provider-neutral non-production shadow candidate and
read-only canary-readiness contract while preserving the owner-local SQLite
runtime as canonical.

The repository CI currently provides Python test execution only and does not
provision a PostgreSQL service or any external shared-runtime provider. P18.8
therefore does not convert configuration requirements into invented
infrastructure observations.

## Controlled Shadow Flow

The contract implements this validation-only flow:

`owner-local provenance manifest -> immutable tenant-scoped snapshot -> isolated non-prod shadow candidate -> read-only observation -> deterministic reconciliation -> canary-readiness design`

The flow is deliberately one-way. The candidate exposes no canonical write or
promotion operation back into the owner-local runtime.

### Source provenance

The source uses the validated P18.3 `ExportManifestContract`:

- source storage scope must be `PROJECT_LOCAL_SQLITE`;
- `workspace_id + project_id` are explicit;
- source schema version is recorded;
- owner-local database SHA-256 is recorded;
- per-table row counts and content checksums are recorded.

`ControlledShadowPackage` binds the manifest to immutable `ShadowRecord`
snapshots and to the provider-neutral PostgreSQL-compatible target schema
contract.

### Immutable record snapshots

Every `ShadowRecord`:

- belongs to exactly one tenant context;
- has a table/object identity;
- stores canonical JSON payload text;
- binds the payload to SHA-256;
- carries a separate semantic-projection SHA-256.

Mixed-tenant snapshots and duplicate object identities fail closed.

## Non-Production Candidate Boundary

`NonProductionShadowCandidate` is explicitly:

- `environment = non_production_contract_harness`;
- read-only;
- non-canonical;
- not production/live;
- provider-neutral;
- not evidence of a real datastore;
- not evidence of real network/TLS reachability;
- unable to authorize canonical cutover;
- unable to authorize shared-runtime activation.

The candidate accepts only one controlled package for the exact tenant and exact
target schema. A second import/overwrite fails closed.

This harness is not a shared SQLite implementation and does not bind the
existing owner-local SQLite database as shared storage.

## Reconciliation

P18.8 compares expected and observed shadow evidence across:

- tenant scope;
- schema version;
- per-table row counts;
- per-table content checksums;
- per-table semantic-projection checksums;
- explicit invariant failures.

Every mismatch is typed and preserved as evidence. `ShadowMismatchBudget`
defines the permitted upper bound. The default budget is zero.

A non-zero explicit budget may classify mismatches as bounded for analytical
shadow work, but it does not make them an exact match and cannot authorize
canonical promotion or shared-runtime activation.

Tenant mismatch never becomes canary-ready even if a numeric mismatch budget is
large enough.

Semantic comparison remains an analytical consistency check only. It does not
change or supplement P13.5/P13.6 factual-verification authority.

## Prior Control Evidence

`Phase18ContractEvidence` references already validated contract gates:

- P18.4 repository/concurrency;
- P18.6 security/secrets;
- P18.7 recovery/rollback.

It separately records external infrastructure observation state for:

- network/TLS;
- datastore reachability;
- off-host recovery;
- provider PITR/WAL-equivalent.

All four are `NOT_OBSERVED` in the provider-neutral P18.8 harness unless real,
separately obtained evidence exists.

This separation prevents a validated software contract from being mislabeled as
an observed deployment fact.

## Provider and Cost Gate

P18.8 does not select a provider.

`ProviderCostGate` supports two modes:

1. external infrastructure is not required for the current provider-neutral
   contract harness, so no provider comparison or selection is claimed;
2. if an external candidate becomes necessary, at least two explicit options
   must be compared before the gate can be complete.

Selecting an evaluated option requires a separate explicit owner approval
identifier. A paid commitment requires that approved selection and cannot be
created by P18.8 readiness evidence itself.

Provider comparison metadata covers at minimum:

- fixed monthly cost;
- variable-cost basis;
- security summary;
- exit/export path.

A future real provider decision should additionally evaluate storage, egress,
identity, backup retention, observability, regional availability, operational
burden and lock-in as required by the Phase 18 implementation plan.

## Read-Only Canary Design

The default canary design uses observation stages:

- 1%;
- 5%;
- 25%;
- 100%.

These are design percentages for read-only observation, not a live traffic
allocation claim.

Every P18.8 canary stage must remain:

- read-only;
- writes disabled;
- automatic promotion disabled;
- canonical cutover unauthorized;
- shared-runtime activation unauthorized;
- production/live unauthorized.

## P18.8 Readiness Evidence

`P18_8ReadinessEvidence` can be constructed only when:

- shadow mismatches are within the explicit budget;
- P18.4/P18.6/P18.7 contract evidence is present;
- provider/cost comparison obligations are satisfied for the current mode;
- a valid non-promoting canary design exists;
- owner-local SQLite remains canonical;
- shared runtime remains inactive;
- migration 033 remains uncreated/unauthorized;
- production/live remains false;
- paid provider commitment is not authorized by the evidence object.

Passing this object means the **provider-neutral shadow/canary contract is ready
for the P18.9 validation matrix**. It does not mean external infrastructure is
fully observed or that shared runtime may be activated.

## Real Infrastructure Evidence Boundary

Current repository CI does not provide a real PostgreSQL/shared-runtime service.
Therefore the P18.8 implementation must keep the following distinction:

### Validated in P18.8 contract harness

- controlled provenance-bound copy semantics;
- exact tenant isolation;
- row-count/content/semantic/invariant reconciliation;
- explicit bounded mismatch reporting;
- read-only non-production candidate behavior;
- P18.4/P18.6/P18.7 evidence composition;
- provider/cost owner-decision gate;
- non-promoting canary design;
- rollback/canonical independence boundaries.

### Not observed by this implementation

- concrete PostgreSQL/shared datastore deployment;
- provider-specific RLS enforcement;
- live HTTPS ingress;
- live TLS certificate/path verification;
- live private datastore reachability;
- concrete encrypted off-host backup;
- provider PITR/WAL restore;
- provider billing/cost observations;
- real canary traffic.

Such evidence may be added only after a separately permissible non-production
infrastructure step and must be rechecked in P18.9 before activation readiness.

## Preserved Boundaries

P18.8 implementation does not change:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite canonical status;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- backend HTTPS/shared ingress: `NOT_DEPLOYED`;
- public sharing: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- factual verification authority: P13.5/P13.6.

ROADMAP/state are intentionally unchanged by the implementation candidate. They
may advance only after full P18.8 validation evidence is reviewed and the gate
can be stated without infrastructure overclaim.
