# E9A Owner-Only Production Runtime Hardening Plan

Status: APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — unnumbered post-Phase-11 owner-only engineering
Decision: `docs/decisions/E9A_OWNER_ONLY_PRODUCTION_HARDENING_DECISION_2026-09-01.md`

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains `NOT_OPERATIONAL`.
E8 Business/publication remains user-deferred.
E9 Shared Production Runtime remains `NOT_APPROVED`.

## 1. Objective

Harden the existing validated OCI owner-only unattended runtime into an owner-only production candidate while preserving:
- one canonical K-Geopolitical Monitor project-local runtime database;
- `PROJECT_LOCAL_ONLY` storage;
- truth/provenance/coverage/forecast/report semantic isolation;
- fail-closed persisted-state behavior;
- no public API/dashboard/GPT exposure;
- no mixed/shared runtime storage.

Candidate-ready is an engineering state only. A separate explicit owner launch decision is required before `PRODUCTION_LIVE = OPERATIONAL` may be declared.

## 2. Existing Validated Foundation

Available foundation:
- E1 translation foundation: BASELINE_VALIDATED;
- E2 source reputation/status history: BASELINE_VALIDATED;
- E3 owner-only read-only backend API: BASELINE_VALIDATED / NOT_CONNECTED;
- E4 OCI Ubuntu 24.04 ARM64 unattended runtime: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION;
- E5 admin dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED;
- E6 reproducibility instrumentation: BASELINE_VALIDATED;
- E7 forecast probability semantics: BASELINE_VALIDATED;
- owner-only GPT publication candidate v1.3: VALIDATED / publication deferred by owner.

E4 already proved:
- real ARM64 host operation;
- systemd restart and physical reboot recovery;
- interrupted-run recovery;
- due-watch resumption;
- controlled live source collection;
- project-local SQLite integrity;
- no public HTTP/HTTPS/database/API ingress in the monitoring service.

## 3. Focused Delta Audit

### 3.1 Storage boundary — strong existing foundation

`RuntimeStoragePolicy` enforces the runtime database under `<project_root>/data` and rejects paths outside the project-local data directory.

Decision: preserve this invariant. E9A must not weaken it to enable shared or mixed storage.

### 3.2 Duplicate supervisor / single-writer gap

The unattended service required an explicit process-wide lease preventing two `kgm-monitor` processes or a manual `--once` invocation from running against the same canonical runtime simultaneously.

Resolved by E9A.1 with an OS advisory project-local runtime lease and fail-closed second-instance behavior.

### 3.3 SQLite durability/concurrency profile gap

Resolved by E9A.2 with one canonical runtime connection profile:
- `foreign_keys = ON`;
- `busy_timeout = 5000 ms`;
- `journal_mode = DELETE`;
- `synchronous = FULL`;
- explicit deferred transaction behavior.

### 3.4 Disaster-recovery gap

E9A.3 established the software/policy backup and restore baseline. Real clean-host/project-local restore timing and RPO/RTO evaluation remain intentionally deferred to E9A.6.

### 3.5 Runtime health/observability gap

Resolved at the implementation/regression layer by E9A.4 owner-only persisted runtime-health instrumentation. Runtime-health labels remain tick-local facts and cannot imply global coverage, source health, uptime or production readiness.

### 3.6 Final security hardening

E9A.5 completed the repository/configuration/policy hardening baseline with x64/native ARM64 regression validation. Real-host/network exception disposition remains part of E9A.6.

Current development exceptions remain explicit:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad egress.

These are not production acceptance.

## 4. Implementation Gates

### E9A.1 — Single-Instance Runtime Lease

State: `BASELINE_VALIDATED`.

Implemented a project-local process lease for unattended execution modes, including `--once`, with atomic/non-blocking acquisition and fail-closed duplicate execution.

### E9A.2 — SQLite Runtime Profile

State: `BASELINE_VALIDATED`.

Canonical profile:
- `foreign_keys = ON`;
- `busy_timeout = 5000 ms`;
- `journal_mode = DELETE`;
- `synchronous = FULL`;
- explicit deferred transaction behavior.

### E9A.3 — Backup and Disaster Recovery

State: `BASELINE_VALIDATED_WITH_REAL_HOST_DR_PENDING`.

Implemented software/policy baseline:
- canonical SQLite online backup;
- bundle `KGM_RUNTIME_BACKUP_V1`;
- SHA-256/size/integrity/migration-state validation;
- tamper detection;
- fail-closed project-local restore;
- no external/off-host provider activation.

Pending E9A.6:
- real clean-host/project-local restore drill;
- measured RPO target `<= 24h` evaluation;
- measured RTO target `<= 2h` evaluation.

### E9A.4 — Owner-Only Runtime Health Instrumentation

State: `IMPLEMENTATION_REGRESSION_VALIDATED`.

Implemented persisted direct runtime-health facts without inferring unavailable process uptime, global coverage or source-health state.

### E9A.5 — Deployment and Security Hardening Review

State: `BASELINE_REGRESSION_VALIDATED_WITH_REAL_HOST_NETWORK_EVIDENCE_PENDING_E9A_6`.

Result:
`docs/implementation/E9A_5_DEPLOYMENT_SECURITY_HARDENING_RESULT.md`

Completed repository/configuration/policy baseline:
- hardened systemd least privilege;
- exact writable runtime path retained at `/opt/k-geopolitical-monitor/data`;
- no service capabilities;
- no monitoring API/dashboard/database listener;
- canonical `.gitignore` for common secret/runtime material;
- security regression contract;
- explicit repository/log secret policy;
- SSH/Bastion/private-admin review;
- outbound runtime/maintenance requirement review;
- rollback/kill procedure;
- monitoring failure isolation;
- `START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY` with Start.me non-canonical and not a runtime dependency.

Validated:
- x64 CI run `33486068223`: `317 passed, 1 warning`, SUCCESS;
- native ARM64 run `33485986978`: `317 passed, 1 warning`, SUCCESS;
- ARM64 one-tick smoke: PASS;
- bootstrap shell validation: PASS;
- systemd unit verification: PASS.

Pending E9A.6:
- effective hardened unit on the real OCI host;
- refreshed OCI ingress evidence;
- public SSH exception disposition;
- outbound egress exception disposition;
- host/journal secret-exposure review;
- practical kill/rollback evidence where safe.

### E9A.6 — Validation Matrix

Required before `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`:
- full x64 regression: PASS;
- full native ARM64 regression: PASS;
- real OCI immutable deployment validation: PASS;
- second-instance lease rejection: PASS;
- normal service restart: PASS;
- physical reboot recovery: PASS;
- interrupted-run recovery: PASS;
- SQLite integrity after reboot/crash tests: PASS;
- backup integrity: PASS;
- clean-host/project-local restore drill: PASS;
- controlled live multi-cycle execution: PASS;
- source failure remains visible: PASS;
- no public-web substitution for backend state: PASS;
- E3/E5 read-only non-mutation regression: PASS;
- provenance/verification/coverage/forecast/report isolation: PASS;
- no shared/mixed runtime storage: PASS;
- no new public ingress: PASS;
- E9A.5 real-host/network/security-exception evidence: PASS or explicitly blocking candidate-ready.

A longer soak test may be executed by GitHub Actions/host automation when designed, but absence of synchronous assistant execution must never be misrepresented as completed evidence.

## 5. Explicit Non-Claims

E9A does not approve or establish:
- ChatGPT Business migration;
- GPT Store/public sharing;
- public or external Action;
- public dashboard;
- public backend API;
- shared runtime database;
- mixed cross-project canonical storage;
- E9 Shared Production Runtime;
- production/live OPERATIONAL status;
- complete global real-time coverage;
- any new external provider.

## 6. Execution Order

1. E9A.1 single-instance runtime lease — validated.
2. E9A.2 SQLite runtime durability/concurrency profile — validated.
3. E9A.3 backup/disaster recovery software baseline — validated; real-host DR pending E9A.6.
4. E9A.4 runtime health instrumentation — regression validated.
5. E9A.5 deployment/security hardening review — regression validated; real-host/network evidence pending E9A.6.
6. E9A.6 x64/ARM64/real-host validation and candidate gate — CURRENT.

Implementation remains additive and minimal. Each sub-gate must preserve existing E1-E7 and Phase 0-11 semantics.

## 7. Current Gate

`E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING = IN_PROGRESS`

Validated/recorded sub-gates:
- `E9A.1_SINGLE_INSTANCE_RUNTIME_LEASE = BASELINE_VALIDATED` — x64/ARM64 `299 passed`;
- `E9A.2_SQLITE_RUNTIME_PROFILE = BASELINE_VALIDATED` — x64/ARM64 `303 passed`;
- `E9A.3_BACKUP_AND_DISASTER_RECOVERY = BASELINE_VALIDATED_WITH_REAL_HOST_DR_PENDING` — x64/ARM64 `308 passed`; clean-host real-host restore timing remains pending for E9A.6;
- `E9A.4_OWNER_ONLY_RUNTIME_HEALTH = IMPLEMENTATION_REGRESSION_VALIDATED` — x64/ARM64 `313 passed, 1 warning`;
- `E9A.5_DEPLOYMENT_SECURITY_HARDENING = BASELINE_REGRESSION_VALIDATED_WITH_REAL_HOST_NETWORK_EVIDENCE_PENDING_E9A_6` — x64/ARM64 `317 passed, 1 warning`.

Current engineering sub-gate:
`E9A.6_VALIDATION_MATRIX`

Candidate-ready, if ultimately earned, remains an engineering classification only. It does not activate Business migration, publication, shared runtime, public ingress or production/live operation.

Production/live:
`NOT_OPERATIONAL`
