# E9A Backup and Disaster Recovery Runbook

Status: OWNER_ONLY_IMPLEMENTATION_BASELINE
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A.3

## 1. Scope

This runbook defines the owner-only backup and restore contract for the K-Geopolitical Monitor canonical project-local SQLite runtime.

It does not activate an off-host storage provider and does not change the canonical storage mode from `PROJECT_LOCAL_ONLY`.

## 2. Canonical State

Canonical runtime database:
`<project_root>/data/kgeopolitical_monitor.db`

Backups are recovery artifacts only. They are not an alternate canonical store and must never become a shared/mixed runtime database.

## 3. Backup Bundle Contract

Format:
`KGM_RUNTIME_BACKUP_V1`

Each bundle contains:
- `runtime.db` — SQLite online backup;
- `manifest.json` — non-secret integrity and schema metadata.

Manifest includes:
- UTC capture timestamp;
- database SHA-256;
- database size;
- SQLite integrity result;
- applied schema migration snapshot and latest migration;
- `PROJECT_LOCAL_ONLY` canonical-storage declaration;
- source commit only when supplied by authoritative deployment instrumentation; otherwise `NOT_INSTRUMENTED`.

The runtime must not infer a deployment commit from conversational memory, file names or an unverified working tree.

## 4. Backup Rules

- Use SQLite online backup; never raw-copy a live database as the canonical backup procedure.
- Every generated backup must pass `PRAGMA integrity_check`.
- Never silently overwrite an existing backup bundle or backup database.
- Backup creation must not mutate canonical monitoring truth.
- Backup destination may be outside the canonical data directory, but it remains a recovery artifact rather than runtime truth.
- Any external/off-host copy must preserve the manifest and database together.

## 5. Restore Rules

Before restore:
- verify bundle format;
- verify expected database filename;
- verify file size against manifest;
- verify SHA-256 against manifest;
- verify SQLite integrity;
- verify schema migration snapshot against manifest.

Restore target:
- a fresh KGM project root;
- canonical target is always `<target_project_root>/data/kgeopolitical_monitor.db`;
- never overwrite an existing canonical runtime database.

After restore:
- run `PRAGMA integrity_check`;
- open the restored project through normal KGM runtime initialization;
- verify representative persisted state;
- run the relevant regression/smoke validation before operational use.

## 6. Retention Policy

Until an off-host provider is separately approved, retention is owner-managed and local/offline.

Minimum candidate policy:
- create at least one validated recovery bundle per 24-hour period when the runtime is considered production candidate/live;
- retain at least 7 daily restore points and at least 4 weekly restore points;
- do not implement automatic destructive pruning until retention automation has its own fail-closed tests;
- low-disk conditions must be surfaced rather than silently deleting the last known-good recovery point.

This policy is a target contract. It is not evidence that scheduled backups are currently running.

## 7. Encryption / Off-Host Policy

For any backup copied off the KGM host:
- encryption at rest is required;
- transport encryption is required;
- access must remain owner-controlled/least privilege;
- secrets/keys must not be committed to Git;
- recovery must be tested with the encrypted artifact path before relying on it.

No S3, OCI Object Storage, Google Drive or other external backup provider is selected or activated by E9A.3. Provider activation requires separate owner approval.

## 8. RPO / RTO Planning Objectives

Planning objectives:
- RPO: <= 24 hours;
- RTO: <= 2 hours for owner-admin restoration.

These are not validated service levels until measured by a clean-host restore drill.

## 9. Clean-Host Restore Drill

Required before `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`:
1. capture a validated versioned backup bundle from the deployed project;
2. transfer/copy it to a clean replacement project root or validation host;
3. verify bundle integrity before restore;
4. restore into the fresh canonical project-local database path;
5. verify SQLite integrity;
6. verify schema migration snapshot;
7. verify representative watch/run/finding/alert/coverage/forecast/report state as applicable;
8. run one controlled unattended tick without public ingress;
9. record actual elapsed recovery time and calculate observed recovery-point age;
10. only then assess the RPO/RTO objectives.

The assistant must not mark this drill PASS unless actual host evidence is captured.

## 10. Current Gate

- backup bundle implementation: IN_VALIDATION;
- off-host provider: NONE_APPROVED;
- automatic backup schedule: NOT_CLAIMED;
- clean-host restore drill: REQUIRED LATER IN E9A.6;
- production/live: NOT_OPERATIONAL.
