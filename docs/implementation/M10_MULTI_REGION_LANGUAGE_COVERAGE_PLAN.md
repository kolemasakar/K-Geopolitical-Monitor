# M10 Multi-Region and Language Coverage Plan

Status: COMPLETED
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 7 - Multi-Region Expansion

## Goal

Add explicit region and language scope, observation attribution and measurable coverage gaps without changing evidence truth, source independence or runtime-storage boundaries.

## Mandatory Boundaries

- Runtime storage remains PROJECT_LOCAL_ONLY.
- Region and language are coverage/attribution metadata, not evidence confidence multipliers.
- A translated, indexed or region-tagged observation does not create a new independent origin.
- Original publisher/origin provenance remains authoritative for M8 verification independence.
- Region/language attribution does not modify M8 claim confidence or verification status.
- Watch scope is explicit and persisted.
- Coverage gaps are measurable and queryable.
- No new external source or translation provider is approved by M10 itself.

## M10.1 Region and Language Registry

Implemented and validated:

- canonical project-local region registry;
- canonical project-local language registry;
- deterministic region/language code normalization;
- optional region grouping.

Gate:
M10_1_SCOPE_REGISTRY_VALIDATED

## M10.2 Watch Scope and Observation Attribution

Implemented and validated:

- required region/language pairs per monitoring watch;
- watch-scoped raw-item attribution;
- SOURCE_METADATA / ANALYST / DECLARED / TRANSLATION attribution types;
- attribution confidence;
- original-language marker;
- fail-closed validation for missing watches, raw items, regions and languages;
- cross-watch attribution isolation.

Gate:
M10_2_ATTRIBUTION_VALIDATED

## M10.3 Region/Language Coverage Reporting

Implemented and validated:

- required scope pairs;
- observed scope pairs;
- missing scope pairs;
- observed region set;
- observed language set;
- deterministic coverage ratio;
- persistent report identity and timestamp;
- restart persistence.

Gate:
M10_3_COVERAGE_VALIDATED

## M10.4 Verification-Isolation Gate

Validated:

- adding region/language attribution does not increase independent-origin count;
- translation metadata does not increase confidence;
- translation metadata does not change verification status;
- claim identity remains unchanged after region/language attribution;
- watch-scoped attribution does not leak across watches;
- state survives runtime restart;
- full deterministic regression CI remains green.

Gate:
M10_MULTI_REGION_LANGUAGE_BASELINE_PASS

## Validation Evidence

- GitHub Actions run 32966128001: PASS.
- Full regression: 88 passed in 2.07s.
- Migration 009 is included in the canonical migration contract.
- M8 verification-isolation regression: PASS.
- Cross-watch attribution isolation: PASS.
- Restart persistence: PASS.

## Completion Boundary

All M10 engineering gates passed.

ROADMAP Phase 7 - Multi-Region Expansion engineering baseline is BASELINE_VALIDATED.

M10 completion does not approve global production coverage, automatic translation providers, shared runtime storage or production/live OPERATIONAL status.
