# Project Checkpoint — P20.4 Collection Health / Latency Validated

Date: 2026-09-16
Status: `VALIDATED`
Gate: `P20_4_COLLECTION_HEALTH_LATENCY_VALIDATED`

Implementation PR: `#101 — Validate P20.4 collection health, latency and missing-source semantics`
Implementation merge anchor: `d2aacd82788c54da5e36e83399a5c9b826bd9460`
Validation run: `35097483496 / CI #1519 / SUCCESS`
Validation result: `1219 passed in 275.97s`.

## Validated contract

P20.4 now provides deterministic, explainable collection-quality semantics over existing P12.5/P19 evidence:

- current collector health and content freshness/latency remain separate dimensions;
- current successful collection with no recent content resolves to `NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY`, not event silence;
- stale collection measurement resolves separately from stale/absent content;
- current transport failure is distinguishable as `UNREACHABLE` from parser/governance degradation;
- expected disabled, unexpected disabled, expected-not-registered and present-unmeasured states are explicit;
- P19 recovery `GAP/UNKNOWN` remains historical coverage evidence and does not by itself reclassify current collector health;
- repository governance metadata is not promoted into a current health measurement without a fresh runtime snapshot.

Current repository-only baseline remains intentionally:

```text
SOURCE_COUNT = 10
MEASURED_SOURCE_COUNT = 0
UNMEASURED_SOURCE_COUNT = 10
CURRENT_HEALTH = UNKNOWN for all 10
```

This does not claim the owner-local runtime is unhealthy; it records that canonical repository state contains no fresh current runtime-health observation for the evaluation instant.

## Epistemic boundaries

```text
COLLECTION_HEALTH != CONTENT_CREDIBILITY
CONTENT_FRESHNESS != FACTUAL_VERIFICATION
NO_RECENT_CONTENT != NO_GEOPOLITICAL_ACTIVITY
RECOVERY_GAP != CURRENT_COLLECTOR_FAILURE
PORTFOLIO_AVAILABILITY != CURRENT_OPERATIONAL_MEASUREMENT
```

## Safety boundary

No live-source expansion, ingest mutation, runtime deployment, service restart, control-plane change, migration 033, paid/shared resource authorization or shared-runtime activation was introduced.

## Transition

Current position:
`PHASE_20_P20_4_VALIDATED_P20_5_READY`

Next gate:
`P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED`
