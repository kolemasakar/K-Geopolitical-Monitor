# K-Geopolitical Monitor
Global geopolitical monitoring system.

Version: 1.8
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
- Engineering implementation: BASELINE_VALIDATED through M10
- M5 full test cycle: PASS - 57 tests in GitHub Actions run 32953343877
- M6 Controlled Pilot Monitoring baseline: PASS - 62 tests in GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests in GitHub Actions run 32962379499
- M7 live public-source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests in GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 strategic alerts hardened regression: PASS - 82 tests in GitHub Actions run 32965387054
- M10 multi-region/language regression: PASS - 88 tests in GitHub Actions run 32966128001
- ROADMAP Phase 5 Controlled Pilot Monitoring engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion engineering baseline: BASELINE_VALIDATED
- Region/language coverage is watch-scoped metadata and does not modify evidence confidence or source independence
- Strategic alerts are project-local, deterministic, evidence-traceable and idempotent
- Controlled live integrations: Consilium RSS and GDELT DOC 2.0
- Shared infrastructure architecture: HYBRID
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending a new explicit architecture approval
- Production/global external integrations: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL
- Current roadmap activity: Phase 8 Advanced Geopolitical Graph preparation
- Next step: extend the existing M4 Knowledge Graph baseline with advanced actor/event graph integration rather than creating a duplicate graph subsystem

Implementation milestone labels M0-M11 are engineering work packages and are not identical to ROADMAP phase numbers.
