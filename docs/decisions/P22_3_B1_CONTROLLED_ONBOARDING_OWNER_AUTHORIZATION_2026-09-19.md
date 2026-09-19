# P22.3 — Controlled High-Priority Onboarding — B1 Owner Authorization

Date: 2026-09-19
Status: `AUTHORIZED / B1_IMPLEMENTATION_READY`
Gate: `WAVE_B_ONBOARDING = APPROVED_FOR_B1_INSTITUTIONAL_COHORT`
Project: `K-Geopolitical Monitor`
Authorization basis: explicit owner instruction to continue on 2026-09-19 after P22.1 and P22.2 validation.

## Narrow interpretation

The owner instruction is interpreted narrowly as approval for the next sequential gate only:

`P22.3 — Controlled High-Priority Onboarding`

and only for the named **B1 institutional cohort** below.

This is **not** blanket authorization for all 13 P22.2 candidates and does not authorize persistent owner operation.

## Authorized B1 cohort

1. `ofac-recent-actions-en`
   - cell: `global.en.sanctions_regulatory`
   - publisher: U.S. Treasury / OFAC
   - P22.2 candidate: `p22-2-b03-ofac`

2. `uk-sanctions-list-en`
   - cell: `global.en.sanctions_regulatory`
   - publisher: UK FCDO
   - P22.2 candidate: `p22-2-b04-uk-sanctions`

3. `russian-government-news-ru`
   - cell: `russia.ru.official_government`
   - publisher: Government of Russia
   - P22.2 candidate: `p22-2-b09-rugov`

4. `white-house-briefings-en`
   - cell: `united_states.en.official_government`
   - publisher: The White House
   - P22.2 candidate: `p22-2-b10-whitehouse`

## Conditional activation rule

Authorization permits fixture, adapter, health, rollback and P20.5 readiness work for the four named candidates.

Repository activation is allowed **only per-source after** all of the following are satisfied:

```text
health_behavior_status = PASS
fixture_validation_status = PASS
rollback_disable_status = PASS
governance_review_status = APPROVED
eligibility_decision = ELIGIBLE_NOT_ACTIVE
```

Any source that fails a prerequisite remains `BLOCKED` and is not activated.

## Authorized actions

- verify exact public anonymous source endpoints;
- implement deterministic read-only adapters/parsers where needed;
- add deterministic fixtures and tests;
- run public/free health/freshness preflight;
- complete P20.5 qualification;
- record direct institutional provenance metadata;
- activate only passing B1 sources in the repository-governed source pack;
- validate deterministic disable/rollback;
- write evidence/result/checkpoint artifacts.

## Explicit non-authorization

This decision does **not** authorize:

- the remaining 9 P22.2 candidates;
- paid, authenticated or restricted providers;
- persistent unattended owner operation;
- mutation of the historical deployed runtime;
- service restart;
- public/shared ingress;
- shared runtime activation;
- migration `033`;
- production/live cutover;
- Plugin build/publication;
- external publication.

## Epistemic boundary

Direct institutional publication establishes what the institution published. It does not automatically establish that the underlying event claim is true.

`independence_credit_granted = false` remains the default at onboarding.

P13.5/P13.6 remain the sole canonical factual-verification authority.

## Authorization state

```text
P22_3_B1_OWNER_AUTHORIZATION = APPROVED
B1_SOURCE_COUNT = 4
B1_REPOSITORY_ACTIVATION = CONDITIONAL_ON_P20_5_PASS
REMAINING_P22_2_CANDIDATES = NOT_AUTHORIZED
PERSISTENT_OWNER_OPERATION = NOT_ACTIVATED
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PRODUCTION_LIVE = NOT_OPERATIONAL
```
