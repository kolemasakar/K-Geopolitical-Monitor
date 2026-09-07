# P18.7 — Shared Runtime Backup, Disaster Recovery and Rollback Contract

Status: `IMPLEMENTATION_IN_PROGRESS / VALIDATION_REQUIRED`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Target gate: `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`

## 1. Purpose

P18.7 defines provider-neutral recovery invariants for a future shared-runtime
candidate while preserving the independently operable owner-only project-local
SQLite runtime.

P18.7 is a contract/test-harness phase. It does **not** provision backup storage,
select a provider, create encryption keys, deploy a shared datastore, allocate
migration `033`, activate shared runtime, or perform canonical cutover.

Actual provider/storage/network recovery evidence must be repeated against the
P18.8 non-production candidate and reviewed again in P18.9 before activation
readiness can be claimed.

## 2. Preserved Boundaries

P18.7 MUST preserve:

- active canonical storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite remains independently operable;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- provider selection/spend: `NONE_APPROVED`;
- public/shared ingress: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- no canonical cutover;
- canonical factual verification authority remains P13.5/P13.6.

Recovery evidence is operational safety evidence only and MUST NOT become factual
verification authority.

## 3. Existing Owner-Local Recovery Line

The existing `runtime_backup.py` remains the owner-local SQLite recovery path.
P18.7 does not modify or replace it.

The local recovery implementation already provides:

- SQLite online backup;
- SQLite integrity verification;
- SHA-256 integrity evidence;
- schema migration snapshot in the manifest;
- restore into a fresh target only;
- refusal to overwrite an existing canonical runtime database;
- explicit `PROJECT_LOCAL_ONLY` storage policy metadata.

This independent path is the rollback anchor if a future shared candidate is
rejected or fails validation.

## 4. Shared Recovery Plan Contract

A future shared-runtime candidate MUST provide:

- encrypted backups;
- an off-host backup copy;
- clean-environment restore drills;
- exact workspace/project tenant binding;
- PITR where supported, or an equivalent recoverable-checkpoint mechanism;
- schema/version provenance;
- integrity verification;
- measured restore evidence;
- a rollback path that leaves owner-local canonical state unchanged.

The P18.7 contract records `provider_id = None`, migration number `NOT_ALLOCATED`,
`shared_runtime_active = false`, and `canonical_cutover_authorized = false`.

## 5. Backup Manifest and Secret Handling

`SharedBackupManifest` is a non-secret integrity/provenance envelope. It carries:

- backup identifier;
- exact `TenantContext` (`workspace_id + project_id`);
- schema version and schema contract identifier;
- timezone-aware capture timestamp;
- recoverable checkpoint identifier;
- content SHA-256;
- row-count reconciliation evidence;
- encryption/off-host requirements;
- an opaque P18.6 `SecretReference` for encryption-key resolution.

The manifest MUST NOT contain an encryption key or other secret value.
`SecretReference` remains only a locator for a future authorized secret resolver.
The reference is excluded from ordinary dataclass representation to reduce
accidental logging exposure.

P18.7 does not create, rotate, fetch or store any real encryption key.

## 6. Restore Isolation and Fail-Closed Validation

A restore request MUST fail closed unless all of the following match the verified
backup manifest:

- requested workspace/project tenant;
- recoverable checkpoint identifier;
- content SHA-256;
- schema version.

The restore target MUST be a clean environment. Restoring into an existing target
is outside the P18.7 contract.

Cross-workspace and cross-project restore requests are forbidden even when object
identifiers or other backup metadata would otherwise match.

## 7. Clean-Environment Restore Drill

A valid restore drill MUST demonstrate:

- exact tenant restored;
- successful post-restore reconciliation;
- zero observed cross-tenant rows;
- valid recovery and execution timestamps;
- integrity/schema/checkpoint checks already passed before restore evidence is
  accepted.

A drill with failed reconciliation or tenant contamination is invalid and cannot
support the P18.7 gate.

## 8. PITR / Equivalent Recoverable Checkpoint

P18.7 does not claim a specific provider-level PITR feature because no provider or
shared datastore exists yet.

The provider-neutral contract requires either:

- PITR capability; or
- an equivalent explicit recoverable-checkpoint mechanism.

The current contract harness uses the equivalent-checkpoint path. When P18.8
selects or instantiates an actual non-production candidate, concrete PITR or
checkpoint behavior must be measured and reconciled against this contract.

## 9. RPO and RTO Evidence

RPO/RTO values may be recorded only from observed restore-drill timestamps:

- observed RPO = recovery target time minus recoverable backup/checkpoint capture
  time;
- observed RTO = restore completion time minus restore start time.

P18.7 does not turn measured values into an SLA, guarantee, or production target.
No RPO/RTO claim is valid without corresponding observed evidence.

Provider-level durable RPO/RTO claims require later real-candidate validation.

## 10. Rollback to Owner-Local Canonical Runtime

A failed shared candidate must be discardable.

Rollback evidence MUST demonstrate:

- shared candidate is discarded;
- owner-local storage scope remains `PROJECT_LOCAL_SQLITE`;
- owner-local canonical database SHA-256 is identical before and after shared
  candidate rollback validation;
- shared runtime remains inactive;
- no canonical cutover occurred.

Any mutation of the owner-local canonical database during shared-candidate
rollback invalidates the P18.7 rollback evidence.

## 11. Recovery Threat Model

| Recovery threat | P18.7 control/evidence |
| --- | --- |
| plaintext shared backup | encrypted-backup contract rejects `encrypted=false` |
| backup stored only with runtime | off-host-copy requirement |
| backup key leaked in metadata/logs | opaque P18.6 `SecretReference`, no value in manifest/repr |
| wrong-tenant restore | exact workspace/project match, negative tests |
| restore into live/dirty target | clean-target requirement |
| corrupted/tampered backup | SHA-256 match required |
| wrong schema restore | schema version match required |
| wrong recovery point | checkpoint identifier match required |
| cross-tenant contamination after restore | restore drill rejects observed cross-tenant rows |
| incomplete/semantically inconsistent restore | reconciliation must pass |
| unmeasured RPO/RTO claim | values derived only from observed timestamps; `sla_claimed=false` |
| failed shared candidate mutates owner-local canonical DB | before/after owner-local digest must remain identical |
| recovery evidence promoted to factual truth | explicit `factual_verification_authority=false` |
| hidden provider/migration/cutover activation | provider unset, migration unallocated, activation/cutover false |

## 12. Validation Requirements

P18.7 MUST NOT be declared `VALIDATED` until evidence exists for:

- targeted P18.7 test pass;
- full repository regression on the implementation head;
- dependency check;
- exact implementation/main validation under the existing x64/native-ARM64
  validation policy where supported;
- owner-local bootstrap/unattended/systemd compatibility where required by the
  Phase 18 validation policy;
- clean-environment recovery contract evidence;
- cross-tenant restore denial;
- unchanged owner-local rollback evidence;
- measured RPO/RTO evidence from the deterministic drill harness;
- formal ROADMAP/state closure only after the preceding evidence is green.

Until formal closure:

`P18_7 = IMPLEMENTATION_IN_PROGRESS / VALIDATION_REQUIRED`

and shared runtime remains inactive.

## 13. Later-Phase Revalidation

P18.8 must validate the actual non-production candidate for:

- real backup encryption/storage controls;
- real off-host durability;
- concrete PITR/checkpoint capability;
- real clean restore and tenant isolation;
- provider/cost implications, if external infrastructure becomes necessary.

P18.9 must re-review recovery, security, rollback and activation-readiness evidence
end to end.

Even successful P18.9 readiness validation does not itself activate the shared
runtime; activation remains a separate explicit owner decision with fresh
launch-time validation.
