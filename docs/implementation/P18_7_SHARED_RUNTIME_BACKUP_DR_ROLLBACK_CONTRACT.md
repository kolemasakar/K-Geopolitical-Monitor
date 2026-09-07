# P18.7 — Shared Runtime Backup, Disaster Recovery and Rollback Contract

Status: `IMPLEMENTATION_CANDIDATE`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Gate: `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`

## Purpose

P18.7 defines the provider-neutral recovery boundary required before any future
shared/team runtime candidate can progress to non-production shadow/canary work.
It proves deterministic backup-envelope, tenant-safe restore, recovery-point,
measured RPO/RTO and owner-local rollback semantics without deploying or
activating shared infrastructure.

The active canonical runtime remains the independently operable owner-only
project-local SQLite profile.

## Non-Goals / Hard Boundary

P18.7 does **not**:

- deploy a shared datastore or backup service;
- select, purchase or activate a provider;
- implement or claim a production cryptographic primitive;
- claim observed off-host backup durability;
- claim observed provider WAL/PITR support;
- expose shared/public ingress or backend HTTPS;
- allocate, create or pre-authorize migration `033`;
- mutate or replace the owner-local canonical SQLite store;
- authorize canonical cutover;
- activate shared runtime;
- authorize production/live operation.

A concrete future provider adapter must supply the real cryptographic and
storage implementation. P18.7 treats its protected payload as opaque ciphertext
plus integrity metadata and an external `SecretReference`. Test-only synthetic
codecs may exercise orchestration semantics, but they are explicitly not
cryptographic or provider evidence.

## Recovery Policy

The P18.7 recovery policy is fail-closed and requires all of the following:

- encrypted backup payload contract;
- encryption key material referenced externally through P18.6
  `SecretReference` semantics;
- deterministic artifact and snapshot SHA-256 integrity evidence;
- one explicit `workspace_id` + `project_id` per snapshot/recovery point;
- clean-environment restore only, never overwrite-in-place;
- exact tenant match on every restored record;
- explicit logical schema version and repository migration-version capture;
- deterministic logical recovery-point selection at/before a requested time;
- measured RPO/RTO derived from observed drill timestamps;
- failed shared candidate discard with unchanged owner-local baseline.

The policy remains provider-neutral:

- `provider_id = None`;
- `contract_only = True`;
- `off_host_backup_observed = False`;
- `provider_pitr_observed = False`;
- `cryptographic_adapter_observed = False`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`.

## Backup Envelope

`EncryptedBackupArtifact` carries:

- backup identity;
- exact tenant context;
- UTC creation time;
- logical shared-schema version;
- repository migration-version snapshot;
- recovery sequence;
- plaintext snapshot SHA-256 identity;
- declared encrypted-payload scheme;
- external secret/key reference;
- opaque ciphertext bytes;
- ciphertext SHA-256.

It rejects:

- absent tenant context;
- invalid timestamps or versions;
- plaintext/none/identity/unencrypted scheme declarations;
- inline/non-P18.6 secret references;
- empty ciphertext;
- ciphertext/checksum mismatch.

The artifact does not expose ciphertext through `repr`. The public metadata
projection excludes ciphertext and the key/secret locator entirely.

## Deterministic Tenant Snapshot

`TenantRecoverySnapshot`:

- is bound to one `TenantContext`;
- captures schema and repository migration versions;
- captures a monotonic logical recovery sequence;
- rejects mixed-tenant records;
- rejects duplicate object identities;
- canonicalizes and sorts records deterministically;
- computes a deterministic SHA-256 content identity.

This is recovery/provenance state only. It has no factual-verification
promotion authority.

## Clean Restore Contract

`InMemoryCleanRestoreTarget` is a provider-free validation harness. Restore:

- requires an empty target;
- requires exact workspace/project scope;
- requires compatible logical schema version;
- requires compatible repository migration version;
- checks every record tenant scope;
- refuses overwrite after a successful restore;
- preserves the restored snapshot content SHA-256 for reconciliation.

`restore_encrypted_backup` requires a future `EncryptedBackupCodec` adapter,
decodes an artifact, re-validates tenant/version/sequence/snapshot identity,
and only then applies it to a clean restore target.

## Point-in-Time / Equivalent Semantics

`RecoveryPoint` and `select_recovery_point` validate the logical requirement that
a restore target can deterministically select the latest durable recovery point
at or before a requested UTC time, with exact tenant isolation.

This does **not** claim a real provider WAL/PITR mechanism. Actual provider PITR
or an equivalent mechanism must be observed and revalidated in P18.8/P18.9 if
the selected infrastructure supports it.

## Measured RPO/RTO

`RecoveryDrillTimeline` derives measurements from four observed UTC timestamps:

- last durable recovery point;
- failure time;
- restore start;
- restore completion.

The timestamps must be monotonic.

- measured RPO = failure time - last durable recovery point;
- measured RTO = restore completion - failure time.

P18.7 does not inherit planned numbers and does not authorize a production SLA
from these contract-harness measurements.

## Owner-Local Rollback Invariance

The existing `runtime_backup.py` owner-local SQLite implementation remains
separate and unchanged. P18.7 adds no shared-storage behavior to it.

`OwnerLocalBaseline` records only the owner-local store identity and SHA-256.
`validate_owner_local_rollback` passes only when:

- the failed shared candidate is explicitly discarded;
- owner-local store identity is unchanged;
- owner-local database SHA-256 is unchanged;
- canonical storage remains `PROJECT_LOCAL_SQLITE`.

The result always keeps:

- `canonical_cutover_authorized = False`;
- `shared_runtime_activated = False`.

## Threat / Failure Matrix

| Threat / failure | Preventive / detective control | Validation mapping |
| --- | --- | --- |
| backup plaintext or inline key material | opaque encrypted-artifact contract + external `SecretReference` | `test_encrypted_artifact_requires_external_reference_and_hides_ciphertext` |
| corrupted backup bytes | ciphertext SHA-256 and decoded snapshot SHA-256 verification | `test_corrupted_ciphertext_is_rejected`, `test_decoded_snapshot_hash_mismatch_is_rejected` |
| cross-workspace/project restore | exact `TenantContext` on snapshot, point and target | `test_cross_tenant_restore_is_rejected`, `test_recovery_point_set_cannot_mix_tenants` |
| mixed-tenant rows inside backup | snapshot construction fails closed | `test_snapshot_rejects_mixed_tenant_records` |
| accidental overwrite of existing target | clean-target-only restore | `test_restore_refuses_non_clean_target` |
| incompatible schema/migration restore | explicit version capture and exact target checks | `test_restore_rejects_schema_or_migration_mismatch` |
| ambiguous recovery point | deterministic latest durable point at/before target | `test_recovery_point_selection_is_deterministic` |
| assumed RPO/RTO represented as fact | measured timestamp-derived evidence only | `test_recovery_drill_measures_rpo_rto`, `test_incomplete_recovery_evidence_fails_closed` |
| failed shared candidate corrupts local canonical state | before/after local SHA/store identity invariance | `test_owner_local_rollback_requires_unchanged_baseline` |
| secret/ciphertext leak to public metadata | data-minimized metadata projection | `test_public_backup_metadata_excludes_private_material` |
| recovery state promotes factual truth | explicit truth-neutral evidence | `test_recovery_evidence_is_truth_neutral` |

## Acceptance Interpretation

P18.7 implementation validation may establish that the **provider-neutral
recovery contract** can:

- restore a synthetic contract snapshot into a clean environment;
- fail closed on cross-tenant restore attempts;
- reconcile exact restored content identity;
- select a logical recovery point deterministically;
- measure RPO/RTO from observed test-drill timestamps;
- discard a failed shared candidate while preserving an unchanged owner-local
  canonical baseline.

It may not represent those results as observed provider encryption, off-host
backup durability, provider PITR, real shared-datastore recovery or production
service levels. Those require later infrastructure evidence.

## Preserved Project Boundaries

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite remains canonical;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- shared/backend HTTPS ingress: not deployed by P18.7;
- production/live: `NOT_OPERATIONAL`;
- canonical factual verification authority: P13.5/P13.6.
