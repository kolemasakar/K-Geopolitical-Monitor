# P21.0 — Coverage Policy Definition & Criticality Contract

Date: 2026-09-16
Status: `IMPLEMENTED / TARGET_POLICY_NOT_YET_APPROVED`
Gate: `P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

## Purpose

P21.0 extends the validated P20.2 target-policy contract without replacing it. The extension adds policy authority, criticality and explicit operational freshness targets required for Phase 21 operational adequacy evaluation.

## Canonical separation

Three objects remain separate:

1. observed coverage evidence — what the governed source network currently contains;
2. target coverage policy — what the project explicitly requires;
3. adequacy evaluation — comparison of evidence against approved policy.

Observed coverage never creates policy automatically. Policy never creates evidence automatically.

## Reused P20.2 semantics

The following remain unchanged:

- matrix key: `geography_scope × language × source_type` with optional `topic_role`;
- requirement states: `REQUIRED / OPTIONAL / NOT_REQUIRED / UNSET`;
- minimum source count;
- minimum independent-origin count;
- minimum healthy-source count;
- maximum stale share;
- maximum dominant-origin share;
- an unmentioned observed cell is not implicitly `NOT_REQUIRED`;
- a policy target may exist with zero observed sources.

## P21.0 additions

Schema:
`docs/contracts/p21_0_coverage_policy_criticality.schema.json`

Added policy-level fields:

- `authority_state = DRAFT / APPROVED / RETIRED`;
- `effective_from`;
- `review_due`.

Added cell-level field:

- `criticality = CRITICAL / HIGH / STANDARD / WATCH / NONE`.

Added operational thresholds:

- `maximum_collection_latency_minutes`;
- `maximum_content_freshness_minutes`.

Added provenance:

- `policy_basis[]` — explicit references/reasons supporting each policy target.

## Criticality semantics

### CRITICAL

Coverage loss materially compromises the intended monitoring function for the policy scope. A `CRITICAL` label does not imply that a geopolitical event is more important or more likely; it is an operational collection requirement.

### HIGH

Coverage is strongly desired and a deficiency should be visible and prioritized for remediation, but the cell is not treated as an immediate critical collection dependency.

### STANDARD

Normal required/optional governed coverage.

### WATCH

Exploratory or conditional coverage. It may be retained for situational value without establishing a broad mandatory baseline.

### NONE

Allowed only where the requirement state is `NOT_REQUIRED`. It does not mean that information from this cell is prohibited; only that the policy does not require coverage.

## Consistency rules

Validation must enforce at least:

- `APPROVED` policy must have an explicit effective timestamp;
- `REQUIRED` cell cannot use `criticality = NONE`;
- `NOT_REQUIRED` cell must use `criticality = NONE` and zero/null non-promotional thresholds;
- `UNSET` cannot be interpreted as `OPTIONAL` or `NOT_REQUIRED`;
- independent-origin thresholds cannot be satisfied by source/domain/language counts;
- freshness/health thresholds are operational requirements, not content-credibility or factual-verification operators;
- target cells may be absent from the current observed matrix;
- no target may imply that a source exists, is healthy, or is independent before evidence establishes it.

## Policy authority rule

Only an `authority_state = APPROVED` target-policy artifact may drive canonical P21.3 adequacy/gap decisions.

A `DRAFT` policy may be schema-validated and reviewed but must not convert P20/P21 coverage cells into canonical `ADEQUATE` or `MISSING_EXPECTED_COVERAGE` states.

## Relationship to P13 verification

Coverage criticality, requirement state, thresholds, adequacy and gap status remain non-promotional metadata.

P13.5/P13.6 remain the sole canonical factual-verification authority.

## Activation boundary

P21.0 is repository-only policy work and does not authorize source onboarding or runtime mutation.

```text
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
```

## Gate status

The contract implementation can be validated independently from target-policy approval.

P21.0 final gate is granted only when:

- this contract/schema is validated;
- a target-policy manifest is explicit and schema-valid;
- its authority state is explicitly approved;
- its scope/criticality/threshold choices are documented;
- no historical P20 evidence is rewritten.

Current state:

`P21_0_CONTRACT_IMPLEMENTED = YES`

`P21_0_TARGET_POLICY = DRAFT_REQUIRED`

`P21_0_GATE = NOT_YET_GRANTED`
