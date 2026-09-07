from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.shared_datastore_schema import MIGRATION_NUMBER_NOT_ALLOCATED
from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext
from kgeopolitical_monitor.shared_runtime_recovery import (
    BackupContractError,
    RestoreContractError,
    RestoreDrillEvidence,
    RestoreRequest,
    RollbackContractError,
    RollbackEvidence,
    SharedBackupManifest,
    SharedRecoveryPlanContract,
    build_p18_7_recovery_plan_contract,
    validate_restore_request,
    validate_rollback_evidence,
)
from kgeopolitical_monitor.shared_runtime_security import SecretReference


CAPTURED_AT = datetime(2026, 9, 7, 18, 0, tzinfo=timezone.utc)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def tenant(workspace_id="ws-a", project_id="project-a"):
    return TenantContext(workspace_id=workspace_id, project_id=project_id)


def encryption_key_reference():
    return SecretReference(source="secret_store", name="P18_7_BACKUP_KEY")


def manifest(**overrides):
    values = {
        "backup_id": "backup-001",
        "tenant_context": tenant(),
        "schema_version": 1,
        "schema_contract_id": "p18.3-schema-v1",
        "captured_at": CAPTURED_AT,
        "checkpoint_id": "checkpoint-001",
        "content_sha256": DIGEST_A,
        "encryption_key_reference": encryption_key_reference(),
        "row_counts": (("shared_event", 2), ("shared_semantic_claim", 3)),
    }
    values.update(overrides)
    return SharedBackupManifest(**values)


def restore_request(**overrides):
    backup_manifest = overrides.pop("manifest", manifest())
    values = {
        "manifest": backup_manifest,
        "requested_tenant": backup_manifest.tenant_context,
        "requested_checkpoint_id": backup_manifest.checkpoint_id,
        "observed_content_sha256": backup_manifest.content_sha256,
        "observed_schema_version": backup_manifest.schema_version,
        "target_is_clean": True,
    }
    values.update(overrides)
    return RestoreRequest(**values)


def test_default_recovery_plan_preserves_phase_18_boundaries():
    plan = build_p18_7_recovery_plan_contract()

    assert plan.encrypted_backups_required is True
    assert plan.off_host_backup_required is True
    assert plan.clean_environment_restore_required is True
    assert plan.tenant_exact_match_required is True
    assert plan.pitr_supported is False
    assert plan.equivalent_checkpoint_restore_supported is True
    assert plan.provider_id is None
    assert plan.migration_number == MIGRATION_NUMBER_NOT_ALLOCATED
    assert plan.migration_033_authorized is False
    assert plan.shared_runtime_active is False
    assert plan.canonical_cutover_authorized is False
    assert plan.factual_verification_authority is False


def test_recovery_plan_requires_pitr_or_equivalent_checkpoint_restore():
    with pytest.raises(RestoreContractError, match="PITR"):
        SharedRecoveryPlanContract(
            pitr_supported=False,
            equivalent_checkpoint_restore_supported=False,
        )


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"encrypted_backups_required": False}, "encrypted"),
        ({"off_host_backup_required": False}, "off-host"),
        ({"clean_environment_restore_required": False}, "clean-environment"),
        ({"tenant_exact_match_required": False}, "tenant-exact"),
    ],
)
def test_recovery_plan_fails_closed_on_required_control_removal(kwargs, expected):
    with pytest.raises((BackupContractError, RestoreContractError), match=expected):
        SharedRecoveryPlanContract(**kwargs)


def test_valid_backup_manifest_is_provider_neutral_non_secret_and_truth_neutral():
    item = manifest()

    assert item.storage_scope is StorageScope.SHARED_CANONICAL
    assert item.provider_id is None
    assert item.migration_number == MIGRATION_NUMBER_NOT_ALLOCATED
    assert item.encrypted is True
    assert item.off_host_copy is True
    assert item.factual_verification_authority is False
    assert item.encryption_key_reference.locator == "secret_store://P18_7_BACKUP_KEY"
    assert "P18_7_BACKUP_KEY" not in repr(item)
    assert "secret_store://" not in repr(item)


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"encrypted": False}, "unencrypted"),
        ({"off_host_copy": False}, "off-host"),
        ({"migration_number": "033"}, "cannot allocate"),
        ({"content_sha256": "not-a-digest"}, "SHA-256"),
        ({"schema_version": 0}, "positive integer"),
        ({"row_counts": ()}, "row-count evidence"),
    ],
)
def test_backup_manifest_rejects_unsafe_or_incomplete_evidence(kwargs, expected):
    with pytest.raises(BackupContractError, match=expected):
        manifest(**kwargs)


def test_backup_manifest_requires_opaque_p18_6_secret_reference():
    with pytest.raises(BackupContractError, match="opaque SecretReference"):
        manifest(encryption_key_reference="inline-secret-value")


def test_backup_manifest_rejects_duplicate_or_negative_row_counts():
    with pytest.raises(BackupContractError, match="duplicate"):
        manifest(row_counts=(("shared_event", 1), ("shared_event", 1)))

    with pytest.raises(BackupContractError, match="non-negative"):
        manifest(row_counts=(("shared_event", -1),))


def test_restore_request_accepts_exact_tenant_clean_target_integrity_schema_and_checkpoint():
    request = restore_request()

    assert validate_restore_request(request) is request


@pytest.mark.parametrize(
    "requested_tenant",
    [
        TenantContext(workspace_id="ws-b", project_id="project-a"),
        TenantContext(workspace_id="ws-a", project_id="project-b"),
    ],
)
def test_restore_request_rejects_cross_tenant_restore(requested_tenant):
    with pytest.raises(RestoreContractError, match="cross-tenant"):
        validate_restore_request(restore_request(requested_tenant=requested_tenant))


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"target_is_clean": False}, "clean environment"),
        ({"requested_checkpoint_id": "checkpoint-other"}, "checkpoint"),
        ({"observed_content_sha256": DIGEST_B}, "digest"),
        ({"observed_schema_version": 2}, "schema version"),
    ],
)
def test_restore_request_rejects_dirty_or_mismatched_target(kwargs, expected):
    with pytest.raises(RestoreContractError, match=expected):
        validate_restore_request(restore_request(**kwargs))


def test_restore_drill_records_observed_rpo_rto_without_sla_claim():
    request = restore_request()
    evidence = RestoreDrillEvidence(
        request=request,
        restored_tenant=request.requested_tenant,
        recovery_target_at=CAPTURED_AT + timedelta(minutes=7),
        started_at=CAPTURED_AT + timedelta(minutes=8),
        completed_at=CAPTURED_AT + timedelta(minutes=10, seconds=30),
        reconciliation_passed=True,
    )

    assert evidence.observed_rpo_seconds == 420.0
    assert evidence.observed_rto_seconds == 150.0
    assert evidence.sla_claimed is False
    assert evidence.factual_verification_authority is False


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"reconciliation_passed": False}, "reconciliation"),
        ({"cross_tenant_rows_observed": True}, "cross-tenant rows"),
    ],
)
def test_restore_drill_rejects_failed_reconciliation_or_tenant_contamination(kwargs, expected):
    request = restore_request()
    values = {
        "request": request,
        "restored_tenant": request.requested_tenant,
        "recovery_target_at": CAPTURED_AT + timedelta(minutes=5),
        "started_at": CAPTURED_AT + timedelta(minutes=6),
        "completed_at": CAPTURED_AT + timedelta(minutes=7),
        "reconciliation_passed": True,
    }
    values.update(kwargs)

    with pytest.raises(RestoreContractError, match=expected):
        RestoreDrillEvidence(**values)


def test_restore_drill_rejects_wrong_restored_tenant_and_invalid_timing():
    request = restore_request()

    with pytest.raises(RestoreContractError, match="differs from backup tenant"):
        RestoreDrillEvidence(
            request=request,
            restored_tenant=tenant(workspace_id="ws-b"),
            recovery_target_at=CAPTURED_AT,
            started_at=CAPTURED_AT,
            completed_at=CAPTURED_AT,
            reconciliation_passed=True,
        )

    with pytest.raises(RestoreContractError, match="completion"):
        RestoreDrillEvidence(
            request=request,
            restored_tenant=request.requested_tenant,
            recovery_target_at=CAPTURED_AT,
            started_at=CAPTURED_AT + timedelta(minutes=2),
            completed_at=CAPTURED_AT + timedelta(minutes=1),
            reconciliation_passed=True,
        )


def test_rollback_evidence_proves_failed_shared_candidate_is_discardable_without_local_mutation():
    evidence = RollbackEvidence(
        candidate_id="shared-candidate-001",
        owner_local_sha256_before=DIGEST_A,
        owner_local_sha256_after=DIGEST_A,
        shared_candidate_discarded=True,
    )

    assert validate_rollback_evidence(evidence) is evidence
    assert evidence.owner_local_storage_scope is StorageScope.PROJECT_LOCAL_SQLITE
    assert evidence.shared_runtime_active is False
    assert evidence.canonical_cutover_performed is False
    assert evidence.factual_verification_authority is False


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"owner_local_sha256_after": DIGEST_B}, "changed"),
        ({"shared_candidate_discarded": False}, "discardable"),
        ({"shared_runtime_active": True}, "cannot activate"),
        ({"canonical_cutover_performed": True}, "cannot perform canonical cutover"),
        ({"owner_local_storage_scope": StorageScope.SHARED_CANONICAL}, "project-local"),
    ],
)
def test_rollback_evidence_fails_closed_on_boundary_violation(kwargs, expected):
    values = {
        "candidate_id": "shared-candidate-001",
        "owner_local_sha256_before": DIGEST_A,
        "owner_local_sha256_after": DIGEST_A,
        "shared_candidate_discarded": True,
    }
    values.update(kwargs)
    evidence = RollbackEvidence(**values)

    with pytest.raises(RollbackContractError, match=expected):
        validate_rollback_evidence(evidence)
