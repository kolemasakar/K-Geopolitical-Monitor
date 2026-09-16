# P21.0 — Coverage Policy Definition & Criticality Contract

Date: 2026-09-16
Status: `VALIDATED / GLOBAL_POLICY_APPROVED`
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

Approval-envelope schema:
`docs/contracts/p21_0_policy_approval_envelope.schema.json`

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

- a canonical approval must identify an exact immutable policy manifest and explicit approval timestamp;
- `REQUIRED` cell cannot use `criticality = NONE`;
- `NOT_REQUIRED` cell must use `criticality = NONE` and zero/null non-promotional thresholds;
- `UNSET` cannot be interpreted as `OPTIONAL` or `NOT_REQUIRED`;
- independent-origin thresholds cannot be satisfied by source/domain/language counts;
- freshness/health thresholds are operational requirements, not content-credibility or factual-verification operators;
- target cells may be absent from the current observed matrix;
- no target may imply that a source exists, is healthy, or is independent before evidence establishes it.

## Immutable approval rule

The reviewed global-baseline proposal remains immutable historical evidence with its internal proposal marker unchanged. Canonical authority is granted by a separate approval envelope that binds the owner decision to the exact Git blob of that reviewed manifest.

Canonical approved pair:

- manifest: `docs/evidence/P21_0_TARGET_COVERAGE_POLICY_PROPOSAL_2026-09-16.json`;
- reviewed manifest version: `0.2-draft-global-baseline`;
- reviewed manifest blob: `d1d7ea7f36443b2b350a290114f3c8a6417a447e`;
- approval: `docs/evidence/P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json`;
- approval authority: `APPROVED`.

This approval-envelope design avoids rewriting the pre-approval artifact after the owner decision while still producing a deterministic canonical authority record. A manifest with a different blob SHA is not covered by this approval and requires a new approval record.

Only the exact manifest bound by a valid `APPROVED` envelope may drive canonical P21.3 adequacy/gap decisions.

## Relationship to P13 verification

Coverage criticality, requirement state, thresholds, adequacy and gap status remain non-promotional metadata.

P13.5/P13.6 remain the sole canonical factual-verification authority.

## OpenAI / ChatGPT surface boundary

P21.0 policy and later adequacy evaluation are deployment-wrapper independent.

OpenAI's Custom GPT retirement changes the future ChatGPT integration surface but does not change this policy contract. Future ChatGPT-facing access is Plugin-first, with Apps/Connectors/custom MCP considered for integrations. A Plugin or integration wrapper cannot create source independence, health, provenance or factual-verification credit.

Canonical platform decision:
`docs/decisions/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md`.

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
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

## Gate status

P21.0 final gate requires:

- contract/schema validation;
- explicit target-policy manifest;
- immutable owner approval bound to the exact reviewed manifest;
- documented scope/criticality/threshold choices;
- preservation of P20 historical evidence;
- regression validation.

Current state:

`P21_0_CONTRACT_IMPLEMENTED = YES`

`P21_0_GLOBAL_BASELINE_APPROVAL = APPROVED`

`P21_0_GATE = P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

`NEXT_GATE = P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`
