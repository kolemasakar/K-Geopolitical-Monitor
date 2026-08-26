# K-Geopolitical Monitor
Global geopolitical monitoring system.

Version: 2.0
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
- Engineering implementation: BASELINE_VALIDATED through M12
- M5 full test cycle: PASS - 57 tests in GitHub Actions run 32953343877
- M6 Controlled Pilot Monitoring baseline: PASS - 62 tests in GitHub Actions run 32961649091
- M7 deterministic regression: PASS - 68 tests in GitHub Actions run 32962379499
- M7 live public-source smoke: PASS - GitHub Actions run 32962576874
- M8 deterministic regression: PASS - 73 tests in GitHub Actions run 32963096313
- M8 live end-to-end controlled pilot: PASS - GitHub Actions run 32963354135
- M9 strategic alerts hardened regression: PASS - 82 tests in GitHub Actions run 32965387054
- M10 multi-region/language regression: PASS - 88 tests in GitHub Actions run 32966128001
- M11 Advanced Geopolitical Graph final regression: PASS - 118 tests in GitHub Actions run 32973378757
- M12 Advanced Forecasting final regression: PASS - 154 tests in GitHub Actions run 32980859938
- ROADMAP Phase 5 Controlled Pilot Monitoring engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph engineering baseline: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting engineering baseline: BASELINE_VALIDATED
- Advanced graph: durable, deterministic, evidence-backed, temporal/causal and explainable
- Advanced forecasting: durable version identity, typed provenance, immutable scenario updates, outcome evaluation, calibration history and explainable queries
- Forecasts remain analytical outputs, not facts
- Graph relationships may be forecast inputs but never become independent source evidence
- Forecast probability and scenario confidence do not modify M8 confidence, independent-origin count or verification status
- Region/language and translation metadata do not create source independence
- Controlled live integrations: Consilium RSS and GDELT DOC 2.0
- Shared infrastructure architecture: HYBRID
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending a new explicit architecture approval
- External forecasting providers: NONE_APPROVED and not required by the validated M12 baseline
- External graph providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL
- Current roadmap activity: Phase 10 Full Reporting Environment preparation
- Next engineering work package: M13 Full Reporting Environment delta audit and implementation plan

Implementation milestone labels M0-M13 are engineering work packages and are not identical to ROADMAP phase numbers.
