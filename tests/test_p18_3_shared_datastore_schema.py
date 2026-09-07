import json
from dataclasses import replace
from pathlib import Path

import pytest

from kgeopolitical_monitor.shared_datastore_schema import (
    MIGRATION_NUMBER_NOT_ALLOCATED,
    TENANT_KEY,
    ColumnContract,
    ExportManifestContract,
    ForeignKeyContract,
    MigrationContract,
    MigrationContractError,
    ReconciliationContractError,
    RelationalDialect,
    RowSecurityContract,
    SchemaCompatibilityContract,
    SharedSchemaContract,
    SharedSchemaContractError,
    TableContract,
    TenantConstraintError,
    build_p18_3_schema_contract,
    reconcile_import_evidence,
    validate_migration_contract,
    validate_shared_schema_contract,
)
from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


def _schema() -> SharedSchemaContract:
    return build_p18_3_schema_contract()


def _migration(**overrides) -> MigrationContract:
    values = {
        "contract_id": "p18-3-logical-transition",
        "from_schema_version": 1,
        "to_schema_version": 2,
        "forward_operations": ("add tenant-scoped relation",),
        "rollback_operations": ("remove tenant-scoped relation",),
        "compatibility": SchemaCompatibilityContract(
            prior_readers_supported=True,
            prior_writers_supported=False,
            mixed_version_window_allowed=False,
        ),
    }
    values.update(overrides)
    return MigrationContract(**values)


def _manifest(**overrides) -> ExportManifestContract:
    values = {
        "export_id": "export-alpha",
        "tenant_context": TenantContext("workspace-alpha", "project-red"),
        "source_storage_scope": StorageScope.PROJECT_LOCAL_SQLITE,
        "source_schema_version": 32,
        "source_database_sha256": "a" * 64,
        "row_counts": (("events", 3), ("claims", 5)),
        "table_checksums": (("events", "b" * 64), ("claims", "c" * 64)),
    }
    values.update(overrides)
    return ExportManifestContract(**values)


def test_p18_3_representative_schema_contract_is_valid():
    contract = _schema()
    assert validate_shared_schema_contract(contract) is contract
    assert contract.dialect is RelationalDialect.POSTGRESQL_COMPATIBLE
    assert contract.storage_scope is StorageScope.SHARED_CANONICAL


def test_p18_3_schema_contract_remains_provider_neutral_and_transactional():
    contract = _schema()
    assert contract.provider_id is None
    assert contract.transactions_required is True


def test_p18_3_representative_canonical_families_are_tenant_scoped():
    tables = {table.name: table for table in _schema().tables}
    assert set(tables) == {
        "shared_event",
        "shared_semantic_claim",
        "shared_forecast",
        "shared_delivery_intent",
        "shared_publication_release",
    }
    for table in tables.values():
        names = {column.name for column in table.columns}
        assert set(TENANT_KEY) <= names
        assert table.primary_key[:2] == TENANT_KEY


def test_shared_schema_rejects_project_local_sqlite_scope():
    contract = replace(_schema(), storage_scope=StorageScope.PROJECT_LOCAL_SQLITE)
    with pytest.raises(SharedSchemaContractError, match="project-local SQLite"):
        validate_shared_schema_contract(contract)


def test_shared_schema_requires_transactional_semantics():
    with pytest.raises(SharedSchemaContractError, match="transactional semantics"):
        validate_shared_schema_contract(replace(_schema(), transactions_required=False))


def test_shared_schema_rejects_concrete_provider_selection():
    with pytest.raises(SharedSchemaContractError, match="provider-neutral"):
        validate_shared_schema_contract(replace(_schema(), provider_id="managed-postgres-vendor"))


def test_every_shared_table_requires_workspace_id():
    base = _schema()
    event = base.tables[0]
    event_without_workspace = TableContract(
        name=event.name,
        columns=tuple(column for column in event.columns if column.name != "workspace_id"),
        primary_key=("project_id", "event_id"),
    )
    with pytest.raises(TenantConstraintError, match="workspace_id"):
        validate_shared_schema_contract(replace(base, tables=(event_without_workspace, *base.tables[1:])))


def test_every_shared_table_requires_project_id():
    base = _schema()
    event = base.tables[0]
    event_without_project = TableContract(
        name=event.name,
        columns=tuple(column for column in event.columns if column.name != "project_id"),
        primary_key=("workspace_id", "event_id"),
    )
    with pytest.raises(TenantConstraintError, match="project_id"):
        validate_shared_schema_contract(replace(base, tables=(event_without_project, *base.tables[1:])))


def test_tenant_columns_cannot_be_nullable():
    base = _schema()
    event = base.tables[0]
    changed = tuple(
        replace(column, nullable=True) if column.name == "workspace_id" else column
        for column in event.columns
    )
    with pytest.raises(TenantConstraintError, match="cannot be nullable"):
        validate_shared_schema_contract(replace(base, tables=(replace(event, columns=changed), *base.tables[1:])))


def test_primary_key_must_begin_with_full_tenant_key():
    base = _schema()
    event = replace(base.tables[0], primary_key=("event_id", "workspace_id", "project_id"))
    with pytest.raises(TenantConstraintError, match="primary key must begin"):
        validate_shared_schema_contract(replace(base, tables=(event, *base.tables[1:])))


def test_database_policy_scope_requires_workspace_and_project():
    base = _schema()
    event = replace(
        base.tables[0],
        row_security=RowSecurityContract(scope_columns=("workspace_id",)),
    )
    with pytest.raises(TenantConstraintError, match="database policy scope"):
        validate_shared_schema_contract(replace(base, tables=(event, *base.tables[1:])))


def test_database_policy_scope_must_fail_closed():
    base = _schema()
    event = replace(base.tables[0], row_security=RowSecurityContract(fail_closed=False))
    with pytest.raises(TenantConstraintError, match="fail-closed"):
        validate_shared_schema_contract(replace(base, tables=(event, *base.tables[1:])))


def test_cross_object_foreign_keys_must_carry_tenant_key():
    base = _schema()
    claim = base.tables[1]
    unsafe_fk = ForeignKeyContract(
        local_columns=("event_id",),
        referenced_table="shared_event",
        referenced_columns=("event_id",),
    )
    unsafe_claim = replace(claim, foreign_keys=(unsafe_fk,))
    with pytest.raises(TenantConstraintError, match="must carry workspace_id/project_id"):
        validate_shared_schema_contract(replace(base, tables=(base.tables[0], unsafe_claim, *base.tables[2:])))


def test_foreign_key_to_unknown_table_fails_closed():
    base = _schema()
    claim = base.tables[1]
    invalid_fk = replace(claim.foreign_keys[0], referenced_table="missing_parent")
    with pytest.raises(SharedSchemaContractError, match="unknown table"):
        validate_shared_schema_contract(
            replace(base, tables=(base.tables[0], replace(claim, foreign_keys=(invalid_fk,)), *base.tables[2:]))
        )


def test_foreign_key_to_unknown_target_column_fails_closed():
    base = _schema()
    claim = base.tables[1]
    invalid_fk = ForeignKeyContract(
        local_columns=("workspace_id", "project_id", "event_id"),
        referenced_table="shared_event",
        referenced_columns=("workspace_id", "project_id", "missing_event_id"),
    )
    with pytest.raises(SharedSchemaContractError, match="lacks columns"):
        validate_shared_schema_contract(
            replace(base, tables=(base.tables[0], replace(claim, foreign_keys=(invalid_fk,)), *base.tables[2:]))
        )


def test_migration_contract_keeps_repository_migration_number_unallocated():
    contract = _migration()
    assert contract.migration_number is None
    assert MIGRATION_NUMBER_NOT_ALLOCATED == "NOT_ALLOCATED"
    assert validate_migration_contract(contract) is contract


@pytest.mark.parametrize("number", [33, 34, 100])
def test_p18_3_does_not_allocate_any_repository_migration_number(number):
    with pytest.raises(MigrationContractError, match="does not allocate"):
        validate_migration_contract(_migration(migration_number=number))


def test_migration_contract_requires_forward_version_advance():
    with pytest.raises(MigrationContractError, match="must advance"):
        validate_migration_contract(_migration(from_schema_version=2, to_schema_version=2))


def test_migration_contract_requires_forward_operations():
    with pytest.raises(MigrationContractError, match="forward operations"):
        validate_migration_contract(_migration(forward_operations=()))


def test_migration_contract_requires_rollback_before_validation():
    with pytest.raises(MigrationContractError, match="rollback operations"):
        validate_migration_contract(_migration(rollback_operations=()))


def test_destructive_migration_is_outside_p18_3_boundary():
    with pytest.raises(MigrationContractError, match="destructive migration"):
        validate_migration_contract(_migration(destructive=True))


def test_migration_contract_cannot_authorize_canonical_cutover():
    with pytest.raises(MigrationContractError, match="canonical cutover"):
        validate_migration_contract(_migration(canonical_cutover=True))


def test_migration_contract_requires_explicit_compatibility_rules():
    with pytest.raises(MigrationContractError, match="compatibility rules"):
        validate_migration_contract(_migration(compatibility=None))  # type: ignore[arg-type]


def test_controlled_export_requires_owner_local_sqlite_source():
    with pytest.raises(ReconciliationContractError, match="owner-local project SQLite"):
        _manifest(source_storage_scope=StorageScope.SHARED_CANONICAL)


def test_controlled_export_requires_source_database_digest():
    with pytest.raises(ReconciliationContractError, match="64-character hex digest"):
        _manifest(source_database_sha256="not-a-digest")


def test_controlled_export_requires_same_row_count_and_checksum_tables():
    with pytest.raises(ReconciliationContractError, match="same tables"):
        _manifest(table_checksums=(("events", "b" * 64),))


def test_controlled_export_rejects_negative_row_counts():
    with pytest.raises(ReconciliationContractError, match="non-negative"):
        _manifest(row_counts=(("events", -1),), table_checksums=(("events", "b" * 64),))


def test_reconciled_import_is_shadow_ready_but_never_cutover_authorized():
    manifest = _manifest()
    result = reconcile_import_evidence(
        manifest=manifest,
        observed_row_counts=manifest.row_counts,
        observed_table_checksums=manifest.table_checksums,
    )
    assert result.tenant_context == manifest.tenant_context
    assert result.ready_for_shadow_validation is True
    assert result.canonical_cutover_authorized is False


def test_import_row_count_mismatch_fails_reconciliation():
    manifest = _manifest()
    with pytest.raises(ReconciliationContractError, match="row counts do not reconcile"):
        reconcile_import_evidence(
            manifest=manifest,
            observed_row_counts=(("events", 4), ("claims", 5)),
            observed_table_checksums=manifest.table_checksums,
        )


def test_import_checksum_mismatch_fails_reconciliation():
    manifest = _manifest()
    with pytest.raises(ReconciliationContractError, match="checksums do not reconcile"):
        reconcile_import_evidence(
            manifest=manifest,
            observed_row_counts=manifest.row_counts,
            observed_table_checksums=(("events", "d" * 64), ("claims", "c" * 64)),
        )


def test_p18_3_implementation_preserves_runtime_and_migration_boundaries():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_2_VALIDATED_P18_3_READY_GATE"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
