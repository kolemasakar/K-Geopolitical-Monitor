# GPT Store Pilot Test Plan

Status: ACTIVE_PREPARATION
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Publish the user-facing GPT when current OpenAI account/workspace rules permit it, then run structured external tests against the validated K-Geopolitical Monitor analytical baseline before planning the next roadmap extension.

This is an unnumbered post-Phase-11 pilot activity. It is not ROADMAP Phase 12 and does not create M14.

## External Platform Eligibility Gate

Before publication, verify current OpenAI GPT publication eligibility for the account/workspace in use.

Current product documentation must be checked at execution time because GPT creation/publishing availability may change.

If GPT Store publication is not available for the current account/workspace, do not reinterpret that as a K-Geopolitical Monitor engineering failure. Use the strongest permitted test-sharing mode and record the platform blocker separately.

## GPT and Backend Boundary

The GPT is the user-facing interaction/orchestration layer.

The GPT itself must not be treated as the unattended 24/7 monitoring host.

Unattended monitoring, durable state, scheduled collection, source reputation history, retries and coverage assessment belong to the K-Geopolitical Monitor backend/runtime.

If GPT Actions are used:
- the backend requires a reachable HTTPS API;
- the Action contract must use an explicit OpenAPI schema;
- public actions must meet current OpenAI privacy-policy requirements;
- action calls must remain bounded by project truth/isolation rules.

## Pilot Functional Test Areas

### A. Query and intent handling

Test at least:
- broad geopolitical research;
- country/region research;
- current event analysis;
- fact/claim verification;
- source comparison;
- actor/entity analysis;
- scenario/forecast request;
- report request;
- coverage limitation request.

### B. Source behavior

Validate that the system:
- uses public sources;
- seeks local sources for local events;
- seeks local-language material where relevant and available;
- keeps source identity and original provenance;
- exposes source reputation/status when relevant;
- does not silently treat social-media publication as verified fact;
- does not use duplicated/reposted material as independent-origin inflation;
- treats compromised sources as reviewable low-trust/narrative evidence rather than deleting their existence.

### C. Verification integrity

Zero-tolerance pilot regressions:
- no automatic VERIFIED state without approved evidence semantics;
- no translation-based source independence;
- no graph-based source independence;
- no forecast-to-fact promotion;
- no coverage-to-verification promotion;
- no report presentation changing upstream truth.

### D. Local-source coverage

For selected test events, define expected local regions/languages before the test.

Measure:
- whether local sources were sought;
- whether at least one suitable local-language source was found when publicly available;
- whether source reputation/status was retained;
- whether local-source absence was reported as GAP/UNKNOWN/UNAVAILABLE rather than hidden.

### E. Failure and degraded behavior

Test:
- one unavailable source;
- all configured live adapters unavailable;
- stale source state;
- unknown source state;
- unsupported coverage dimension;
- malformed/compromised source identity;
- empty successful fetch;
- backend/API unavailable;
- incomplete regional coverage.

The system must fail closed and expose limitations.

### F. User-facing report quality

Evaluate:
- clarity;
- evidence traceability;
- distinction between facts, verification state, analysis, graph inference and forecasts;
- visibility of uncertainty;
- visibility of source limitations;
- usefulness of strategic summary;
- reproducibility for equivalent persisted inputs.

## Pilot Metrics

Required metrics should include:
- test_case_count;
- success/failure outcome;
- critical_truth_violation_count;
- hallucinated_or_untraceable_source_count;
- local_source_expected_count;
- local_source_satisfied_count;
- local_language_expected_count;
- local_language_satisfied_count;
- source_status_visibility_failures;
- verification_boundary_failures;
- coverage_boundary_failures;
- backend/action failures;
- median response usefulness score from testers;
- defect severity distribution.

Critical acceptance target:
- critical_truth_violation_count = 0.

## Test Cohorts

Recommended progression:

1. Internal deterministic/preview cohort
- project owner/developer;
- known benchmark prompts;
- expected evidence and boundary outcomes.

2. Controlled external cohort
- small set of testers;
- different geopolitical knowledge levels;
- real-world prompts not used during development;
- collect structured feedback and failure examples.

3. Public GPT Store pilot, if publication is permitted
- observe real usage patterns;
- capture reproducible defects only through privacy-safe telemetry/feedback mechanisms;
- do not add external publishing/notification behavior during this stage.

## Test Result Classification

Each issue should be classified as one of:
- PRODUCT_BEHAVIOR;
- SOURCE_COVERAGE;
- SOURCE_REPUTATION;
- LOCAL_LANGUAGE_COVERAGE;
- VERIFICATION_INTEGRITY;
- FORECAST_QUALITY;
- REPORT_QUALITY;
- GPT_INSTRUCTION;
- ACTION_API;
- RUNTIME_RELIABILITY;
- PERFORMANCE;
- UX;
- PLATFORM_LIMITATION;
- NEW_REQUIREMENT.

Severity:
- CRITICAL;
- HIGH;
- MEDIUM;
- LOW.

## Exit Gate

The pilot may be declared successful only when:
- no unresolved CRITICAL verification/truth-boundary defect exists;
- core research/fact-check/report workflows are reproducibly usable;
- local-source/local-language behavior is measurable and failures remain visible;
- GPT instruction behavior is stable enough for public use;
- action/backend failures fail closed;
- source provenance remains traceable;
- the project has an evidence-backed list of defects, requested improvements and new requirements.

## Post-Pilot Rule

Only after successful pilot testing:
- perform a structured pilot retrospective;
- approve/reject discovered new requirements;
- design automatic translation as the first planned expansion;
- review source reputation/catalog schema extension;
- review unattended monitoring deployment resources;
- review shared production runtime only if test/launch conditions justify it;
- draft the next ROADMAP extension.

No next roadmap phase is pre-approved by this pilot plan.
