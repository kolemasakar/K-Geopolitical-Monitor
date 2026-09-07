import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

import pytest

from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext
from kgeopolitical_monitor.shared_runtime_recovery import (
    BackupContractError,
    BackupIntegrityError,
    EncryptedBackupArtifact,
    InMemoryCleanRestoreTarget,
    OwnerLocalBaseline,
    OwnerLocalRollbackError,
    RecoveryDrillEvidence,
    RecoveryDrillTimeline,
    RecoveryObjectiveEvidenceError,
    RecoveryPoint,
    RecoveryPointError,
    RecoveryRecord,
    RestoreIsolationError,
    RestoreTargetNotCleanError,
    SharedRuntimeRecoveryPolicy,
    TenantRecoverySnapshot,
    public_backup_metadata,
    restore_encrypted_backup,
    select_recovery_point,
    validate_owner_local_rollback,
    verify_decoded_snapshot,
)
from kgeopolitical_monitor.shared_runtime_security import SecretExposureError, SecretReference


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "implementation"
    / "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_CONTRACT.md"
)


def now() -> datetime:
    return datetime(2026, 9, 7, 20, 0, tzinfo=timezone.utc)


def tenant(workspace: str = "workspace-a", project: str = "project-1") -> TenantContext:
    return TenantContext(workspace_id=workspace, project_id=project)


def record(
    object_type: str = "event",
    object_id: str = "event-1",
    *,
    tenant_context: TenantContext | None = None,
    payload: dict | None = None,
) -> RecoveryRecord:
    return RecoveryRecord.from_payload(
        tenant_context=tenant_context or tenant(),
        object_type=object_type,
        object_id=object_id,
        payload=payload or {"summary": "safe", "rank": 1},
    )


def snapshot(
    *,
    tenant_context: TenantContext | None = None,
    captured_at: datetime | None = None,
    logical_schema_version: int = 1,
    repository_migration_version: int = 32,
    recovery_sequence: int = 7,
    records: tuple[RecoveryRecord, ...] | None = None,
) -> TenantRecoverySnapshot:
    scope = tenant_context or tenant()
    rows = records or (
        record("claim", "claim-1", tenant_context=scope, payload={"text": "claim"}),
        record("event", "event-1", tenant_context=scope, payload={"summary": "event"}),
    )
    return TenantRecoverySnapshot(
        tenant_context=scope,
        captured_at=captured_at or now(),
        logical_schema_version=logical_schema_version,
        repository_migration_version=repository_migration_version,
        recovery_sequence=recovery_sequence,
        records=rows,
    )


def key_ref() -> SecretReference:
    return SecretReference(source="env", name="KGM_TEST_BACKUP_KEY_REFERENCE")


def artifact_for(
    item: TenantRecoverySnapshot,
    *,
    ciphertext: bytes | None = None,
    encryption_scheme: str = "TEST_ONLY_SYNTHETIC_CODEC",
) -> EncryptedBackupArtifact:
    protected = ciphertext or (b"TEST_ONLY_OPAQUE:" + item.content_sha256.encode("ascii"))
    return EncryptedBackupArtifact(
        backup_id=f"backup-{item.recovery_sequence}",
        tenant_context=item.tenant_context,
        created_at=item.captured_at,
        logical_schema_version=item.logical_schema_version,
        repository_migration_version=item.repository_migration_version,
        recovery_sequence=item.recovery_sequence,
        snapshot_sha256=item.content_sha256,
        encryption_scheme=encryption_scheme,
        key_reference=key_ref(),
        ciphertext=protected,
        ciphertext_sha256=sha256(protected).hexdigest(),
    )


class SyntheticTestOnlyCodec:
    """Reversible in-memory test fixture; explicitly not cryptographic evidence."""

    codec_id = "synthetic-test-only"

    def __init__(self):
        self._snapshots: dict[str, TenantRecoverySnapshot] = {}

    def seal(
        self,
        item: TenantRecoverySnapshot,
        *,
        key_reference: SecretReference,
    ) -> EncryptedBackupArtifact:
        protected = b"TEST_ONLY_OPAQUE:" + item.content_sha256.encode("ascii")
        artifact = EncryptedBackupArtifact(
            backup_id=f"test-{item.tenant_context.workspace_id}-{item.recovery_sequence}",
            tenant_context=item.tenant_context,
            created_at=item.captured_at,
            logical_schema_version=item.logical_schema_version,
            repository_migration_version=item.repository_migration_version,
            recovery_sequence=item.recovery_sequence,
            snapshot_sha256=item.content_sha256,
            encryption_scheme="TEST_ONLY_SYNTHETIC_CODEC",
            key_reference=key_reference,
            ciphertext=protected,
            ciphertext_sha256=sha256(protected).hexdigest(),
        )
        self._snapshots[artifact.backup_id] = item
        return artifact

    def open(self, artifact: EncryptedBackupArtifact) -> TenantRecoverySnapshot:
        return self._snapshots[artifact.backup_id]


def test_recovery_policy_is_provider_neutral_contract_only():
    policy = SharedRuntimeRecoveryPolicy()
    assert policy.provider_id is None
    assert policy.contract_only is True
    assert policy.off_host_backup_observed is False
    assert policy.provider_pitr_observed is False
    assert policy.cryptographic_adapter_observed is False
    assert policy.shared_runtime_activated is False
    assert policy.canonical_cutover_authorized is False


@pytest.mark.parametrize(
    "field",
    [
        "backup_encryption_required",
        "external_key_reference_required",
        "clean_restore_required",
        "exact_tenant_restore_required",
        "measured_recovery_objectives_required",
        "owner_local_rollback_required",
    ],
)
def test_recovery_policy_safeguards_cannot_be_disabled(field):
    with pytest.raises(BackupContractError):
        SharedRuntimeRecoveryPolicy(**{field: False})


def test_recovery_record_payload_is_canonical_and_snapshot_not_mutated_by_source_mapping():
    payload = {"z": 2, "a": {"value": 1}}
    item = RecoveryRecord.from_payload(
        tenant_context=tenant(),
        object_type="event",
        object_id="event-1",
        payload=payload,
    )
    payload["a"]["value"] = 999
    assert item.payload_json == '{"a":{"value":1},"z":2}'


def test_recovery_record_is_frozen():
    item = record()
    with pytest.raises(FrozenInstanceError):
        item.object_id = "changed"


def test_snapshot_is_deterministic_across_record_order():
    a = record("event", "event-1", payload={"b": 2, "a": 1})
    b = record("claim", "claim-1", payload={"text": "x"})
    first = snapshot(records=(a, b))
    second = snapshot(records=(b, a))
    assert first.records == second.records
    assert first.content_sha256 == second.content_sha256


def test_snapshot_rejects_mixed_tenant_records():
    with pytest.raises(RestoreIsolationError):
        snapshot(
            records=(
                record(tenant_context=tenant("workspace-a", "project-1")),
                record("claim", "claim-2", tenant_context=tenant("workspace-b", "project-1")),
            )
        )


def test_snapshot_rejects_duplicate_object_identity():
    with pytest.raises(BackupContractError):
        snapshot(records=(record(), record(payload={"summary": "different"})))


def test_snapshot_requires_timezone_aware_capture_time():
    with pytest.raises(BackupContractError):
        snapshot(captured_at=datetime(2026, 9, 7, 20, 0))


def test_encrypted_artifact_requires_external_reference_and_hides_ciphertext():
    item = snapshot()
    artifact = artifact_for(item)
    assert artifact.key_reference.locator == "env://KGM_TEST_BACKUP_KEY_REFERENCE"
    assert artifact.provider_id is None
    assert artifact.contract_only is True
    assert "TEST_ONLY_OPAQUE" not in repr(artifact)
    assert "ciphertext=b" not in repr(artifact)
    with pytest.raises(SecretExposureError):
        SecretReference(source="inline", name="actual-secret")


@pytest.mark.parametrize("scheme", ["none", "plaintext", "identity", "unencrypted", "   "])
def test_encrypted_artifact_rejects_unprotected_scheme_declarations(scheme):
    with pytest.raises(BackupContractError):
        artifact_for(snapshot(), encryption_scheme=scheme)


def test_corrupted_ciphertext_is_rejected():
    artifact = artifact_for(snapshot())
    with pytest.raises(BackupIntegrityError):
        replace(artifact, ciphertext=artifact.ciphertext + b"corruption")


def test_artifact_rejects_empty_ciphertext():
    item = snapshot()
    with pytest.raises(BackupContractError):
        EncryptedBackupArtifact(
            backup_id="backup-empty",
            tenant_context=item.tenant_context,
            created_at=item.captured_at,
            logical_schema_version=1,
            repository_migration_version=32,
            recovery_sequence=7,
            snapshot_sha256=item.content_sha256,
            encryption_scheme="AES_GCM_ADAPTER_DECLARATION",
            key_reference=key_ref(),
            ciphertext=b"",
            ciphertext_sha256=sha256(b"").hexdigest(),
        )


def test_public_backup_metadata_excludes_private_material():
    artifact = artifact_for(snapshot())
    metadata = public_backup_metadata(artifact)
    encoded = json.dumps(metadata, sort_keys=True)
    assert "ciphertext" in metadata["ciphertext_sha256"].__class__.__name__.casefold() or isinstance(metadata["ciphertext_sha256"], str)
    assert "key_reference" not in metadata
    assert "secret" not in encoded.casefold()
    assert key_ref().locator not in encoded
    assert "TEST_ONLY_OPAQUE" not in encoded
    assert metadata["canonical_cutover_authorized"] is False
    assert metadata["shared_runtime_activated"] is False
    assert metadata["factual_verification_authority"] is False


def test_decoded_snapshot_exact_identity_is_accepted():
    item = snapshot()
    assert verify_decoded_snapshot(artifact=artifact_for(item), snapshot=item) is item


def test_decoded_snapshot_hash_mismatch_is_rejected():
    item = snapshot()
    artifact = artifact_for(item)
    changed = snapshot(
        recovery_sequence=item.recovery_sequence,
        records=(record(payload={"summary": "changed"}),),
    )
    with pytest.raises(BackupIntegrityError):
        verify_decoded_snapshot(artifact=artifact, snapshot=changed)


def test_decoded_snapshot_cross_tenant_is_rejected():
    item = snapshot()
    artifact = artifact_for(item)
    other = snapshot(tenant_context=tenant("workspace-b", "project-1"))
    with pytest.raises(RestoreIsolationError):
        verify_decoded_snapshot(artifact=artifact, snapshot=other)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"logical_schema_version": 2},
        {"repository_migration_version": 31},
        {"recovery_sequence": 8},
    ],
)
def test_decoded_snapshot_version_or_sequence_mismatch_is_rejected(kwargs):
    item = snapshot()
    artifact = artifact_for(item)
    changed = snapshot(**kwargs)
    with pytest.raises(BackupIntegrityError):
        verify_decoded_snapshot(artifact=artifact, snapshot=changed)


def test_clean_environment_restore_succeeds_and_reconciles_snapshot_hash():
    item = snapshot()
    target = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        logical_schema_version=1,
        repository_migration_version=32,
    )
    restored = target.restore(item)
    assert restored == item.records
    assert target.restored_snapshot_sha256 == item.content_sha256
    assert target.is_clean is False


def test_restore_refuses_non_clean_target():
    item = snapshot()
    target = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        logical_schema_version=1,
        repository_migration_version=32,
    )
    target.restore(item)
    with pytest.raises(RestoreTargetNotCleanError):
        target.restore(item)


def test_cross_tenant_restore_is_rejected():
    item = snapshot()
    for other in (
        tenant("workspace-b", "project-1"),
        tenant("workspace-a", "project-2"),
    ):
        target = InMemoryCleanRestoreTarget(
            tenant_context=other,
            logical_schema_version=1,
            repository_migration_version=32,
        )
        with pytest.raises(RestoreIsolationError):
            target.restore(item)


def test_restore_rejects_schema_or_migration_mismatch():
    item = snapshot()
    wrong_schema = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        logical_schema_version=2,
        repository_migration_version=32,
    )
    with pytest.raises(BackupIntegrityError):
        wrong_schema.restore(item)

    wrong_migration = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        logical_schema_version=1,
        repository_migration_version=31,
    )
    with pytest.raises(BackupIntegrityError):
        wrong_migration.restore(item)


def test_encrypted_backup_orchestration_restores_only_after_decode_verification():
    item = snapshot()
    codec = SyntheticTestOnlyCodec()
    artifact = codec.seal(item, key_reference=key_ref())
    target = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        logical_schema_version=1,
        repository_migration_version=32,
    )
    restored = restore_encrypted_backup(artifact=artifact, codec=codec, target=target)
    assert restored == item.records
    assert target.restored_snapshot_sha256 == item.content_sha256


def test_recovery_point_selection_is_deterministic():
    scope = tenant()
    p1_snapshot = snapshot(captured_at=now() - timedelta(minutes=20), recovery_sequence=1)
    p2_snapshot = snapshot(captured_at=now() - timedelta(minutes=10), recovery_sequence=2)
    p3_snapshot = snapshot(captured_at=now(), recovery_sequence=3)
    points = (
        RecoveryPoint(scope, p3_snapshot.captured_at, 3, p3_snapshot),
        RecoveryPoint(scope, p1_snapshot.captured_at, 1, p1_snapshot),
        RecoveryPoint(scope, p2_snapshot.captured_at, 2, p2_snapshot),
    )
    selected = select_recovery_point(
        tenant_context=scope,
        points=points,
        target_at=now() - timedelta(minutes=5),
    )
    assert selected.sequence == 2
    assert selected.snapshot.content_sha256 == p2_snapshot.content_sha256


def test_recovery_point_set_cannot_mix_tenants():
    a_snapshot = snapshot(recovery_sequence=1)
    b_scope = tenant("workspace-b", "project-1")
    b_snapshot = snapshot(tenant_context=b_scope, recovery_sequence=2)
    with pytest.raises(RestoreIsolationError):
        select_recovery_point(
            tenant_context=tenant(),
            points=(
                RecoveryPoint(tenant(), a_snapshot.captured_at, 1, a_snapshot),
                RecoveryPoint(b_scope, b_snapshot.captured_at, 2, b_snapshot),
            ),
            target_at=now(),
        )


def test_recovery_point_selection_fails_without_durable_point_before_target():
    item = snapshot(recovery_sequence=1)
    point = RecoveryPoint(item.tenant_context, item.captured_at, 1, item)
    with pytest.raises(RecoveryPointError):
        select_recovery_point(
            tenant_context=item.tenant_context,
            points=(point,),
            target_at=item.captured_at - timedelta(seconds=1),
        )


def test_recovery_drill_measures_rpo_rto():
    failure = now()
    timeline = RecoveryDrillTimeline(
        last_durable_recovery_point_at=failure - timedelta(seconds=45),
        failure_at=failure,
        restore_started_at=failure + timedelta(seconds=15),
        restore_completed_at=failure + timedelta(seconds=120),
    )
    assert timeline.measured_rpo_seconds == 45.0
    assert timeline.measured_rto_seconds == 120.0


def test_recovery_drill_rejects_non_monotonic_or_naive_timestamps():
    with pytest.raises(RecoveryObjectiveEvidenceError):
        RecoveryDrillTimeline(
            last_durable_recovery_point_at=now(),
            failure_at=now() - timedelta(seconds=1),
            restore_started_at=now(),
            restore_completed_at=now(),
        )
    with pytest.raises(RecoveryObjectiveEvidenceError):
        RecoveryDrillTimeline(
            last_durable_recovery_point_at=datetime(2026, 9, 7, 19, 0),
            failure_at=now(),
            restore_started_at=now(),
            restore_completed_at=now(),
        )


def test_recovery_evidence_is_truth_neutral_and_no_sla_is_authorized():
    failure = now()
    evidence = RecoveryDrillEvidence(
        tenant_context=tenant(),
        clean_environment_restore_succeeded=True,
        tenant_isolation_validated=True,
        content_reconciled=True,
        timeline=RecoveryDrillTimeline(
            last_durable_recovery_point_at=failure - timedelta(seconds=30),
            failure_at=failure,
            restore_started_at=failure + timedelta(seconds=10),
            restore_completed_at=failure + timedelta(seconds=90),
        ),
    )
    assert evidence.measured_rpo_seconds == 30.0
    assert evidence.measured_rto_seconds == 90.0
    assert evidence.provider_pitr_observed is False
    assert evidence.service_level_claim_authorized is False
    assert evidence.factual_verification_authority is False


def test_incomplete_recovery_evidence_fails_closed():
    timeline = RecoveryDrillTimeline(
        last_durable_recovery_point_at=now(),
        failure_at=now(),
        restore_started_at=now(),
        restore_completed_at=now(),
    )
    with pytest.raises(RecoveryObjectiveEvidenceError):
        RecoveryDrillEvidence(
            tenant_context=tenant(),
            clean_environment_restore_succeeded=True,
            tenant_isolation_validated=False,
            content_reconciled=True,
            timeline=timeline,
        )
    with pytest.raises(RecoveryObjectiveEvidenceError):
        RecoveryDrillEvidence(
            tenant_context=tenant(),
            clean_environment_restore_succeeded=True,
            tenant_isolation_validated=True,
            content_reconciled=True,
            timeline=timeline,
            service_level_claim_authorized=True,
        )


def baseline(store_id: str = "owner-local-runtime-db", digest: str | None = None) -> OwnerLocalBaseline:
    return OwnerLocalBaseline(
        store_id=store_id,
        database_sha256=digest or ("a" * 64),
    )


def test_owner_local_rollback_requires_unchanged_baseline():
    before = baseline()
    after = baseline()
    evidence = validate_owner_local_rollback(
        before=before,
        after=after,
        shared_candidate_discarded=True,
    )
    assert evidence.owner_local_unchanged is True
    assert evidence.shared_candidate_discarded is True
    assert evidence.canonical_cutover_authorized is False
    assert evidence.shared_runtime_activated is False


def test_owner_local_rollback_rejects_changed_hash_or_store_identity():
    before = baseline()
    with pytest.raises(OwnerLocalRollbackError):
        validate_owner_local_rollback(
            before=before,
            after=baseline(digest="b" * 64),
            shared_candidate_discarded=True,
        )
    with pytest.raises(OwnerLocalRollbackError):
        validate_owner_local_rollback(
            before=before,
            after=baseline(store_id="different-owner-store"),
            shared_candidate_discarded=True,
        )


def test_owner_local_rollback_requires_shared_candidate_discard():
    with pytest.raises(OwnerLocalRollbackError):
        validate_owner_local_rollback(
            before=baseline(),
            after=baseline(),
            shared_candidate_discarded=False,
        )


def test_owner_local_baseline_cannot_be_reclassified_as_shared_storage():
    with pytest.raises(OwnerLocalRollbackError):
        OwnerLocalBaseline(
            store_id="owner-local-runtime-db",
            database_sha256="a" * 64,
            canonical_storage_policy=StorageScope.SHARED_CANONICAL,
        )


def test_p18_7_contract_document_preserves_provider_and_crypto_evidence_boundary():
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    assert "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED" in contract
    assert "does **not**" in contract
    assert "production cryptographic primitive" in contract
    assert "provider WAL/PITR" in contract
    assert "Test-only synthetic" in contract
    assert "PROJECT_LOCAL_ONLY" in contract
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in contract
    assert "NOT_CREATED / NOT_PREAUTHORIZED" in contract
    assert "NONE_APPROVED" in contract
    assert "P13.5/P13.6" in contract


def test_p18_7_preserves_current_phase18_activation_and_migration_boundaries():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    minor = int(state["roadmap"]["state_sync_version"].split(".")[1])
    assert minor >= 31
    assert "P18_6_VALIDATED" in state["phases"]["18"]
    assert "P18_7_READY" in state["phases"]["18"] or "P18_7_VALIDATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["verification_authority"] == "P13.5/P13.6"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
