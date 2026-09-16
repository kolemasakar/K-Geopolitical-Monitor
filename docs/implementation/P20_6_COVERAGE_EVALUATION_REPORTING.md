# P20.6 — Coverage Evaluation & Reporting

Status: `IMPLEMENTED_FOR_VALIDATION`
Gate: `P20_6_COVERAGE_EVALUATION_REPORTING_VALIDATED`

## Purpose

P20.6 composes already-established Phase 20 evidence into reproducible machine-readable and operator-readable reports. It does not create new source observations, infer missing provenance, activate sources, or change factual-verification state.

Canonical inputs:

1. P20.2 observed coverage matrix and target-policy semantics;
2. P20.3 source independence / monoculture evidence;
3. P20.4 collection health / latency / missing-source evidence.

P20.5 onboarding readiness is intentionally not equivalent to active coverage and therefore does not add source observations to a report.

## Evaluation rules

Evaluation is fail-closed.

- `UNKNOWN` is distinct from both a confirmed gap and adequate coverage.
- Policy `UNSET` blocks `ADEQUATE`, `THIN`, `MISSING_EXPECTED_COVERAGE`, and `NOT_REQUIRED_BY_POLICY` conclusions that require declared target policy.
- Unknown origin identity blocks precise independent-origin, redundancy, dominant-origin and monoculture conclusions.
- Unmeasured health blocks current `HEALTHY`, `DEGRADED_COLLECTION`, stale/failed-source and latency-outlier conclusions.
- Portfolio availability metadata is governance context, not a substitute for current collection-health measurement.
- A current collection failure cannot be translated into low geopolitical activity.
- A quiet healthy feed cannot be translated into collector failure.

When evidence is complete, deterministic status precedence is:

```text
NOT_REQUIRED_BY_POLICY
→ MISSING_EXPECTED_COVERAGE
→ DEGRADED_COLLECTION
→ MONOCULTURE_RISK
→ ADEQUATE
→ THIN
→ UNKNOWN
```

The precedence is a reporting rule, not a truth rule. It identifies the most material source-network condition for the cell while preserving reason codes.

## Required report sections

Machine-readable and operator-readable outputs expose:

```text
GLOBAL_SUMMARY
REGION_GAPS
LANGUAGE_GAPS
SOURCE_TYPE_GAPS
MONOCULTURE_WARNINGS
STALE_OR_FAILED_SOURCES
LATENCY_OUTLIERS
MISSING_EXPECTED_SOURCES
CHANGES_SINCE_PREVIOUS_REPORT
```

Every section has an explicit state. Empty arrays alone are not interpreted as proof of no problem; `UNKNOWN` with reason codes is valid and required when the evidence basis is incomplete.

## Current canonical result

Current repository evidence yields:

```text
OBSERVED_CELLS = 17
GOVERNED_SOURCES = 10
COVERAGE_POLICY = UNSET
KNOWN_ORIGIN_SOURCES = 0
MEASURED_HEALTH_SOURCES = 0
ADEQUATE = 0
CONFIRMED_GAPS = 0
CONFIRMED_MONOCULTURE = 0
CONFIRMED_COLLECTION_DEGRADATION = 0
UNKNOWN_CELLS = 17
```

This is not a negative assessment of geopolitical coverage. It is an explicit statement that the current repository evidence does not yet justify a stronger coverage classification.

## Changes since previous report

The first canonical P20.6 report has `NO_PREVIOUS_REPORT`. Future comparisons must compare equivalent schema/policy semantics and must not manufacture change history from repository timestamps or uninstrumented runtime history.

## Epistemic boundary

Coverage evaluation remains operational/source-network evidence. It cannot promote a claim to verified, increase independent claim evidence, resolve contradictions, or change factual confidence. P13.5/P13.6 remain the current factual-verification authority; P21 may extend claim-level evaluation later.

## Safety boundary

P20.6 performs no runtime deployment, service restart, live-source expansion, ingest change, migration 033, paid-resource authorization, or shared-runtime activation.
