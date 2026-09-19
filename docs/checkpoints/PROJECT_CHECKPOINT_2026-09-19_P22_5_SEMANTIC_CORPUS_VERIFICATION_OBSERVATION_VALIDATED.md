# Project Checkpoint — P22.5 Semantic Corpus & Verification Observation Validated

Date: 2026-09-19

Gate: `P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED`

Decision: `VALIDATED_WITH_ALL_CLAIMS_DETECTED_AND_UNDERLYING_ORIGIN_UNRESOLVED`

## Accepted exact-main evidence

- canonical bridge SHA: `a4dfeee3765116e6b2c261413129b7329f754202`;
- host: `kgm-e4-owner-pilot`;
- architecture: `aarch64`;
- exact cohort: `28` legacy live claims -> `28` canonical semantic claims;
- verification decisions: `28 DETECTED`;
- evidence relations: `28 ATTRIBUTION_ONLY`;
- canonical independence assessments: `0`;
- canonical contradictions: `0`;
- P13.6 linked-with-decision projections: `28`;
- legacy promotion count: `0`;
- database integrity: `ok`.

## Historical gap

The earlier zero-semantic-corpus observation remains preserved and is superseded only as the current state by the integrated canonical bridge. It is not rewritten.

## Validation contingency

GitHub Actions quota is exhausted for the current billing cycle. The active cost-control contract is:

`docs/decisions/GITHUB_ACTIONS_QUOTA_CONTINGENCY_2026-09-19.md`

Exact-head owner-local validation is required until 2026-10-01. Functional and truth/provenance gates are unchanged.

## Boundaries

```text
PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

Next gate: `P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED`.
