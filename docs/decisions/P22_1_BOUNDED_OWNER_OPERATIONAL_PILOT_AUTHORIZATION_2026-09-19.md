# P22.1 — Bounded Owner-Only Operational Pilot — Owner Authorization

Date: 2026-09-19
Status: `AUTHORIZED / READY_TO_EXECUTE`
Gate: `OWNER_ONLY_OPERATIONAL_ACTIVATION = APPROVED_FOR_BOUNDED_P22_1_PILOT`
Project: `K-Geopolitical Monitor`
Authorization basis: explicit owner instruction to continue on 2026-09-19 after P22.2 closure and presentation of the remaining owner gates.

## Narrow interpretation

The owner instruction is interpreted narrowly as approval for the next sequential gate only:

`P22.1 — Bounded Owner-Only Operational Pilot`.

It does **not** authorize P22.3 Wave-B onboarding.

## Authorized scope

One bounded owner-local pilot session on the dedicated owner node:

`kgm-e4-owner-pilot`

Authorized actions:

- run a read-only/preflight inspection of the owner-local KGM runtime;
- use the existing governed source set only;
- perform one bounded operational monitoring session / due-cycle sweep;
- collect current public/free source material already authorized by the existing source network;
- persist project-local runtime evidence produced by that bounded pilot;
- inspect resulting owner workspace, source health, monitoring runs, findings, semantic/provenance bindings and coverage limitations;
- write evidence/results/checkpoint artifacts back to the repository.

## Explicit non-authorization

This decision does **not** authorize:

- Wave-B onboarding or repository activation of P22.2 candidates;
- enabling a persistent unattended scheduler beyond the bounded pilot session;
- public ingress;
- shared runtime;
- paid or secret-bearing providers;
- runtime deployment or service restart outside the bounded pilot mechanism;
- migration `033`;
- production/live cutover;
- Plugin build/publication;
- external publication;
- Phase 17 publication activation;
- Phase 18 shared-runtime activation.

## Runtime boundary

The pilot remains:

```text
RUNTIME_STORAGE = PROJECT_LOCAL_ONLY
PRODUCTION_LIVE = NOT_OPERATIONAL
PUBLIC_INGRESS = NO
SHARED_RUNTIME_ACTIVE = NO
PAID_PROVIDERS = NONE_APPROVED
WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED
```

## Epistemic boundary

P13.5/P13.6 remain the sole canonical factual-verification authority.

Operational collection, source health, finding counts, analytical confidence, forecast inputs and owner feedback cannot promote factual truth.

## Authorization state

```text
P22_1_OWNER_AUTHORIZATION = APPROVED_FOR_BOUNDED_PILOT
P22_1_EXECUTION_SCOPE = ONE_BOUNDED_OWNER_LOCAL_SESSION
P22_1_TARGET_NODE = kgm-e4-owner-pilot
P22_3_WAVE_B_ONBOARDING = OWNER_DECISION_REQUIRED
```
