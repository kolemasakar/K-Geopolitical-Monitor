# P18.7 — Recovery Artifact Hardening Supplement

Status: `IMPLEMENTATION_CANDIDATE`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Parent contract: `docs/implementation/P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_CONTRACT.md`
Target gate: `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`

## Why this supplement exists

The canonical P18.7 implementation establishes provider-neutral backup-manifest,
restore-request, restore-drill and owner-local rollback contracts. This additive
hardening closes four gaps before formal validation:

- a manifest declaring `encrypted=True` is not by itself integrity evidence for
  the protected bytes;
- a restore request validating metadata is not by itself proof that actual
  tenant-scoped records reconcile in a clean target;
- an equivalent-checkpoint requirement needs deterministic point-selection
  semantics;
- restore execution duration is useful drill evidence, but full measured RTO
  must be bounded from observed failure time to restored completion, not only
  from restore-command start.

The supplement is additive and does not replace the already merged P18.7 API.

## Artifact envelope

`EncryptedBackupArtifact` wraps the canonical `SharedBackupManifest` and adds:

- opaque ciphertext bytes hidden from `repr`;
- declared encrypted-payload scheme;
- ciphertext SHA-256 stored independently and verified on construction;
- explicit evidence flags showing that provider encryption, off-host storage
  and provider PITR have **not** yet been observed.

The envelope does not implement a cryptographic primitive. A future
`EncryptedBackupCodec` adapter must do that. Synthetic reversible codecs used in
tests are orchestration fixtures only and are not cryptographic evidence.

## Deterministic decoded snapshot

`TenantRecoverySnapshot` contains immutable canonical JSON record snapshots for
one exact `workspace_id + project_id`, one schema version and one checkpoint.
It:

- rejects mixed-tenant rows;
- rejects duplicate object identities;
- canonicalizes record order and payload JSON;
- computes deterministic content SHA-256;
- derives deterministic per-object-type row counts.

`verify_artifact_snapshot_binding` requires tenant, schema, checkpoint, content
SHA-256 and row counts to reconcile with the canonical `SharedBackupManifest`.

## Clean restore with records

`InMemoryCleanRestoreTarget` validates provider-free restore semantics using the
actual decoded record snapshots:

- target must start empty;
- workspace/project must match exactly;
- schema must match;
- the target refuses overwrite after one restore;
- restored content SHA-256 is retained for reconciliation.

This is contract-harness evidence, not observed restoration of a deployed
shared datastore.

## Logical recovery-point selection

`LogicalRecoveryPoint` and `select_logical_recovery_point` require one exact
tenant and choose the latest durable point at or before the requested time,
using sequence only as a deterministic tie-breaker.

This is the provider-neutral equivalent-checkpoint contract. It does not claim
provider WAL/PITR support.

## Recovery objective measurement clarification

The canonical restore drill already measures backup/checkpoint staleness and
restore execution duration. The hardening layer adds
`MeasuredRecoveryObjectiveEvidence` for full failure-based evidence:

- measured RPO = failure time - last durable recovery point;
- measured RTO = restore completion time - observed failure time.

The timestamps must satisfy:

`last durable <= failure <= restore start <= restore completion`.

These values remain measured test evidence only:

- `service_level_claim_authorized = False`;
- `provider_pitr_observed = False`;
- `factual_verification_authority = False`.

## Off-host evidence interpretation

The parent manifest's `off_host_copy=True` is interpreted as a **required
contract declaration**, not observed provider/storage evidence. The additive
artifact explicitly records:

`off_host_storage_observed = False`

until P18.8/P18.9 can test a real non-production candidate.

## Public/non-sensitive metadata

`public_artifact_metadata` excludes:

- ciphertext bytes;
- the P18.6 encryption-key `SecretReference` and locator;
- any secret value.

It distinguishes the off-host requirement from observed off-host evidence and
keeps activation/cutover/truth authority false.

## Negative validation matrix

| Risk | Fail-closed evidence |
| --- | --- |
| ciphertext corruption | independent ciphertext SHA-256 mismatch rejected |
| manifest/snapshot substitution | tenant/schema/checkpoint/content/row-count binding rejected |
| cross-tenant decoded rows | snapshot construction and restore both reject |
| dirty target overwrite | second/non-clean restore rejected |
| ambiguous logical point | no eligible point fails; mixed tenants fail |
| understated RTO | failure-based timeline includes pre-restore delay |
| ciphertext/key locator leak | public metadata projection excludes both |
| infrastructure overclaim | observed-provider/off-host/PITR flags remain false |

## Preserved boundaries

This hardening does not change:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite canonical status;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- backend/shared ingress: `NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`;
- factual verification authority: P13.5/P13.6.
