# M10 Multi-Region and Language Coverage Plan

Status: ACTIVE
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
- M10 must not modify M8 claim confidence or verification status merely because more region/language tags exist.
- Watch scope must be explicit and persisted.
- Coverage gaps must be measurable and queryable.
- No new external source provider is approved by M10 itself.

## M10.1 Region and Language Registry

Implement project-local canonical registries for:

- region code;
- region name;
- optional region group;
- language code;
- language name.

Codes must be normalized and deterministic.

Gate:
M10_1_SCOPE_REGISTRY_VALIDATED

## M10.2 Watch Scope and Observation Attribution

Implement:

- required region/language pairs per monitoring watch;
- watch-scoped raw-item attribution;
- attribution type and confidence;
- original-language marker;
- validation that referenced watches, raw items, regions and languages exist.

Gate:
M10_2_ATTRIBUTION_VALIDATED

## M10.3 Region/Language Coverage Reporting

Implement deterministic coverage reports containing:

- required scope pairs;
- observed scope pairs;
- missing scope pairs;
- observed region set;
- observed language set;
- coverage ratio;
- persistent report timestamp.

Gate:
M10_3_COVERAGE_VALIDATED

## M10.4 Verification-Isolation Gate

Validate that:

- adding region/language attribution does not increase independent-origin count;
- adding translation/language metadata does not increase confidence;
- watch-scoped attribution does not leak across watches;
- state survives runtime restart;
- full deterministic regression CI remains green.

Gate:
M10_MULTI_REGION_LANGUAGE_BASELINE_PASS

## Completion Boundary

M10 is complete only when all gates pass and the full deterministic regression suite succeeds.

M10 completion may validate the ROADMAP Phase 7 engineering baseline, but does not approve global production coverage or automatic translation providers.
