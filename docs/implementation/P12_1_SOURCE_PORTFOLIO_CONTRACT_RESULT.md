# P12.1 — Source Portfolio Contract and Governance Result

Date: 2026-09-01
Status: `VALIDATED`
Project: K-Geopolitical Monitor
Gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## Result

P12.1 is complete and baseline-validated.

Implemented:

- additive migration `022_source_portfolio_contract.sql`;
- immutable versioned table `source_portfolio_versions`;
- `SourcePortfolioService`;
- canonical source-identity consistency checks;
- deterministic per-source versioning and supersession;
- current/history/current-portfolio projections;
- fail-closed governance validation;
- paid-provider separate-approval enforcement;
- SQL UPDATE/DELETE immutability;
- epistemic isolation properties.

## Contract Coverage

The portfolio model records:

- source ID/name and publisher identity;
- source class and role;
- region/language scope;
- access, cost and authentication modes;
- expected freshness and collection cadence;
- adapter identity/version;
- exact outbound hostnames and protocol;
- fallback/replacement IDs;
- availability/degradation;
- data classification;
- origin/provenance characteristics;
- independence constraints;
- licensing/terms notes;
- owner/reviewer/review state;
- paid-provider approval state.

## Validation

Implementation/validation commit:
`905a727d85701bf43d18de2d5216b83ab9a2b8bd`

GitHub Actions:

- CI run: `33520371480`;
- job: `99897786494`;
- result: `334 passed, 1 warning / SUCCESS`.

Diff from P12.0 closure baseline contains only:

- P12.1 migration;
- P12.1 source-portfolio service;
- P12.1 tests;
- database migration expectation update;
- P12.1 implementation record.

No live collector/runtime adapter was changed by the validation commit.

## Truth / Coverage Isolation

Validated portfolio records:

- do not activate collection;
- do not establish independent corroboration;
- do not change claim truth;
- do not change verification state;
- do not change coverage confidence.

An official/approved source remains evidence for what it states, not automatic proof of the underlying event.

## Paid / Credential Boundary

- P12.1 approves no paid provider.
- A PAID source may be documented as PLANNED.
- PAID + APPROVED requires separate explicit `paid_provider_approved=True`.
- Public anonymous access cannot require credentials.
- Credentialed/restricted access requires an explicit authentication mode.

## Runtime / Exposure Boundary

Unchanged:

- `Runtime storage mode: PROJECT_LOCAL_ONLY`;
- `Production/live operational status: NOT_OPERATIONAL`;
- no public API/dashboard ingress;
- backend HTTPS not deployed;
- private GPT Action not connected;
- shared runtime not approved;
- public sharing user-deferred.

## Source Activation State

Validated live baseline remains:

- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

P12.1 activated no additional live source.

## Next

`P12.2_LIVE_ADAPTER_FRAMEWORK_V2 / NEXT_NOT_STARTED`

P12.2 must use the P12.1 source-portfolio governance contract rather than bypass it.
