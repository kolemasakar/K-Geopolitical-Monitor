# GPT Store Pilot Test Plan

Status: ACTIVE_PRIVATE_PILOT_PREPARATION
Date: 2026-08-26
Project: K-Geopolitical Monitor

## Goal

Use the existing private K-Geopolitical Monitor GPT as the initial free owner-only test surface for the validated K-Geopolitical Monitor analytical baseline.

Public sharing and GPT Store publication are deferred until private testing is successful and an eligible paid workspace/account is justified and approved.

This is an unnumbered post-Phase-11 pilot activity. It is not ROADMAP Phase 12 and does not create M14.

## Current Access Model

Initial mode:
- K-Geopolitical Monitor GPT exists under the project owner's account;
- sharing remains private/owner-only;
- testing is performed only by the project owner;
- no paid workspace migration is required for the initial pilot;
- current public-sharing restrictions are classified as PLATFORM_LIMITATION, not as a K-Geopolitical Monitor engineering defect.

The existing private GPT is sufficient for configuration, instruction tuning, Action/API integration and owner-only functional testing.

## Future Publication Gate

After successful private testing:
- review current OpenAI account/workspace publication rules;
- decide whether a paid eligible workspace/account is justified;
- if approved, move or recreate the required GPT configuration in the eligible environment;
- run a controlled sharing test before any GPT Store publication;
- only then consider public GPT Store exposure.

Public sharing is deferred, not cancelled.

## GPT and Backend Boundary

The GPT is the user-facing interaction/orchestration layer.

The GPT itself must not be treated as the unattended 24/7 monitoring host.

Unattended monitoring, durable state, scheduled collection, source reputation history, retries and coverage assessment belong to the K-Geopolitical Monitor backend/runtime.

If GPT Actions are used:
- the backend requires a reachable HTTPS API;
- the Action contract must use an explicit OpenAPI schema;
- action calls must remain bounded by project truth/isolation rules;
- privacy/publication requirements become mandatory before any public sharing stage.

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
- median response usefulness score from the project owner;
- defect severity distribution.

Critical acceptance target:
- critical_truth_violation_count = 0.

## Test Cohorts

Current approved progression:

1. Owner-only private cohort
- project owner only;
- deterministic benchmark prompts;
- real-world prompts;
- expected evidence and truth-boundary outcomes;
- source/local-language checks;
- Action/backend failure checks.

2. Controlled external cohort
- deferred until owner-only testing is successful and a sharing-capable account/workspace is approved.

3. Public GPT Store pilot
- deferred until a paid eligible environment is approved and controlled sharing succeeds.

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

## Exit Gate For Owner-Only Pilot

The owner-only pilot may be declared successful only when:
- no unresolved CRITICAL verification/truth-boundary defect exists;
- core research/fact-check/report workflows are reproducibly usable;
- local-source/local-language behavior is measurable and failures remain visible;
- GPT instruction behavior is stable enough to justify broader sharing;
- action/backend failures fail closed;
- source provenance remains traceable;
- the project has an evidence-backed list of defects, requested improvements and new requirements.

## Post-Pilot Rule

Only after successful owner-only testing:
- perform a structured pilot retrospective;
- approve/reject discovered new requirements;
- decide whether a paid eligible GPT workspace/account is justified;
- design automatic translation as the first planned expansion;
- review source reputation/catalog schema extension;
- review unattended monitoring deployment resources;
- review shared production runtime only if test/launch conditions justify it;
- draft the next ROADMAP extension.

No next roadmap phase is pre-approved by this pilot plan.
