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

The current unattended service is restart-safe, but there is no explicit process-wide lease preventing two `kgm-monitor` processes or a manual `--once` invocation from running against the same canonical runtime simultaneously.

Risk:
- duplicate due-cycle execution;
- avoidable write contention;
- ambiguous runtime ownership.

Required gate: E9A.1 single-instance lease.

### 3.3 SQLite durability/concurrency profile gap

Current database initialization explicitly enables foreign keys, but ordinary runtime connections do not use one centralized production connection profile and do not explicitly define durability/concurrency settings such as busy timeout, journal mode and synchronous mode.

Risk:
- inconsistent connection behavior;
- avoidable `database is locked` failures;
- unclear durability assumptions.

Required gate: E9A.2 explicit SQLite runtime profile with measured validation before adopting WAL or other settings.

### 3.4 Disaster-recovery gap

E4 validates project-local SQLite online backup/restore and integrity checks, but there is no complete off-host disaster-recovery contract, retention policy, restore drill to a clean replacement host, or approved RPO/RTO target.

Required gate: E9A.3 backup/DR contract and restore validation. No new backup provider may be activated without separate approval.

### 3.5 Runtime health/observability gap

Systemd process state is validated, but the canonical runtime does not yet expose a dedicated persisted/local heartbeat contract for last supervisor tick, last successful operational cycle, current degradation and instrumentation freshness without inference.

Required gate: E9A.4 owner-only runtime health instrumentation.

### 3.6 Final security hardening remains deferred

Current owner-approved development exceptions remain:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad egress.

These are acceptable for active development but not automatically accepted as final production hardening.

Required gate: E9A.5 final-security review before any launch decision.

## 4. Implementation Gates

### E9A.1 — Single-Instance Runtime Lease

Implement a project-local process lease for all unattended execution modes, including `--once`.

Requirements:
- lease path remains inside KGM project-local runtime data;
- acquisition is atomic and non-blocking;
- a second process fails closed with a clear error;
- OS process exit/crash releases the active lock without requiring unsafe stale-lock deletion;
- PID/instance metadata may be diagnostic only and must not be treated as authoritative if the OS lock is not held;
- no change to watch/run truth semantics;
- x64 and ARM64 tests.

Preferred Linux implementation: OS advisory file lock (`flock`) over a project-local lock file. Cross-platform development fallback may be added only if it preserves equivalent fail-closed behavior.

### E9A.2 — SQLite Runtime Profile

Create one explicit connection policy/helper and migrate runtime write/read connections incrementally to it.

Required baseline:
- `foreign_keys = ON`;
- deterministic `busy_timeout`;
- explicit transaction behavior;
- explicit durability profile documented and testable.

Journal/synchronous decision:
- do not blindly force WAL;
- measure and validate current filesystem/backup/systemd behavior;
- if WAL is selected, validate checkpoint, backup, restore, crash/reboot integrity and read-only API/dashboard compatibility;
- preserve query-only mode for E3/E5 readers.

Required tests:
- concurrent read while writer active;
- bounded write contention/fail behavior;
- crash/reopen integrity;
- backup consistency;
- migration compatibility;
- no truth-state mutation from read-only surfaces.

### E9A.3 — Backup and Disaster Recovery

Define an owner-only DR contract.

Requirements:
- canonical SQLite online backup remains the source mechanism;
- every backup passes `PRAGMA integrity_check`;
- backups never overwrite silently;
- restore never overwrites a live canonical DB silently;
- restore target remains project-local;
- backup metadata includes source commit/schema state and capture timestamp where available;
- documented retention and encryption requirements;
- off-host copy architecture may be designed, but provider activation requires separate owner approval;
- clean-host restore drill required before candidate-ready gate.

Initial target objectives to validate rather than assume:
- RPO target: <= 24 hours;
- RTO target: <= 2 hours for owner-admin restoration.

These targets are planning objectives until measured in a restore drill.

### E9A.4 — Owner-Only Runtime Health Instrumentation

Add a local/persisted health contract without inventing unavailable metrics.

Minimum fields:
- last supervisor tick timestamp;
- last completed cycle timestamp where instrumented;
- last successful collection/cycle timestamp where traceably available;
- current service/runtime degradation summary from persisted state;
- lease/instance state as locally observable;
- instrumentation version.

Rules:
- do not infer process uptime from unrelated timestamps;
- missing instrumentation remains explicit;
- health metadata cannot strengthen verification, coverage or forecast confidence;
- no public endpoint is required.

### E9A.5 — Deployment and Security Hardening Review

Before candidate-ready:
- verify systemd least privilege and writable paths;
- verify no database port exposure;
- verify no public API/dashboard listener;
- verify secrets absent from repository/log responses;
- review SSH exposure and Bastion/private-admin alternatives;
- review outbound network requirements for OS maintenance and approved source adapters before any egress restriction;
- define rollback/kill procedure;
- preserve monitoring failure isolation.

The current SSH/egress exception may remain during implementation; candidate-ready classification must explicitly state any unresolved exception.

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
- no new public ingress: PASS.

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

1. E9A.1 single-instance runtime lease.
2. E9A.2 SQLite runtime durability/concurrency profile.
3. E9A.3 backup/disaster recovery.
4. E9A.4 runtime health instrumentation.
5. E9A.5 deployment/security hardening review.
6. E9A.6 x64/ARM64/real-host validation and candidate gate.

Implementation should remain additive and minimal. Each sub-gate must preserve existing E1-E7 and Phase 0-11 semantics.

## 7. Current Gate

`E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING = IN_PROGRESS`

Validated/recorded sub-gates:
- `E9A.1_SINGLE_INSTANCE_RUNTIME_LEASE = BASELINE_VALIDATED` — x64/ARM64 `299 passed`;
- `E9A.2_SQLITE_RUNTIME_PROFILE = BASELINE_VALIDATED` — x64/ARM64 `303 passed`;
- `E9A.3_BACKUP_AND_DISASTER_RECOVERY = BASELINE_VALIDATED_WITH_REAL_HOST_DR_PENDING` — x64/ARM64 `308 passed`; clean-host real-host restore timing remains pending for E9A.6;
- `E9A.4_OWNER_ONLY_RUNTIME_HEALTH = IMPLEMENTATION_REGRESSION_VALIDATED` — repair commit `6db189a2ad672e4bc8099be378e2e2a0044de1ed`; x64 CI run `33482602853` and ARM64 run `33482602833`, both `313 passed, 1 warning`.

Current engineering sub-gate:
`E9A.5_DEPLOYMENT_SECURITY_HARDENING`

Pending final gate:
`E9A.6_VALIDATION_MATRIX`

Candidate-ready, if ultimately earned, remains an engineering classification only. It does not activate Business migration, publication, shared runtime, public ingress or production/live operation.

Production/live:
`NOT_OPERATIONAL`
