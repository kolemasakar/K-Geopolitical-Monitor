# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 2.4
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
- AdvancedForecastQuery added current/history/scenario/provenance/outcome/evaluation/calibration queries.
- M12.5 fixed regression run 32977809109: 148 passed in 11.05s.
- M12 final regression run 32980859938: 154 passed in 8.19s.
- M12 and ROADMAP Phase 9 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M13 Full Reporting Environment

- Existing findings, alerts, coverage, graph and forecast output surfaces were audited and converged into one canonical reporting subsystem.
- Migration 015 added immutable report snapshots, ordered sections and typed report references.
- One common ReportAssembler preserves source evidence, graph inference, forecast scenarios, assumptions and coverage as distinct presentation classes/references.
- Strategic Alert, Global Geopolitical Brief, Regional/Country Brief, Event Dossier, report-scoped Storyline Report, Forecast Report and Strategic Outlook implemented.
- Deterministic structured and Markdown rendering implemented from the same immutable persisted ReportBundle.
- Rendering is reproducible after restart and uses existing RuntimeStoragePolicy for project-local runtime database enforcement.
- Reporting isolation regressions prove rendering/assembly do not mutate M8 verification confidence/origin count, M10 coverage metadata, M11 graph state or M12 forecast state.
- M13.1 run 32982639826: 160 passed in 11.40s.
- M13.2 run 32989895962: 170 passed in 12.00s.
- M13.3-M13.5 combined run 32992328055: 193 passed in 10.98s.
- M13.6 run 32993269910: 199 passed in 12.10s.
- M13 and ROADMAP Phase 10 recorded as BASELINE_VALIDATED.

## 2026-08-26 - ROADMAP Phase 11 Global Operational Coverage

- Phase 11 delta audit converged existing M6/M7/M10 coverage state and M13 presentation without creating a new verification engine.
- Migration 016 added deterministic operational coverage contracts, typed requirements, immutable snapshots and per-requirement results.
- Migration 017 added per-source collection attempts so successful zero-item acquisition, failure, staleness and unknown state remain distinguishable.
- LiveSourceCollector was hardened so adapter/item source identity mismatch fails closed before ingestion.
- SOURCE_CLASS, SOURCE_ID/SOURCE_AVAILABILITY, REGION_LANGUAGE and FRESHNESS dimensions were converged into one deterministic evaluator.
- Unsupported declared dimensions remain explicit UNMEASURED limitations.
- Coverage statuses are SATISFIED, GAP, UNAVAILABLE, STALE, UNKNOWN and UNMEASURED.
- coverage_ratio measures satisfied required units; coverage_confidence measures assessment observability rather than geopolitical factual confidence.
- Historical/latest coverage query and coverage-aware Global/Regional reporting were integrated through the existing M13 report store.
- GLOBAL remains an explicit scope key; it does not imply complete world coverage and does not hide gaps or limitations.
- Cross-layer regression proved Phase 11 does not mutate M8 verification/origin truth, M11 graph state, M12 forecast probabilities or M13 persisted report snapshots.
- P11.1 run 32996565227: 203 passed in 15.48s.
- P11.2 run 32997440380: 210 passed in 16.63s.
- P11.3 run 32997961490: 217 passed in 27.46s.
- P11.4 run 32999092257: 219 passed in 20.55s.
- P11.5 run 32999835225: 223 passed in 83.96s.
- P11.6 run 33000478908: 226 passed in 17.67s.
- Runtime storage remained PROJECT_LOCAL_ONLY and production/live status remained NOT_OPERATIONAL.
- ROADMAP Phase 11 recorded as BASELINE_VALIDATED without inventing an M14 milestone label.

## 2026-08-27 - Post-Phase-11 unattended runtime harness

- UnattendedMonitoringService added as a thin supervisor over existing due-cycle execution.
- Startup recovery is performed once per process start and unexpected supervisor exceptions remain visible for external service management.
- LiveOperationalCycle added to persist failed monitoring-run state for collection/processing failures and to avoid retry-every-poll cadence loops.
- Successful zero-item live collection remains a completed monitoring attempt.
- No schema or verification-truth semantics were changed.
- Runtime storage remained PROJECT_LOCAL_ONLY.
- GitHub Actions run 33012596904: 236 passed.
- Cloud unattended runtime remained NOT_DEPLOYED and production/live remained NOT_OPERATIONAL.

## 2026-08-27 - Private K-Geopolitical Monitor GPT owner-only pilot

- Private GPT configured as OWNER_ONLY with Web Search and Code Interpreter/Data Analysis enabled.
- No backend Action/API was connected during the pilot.
- Pilot matrix executed across 18 scenarios covering current research, local-language sources, social provenance, same-origin duplication, conflicting sources, compromised sources, official-source limits, graph inference, forecast/fact separation, global coverage, backend hallucination traps, report truth boundaries and research reproducibility.
- Final result: 18/18 PASS, 0 FAIL, 0 BLOCKED.
- Critical truth-boundary violations: 0.
- Hallucinated/untraceable source failures: 0.
- Verification-boundary failures: 0.
- Coverage-boundary failures: 0.
- Backend-access hallucination failures: 0.
- GPT-18/full pilot matrix closure commit: 74f800ffa427e52638b64ed7e37afffc929cad95.
- GPT-18/full pilot matrix closure CI run 33046581445: SUCCESS.
- Owner-only pilot plan closure commit: ba57f30563b936aa4cd9cfa891f726444e07221f.
- Owner-only pilot plan closure CI run 33046621582: SUCCESS.
- Owner-only pilot declared SUCCESSFUL for continued owner-only use.
- Public sharing remained DEFERRED.
- Backend Action/API remained NOT_CONNECTED.
- Production/live remained NOT_OPERATIONAL.
- No ROADMAP Phase 12 or M14 was created.

## 2026-08-27 - Post-pilot retrospective and expansion plan

- Canonical retrospective/expansion artifact created at docs/implementation/POST_PRIVATE_GPT_PILOT_RETROSPECTIVE_AND_EXPANSION_PLAN.md.
- Retrospective commit: 8d874ca70421f4fe367484e3e9bdf562533af2f2.
- Retrospective CI run 33046677596: SUCCESS.
- Low-severity pilot refinements were carried forward without reclassifying them as critical defects.
- E1 Automatic Translation Foundation approved for design and local implementation as the first expansion.
- E2 Source Reputation and Status History approved for design.
- E3 Private GPT Backend Action API approved for design with an initial read-only fail-closed scope.
- E4 Free Unattended Runtime Deployment approved for validation only.
- E5 Admin Read-Only Dashboard, E6 Reproducibility Instrumentation and E7 Forecast Probability Semantics recorded as planned workstreams.
- E8 Controlled External Sharing/Public GPT and E9 Shared Production Runtime remain NOT_APPROVED.
- External translation provider remains NONE_APPROVED.
- Runtime storage remains PROJECT_LOCAL_ONLY.
- No new numbered ROADMAP phase was approved.

## 2026-08-27 - Canonical documentation synchronization

- README.md, ROADMAP.md and ARCHITECTURE.md reconciled with the successful owner-only GPT pilot and post-pilot workstream state.
- Documentation version advanced to 2.3 for the canonical top-level state documents.
- The post-pilot workstreams are explicitly documented as unnumbered activities and do not create ROADMAP Phase 12 or M14.
- Production/live remains NOT_OPERATIONAL.
- A dedicated project control-state checkpoint was created under docs/checkpoints/.

## 2026-08-29 - E1 Automatic Translation Foundation

- Existing M10 language/TRANSLATION attribution behavior was audited and retained.
- Migration 018 added raw_item_translations as a durable versioned translation store.
- Original raw-item text remains unchanged; translated text is stored separately.
- Source/target language, method/provider/version, translation status, uncertainty/error and timestamp are persisted.
- Translation statuses are SUCCESS, FAILED, UNAVAILABLE, UNSUPPORTED and AMBIGUOUS.
- TranslationService and provider-neutral TranslationAdapter contracts were added.
- DeterministicTranslationAdapter was added only for local deterministic validation; it is not an external provider.
- Live translations inherit the normalized publisher origin host already used by M8.
- Non-live raw items without live provenance fall back to source_id as origin identity.
- Conflicting live provenance origins fail closed.
- Translation never creates a new independent origin and does not change M8 verification state or independent-origin count.
- Retranslation creates additive version history and survives runtime restart.
- Canonical E1 implementation commits: 95ccc5208447f7a144208f10cbf4fbf64411ce00, d60660067e44d5cbbe610a0b74ff50a0f096da4b, 51bbb41e6edb716760727d06902ac90e8e6ce5c5 and 9b5f300b0b798cd106ab84d57d14e01c52b4af62.
- GitHub Actions run 33244484173, job 99079456390: SUCCESS, 241 passed in 37.10s.
- E1 recorded as BASELINE_VALIDATED.
- External translation provider remains NONE_APPROVED.
- Runtime storage remains PROJECT_LOCAL_ONLY.
- Production/live remains NOT_OPERATIONAL.
- Current post-pilot engineering workstream becomes E2 Source Reputation and Status History.
- No ROADMAP Phase 12 or M14 was created.

## Current State

- Documentation: RECONCILED through E1 Automatic Translation Foundation
- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- ROADMAP Phase 10 Full Reporting Environment: BASELINE_VALIDATED
- ROADMAP Phase 11 Global Operational Coverage: BASELINE_VALIDATED
- Post-Phase-11 unattended supervisor/live-cycle local baseline: VALIDATED
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External coverage providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- External translation provider: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Private GPT backend Action/API: NOT_CONNECTED
- Unattended cloud runtime: NOT_DEPLOYED
- Public GPT sharing: DEFERRED
- Shared production runtime: NOT_APPROVED
- Current engineering activity: E2 Source Reputation and Status History design and local implementation
- Next roadmap phase: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL
