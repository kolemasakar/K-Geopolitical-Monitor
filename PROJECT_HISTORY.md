# PROJECT_HISTORY

Chronological record of major approved project milestones.

Version: 4.0
Status: ACTIVE

## 2026-08-24 — Project foundation

- Repository documentation foundation created.
- Product concept, roadmap and documentation governance approved.
- Engineering milestones M0-M4 established; M4 Knowledge Graph / Global Intelligence baseline completed.

## 2026-08-26 — M4 to M5 remediation and M5 readiness

- Repository/documentation alignment and reproducible CI baseline established.
- Shared Infrastructure Architecture Review selected HYBRID architecture.
- `PROJECT_LOCAL_ONLY` runtime storage became mandatory for the current implementation line.

## 2026-08-26 — M5 Operational Intelligence Platform

- Project-local watch/run persistence, monitoring orchestration, failure isolation, retry/recovery and ranked findings implemented.
- Run `32953343877`: 57 passed.
- M5 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M6 Controlled Pilot Monitoring

- Deterministic controlled-pilot adapters/provenance and coverage-gap handling implemented.
- Run `32961649091`: 62 passed.

## 2026-08-26 — M7 Live Public-Source Pilot

- Consilium RSS and GDELT DOC 2.0 controlled read-only integrations validated.
- GDELT constrained to discovery/index metadata.
- Run `32962379499`: 68 passed; live smoke `32962576874`: PASS.

## 2026-08-26 — M8 Live End-to-End Controlled Pilot

- Live acquisition connected to claim analysis/findings.
- Evidence independence changed to publisher/underlying-origin semantics; same-origin duplicates do not inflate verification.
- Run `32963096313`: 73 passed; live E2E `32963354135`: PASS.
- ROADMAP Phase 5 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M9 Strategic Alerts and Continuous Monitoring

- Durable alert policies/state/events, deduplication, lifecycle, persistence and priority/cadence separation implemented.
- Run `32965387054`: 82 passed.
- ROADMAP Phase 6 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M10 Multi-Region and Language Coverage

- Canonical region/language scope, attribution and coverage persistence implemented.
- Translation/region attribution remains isolated from verification truth.
- Run `32966128001`: 88 passed.
- ROADMAP Phase 7 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M11 Advanced Geopolitical Graph

- Durable project-local graph identity, lifecycle/history, temporal snapshots and bounded traversal implemented.
- Graph analytics do not mutate factual verification.
- Run `32973378757`: 118 passed.
- ROADMAP Phase 8 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M12 Advanced Forecasting

- Durable forecast/scenario versions, typed provenance, outcomes/evaluations and calibration history implemented.
- Graph input remains analytical context rather than independent evidence.
- Run `32980859938`: 154 passed.
- ROADMAP Phase 9 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — M13 Full Reporting Environment

- Immutable report snapshots/sections/references and common deterministic structured/Markdown rendering implemented.
- Presentation does not mutate upstream truth.
- Run `32993269910`: 199 passed.
- ROADMAP Phase 10 recorded as `BASELINE_VALIDATED`.

## 2026-08-26 — ROADMAP Phase 11 Global Operational Coverage

- Coverage contracts/results and per-source collection attempts implemented.
- `coverage_ratio` and `coverage_confidence` received distinct deterministic semantics.
- `GLOBAL` remains scope, not proof of complete global monitoring.
- Run `33000478908`: 226 passed.
- Phase 11 recorded as `BASELINE_VALIDATED`; no M14 was created.

## 2026-08-27 — Unattended runtime harness

- UnattendedMonitoringService and cadence-safe live operational cycle added.
- Failed runs remain persisted and do not retry on every supervisor poll.
- Run `33012596904`: 236 passed.

## 2026-08-27 — Owner-only private GPT pilot

- Private GPT owner-only pilot completed with no backend Action connected.
- Truth-boundary matrix: `18/18 PASS`.
- Public sharing remained deferred.

## 2026-08-29 — E1 Automatic Translation Foundation

- Migration 018 added versioned translations separate from immutable original raw text.
- Translation inherits origin and cannot create independent-source credit.
- Run `33244484173`: 241 passed.

## 2026-08-29 — E2 Source Reputation and Status History

- Migration 019 added append-only source reputation/status history.
- `COMPROMISED` remains context, not an automatic FALSE operator.
- Run `33244795277`: 248 passed.

## 2026-08-29 — E3 Private GPT Backend Action API

- Owner-only read-only persisted-state FastAPI facade implemented and validated.
- No-mutation and no-public-web-substitution behavior validated.
- Run `33247311921`: 254 passed.
- HTTPS remained not deployed; private GPT Action remained not connected.

## 2026-08-29 — E4 Free Unattended Runtime Deployment

- Real OCI Ubuntu 24.04 ARM64 owner-only runtime validated for immutable deployment, systemd startup, reboot recovery, interrupted-run recovery, due-watch resumption and controlled live collection.
- Run `33258520620`: SUCCESS.
- Public SSH TCP/22 from `0.0.0.0/0` and broad egress retained as explicit development exceptions.

## 2026-08-29 — E5 Admin Read-Only Dashboard

- Owner/admin read-only dashboard implemented over the E3 reader with no parallel database.
- x64 run `33263584520`: 282 passed; native ARM64 `33263584515`: SUCCESS.
- Dashboard remained not deployed.

## 2026-08-29 — E6 Reproducibility Instrumentation

- Migration 020 added persisted reproducibility audit projection, exact instrumented query/cut-off capture, adapter fingerprinting and artifact hashing.
- Missing history remains `NOT_INSTRUMENTED`, not reconstructed.
- x64 `33264133429`: 290 passed; native ARM64 `33264133407`: 290 passed.

## 2026-08-29 — E7 Forecast Probability Semantics

- Canonical `KGM_FORECAST_SEMANTICS_V1` separated raw probability, calibrated probability and scenario confidence across API/dashboard/report surfaces.
- Forecast values cannot promote factual verification.
- x64 `33265984585`: 294 passed; native ARM64 `33265984622`: 294 passed.

## 2026-08-29 — E7 closure / D0-E8 preflight line

- Post-E7 transition saved.
- D0 reconciled current documentation at that time and E8 read-only publication preflight was approved.
- E8 implementation/public sharing and E9 shared runtime remained unapproved.
- Later owner decisions superseded that trajectory; the historical decision remains retained as historical evidence.

## 2026-09-01 — E9A Owner-Only Production Runtime Hardening

- E9A executed as an unnumbered post-Phase-11 hardening workstream.
- E9A.1 single-instance runtime lease validated.
- E9A.2 canonical SQLite durability/concurrency profile validated.
- E9A.3 backup/restore and real clean-project-root DR drill validated.
- E9A.4 owner-only runtime-health instrumentation validated.
- E9A.5 systemd/runtime/security hardening validated.
- E9A.6 completed x64, native ARM64 and real OCI matrix.
- Real OCI state-preserving run `33486944907`: SUCCESS.
- rpcbind persistent-closure run `33488954688`: SUCCESS.
- TCP/UDP port 111 removed and remained absent after physical reboot.
- Final x64 run `33503085538`: `318 passed, 1 warning`, SUCCESS.
- Final native ARM64 run `33503085489`: native `aarch64`, `318 passed, 1 warning`, SUCCESS.
- Public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress remain explicit owner-approved candidate exceptions.
- Final E9A state: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — Post-E9A canonical synchronization

- E9A final validation recorded in `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`.
- Candidate checkpoint saved at `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_E9A_RUNTIME_HARDENING_CANDIDATE_READY.md`.
- Post-E9A canonical sync run `33504369245`: `318 passed, 1 warning`, SUCCESS.
- E8 publication/sharing remained user-deferred and E9 shared runtime remained not approved.

## 2026-09-01 — ROADMAP v4 approved / Phase 12 activated

- Repository-grounded system development analysis concluded engineering/runtime breadth is ahead of intelligence depth/source breadth.
- Owner approved strategic direction: `INTELLIGENCE QUALITY + SOURCE EXPANSION + OWNER OPERATIONAL VALUE`.
- ROADMAP advanced to v4.0.
- Approved sequential phases: Phase 12 through Phase 16.
- Phase 17 publication readiness remains conditional/not activated.
- Phase 18 shared/team runtime requires new architecture approval.
- No M14 was created.
- Phase 12 implementation plan added at `docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md`.
- Phase 12 ready checkpoint saved at `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_ROADMAP_V4_PHASE_12_READY.md`.
- Transition bootstrap added at `BOOTSTRAP_PACKAGE_2026-09-01_K-GEOPOLITICAL-MONITOR_ROADMAP_V4_PHASE_12_TRANSITION.md`.
- Exact resume gate set to `P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`.

## 2026-09-01 — P12.0 canonical convergence started

- Current-state audit confirmed secondary canonical drift after ROADMAP v4 transition.
- P12.0 scope includes architecture, security/data, integration/source, README/history and stale model-state claims.
- Historical ADR/decision records remain preserved rather than rewritten.
- No runtime/schema/production/public/shared-storage activation is part of P12.0.

## Current State

- Documentation: `P12.0_CANONICAL_CONVERGENCE_IN_PROGRESS`;
- ROADMAP: `APPROVED / v4.0`;
- engineering baseline: validated through ROADMAP Phase 11 plus E1-E7 and E9A;
- owner-only private GPT pilot: `18/18 PASS`;
- E8 external sharing/publication: `USER_DEFERRED`;
- E9A owner-only runtime hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9 Shared Production Runtime: `NOT_APPROVED`;
- Shared Infrastructure ADR: `APPROVED / HYBRID`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical storage: blocked pending new architecture approval;
- controlled-live starting integrations: Consilium RSS + GDELT DOC 2.0;
- additional Phase 12 sources: not activated by P12.0;
- private GPT backend Action connection: `NOT_CONNECTED`;
- backend HTTPS: `NOT_DEPLOYED`;
- admin dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public GPT sharing: user-deferred;
- current numbered ROADMAP phase: `Phase 12`;
- current engineering activity: `P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`;
- next gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- production/live: `NOT_OPERATIONAL`.
