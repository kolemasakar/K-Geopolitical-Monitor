# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 1.4
Status: ACTIVE

## 2026-08-24

- Repository documentation foundation created.
- Product concept approved.
- Roadmap approved.
- Documentation governance approved.
- Phase 1 technical documentation package initialized.
- Engineering implementation milestone records M0-M4 added under docs/implementation/.
- M4 completion report recorded the Knowledge Graph and Global Intelligence baseline.

## 2026-08-26 - M4 to M5 remediation

- Repository state audit performed before M5.
- Documentation drift identified and reconciled across canonical state files.
- M4 dedicated validation gate replaced with functional acceptance tests.
- Intelligence Query baseline hardened with deterministic graph search, causal-chain traversal and evidence-based explanation.
- Targeted M4 acceptance gate passed: 4 tests.
- Reproducible Python project contract added through pyproject.toml.
- Canonical migration runner and repeatability test added.
- GitHub Actions CI baseline added.
- Historical M0/M1 contract defects and floating-point test defects found by CI were corrected.
- Full regression CI passed: 45 tests on Python 3.11.16, workflow run 32950015789.
- M5 security, data and cross-project integration boundaries documented.
- Shared Infrastructure Architecture Review completed across K-Geopolitical Monitor, K_Research_Critic, K-Trader, VoiceBridge and AI_general.
- HYBRID shared-infrastructure architecture selected.
- M5 readiness gate passed.

## 2026-08-26 - M5 Operational Intelligence Platform

- Owner approved continuation without mixed runtime storage through successful completion of the full M5 test cycle.
- Shared Infrastructure ADR approved with mandatory PROJECT_LOCAL_ONLY runtime storage for M5.
- M5 implementation plan established M5.1-M5.4 validation gates.
- Project-local runtime storage policy implemented with rejection of runtime database paths outside the project data directory.
- Operational monitoring schema added for watches and runs.
- Watch persistence, run lifecycle and deterministic due-watch selection implemented.
- Controlled monitoring cycle orchestration implemented.
- Per-watch failure isolation, retry metadata and interrupted-run recovery implemented.
- Operational findings persistence and deterministic ranking implemented.
- Evidence-reference traceability and explanation requirements enforced for operational findings.
- M5 schema migrations extended and validated for repeatable initialization.
- M5.1 Runtime Foundation gate passed.
- M5.2 Monitoring Cycle gate passed.
- M5.3 Operational Output gate passed.
- M5 full test cycle passed on implementation commit 1bd258e17cd99b94aa2c751f2fb9f10459f4457c.
- GitHub Actions run 32953343877 completed successfully: 57 passed in 1.05s on Python 3.11.16.
- M5 completion recorded as BASELINE_VALIDATED.
- Successful test completion did not enable shared runtime storage; a new explicit architecture approval remains required for any future mixed/shared runtime storage.

## 2026-08-26 - M6 Controlled Pilot Monitoring

- M6 controlled pilot plan established project-local source, coverage and regression gates.
- Deterministic JSONL pilot-source adapter implemented under data/pilot_sources.
- Pilot source paths outside the project-local controlled-source boundary are rejected.
- Approved source-class validation implemented from SOURCE_POLICY.md.
- Source identity and raw source items are persisted in canonical project-local tables.
- Operational findings retain raw-item and source evidence references.
- Persistent pilot coverage reporting implemented with observed source classes, required source classes, explicit gaps and coverage confidence.
- Controlled-pilot execution validated across cadence windows and runtime restart.
- Repeated pilot ingestion is idempotent for canonical raw-item identities.
- Invalid source classes fail the affected run without generating operational findings.
- Canonical migration 005_controlled_pilot_coverage.sql added and included in repeatability validation.
- Full repository CI passed at validation checkpoint c1ef35841e85fdc1d3b1c2c02cd88ef8ae379af2.
- GitHub Actions run 32961649091 completed successfully: 62 passed in 0.91s on Python 3.11.16.
- M6 controlled pilot baseline recorded as BASELINE_VALIDATED.
- SOURCE_POLICY.md reconciled to the implemented source/provenance state.
- EXTERNAL_INTEGRATIONS.md reconciled to the approved PROJECT_LOCAL_ONLY boundary.
- M6 validation does not approve a production external source or live operational deployment.

## Current State

- Documentation: RECONCILED through M6
- Engineering implementation: BASELINE_VALIDATED through M6
- M4 acceptance: PASS
- M5 full test cycle: PASS
- M6 controlled pilot baseline: PASS
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Production external integrations: NONE_APPROVED
- Current roadmap activity: Phase 5 Controlled Pilot Monitoring
- Live public-source pilot: READY_FOR_INTEGRATION_REVIEW
- Production/live operational status: NOT_OPERATIONAL
- Next development activity: define and validate explicit live public-source integration records
