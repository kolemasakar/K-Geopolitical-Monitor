# P18.7 — Shared Runtime Backup, Disaster Recovery and Rollback Result

Status: `VALIDATED / P18_8_READY`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Gate: `P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED`
Implementation anchor: `cdd23c945cccdc27a43fa14d18ebeb6309b991f1`
Parent contract: `docs/implementation/P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_CONTRACT.md`
Artifact hardening: `docs/implementation/P18_7_SHARED_RUNTIME_RECOVERY_ARTIFACT_HARDENING.md`

## Implementation Line

P18.7 was assembled in two compatible implementation steps:

- PR #28 established the provider-neutral backup manifest, restore request/drill,
  recovery-plan and owner-local rollback contracts;
- PR #30 added artifact-level integrity, deterministic decoded tenant snapshots,
  actual provider-free clean-target record reconciliation, deterministic logical
  recovery-point selection and failure-based RPO/RTO measurement.

A superseded exploratory PR #29 was closed unmerged after PR #28 reached
canonical `main` first. Its useful stronger controls were ported additively via
PR #30 rather than replacing or duplicating the canonical P18.7 API.

## Exact Validation Evidence

Final P18.7 implementation anchor:

`cdd23c945cccdc27a43fa14d18ebeb6309b991f1`

Validation evidence:

- PR #30 CI run `34159435003`, job `101857964148`: `1034 passed in 112.58s / SUCCESS`; dependency check PASS;
- exact-main x64 run `34159594021`, job `101858434798`: exact checkout `cdd23c945cccdc27a43fa14d18ebeb6309b991f1`, `1034 passed in 116.27s / SUCCESS`; dependency check PASS;
- exact-main native ARM64 run `34159594044`, job `101858434830`: exact checkout `cdd23c945cccdc27a43fa14d18ebeb6309b991f1`, native `aarch64`, `1034 passed in 112.01s / SUCCESS`; dependency check, bootstrap shell, unattended one-tick and systemd unit contract PASS;
- unattended smoke evidence: `execution_count: 0`, `recovered_runs: 0`.

The earlier exact-main validation of the PR #28 base implementation also passed
`1000` tests on x64 and native ARM64 before the additive hardening was merged.
The final gate evidence above intentionally uses the later `cdd23c...` exact
main anchor containing both implementation layers.

## Validated Recovery Contract

The final P18.7 provider-neutral contract validates all of the following:

- backup manifests are tenant-scoped and capture schema version, schema contract,
  UTC capture time, checkpoint identity, deterministic content SHA-256,
  row-count metadata and an external P18.6 `SecretReference` for encryption-key
  material;
- the protected artifact layer requires an explicitly encrypted payload scheme,
  opaque ciphertext bytes and an independent ciphertext SHA-256 integrity check;
- ciphertext is private material and is omitted from representation/public
  metadata; the encryption key/secret locator is also omitted from
  public/non-sensitive artifact metadata;
- decoded recovery snapshots contain immutable canonical JSON rows for exactly
  one `workspace_id + project_id`, reject duplicate object identities and
  mixed-tenant rows, and derive deterministic content SHA-256 plus row counts;
- artifact-to-snapshot verification binds exact tenant, schema version,
  checkpoint identity, content SHA-256 and row counts before restore;
- clean-environment restore uses actual decoded tenant-scoped records, refuses
  overwrite of a non-clean target, requires exact tenant and compatible schema,
  and retains restored content identity for reconciliation;
- recovery-point selection deterministically chooses the latest durable logical
  checkpoint at or before a requested time and rejects mixed-tenant point sets;
- measured RPO is derived from observed failure time minus the latest durable
  recovery point;
- measured RTO is derived from observed failure time through restore completion,
  so pre-restore delay is not silently excluded;
- measured recovery values are evidence only and cannot authorize a service-level
  claim by themselves;
- owner-local rollback evidence requires a failed shared candidate to be
  discardable while the independently operable owner-local project SQLite
  baseline remains unchanged;
- recovery, backup and rollback evidence remains truth-neutral and cannot
  promote factual verification.

## Acceptance Results

### Clean-environment restore

PASS at the provider-neutral contract-harness level.

The harness restores deterministic tenant-scoped record snapshots into a clean
in-memory target, reconciles exact snapshot content identity, rejects dirty
restore targets and fails closed on tenant/schema mismatch.

This is **not** evidence that a deployed shared datastore has been restored.

### Tenant-safe restore

PASS.

Cross-workspace, cross-project, mixed-tenant snapshot and mixed-tenant
recovery-point cases fail closed.

### Failed shared-candidate rollback

PASS at the provider-neutral contract level.

Rollback evidence requires the shared candidate to be discarded without
changing the owner-local canonical SQLite baseline identity. P18.7 does not
mutate or replace that owner-local runtime line.

### RPO/RTO measurement

PASS for measured contract-harness semantics.

RPO/RTO are derived from explicit observed drill timestamps and are never
inherited from planning assumptions. The hardening layer makes full RTO
failure-based (`failure -> restore completed`) rather than equating only restore
command duration with RTO.

The measured harness values do not establish a production SLA/SLO.

## Infrastructure Evidence Boundary

P18.7 deliberately distinguishes a **required contract** from observed external
infrastructure.

The canonical backup manifest requires encrypted and off-host backup semantics,
but:

- `encrypted=True` is a required manifest contract, not proof that a selected
  production cryptographic implementation exists;
- `off_host_copy=True` is a required recovery contract, not observed proof that
  an off-host provider copy was created;
- the additive artifact contract records
  `cryptographic_adapter_observed = False`;
- it records `off_host_storage_observed = False`;
- it records `provider_pitr_observed = False`;
- no real shared datastore exists for an observed provider restore drill.

A concrete cryptographic adapter, real off-host durability, real provider
PITR/WAL or equivalent, and real shared-datastore restore/reachability evidence
belong to P18.8/P18.9 after an actual non-production shared candidate exists.
P18.7 therefore does not overstate planned configuration as observed
infrastructure state.

## Preserved Boundaries

P18.7 did not:

- deploy shared storage or a backup provider;
- select or purchase a provider;
- allocate, create or pre-authorize migration `033`;
- expose shared/public ingress or deploy backend HTTPS;
- switch canonical storage;
- authorize canonical cutover;
- activate shared runtime;
- change production/live status;
- alter P13.5/P13.6 factual-verification authority.

Canonical boundaries remain:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite remains canonical and independently operable;
- mixed/shared canonical runtime: `BLOCKED`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- backend HTTPS/shared ingress: `NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`;
- canonical factual verification authority: P13.5/P13.6.

## Closure State

P18.7 is formally synchronized as `VALIDATED`, with P18.8 advanced only to
`READY_TO_BEGIN`. This closure records the validated provider-neutral recovery
contract and exact implementation evidence; it does not claim deployed recovery
infrastructure, provider approval, shared-runtime activation, canonical cutover
or production/live operation.
