# K-Geopolitical Monitor
Global geopolitical monitoring system.

Version: 1.7
Status: ACTIVE

## Purpose

K-Geopolitical Monitor is designed for discovery, verification, analysis and forecasting of significant geopolitical developments.

## Documentation

- PROJECT_CONCEPT_FOUNDATION.md - approved product intent
- ROADMAP.md - approved development phases
- PROJECT_DOCUMENTATION_GOVERNANCE.md - documentation governance
- docs/implementation/ - implementation milestone records and validation artifacts

## Current State

- Product concept: APPROVED
- Engineering implementation: BASELINE_VALIDATED through M9
- M5 full test cycle: PASS - 57 tests in GitHub Actions run 32953343877
- M6 Controlled Pilot Monitoring baseline: PASS - 62 tests in GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests in GitHub Actions run 32962379499
- M7 live public-source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests in GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 strategic alerts hardened regression: PASS - 82 tests in GitHub Actions run 32965387054
- ROADMAP Phase 5 Controlled Pilot Monitoring engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring engineering baseline: BASELINE_VALIDATED
- Strategic alerts: project-local, deterministic, evidence-traceable and idempotent
- Alert priorities: NORMAL / HIGH / CRITICAL; priority does not alter evidence confidence or bypass cadence
- Controlled live integrations: Consilium RSS and GDELT DOC 2.0
- Shared infrastructure architecture: HYBRID
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending a new explicit architecture approval
- Production/global external integrations: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL
- Current roadmap activity: Phase 7 Multi-Region Expansion preparation
- Next step: define and validate M10 region/language coverage contracts while preserving origin-based verification and project-local storage

Implementation milestone labels M0-M10 are engineering work packages and are not identical to ROADMAP phase numbers.
