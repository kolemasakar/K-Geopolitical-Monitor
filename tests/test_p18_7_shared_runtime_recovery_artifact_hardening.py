import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

import pytest

from kgeopolitical_monitor.shared_runtime_contract import TenantContext
from kgeopolitical_monitor.shared_runtime_recovery import (
    BackupContractError,
    SharedBackupManifest,
)
from kgeopolitical_monitor.shared_runtime_recovery_artifacts import (
    ArtifactIntegrityError,
    ArtifactTenantIsolationError,
    EncryptedBackupArtifact,
    InMemoryCleanRestoreTarget,
    LogicalRecoveryPoint,
    MeasuredRecoveryObjectiveEvidence,
    RecoveryObjectiveMeasurementError,
    RecoveryPointSelectionError,
    RecoveryRecordSnapshot,
    RecoveryTargetNotCleanError,
    TenantRecoverySnapshot,
    public_artifact_metadata,
    restore_encrypted_artifact,
    select_logical_recovery_point,
    verify_artifact_snapshot_binding,
)
from kgeopolitical_monitor.shared_runtime_security import SecretReference


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
SUPPLEMENT_PATH = (
    ROOT
    / "docs"
    / "implementation"
    / "P18_7_SHARED_RUNTIME_RECOVERY_ARTIFACT_HARDENING.md"
)

NOW = datetime(2026, 9, 7, 20, 30, tzinfo=timezone.utc)


def tenant(workspace="ws-a", project="project-a"):
    return TenantContext(workspace_id=workspace, project_id=project)


def row(
    object_type="shared_event",
    object_id="event-1",
    *,
    scope=None,
    payload=None,
):
    return RecoveryRecordSnapshot.from_payload(
        tenant_context=scope or tenant(),
        object_type=object_type,
        object_id=object_id,
        payload=payload or {"summary": "safe", "rank": 1},
    )


def snapshot(
    *,
    scope=None,
    captured_at=NOW,
    schema_version=1,
    checkpoint_id="checkpoint-001",
    records=None,
):
    target = scope or tenant()
    values = records or (
        row("shared_semantic_claim", "claim-1", scope=target, payload={"text": "claim"}),
        row("shared_event", "event-1", scope=target, payload={"summary": "event"}),
    )
    return TenantRecoverySnapshot(
        tenant_context=target,
        schema_version=schema_version,
        checkpoint_id=checkpoint_id,
        captured_at=captured_at,
        records=values,
    )


def key_ref():
    return SecretReference(source="secret_store", name="P18_7_TEST_KEY_REFERENCE")


def manifest_for(item, **overrides):
    values = {
        "backup_id": "backup-artifact-001",
        "tenant_context": item.tenant_context,
        "schema_version": item.schema_version,
        "schema_contract_id": "p18.3-schema-v1",
        "captured_at": item.captured_at,
        "checkpoint_id": item.checkpoint_id,
        "content_sha256": item.content_sha256,
        "encryption_key_reference": key_ref(),
        "row_counts": item.row_counts,
    }
    values.update(overrides)
    return SharedBackupManifest(**values)


def artifact_for(item, *, protected=None, scheme="TEST_ONLY_SYNTHETIC_CODEC", manifest=None):
    ciphertext = protected or (b"TEST_ONLY_OPAQUE:" + item.content_sha256.encode("ascii"))
    return EncryptedBackupArtifact(
        manifest=manifest or manifest_for(item),
        encryption_scheme=scheme,
        ciphertext=ciphertext,
        ciphertext_sha256=sha256(ciphertext).hexdigest(),
    )


class SyntheticTestOnlyCodec:
    codec_id = "synthetic-test-only-not-cryptographic-evidence"

    def __init__(self, decoded):
        self.decoded = decoded

    def open(self, artifact):
        return self.decoded


def test_record_payload_is_canonical_and_independent_from_source_mapping():
    payload = {"z": 2, "a": {"value": 1}}
    item = RecoveryRecordSnapshot.from_payload(
        tenant_context=tenant(),
        object_type="shared_event",
        object_id="event-1",
        payload=payload,
    )
    payload["a"]["value"] = 999
    assert item.payload_json == '{"a":{"value":1},"z":2}'


def test_record_snapshot_is_frozen():
    item = row()
    with pytest.raises(FrozenInstanceError):
        item.object_id = "changed"


def test_snapshot_hash_and_row_counts_are_deterministic_across_record_order():
    a = row("shared_event", "event-1", payload={"b": 2, "a": 1})
    b = row("shared_semantic_claim", "claim-1", payload={"text": "x"})
    first = snapshot(records=(a, b))
    second = snapshot(records=(b, a))
    assert first.records == second.records
    assert first.content_sha256 == second.content_sha256
    assert first.row_counts == (
        ("shared_event", 1),
        ("shared_semantic_claim", 1),
    )


def test_snapshot_rejects_mixed_tenant_rows():
    with pytest.raises(ArtifactTenantIsolationError):
        snapshot(
            records=(
                row(scope=tenant("ws-a", "project-a")),
                row("shared_semantic_claim", "claim-2", scope=tenant("ws-b", "project-a")),
            )
        )


def test_snapshot_rejects_duplicate_object_identity():
    with pytest.raises(BackupContractError):
        snapshot(records=(row(), row(payload={"summary": "different"})))


def test_artifact_adds_ciphertext_integrity_without_claiming_provider_evidence():
    item = snapshot()
    artifact = artifact_for(item)
    assert artifact.manifest.encrypted is True
    assert artifact.manifest.off_host_copy is True
    assert artifact.provider_id is None
    assert artifact.contract_only is True
    assert artifact.off_host_storage_observed is False
    assert artifact.cryptographic_adapter_observed is False
    assert artifact.provider_pitr_observed is False
    assert artifact.ciphertext_sha256 == sha256(artifact.ciphertext).hexdigest()
    assert "TEST_ONLY_OPAQUE" not in repr(artifact)


@pytest.mark.parametrize("scheme", ["none", "plaintext", "identity", "unencrypted", "   "])
def test_artifact_rejects_unencrypted_scheme_declarations(scheme):
    with pytest.raises(BackupContractError):
        artifact_for(snapshot(), scheme=scheme)


def test_artifact_rejects_ciphertext_corruption():
    artifact = artifact_for(snapshot())
    with pytest.raises(ArtifactIntegrityError):
        replace(artifact, ciphertext=artifact.ciphertext + b"corruption")


def test_artifact_rejects_empty_ciphertext():
    item = snapshot()
    with pytest.raises(BackupContractError):
        EncryptedBackupArtifact(
            manifest=manifest_for(item),
            encryption_scheme="AES_GCM_ADAPTER_DECLARATION",
            ciphertext=b"",
            ciphertext_sha256=sha256(b"").hexdigest(),
        )


def test_manifest_snapshot_binding_accepts_exact_decoded_content():
    item = snapshot()
    artifact = artifact_for(item)
    assert verify_artifact_snapshot_binding(artifact=artifact, snapshot=item) is item


def test_manifest_snapshot_binding_rejects_content_substitution():
    item = snapshot()
    artifact = artifact_for(item)
    changed = snapshot(records=(row(payload={"summary": "changed"}),))
    with pytest.raises(ArtifactIntegrityError):
        verify_artifact_snapshot_binding(artifact=artifact, snapshot=changed)


def test_manifest_snapshot_binding_rejects_cross_tenant_decode():
    item = snapshot()
    artifact = artifact_for(item)
    other = snapshot(scope=tenant("ws-b", "project-a"))
    with pytest.raises(ArtifactTenantIsolationError):
        verify_artifact_snapshot_binding(artifact=artifact, snapshot=other)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"schema_version": 2},
        {"checkpoint_id": "checkpoint-other"},
    ],
)
def test_manifest_snapshot_binding_rejects_schema_or_checkpoint_substitution(kwargs):
    item = snapshot()
    artifact = artifact_for(item)
    changed = snapshot(**kwargs)
    with pytest.raises(ArtifactIntegrityError):
        verify_artifact_snapshot_binding(artifact=artifact, snapshot=changed)


def test_manifest_snapshot_binding_rejects_row_count_mismatch_even_with_declared_digest():
    item = snapshot()
    altered_manifest = manifest_for(
        item,
        row_counts=(("shared_event", 2), ("shared_semantic_claim", 0)),
    )
    artifact = artifact_for(item, manifest=altered_manifest)
    with pytest.raises(ArtifactIntegrityError):
        verify_artifact_snapshot_binding(artifact=artifact, snapshot=item)


def test_clean_target_restores_actual_records_and_reconciles_hash():
    item = snapshot()
    target = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        schema_version=item.schema_version,
    )
    restored = target.restore(item)
    assert restored == item.records
    assert target.restored_content_sha256 == item.content_sha256
    assert target.is_clean is False


def test_clean_target_refuses_overwrite_after_restore():
    item = snapshot()
    target = InMemoryCleanRestoreTarget(
        tenant_context=item.tenant_context,
        schema_version=item.schema_version,
    )
    target.restore(item)
    with pytest.raises(RecoveryTargetNotCleanError):
        target.restore(item)


def test_clean_target_rejects_cross_workspace_and_cross_project_restore():
    item = snapshot()
    for other in (tenant("ws-b", "project-a"), tenant("ws-a", "project-b")):
        target = InMemoryCleanRestoreTarget(tenant_context=other, schema_version=1)
        with pytest.raises(ArtifactTenantIsolationError):
            target.restore(item)


def test_clean_target_rejects_schema_mismatch():
    item = snapshot()
    target = InMemoryCleanRestoreTarget(tenant_context=item.tenant_context, schema_version=2)
    with pytest.raises(ArtifactIntegrityError):
        target.restore(item)


def test_encrypted_artifact_restore_verifies_binding_before_actual_restore():
    item = snapshot()
    artifact = artifact_for(item)
    target = InMemoryCleanRestoreTarget(tenant_context=item.tenant_context, schema_version=1)
    restored = restore_encrypted_artifact(
        artifact=artifact,
        codec=SyntheticTestOnlyCodec(item),
        target=target,
    )
    assert restored == item.records
    assert target.restored_content_sha256 == item.content_sha256


def test_encrypted_artifact_restore_blocks_codec_returning_wrong_tenant():
    item = snapshot()
    artifact = artifact_for(item)
    target = InMemoryCleanRestoreTarget(tenant_context=item.tenant_context, schema_version=1)
    with pytest.raises(ArtifactTenantIsolationError):
        restore_encrypted_artifact(
            artifact=artifact,
            codec=SyntheticTestOnlyCodec(snapshot(scope=tenant("ws-b", "project-a"))),
            target=target,
        )
    assert target.is_clean is True


def test_logical_recovery_point_selection_is_deterministic_at_or_before_target():
    scope = tenant()
    s1 = snapshot(captured_at=NOW - timedelta(minutes=20), checkpoint_id="cp-1")
    s2 = snapshot(captured_at=NOW - timedelta(minutes=10), checkpoint_id="cp-2")
    s3 = snapshot(captured_at=NOW, checkpoint_id="cp-3")
    points = (
        LogicalRecoveryPoint(scope, s3.captured_at, 3, s3),
        LogicalRecoveryPoint(scope, s1.captured_at, 1, s1),
        LogicalRecoveryPoint(scope, s2.captured_at, 2, s2),
    )
    selected = select_logical_recovery_point(
        tenant_context=scope,
        points=points,
        target_at=NOW - timedelta(minutes=5),
    )
    assert selected.sequence == 2
    assert selected.snapshot.checkpoint_id == "cp-2"


def test_logical_recovery_point_selection_rejects_mixed_tenants():
    a = snapshot(checkpoint_id="cp-a")
    b_scope = tenant("ws-b", "project-a")
    b = snapshot(scope=b_scope, checkpoint_id="cp-b")
    with pytest.raises(ArtifactTenantIsolationError):
        select_logical_recovery_point(
            tenant_context=tenant(),
            points=(
                LogicalRecoveryPoint(tenant(), a.captured_at, 1, a),
                LogicalRecoveryPoint(b_scope, b.captured_at, 2, b),
            ),
            target_at=NOW,
        )


def test_logical_recovery_point_selection_fails_when_target_precedes_all_points():
    item = snapshot()
    point = LogicalRecoveryPoint(item.tenant_context, item.captured_at, 1, item)
    with pytest.raises(RecoveryPointSelectionError):
        select_logical_recovery_point(
            tenant_context=item.tenant_context,
            points=(point,),
            target_at=item.captured_at - timedelta(seconds=1),
        )


def test_failure_based_recovery_objectives_measure_full_rpo_and_rto():
    evidence = MeasuredRecoveryObjectiveEvidence(
        last_durable_recovery_point_at=NOW - timedelta(seconds=45),
        failure_at=NOW,
        restore_started_at=NOW + timedelta(seconds=30),
        restore_completed_at=NOW + timedelta(seconds=120),
    )
    assert evidence.measured_rpo_seconds == 45.0
    assert evidence.measured_rto_seconds == 120.0
    assert evidence.service_level_claim_authorized is False
    assert evidence.provider_pitr_observed is False
    assert evidence.factual_verification_authority is False


def test_failure_based_recovery_objectives_include_pre_restore_delay_in_rto():
    evidence = MeasuredRecoveryObjectiveEvidence(
        last_durable_recovery_point_at=NOW,
        failure_at=NOW,
        restore_started_at=NOW + timedelta(seconds=30),
        restore_completed_at=NOW + timedelta(seconds=120),
    )
    restore_execution_duration = (evidence.restore_completed_at - evidence.restore_started_at).total_seconds()
    assert restore_execution_duration == 90.0
    assert evidence.measured_rto_seconds == 120.0


def test_recovery_objective_evidence_rejects_non_monotonic_or_naive_timestamps():
    with pytest.raises(RecoveryObjectiveMeasurementError):
        MeasuredRecoveryObjectiveEvidence(
            last_durable_recovery_point_at=NOW,
            failure_at=NOW - timedelta(seconds=1),
            restore_started_at=NOW,
            restore_completed_at=NOW,
        )
    with pytest.raises(RecoveryObjectiveMeasurementError):
        MeasuredRecoveryObjectiveEvidence(
            last_durable_recovery_point_at=datetime(2026, 9, 7, 20, 0),
            failure_at=NOW,
            restore_started_at=NOW,
            restore_completed_at=NOW,
        )


def test_public_artifact_metadata_excludes_ciphertext_and_secret_locator():
    item = snapshot()
    artifact = artifact_for(item)
    metadata = public_artifact_metadata(artifact)
    encoded = json.dumps(metadata, sort_keys=True)
    assert "ciphertext" not in metadata
    assert "encryption_key_reference" not in metadata
    assert key_ref().locator not in encoded
    assert "P18_7_TEST_KEY_REFERENCE" not in encoded
    assert "TEST_ONLY_OPAQUE" not in encoded
    assert metadata["off_host_copy_required"] is True
    assert metadata["off_host_storage_observed"] is False
    assert metadata["canonical_cutover_authorized"] is False
    assert metadata["shared_runtime_activated"] is False
    assert metadata["factual_verification_authority"] is False


def test_hardening_supplement_marks_infrastructure_and_crypto_evidence_as_unobserved():
    text = SUPPLEMENT_PATH.read_text(encoding="utf-8")
    assert "ciphertext SHA-256" in text
    assert "not cryptographic evidence" in text
    assert "off_host_storage_observed = False" in text
    assert "failure time" in text
    assert "provider WAL/PITR" in text
    assert "PROJECT_LOCAL_ONLY" in text
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
    assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
    assert "NONE_APPROVED" in text
    assert "P13.5/P13.6" in text


def test_artifact_hardening_preserves_phase18_boundary_state_forward_compatibly():
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
