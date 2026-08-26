# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 1.5
Status: ACTIVE

## 2026-08-24

- Repository documentation foundation created.
- Product concept approved.
- Roadmap approved.
- Documentation governance approved.
- Engineering implementation milestone records M0-M4 added under docs/implementation/.
- M4 completion report recorded the Knowledge Graph and Global Intelligence baseline.

## 2026-08-26 - M4 to M5 remediation

- Repository state audit and documentation reconciliation completed.
- M4 phase-gate validation hardened.
- Reproducible Python, migration and GitHub Actions CI baselines added.
- Shared Infrastructure Architecture Review completed; HYBRID architecture selected.
- M5 readiness gate passed.

## 2026-08-26 - M5 Operational Intelligence Platform

- Shared Infrastructure ADR approved with mandatory PROJECT_LOCAL_ONLY runtime storage.
- Project-local watch/run persistence, monitoring orchestration, failure isolation, retry and recovery implemented.
- Ranked operational findings with evidence references and explanations implemented.
- M5 full test cycle passed on GitHub Actions run 32953343877: 57 passed in 1.05s.
- M5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M6 Controlled Pilot Monitoring

- Deterministic JSONL pilot-source adapter implemented under data/pilot_sources.
- Source identity, raw items, evidence references and coverage reports persisted project-locally.
- Coverage gaps/confidence, path isolation, cadence/restart determinism and invalid-source failure behavior validated.
- GitHub Actions run 32961649091: 62 passed in 0.91s.
- M6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M7 Live Public-Source Pilot

- Explicit controlled-pilot integration records approved for Consilium press-release RSS and GDELT DOC 2.0.
- Both integrations are read-only and require no credentials for the current pilot.
- GDELT was constrained to discovery/index metadata and is not treated as independent verification of publisher claims.
- HTTPS-only live-source transport implemented with timeout and response-size limits.
- Consilium RSS and GDELT JSON adapters implemented with fail-closed parsing.
- Deterministic live-source item IDs, canonical source/raw-item persistence and per-collection provenance implemented.
- Source collection audit supports COMPLETED, PARTIAL and FAILED states with per-source failure accounting.
- Repeated collection preserves multiple collection contexts without duplicating canonical raw items.
- Deterministic M0-M7 regression suite passed: GitHub Actions run 32962379499, 68 passed in 0.77s.
- One-time live network smoke workflow passed: GitHub Actions run 32962576874.
- Live smoke parsed 7 Consilium items and 5 GDELT items for query Ukraine.
- Live Source Smoke workflow returned to manual workflow_dispatch-only mode after validation.
- M7 recorded as BASELINE_VALIDATED.
- M7 does not approve production/global operation or shared runtime storage.

## Current State

- Documentation: RECONCILED through M7
- Engineering implementation: BASELINE_VALIDATED through M7
- M5 full test cycle: PASS
- M6 controlled pilot baseline: PASS
- M7 deterministic regression: PASS
- M7 live-source smoke: PASS
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Controlled-pilot external integrations: 2
- Production/global external integrations: NONE_APPROVED
- ROADMAP Phase 5 Controlled Pilot Monitoring: ACTIVE
- Next development activity: M8 Live End-to-End Controlled Pilot Processing
- Production/live operational status: NOT_OPERATIONAL
