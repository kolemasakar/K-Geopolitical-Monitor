# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 2.0
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

## 2026-08-26 - M8 Live End-to-End Controlled Pilot

- Approved M7 live collections connected to project-local claim analysis and operational output.
- Deterministic normalized-title claim grouping and collection-scoped analysis persistence implemented.
- Evidence independence changed from adapter identity to original publisher/origin identity.
- Single-origin evidence remains DETECTED; two distinct origins are required for PARTLY_VERIFIED.
- Same-origin duplicate observations do not inflate verification status.
- GDELT remains discovery-only metadata and is not counted as independent verification of publisher content.
- Operational findings retain claim, raw-item and original-origin traceability.
- Deterministic M0-M8 regression passed: GitHub Actions run 32963096313, 73 passed in 1.07s.
- Initial live E2E smoke exposed a GDELT HTTP 429 response and validated the need for per-source failure isolation.
- Passing live E2E smoke: GitHub Actions run 32963354135.
- Runtime storage remained PROJECT_LOCAL_ONLY.
- M8 and ROADMAP Phase 5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M9 Strategic Alerts and Continuous Monitoring

- Migration 008 added project-local watch alert policies, strategic alerts and immutable alert events.
- Strategic alerts derive from persisted operational findings.
- Importance, confidence and verification-rank thresholds implemented.
- Stable normalized-title deduplication and cross-cycle alert updates implemented.
- OPEN, UPDATED, INVALIDATED and RESOLVED alert states implemented with persistent history.
- Alert state survives runtime restart.
- NORMAL, HIGH and CRITICAL priority orders already-due watches and never bypasses cadence.
- Hardened M9 acceptance passed: GitHub Actions run 32965387054, 82 passed in 1.71s.
- M9 and ROADMAP Phase 6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M10 Multi-Region and Language Coverage

- Migration 009 added canonical region/language registries, watch-scoped scope requirements, observation attribution and coverage reports.
- Region and language codes are normalized deterministically.
- Raw-item attribution is scoped to a watch and fails closed for wrong-watch or unknown-scope input.
- Required, observed and missing region/language scope pairs are persisted with a deterministic coverage ratio.
- Region/language and translation attribution do not alter M8 claim identity, independent origins, confidence or verification status.
- Region/language state survives runtime restart.
- GitHub Actions run 32966128001: 88 passed in 2.07s.
- M10 and ROADMAP Phase 7 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M11 Advanced Geopolitical Graph

- M4 graph fragments were audited and converged into one durable advanced graph contract rather than a parallel graph subsystem.
- Migration 010 added project-local graph nodes, logical edges, edge evidence and edge history.
- Deterministic canonical node and edge identities implemented with M4 compatibility projection.
- Explicit actor-reference, canonical event, M8 claim and operational finding projection implemented without creating a second canonical truth store.
- Evidence-backed relationship lifecycle implemented with SUPPORTS, CONTRADICTS and CONTEXT evidence roles.
- ACTIVE, UPDATED, INVALIDATED and RESOLVED states preserve material relationship history without destructive deletion.
- Temporal validity intervals, historical snapshots and current-state filtering implemented.
- Bounded cycle-safe causal/influence traversal implemented.
- An initial M11.4 CI failure exposed hash-based traversal ordering; the engine was corrected to canonical semantic ordering without weakening the acceptance test.
- Existing IntelligenceQuery was extended with durable neighborhood, multi-hop, actor relationship, actor-event, historical relation and causal queries.
- Advanced query explanations expose graph IDs, canonical references and evidence references.
- Dedicated M11.6 cross-layer regression proved graph projection/inference/query does not mutate M8 confidence, independent-origin count or verification status and that M10 translation metadata does not create source independence.
- M11 final regression passed: GitHub Actions run 32973378757, 118 passed in 4.24s.
- Runtime storage remained PROJECT_LOCAL_ONLY; no external graph provider is required.
- M11 and ROADMAP Phase 8 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M12 Advanced Forecasting

- Existing forecasting, calibration and historical-validation modules were audited and extended rather than replaced with a parallel stack.
- Migration 011 added durable forecasts, immutable forecast versions and immutable scenario versions.
- Deterministic forecast/version/scenario identities, monotonic versioning and normalized raw/calibrated probability distributions implemented.
- Migration 012 added typed provenance-bound forecast inputs with explicit SOURCE_EVIDENCE, CANONICAL_EVENT, GRAPH_RELATIONSHIP, OPERATIONAL_FINDING and ANALYST_ASSUMPTION kinds.
- Durable input references fail closed; graph relationships remain analytical inputs rather than independent source evidence.
- Scenario lifecycle supports complete drivers, constraints, triggers, inhibitors, uncertainty and invalidation signals with immutable next-version updates.
- Migration 013 added evidence-backed outcome resolution and immutable exact-version forecast evaluation.
- Binary Brier/calibration metrics reuse the existing metric helpers; PARTIAL and AMBIGUOUS outcomes remain deliberately unscored.
- Migration 014 added reproducible calibration history with explicit method/version metadata, exact evaluation-ID cohorts and a minimum five-scorable-evaluation contract.
- Initial M12.5 CI exposed inconsistent RAW/CALIBRATED bucket return ordering; repository ordering was corrected without changing calibration values or weakening the test.
- M12.5 fixed regression passed: GitHub Actions run 32977809109, 148 passed in 11.05s.
- AdvancedForecastQuery added current forecast, immutable version history, scenario comparison, provenance explanation and outcome/evaluation/calibration history.
- M12.6 regressions proved forecasting queries do not mutate M8 verification/confidence/origin state or M11 graph state and that graph-derived inputs remain separate from source evidence.
- M12 final regression passed: GitHub Actions run 32980859938, 154 passed in 8.19s.
- Runtime storage remained PROJECT_LOCAL_ONLY; no external forecasting provider is required.
- M12 and ROADMAP Phase 9 recorded as BASELINE_VALIDATED.

## Current State

- Documentation: RECONCILED through M12
- Engineering implementation: BASELINE_VALIDATED through M12
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 10 Full Reporting Environment preparation
- Next development activity: M13 Full Reporting Environment delta audit and implementation plan
- Production/live operational status: NOT_OPERATIONAL
