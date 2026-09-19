# Project Checkpoint — P22.3 Controlled High-Priority Onboarding Validated

Date: 2026-09-19  
Project: `K-Geopolitical Monitor`  
Gate: `P22_3_CONTROLLED_HIGH_PRIORITY_ONBOARDING_VALIDATED`  
Decision: `VALIDATED_WITH_PARTIAL_ONBOARDING`

## Canonical implementation evidence

- implementation PR: `#140`;
- implementation merge anchor: `9c730ccd4a646aecbd0ada13b972701b65596adf`;
- exact-main live probe SHA: `445699eb8b60fec3a70cbbfb5d831ffb35aa26a3`;
- owner-local host: `kgm-e4-owner-pilot`;
- architecture: `aarch64`;
- CI run: `35451792014`;
- CI job: `105920115982`;
- CI result: `1343 passed in 107.57s / SUCCESS`.

## B1 measured result

Authorized B1 cohort size: `4`.

Repository-active after complete P20.5 PASS:

- `ofac-recent-actions-en`;
- `white-house-briefings-en`.

Blocked and not repository-active:

- `uk-sanctions-list-en` — `BOUNDED_RESPONSE_LIMIT` (official CSV measured `49,928,338` bytes against bounded `10,000,000` byte probe limit);
- `russian-government-news-ru` — `TRANSPORT_TIMEOUT`.

Summary:

```text
MEASURED_SOURCES = 4
COLLECTOR_SUCCESS = 2
COLLECTOR_FAILURE = 2
COLLECTED_ITEMS = 28
P20_5_ELIGIBLE_NOT_ACTIVE = 2
P20_5_BLOCKED = 2
REPOSITORY_ACTIVE = 2
LIVE_ACTIVATION = 0
CONTENT_FRESHNESS_CREDIT = 0
INDEPENDENCE_CREDIT = 0
```

New repository paths affect:

- `global.en.sanctions_regulatory`;
- `united_states.en.official_government`.

This checkpoint does not claim that either cell is adequate. P22.4 must apply the approved policy thresholds and measured freshness/origin constraints.

## Containment

The owner-local probe did not mutate the historical deployed runtime:

```text
DEPLOYED_SHA_BEFORE = b31b2136b5fe982d0b63b0135479b1549041906c
DEPLOYED_SHA_AFTER  = b31b2136b5fe982d0b63b0135479b1549041906c
SERVICE_BEFORE = active
SERVICE_AFTER  = active
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED
PRODUCTION_LIVE = NOT_OPERATIONAL
```

P13.5/P13.6 remain factual-verification authority. Official publication paths establish what an institution published and do not automatically establish the truth of the underlying claim.

## Remaining boundaries

- the two blocked B1 sources require explicit technical repair/revalidation before any later activation;
- the remaining 9 P22.2 candidates are not authorized by this checkpoint;
- paid/shared resources remain unauthorized;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- Plugin build/publication remains inactive.

## Next gate

`P22_4_OPERATIONAL_COVERAGE_REBASELINE_VALIDATED`
