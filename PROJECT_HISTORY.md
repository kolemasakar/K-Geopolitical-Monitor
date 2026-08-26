# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 2.1
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
- GitHub Actions run 32953343877: 57 passed in 1.05s.
- M5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M6 Controlled Pilot Monitoring

- Deterministic JSONL pilot-source adapter and project-local provenance persistence implemented.
- Coverage gaps/confidence, path isolation, cadence/restart determinism and invalid-source failure behavior validated.
- GitHub Actions run 32961649091: 62 passed in 0.91s.
- M6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M7 Live Public-Source Pilot

- Controlled read-only Consilium RSS and GDELT DOC 2.0 integrations implemented.
- GDELT constrained to discovery/index metadata rather than independent verification.
- Source collection audit, HTTPS transport constraints, deterministic item identity and per-source failure isolation validated.
- GitHub Actions run 32962379499: 68 passed in 0.77s.
- Live source smoke run 32962576874 passed.
- M7 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M8 Live End-to-End Controlled Pilot

- Live collections connected to claim analysis and operational findings.
- Evidence independence changed to original publisher/origin identity.
- Single-origin evidence remains DETECTED; two distinct origins are required for PARTLY_VERIFIED.
- Same-origin duplicates do not inflate verification status.
- Deterministic regression run 32963096313: 73 passed in 1.07s.
- Passing live E2E smoke: run 32963354135.
- Runtime storage remained PROJECT_LOCAL_ONLY.
- M8 and ROADMAP Phase 5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M9 Strategic Alerts and Continuous Monitoring

- Migration 008 added alert policies, strategic alerts and immutable alert events.
- Stable deduplication, cross-cycle updates, OPEN/UPDATED/INVALIDATED/RESOLVED lifecycle and restart persistence implemented.
- Priority orders due watches without bypassing cadence or modifying evidence truth.
- GitHub Actions run 32965387054: 82 passed in 1.71s.
- M9 and ROADMAP Phase 6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M10 Multi-Region and Language Coverage

- Migration 009 added canonical region/language registries, watch-scoped requirements, attribution and coverage reports.
- Required/observed/missing scopes and coverage ratio implemented.
- Region/language and translation attribution do not alter M8 claim identity, origins, confidence or verification.
- GitHub Actions run 32966128001: 88 passed in 2.07s.
- M10 and ROADMAP Phase 7 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M11 Advanced Geopolitical Graph

- M4 graph fragments audited and converged into one durable advanced graph contract.
- Migration 010 added project-local graph nodes, logical edges, edge evidence and material history.
- Deterministic identity, canonical actor/event/claim/finding projection, evidence-backed lifecycle, temporal snapshots and bounded causal traversal implemented.
- Existing IntelligenceQuery extended rather than replaced.
- Cross-layer isolation proved graph analytics do not mutate M8/M10 truth semantics.
- GitHub Actions run 32973378757: 118 passed in 4.24s.
- M11 and ROADMAP Phase 8 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M12 Advanced Forecasting

- Existing forecasting/calibration/history modules extended rather than replaced.
- Migrations 011-014 added immutable forecast/scenario versions, typed provenance, outcomes/evaluations and calibration history.
- Graph inputs remain analytical and never become independent source evidence.
- PARTIAL/AMBIGUOUS outcomes remain unscored.
- Minimum calibration cohort set to five scorable evaluations.
- AdvancedForecastQuery added current/history/scenario/provenance/outcome/evaluation/calibration queries.
- M12.5 fixed regression run 32977809109: 148 passed in 11.05s.
- M12 final regression run 32980859938: 154 passed in 8.19s.
- M12 and ROADMAP Phase 9 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M13 Full Reporting Environment

- Existing findings, alerts, coverage, graph and forecast output surfaces were audited and converged into one canonical reporting subsystem.
- Migration 015 added immutable report snapshots, ordered sections and typed report references.
- One common ReportAssembler preserves source evidence, graph inference, forecast scenarios, assumptions and coverage as distinct presentation classes/references.
- Strategic Alert, Global Geopolitical Brief and Regional/Country Brief assembly implemented.
- Regional reports fail closed on invalid region/language scope and keep incomplete coverage visible.
- Event Dossier assembly is anchored to canonical events.
- Storyline Report remains report-scoped composition; no canonical storyline table was created.
- Forecast Report is anchored to durable forecast versions and preserves probability/confidence/uncertainty/invalidation semantics.
- Strategic Outlook is scope-only explicit composition of selected persisted forecasts/context.
- Deterministic structured and Markdown rendering implemented from the same immutable persisted ReportBundle.
- Rendering is reproducible after restart and uses existing RuntimeStoragePolicy for project-local runtime database enforcement.
- Reporting isolation regressions prove rendering/assembly do not mutate M8 verification confidence/origin count, M10 coverage metadata, M11 graph state or M12 forecast state.
- M13.1 run 32982639826: 160 passed in 11.40s.
- M13.2 run 32989895962: 170 passed in 12.00s.
- M13.3-M13.5 combined run 32992328055: 193 passed in 10.98s.
- M13.6 run 32993269910: 199 passed in 12.10s.
- Runtime storage remained PROJECT_LOCAL_ONLY; no external reporting/publishing provider is required.
- M13 and ROADMAP Phase 10 recorded as BASELINE_VALIDATED.

## Current State

- Documentation: RECONCILED through M13
- Engineering implementation: BASELINE_VALIDATED through M13
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- ROADMAP Phase 10 Full Reporting Environment: BASELINE_VALIDATED
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- Automatic translation providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current roadmap activity: Phase 11 Global Operational Coverage preparation
- Next development activity: Phase 11 delta audit and implementation planning
- Production/live operational status: NOT_OPERATIONAL
