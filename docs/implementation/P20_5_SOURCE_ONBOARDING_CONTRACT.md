# P20.5 — Source Onboarding Contract

Status: `IMPLEMENTED_FOR_VALIDATION`
Gate: `P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED`

## Objective

Define a deterministic, fail-closed contract for deciding whether a proposed source is ready to become coverage-eligible, without activating it, changing live ingestion, or granting independent-origin credit.

## Required onboarding evidence

A candidate must provide all of the following before it can resolve to `ELIGIBLE_NOT_ACTIVE`:

- deterministic `source_id`;
- display name and canonical P20.1 `source_type`;
- explicit geography and language scopes;
- primary domain/endpoint and collection method;
- access, cost, authentication and data-classification metadata;
- explicit resource-authorization state;
- expected freshness and collection cadence;
- validated health-check behavior consistent with P20.4 semantics;
- passing synthetic/fixture collection evidence;
- passing disable/rollback behavior;
- approved governance review;
- origin/syndication metadata where known, otherwise explicit unknown provenance.

Unknown provenance is permitted for onboarding readiness, but never creates independent-origin credit. P20.3 remains authoritative for source-origin topology/monoculture evaluation.

## Resource authorization rule

Separate authorization is required when any of the following is true:

```text
cost_mode == PAID
OR authentication_mode != NONE
OR access_mode == RESTRICTED
OR data_classification != PUBLIC
```

If authorization is required, `resource_authorization_state` must be `APPROVED`. Otherwise the candidate is `BLOCKED`.

For public/free/anonymous/public-data sources, `resource_authorization_state=NOT_REQUIRED` is the normal path.

The current project baseline has no approved paid provider, secret-backed source or shared-resource activation.

## Eligibility decision

P20.5 outputs exactly one readiness decision:

```text
ELIGIBLE_NOT_ACTIVE
BLOCKED
REJECTED
```

`ELIGIBLE_NOT_ACTIVE` requires complete required metadata, passing health/fixture/rollback evidence, approved governance and satisfied resource authorization.

`REJECTED` is reserved for an explicit governance rejection.

All other incomplete or unsafe cases are `BLOCKED` with explicit reason codes.

## Non-activation boundary

The P20.5 record has immutable semantics:

```text
live_activation_authorized = false
live_activation_state = NOT_ACTIVE
independence_credit_granted = false
```

A candidate may therefore be ready for a later activation workflow while remaining inactive. Live activation requires a separate explicit decision/gate outside P20.5.

## Provenance boundary

Known `origin_group_id` or syndication relation may be carried as evidence, but onboarding itself cannot certify independence. Unknown provenance remains nullable/`UNKNOWN`; absence of a known copy relation is not evidence of independence.

## Disable / rollback boundary

A coverage-eligible candidate must demonstrate deterministic disable/rollback behavior before eligibility. This is readiness evidence only and does not execute a runtime rollback or activation.

## Current baseline

P20.5 starts with:

```text
CURRENT_GOVERNED_SOURCES = 10
NEW_SOURCE_CANDIDATES = 0
NEW_COVERAGE_ELIGIBLE_SOURCES = 0
LIVE_ACTIVATIONS_AUTHORIZED = 0
PAID_PROVIDERS_APPROVED = 0
```

No existing source is re-onboarded or mutated by P20.5.

## Safety boundary

P20.5 is contract/evidence/test-fixture work only. It does not authorize live-source expansion, live ingest mutation, runtime deployment, service restart, control-plane mutation, migration 033, paid-resource purchase, secret creation or shared-runtime activation.

Next gate after validation: `P20_6_COVERAGE_EVALUATION_REPORTING_VALIDATED`.
