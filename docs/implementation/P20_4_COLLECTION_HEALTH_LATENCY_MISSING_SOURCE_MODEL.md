# P20.4 — Collection Health, Latency & Missing-Source Semantics

Status: `IMPLEMENTED_FOR_VALIDATION`
Gate: `P20_4_COLLECTION_HEALTH_LATENCY_VALIDATED`

## Objective

Normalize existing P12.5 source-health/freshness signals and P19 recovery coverage into deterministic P20 collection-quality semantics without adding a second collector, changing runtime behavior, or treating operational health as factual truth.

## Reused evidence

P20.4 composes existing evidence only:

- P12.1/P20.1 source registration and cadence/freshness metadata;
- P12.5 `operational_state`, `measurement_freshness`, `content_freshness`, attempt age/status and error class;
- P19 recovery coverage (`COMPLETE`, `GAP`, `UNKNOWN`) as a separate historical-coverage dimension.

P20.4 does not change P13.5/P13.6 verification authority.

## Canonical health states

```text
HEALTHY
DEGRADED
STALE
UNREACHABLE
DISABLED_EXPECTED
DISABLED_UNEXPECTED
NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY
UNKNOWN
```

### Deterministic precedence

1. An expected source that is not registered is explicit `EXPECTED_NOT_REGISTERED`; health remains `UNKNOWN` rather than inventing a collector failure.
2. A registered disabled source is `DISABLED_EXPECTED` only when the disable is explicitly expected; otherwise it is `DISABLED_UNEXPECTED`.
3. A registered enabled source with no persisted attempt measurement is `UNKNOWN` / `PRESENT_UNMEASURED`.
4. Collection measurement is stale when attempt age exceeds the existing P12.5 measurement limit: `max(collection_cadence_minutes * 2, expected_freshness_minutes)`.
5. A current failed attempt with `TRANSPORT` error is `UNREACHABLE`.
6. A current failed attempt with parser/governance/unknown error is `DEGRADED`.
7. A current successful attempt for a governance-degraded source remains `DEGRADED`.
8. A current successful collector with no observed recent content is `NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY`; it is not silently converted to geopolitical silence.
9. A current successful collector with content older than `expected_freshness_minutes` is also `NO_RECENT_CONTENT_BUT_COLLECTOR_HEALTHY`; content latency is `EXCEEDED_EXPECTATION` while collection latency remains healthy.
10. A current successful collector with fresh content is `HEALTHY`.

## Latency semantics

Collection and content latency are separate.

`collection_latency_state`:

```text
WITHIN_EXPECTATION
EXCEEDED_EXPECTATION
UNKNOWN
NOT_APPLICABLE
```

The collection expectation reuses the P12.5 measurement limit and does not introduce a new global timeout.

`content_latency_state`:

```text
WITHIN_EXPECTATION
EXCEEDED_EXPECTATION
NO_CONTENT_OBSERVED
UNKNOWN
NOT_APPLICABLE
```

Content expectation reuses each source's governed `expected_freshness_minutes`.

## Missing-source semantics

```text
PRESENT_MEASURED
PRESENT_UNMEASURED
EXPECTED_NOT_REGISTERED
DISABLED_EXPECTED
DISABLED_UNEXPECTED
UNKNOWN
```

A missing expected source or missing measurement must be visible. Neither condition may be interpreted as a quiet information environment.

## Recovery boundary

P19 recovery coverage is preserved independently:

```text
COMPLETE
GAP
UNKNOWN
NOT_APPLICABLE
```

`GAP` means a known historical coverage gap. It does not by itself turn a currently healthy collector into `DEGRADED` or `UNREACHABLE`. This preserves the distinction between current collector health and historical coverage completeness.

## Current repository baseline

The canonical repository contains governed metadata for 10 source paths, but it does not contain a fresh live P12.5 runtime snapshot for the current evaluation instant. Therefore P20.4 current repository-only baseline is intentionally:

```text
source_count = 10
measured_source_count = 0
unmeasured_source_count = 10
health_state = UNKNOWN for all 10
```

The European Parliament governance state remains `DEGRADED`, but that governance metadata is not promoted into a current operational measurement in the absence of a fresh snapshot.

## Epistemic boundaries

```text
COLLECTION_HEALTH != CONTENT_CREDIBILITY
CONTENT_FRESHNESS != FACTUAL_VERIFICATION
NO_RECENT_CONTENT != NO_GEOPOLITICAL_ACTIVITY
RECOVERY_GAP != CURRENT_COLLECTOR_FAILURE
PORTFOLIO_AVAILABILITY != CURRENT_OPERATIONAL_MEASUREMENT
```

## Safety boundary

P20.4 is contract/evidence/test-fixture work only. It does not authorize live-source onboarding, ingestion mutation, runtime deployment, service restart, migration 033, paid resources, shared-runtime activation or a production/live claim.

Next gate after validation: `P20_5_SOURCE_ONBOARDING_CONTRACT_VALIDATED`.
