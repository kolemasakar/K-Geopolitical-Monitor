# E9A Owner-Only Production Runtime Hardening Plan

Status: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — unnumbered post-Phase-11 owner-only engineering
Decision: `docs/decisions/E9A_OWNER_ONLY_PRODUCTION_HARDENING_DECISION_2026-09-01.md`
Final validation: `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`

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

Objective result:
`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`.

Candidate-ready is an engineering state only. A separate explicit owner launch decision is required before `PRODUCTION_LIVE = OPERATIONAL` may be declared.

## 2. Validated Foundation

Validated foundation:
- E1 translation foundation: BASELINE_VALIDATED;
- E2 source reputation/status history: BASELINE_VALIDATED;
- E3 owner-only read-only backend API: BASELINE_VALIDATED / NOT_CONNECTED;
- E4 OCI Ubuntu 24.04 ARM64 unattended runtime: REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS;
- E5 admin dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED;
- E6 reproducibility instrumentation: BASELINE_VALIDATED;
- E7 forecast probability semantics: BASELINE_VALIDATED;
- owner-only GPT publication candidate v1.3: VALIDATED / publication deferred by owner.

E4/E9A real-host validation proved:
- real ARM64 host operation;
- systemd restart and physical reboot recovery;
- interrupted-run recovery;
- due-watch resumption;
- controlled live source collection;
- project-local SQLite integrity;
- no public HTTP/HTTPS/database/API listener in the monitoring service;
- project-local backup/restore recovery;
- hardened service boundary;
- persistent removal of unnecessary rpcbind port 111.

## 3. Focused Delta Audit Closure

### 3.1 Storage boundary

`RuntimeStoragePolicy` enforces the runtime database under `<project_root>/data` and rejects paths outside the project-local data directory.

Result: preserved. E9A did not introduce shared or mixed canonical runtime storage.

### 3.2 Duplicate supervisor / single-writer gap

Resolved by E9A.1 with an OS advisory project-local runtime lease and fail-closed second-instance behavior.

### 3.3 SQLite durability/concurrency profile gap

Resolved by E9A.2 with one canonical runtime connection profile:
- `foreign_keys = ON`;
- `busy_timeout = 5000 ms`;
- `journal_mode = DELETE`;
- `synchronous = FULL`;
- explicit deferred transaction behavior.

### 3.4 Disaster-recovery gap

E9A.3 established the software/policy backup and restore baseline.

E9A.6 then completed the real clean-project-root restore drill and measured the engineering objectives:
- restored table count: `51`;
- restored/source table counts identical;
- restored DB integrity: PASS;
- restored one-tick execution: PASS;
- recovery elapsed: `1 second`;
- recovery-point age at evaluation: `0.000 seconds`;
- RTO objective `<= 2h`: PASS for this drill;
- RPO objective `<= 24h`: PASS for this drill.

These are validation-drill results, not operational SLA commitments.

### 3.5 Runtime health/observability gap

Resolved at the implementation/regression layer by E9A.4 owner-only persisted runtime-health instrumentation. Runtime-health labels remain tick-local facts and cannot imply global coverage, source health, uptime or production readiness.

### 3.6 Final security hardening

E9A.5 completed the repository/configuration/policy hardening baseline. E9A.6 completed the required real-host validation and disposition.

Validated real-host security evidence includes:
- effective hardened systemd properties and exact writable path;
- root-owned code/unit and `kgm:kgm` runtime identity;
- second-instance fail-closed behavior;
- emergency stop/disable/re-enable recovery;
- physical reboot recovery;
- journal secret-pattern review with zero detected hits;
- no monitoring HTTP/HTTPS/database/API listener;
- unnecessary `rpcbind` disabled/masked after fail-closed NFS dependency checks;
- TCP/UDP port 111 remained absent after physical reboot.

Explicit owner-approved candidate exceptions remain:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

These remain security exceptions. They are not least-privilege production-network acceptance and do not authorize public KGM application ingress.

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

State: `BASELINE_VALIDATED_WITH_REAL_HOST_DR_VALIDATED`.

Implemented and validated:
- canonical SQLite online backup;
- bundle `KGM_RUNTIME_BACKUP_V1`;
- SHA-256/size/integrity/migration-state validation;
- tamper detection;
- fail-closed project-local restore;
- real clean-project-root restore drill;
- engineering RPO/RTO objective evaluation;
- no external/off-host provider activation.

### E9A.4 — Owner-Only Runtime Health Instrumentation

State: `IMPLEMENTATION_REGRESSION_VALIDATED`.

Implemented persisted direct runtime-health facts without inferring unavailable process uptime, global coverage or source-health state.

### E9A.5 — Deployment and Security Hardening Review

State: `BASELINE_VALIDATED_WITH_REAL_HOST_EVIDENCE_AND_OWNER_EXCEPTIONS`.

Result:
`docs/implementation/E9A_5_DEPLOYMENT_SECURITY_HARDENING_RESULT.md`

Repository/configuration/policy baseline plus E9A.6 real-host evidence now cover:
- hardened systemd least privilege;
- exact writable runtime path `/opt/k-geopolitical-monitor/data`;
- no service capabilities;
- no monitoring API/dashboard/database listener;
- canonical secret/runtime ignore policy;
- SSH/egress exception documentation;
- rollback/kill procedure;
- monitoring failure isolation;
- real-host journal review;
- real-host reboot/recovery;
- rpcbind/port 111 removal and reboot persistence.

### E9A.6 — Validation Matrix

State: `VALIDATED`.

Result:
`docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`

Final regression anchors:
- x64 CI run `33502510214`, job `99838870836`: `318 passed, 1 warning`, SUCCESS;
- native ARM64 run `33502510195`, job `99838870759`: native `aarch64`, `318 passed, 1 warning`, SUCCESS;
- ARM64 bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit verification: PASS.

Real-host anchors:
- E9A.6 state-preserving OCI validation run `33486944907`, job `99789127086`: SUCCESS;
- rpcbind persistent-closure run `33488954688`, job `99795604234`: SUCCESS.

The reversible ARM64 trigger was fully removed. Canonical restored commit `611e6071a2d0f9e9f84392ddd27edaf8c38d0b38` and hardening commit `fa514214b9510af6ecb2a35887ec16f15f73adf0` share Git tree SHA `0bdfde547e756dcbf9ac3c9c84347c84be41574e`.

A longer soak test may be executed later when separately designed, but no unexecuted soak is represented as completed evidence.

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
- any new external provider;
- operational RPO/RTO SLA guarantees.

## 6. Execution Order

1. E9A.1 single-instance runtime lease — validated.
2. E9A.2 SQLite runtime durability/concurrency profile — validated.
3. E9A.3 backup/disaster recovery — validated including real-host DR drill in E9A.6.
4. E9A.4 runtime health instrumentation — regression validated.
5. E9A.5 deployment/security hardening — validated with real-host evidence and explicit owner exceptions.
6. E9A.6 x64/ARM64/real-host validation and candidate gate — validated.

E9A engineering execution is complete.

## 7. Current Gate

`E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING = OWNER_ONLY_PRODUCTION_CANDIDATE_READY`

Validated/recorded sub-gates:
- `E9A.1_SINGLE_INSTANCE_RUNTIME_LEASE = BASELINE_VALIDATED`;
- `E9A.2_SQLITE_RUNTIME_PROFILE = BASELINE_VALIDATED`;
- `E9A.3_BACKUP_AND_DISASTER_RECOVERY = BASELINE_VALIDATED_WITH_REAL_HOST_DR_VALIDATED`;
- `E9A.4_OWNER_ONLY_RUNTIME_HEALTH = IMPLEMENTATION_REGRESSION_VALIDATED`;
- `E9A.5_DEPLOYMENT_SECURITY_HARDENING = BASELINE_VALIDATED_WITH_REAL_HOST_EVIDENCE_AND_OWNER_EXCEPTIONS`;
- `E9A.6_VALIDATION_MATRIX = VALIDATED`.

`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`

Candidate-ready remains an engineering classification only. It does not activate Business migration, publication, shared runtime, public ingress or production/live operation.

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`E9_SHARED_PRODUCTION_RUNTIME = NOT_APPROVED`

`BUSINESS_MIGRATION = HOLD_UNTIL_SEPARATE_OWNER_REQUEST`

`GPT_PUBLICATION_OR_PUBLIC_SHARING = HOLD_UNTIL_SEPARATE_OWNER_REQUEST`
