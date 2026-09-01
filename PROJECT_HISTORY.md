# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 3.0
Status: ACTIVE

## 2026-08-24 - Project foundation

- Repository documentation foundation created.
- Product concept, roadmap and documentation governance approved.
- Engineering implementation milestones M0-M4 added.
- M4 Knowledge Graph and Global Intelligence baseline completed.

## 2026-08-26 - M4 to M5 remediation

- Repository state audit and documentation reconciliation completed.
- M4 phase-gate validation hardened.
- Reproducible Python, migration and GitHub Actions CI baselines added.
- Shared Infrastructure Architecture Review completed; HYBRID architecture selected.
- M5 readiness gate passed.

## 2026-08-26 - M5 Operational Intelligence Platform

- Shared Infrastructure ADR approved with mandatory `PROJECT_LOCAL_ONLY` runtime storage.
- Project-local watch/run persistence, monitoring orchestration, failure isolation, retry/recovery and ranked findings implemented.
- Run `32953343877`: 57 passed.
- M5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M6 Controlled Pilot Monitoring

- Deterministic controlled-pilot adapter, project-local provenance and coverage-gap handling implemented.
- Run `32961649091`: 62 passed.
- M6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M7 Live Public-Source Pilot

- Controlled read-only Consilium RSS and GDELT DOC 2.0 integrations implemented.
- GDELT constrained to discovery/index metadata rather than independent verification.
- Run `32962379499`: 68 passed; live smoke `32962576874` passed.
- M7 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M8 Live End-to-End Controlled Pilot

- Live collections connected to claim analysis and operational findings.
- Evidence independence changed to original publisher/underlying-origin identity.
- Same-origin duplicates do not inflate verification state.
- Run `32963096313`: 73 passed; live E2E `32963354135` passed.
- ROADMAP Phase 5 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M9 Strategic Alerts and Continuous Monitoring

- Migration 008 added durable alert policies/state/events.
- Stable deduplication, alert lifecycle, restart persistence and priority/cadence separation implemented.
- Run `32965387054`: 82 passed.
- ROADMAP Phase 6 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M10 Multi-Region and Language Coverage

- Migration 009 added canonical region/language scope, attribution and coverage persistence.
- Translation/region attribution remains isolated from M8 verification truth.
- Run `32966128001`: 88 passed.
- ROADMAP Phase 7 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M11 Advanced Geopolitical Graph

- M4 graph fragments converged into one durable project-local graph contract.
- Migration 010, deterministic identity, lifecycle/history, temporal snapshots and bounded causal traversal implemented.
- Graph analytics do not mutate M8/M10 truth.
- Run `32973378757`: 118 passed.
- ROADMAP Phase 8 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M12 Advanced Forecasting

- Existing forecasting/calibration/history components extended rather than replaced.
- Migrations 011-014 added immutable forecast/scenario versions, typed provenance, outcomes/evaluations and calibration history.
- Graph inputs remain analytical and never become independent evidence.
- Run `32980859938`: 154 passed.
- ROADMAP Phase 9 recorded as BASELINE_VALIDATED.

## 2026-08-26 - M13 Full Reporting Environment

- Existing output surfaces converged into one canonical reporting subsystem.
- Migration 015 added immutable report snapshots, sections and typed references.
- Deterministic structured/Markdown rendering implemented with truth-state isolation.
- Final run `32993269910`: 199 passed.
- ROADMAP Phase 10 recorded as BASELINE_VALIDATED.

## 2026-08-26 - ROADMAP Phase 11 Global Operational Coverage

- Coverage-measurement layer implemented without creating a new verification engine.
- Migrations 016-017 added coverage contracts/results and per-source collection attempts.
- SOURCE_CLASS, SOURCE_ID/SOURCE_AVAILABILITY, REGION_LANGUAGE and FRESHNESS evaluation converged.
- `coverage_ratio` and `coverage_confidence` were given distinct deterministic meanings.
- GLOBAL remains an explicit scope key, not a universal-completeness claim.
- Final run `33000478908`: 226 passed.
- ROADMAP Phase 11 recorded as BASELINE_VALIDATED; no M14 created.

## 2026-08-27 - Post-Phase-11 unattended runtime harness

- UnattendedMonitoringService and cadence-safe LiveOperationalCycle added.
- Failed monitoring runs remain persisted and do not retry every supervisor poll.
- Run `33012596904`: 236 passed.
- Runtime storage remained `PROJECT_LOCAL_ONLY`.

## 2026-08-27 - Private owner-only GPT pilot

- Private GPT configured OWNER_ONLY with web research/data-analysis capabilities.
- No backend Action/API connected during the pilot.
- 18-scenario truth-boundary matrix completed: 18/18 PASS.
- Closure runs `33046581445`, `33046621582`, `33046677596`: SUCCESS.
- Public sharing remained DEFERRED; no ROADMAP Phase 12 or M14 created.

## 2026-08-29 - E1 Automatic Translation Foundation

- Migration 018 added versioned `raw_item_translations`.
- Original source text remains unchanged and translations are stored separately.
- Translation inherits origin and never creates independent-source credit.
- Run `33244484173`: 241 passed.
- E1 recorded as BASELINE_VALIDATED.

## 2026-08-29 - E2 Source Reputation and Status History

- Migration 019 added append-only `source_reputation_history`.
- COMPROMISED remains a source-context state, not an automatic FALSE operator.
- Source reputation does not mutate claim truth or independent-origin count.
- Run `33244795277`: 248 passed.
- E2 recorded as BASELINE_VALIDATED.

## 2026-08-29 - E3 Private GPT Backend Action API

- Owner-only read-only FastAPI persisted-state facade implemented.
- Bearer authentication, read-only/query-only project-local SQLite, no-mutation and no-web-substitution behavior validated.
- Run `33247311921`: 254 passed.
- E3 recorded as BASELINE_VALIDATED.
- HTTPS deployment remained NOT_DEPLOYED; GPT Action remained NOT_CONNECTED.

## 2026-08-29 - E4 Free Unattended Runtime Deployment

- Real OCI Ubuntu 24.04 ARM64 owner-only runtime validated.
- Immutable deployment/bootstrap, real reboot recovery, interrupted-run recovery, due-watch resumption and controlled live collection validated.
- Database/API ingress remained closed; runtime storage remained `PROJECT_LOCAL_ONLY`.
- Run `33258520620`: SUCCESS.
- E4 recorded as `BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`.
- Temporary exception retained public SSH TCP/22 from `0.0.0.0/0` and broad egress pending final hardening.
- Runtime state became `DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / NOT_PRODUCTION`.

## 2026-08-29 - E5 Admin Read-Only Dashboard

- Owner/admin-only read-only dashboard implemented over the existing E3 reader.
- No parallel database introduced.
- Static script-free HTML, restrictive security headers and truth-boundary wording validated.
- x64 run `33263584520`: 282 passed; native ARM64 run `33263584515`: SUCCESS.
- E5 recorded as BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED.

## 2026-08-29 - E6 Reproducibility Instrumentation

- Migration 020 added additive reproducibility audit projection.
- Exact query snapshot, timezone-aware cut-off, adapter fingerprint, source-attempt linkage and deterministic persisted-artifact SHA-256 hashing added.
- Missing request locators remain `NOT_INSTRUMENTED`; unavailable history is not reconstructed.
- Provenance annotations do not alter verification state, confidence or independent-origin count.
- x64 run `33264133429`: 290 passed; native ARM64 run `33264133407`: 290 passed.
- E6 recorded as BASELINE_VALIDATED.

## 2026-08-29 - E7 Forecast Probability Semantics

- M12 persisted raw/calibrated/scenario-confidence separation retained.
- Canonical semantic contract `KGM_FORECAST_SEMANTICS_V1` introduced.
- Read-only `/v1/forecasts/active` API projection added.
- Dashboard and reports expose Raw / Calibrated / Scenario confidence separately.
- Adversarial regression proved forecast values `0.95 / 0.98 / 0.99` do not promote an upstream `DETECTED / 0.31 / 1-origin` claim.
- No migration 021 and no parallel forecasting subsystem introduced.
- Canonical E7 engineering baseline: `72f049b30fcaa3711c7712c8df7d1da1f934f650`.
- x64 run `33265984585`: 294 passed; native ARM64 run `33265984622`: 294 passed.
- E7 recorded as BASELINE_VALIDATED.

## 2026-08-29 - E7 closure and transition

- ROADMAP advanced to v2.8 with E7 BASELINE_VALIDATED.
- E7 closure commit: `585fdae9d2ca816b4d5250e1aade3470d959e11d`.
- Closure CI run `33266213476`: 294 passed.
- Post-E7 bootstrap package added at `BOOTSTRAP_PACKAGE_2026-08-29_K-GEOPOLITICAL-MONITOR_POST_E7_TRANSITION.md`.
- Transition commit: `13af50a9e46a26ed745d5c1159cce3d4e6cef4d5`.
- Transition CI run `33266465042`: 294 passed.
- E8/E9 remained implementation-deferred and no numbered ROADMAP phase was approved.

## 2026-08-29 - D0 documentation convergence / E8 preflight approval

- Owner approved D0 documentation convergence and an E8 read-only preflight/delta audit.
- E8 implementation, public sharing, production exposure, shared runtime storage and E9 remained outside the validated runtime state.
- D0 reconciled README, ARCHITECTURE and PROJECT_HISTORY with the post-E7 state at that time.
- Later owner decisions superseded the E8 trajectory; current state is recorded below.

## 2026-09-01 - E9A Owner-Only Production Runtime Hardening

- E9A was executed as an unnumbered post-Phase-11 engineering workstream; no ROADMAP Phase 12 or M14 was created.
- E9A.1 added fail-closed project-local single-instance runtime leasing.
- E9A.2 established the canonical SQLite durability/concurrency profile.
- E9A.3 established canonical backup/restore and completed a real clean-project-root disaster-recovery drill.
- E9A.4 added owner-only persisted runtime-health instrumentation without truth/coverage inflation.
- E9A.5 hardened systemd/runtime/security policy and retained explicit owner security exceptions.
- E9A.6 completed x64, native ARM64 and real OCI validation.
- Real OCI state-preserving validation run `33486944907`: SUCCESS.
- rpcbind persistent-closure run `33488954688`: SUCCESS.
- Unnecessary TCP/UDP port 111 was removed; closure persisted after physical reboot.
- Final canonical x64 run `33503085538`: 318 passed, 1 warning, SUCCESS.
- Final canonical native ARM64 run `33503085489`: native `aarch64`, 318 passed, 1 warning, SUCCESS.
- Runtime storage remained `PROJECT_LOCAL_ONLY`.
- Public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress remain explicit owner-approved candidate exceptions.
- E9A final state: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`.
- `PRODUCTION_LIVE` remained `NOT_OPERATIONAL`.
- E8 publication/sharing remains user-deferred until separate request.
- E9 Shared Production Runtime remains NOT_APPROVED.

## 2026-09-01 - Post-E9A canonical documentation synchronization

- E9A final validation result recorded in `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`.
- Canonical checkpoint recorded in `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_E9A_RUNTIME_HARDENING_CANDIDATE_READY.md`.
- ROADMAP advanced to v3.0 and old `E9A CURRENT / E9A.1` resume state was removed.
- README and PROJECT_HISTORY synchronized to the candidate-ready engineering state.
- No new roadmap phase/workstream was invented after E9A closure.

## Current State

- Documentation: RECONCILED through E9A closure
- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- E3 Private GPT Backend Action API: BASELINE_VALIDATED
- E4 Free Unattended Runtime Deployment: REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS
- E5 Admin Read-Only Dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED
- E6 Reproducibility Instrumentation: BASELINE_VALIDATED
- E7 Forecast Probability Semantics: BASELINE_VALIDATED
- E8 Controlled External Sharing / Public GPT: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- E9A Owner-Only Production Runtime Hardening: OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE
- E9 Shared Production Runtime: DEFERRED / NOT_APPROVED
- Shared Infrastructure ADR: APPROVED / HYBRID
- Runtime storage mode: `PROJECT_LOCAL_ONLY`
- Mixed/shared runtime storage: BLOCKED_PENDING_NEW_ARCHITECTURE_APPROVAL
- Controlled-pilot external integrations: 2
- External translation/graph/forecast/reporting/coverage/notification providers: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Owner-only unattended cloud runtime: `DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / OWNER_ONLY_PRODUCTION_CANDIDATE_READY / NOT_PRODUCTION`
- Backend Action API foundation: VALIDATED_LOCAL_READ_ONLY
- Private GPT backend Action connection: NOT_CONNECTED
- Backend HTTPS deployment: NOT_DEPLOYED
- Admin dashboard deployment: NOT_DEPLOYED
- Public GPT sharing: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- Current engineering activity: NONE_APPROVED_AFTER_E9A_CLOSURE
- Next numbered ROADMAP phase: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL