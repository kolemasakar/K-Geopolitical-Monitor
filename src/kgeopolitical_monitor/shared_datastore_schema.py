"""P18.3 provider-neutral shared datastore schema and migration contracts.

This module defines an in-memory relational contract only. It does not create,
connect to, migrate, or activate a shared datastore. The active canonical
runtime remains project-local SQLite until a later, separately authorized
cutover/activation gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable

from .shared_runtime_contract import StorageScope, TenantContext


TENANT_KEY = ("workspace_id", "project_id")
MIGRATION_NUMBER_NOT_ALLOCATED = "NOT_ALLOCATED"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SharedSchemaContractError(ValueError):
    """Base error for invalid shared relational schema contracts."""


class TenantConstraintError(SharedSchemaContractError):
    """Raised when a table/reference can escape its tenant boundary."""


class MigrationContractError(ValueError):
    """Raised when a proposed migration violates the P18.3 boundary."""


class ReconciliationContractError(ValueError):
    """Raised when export/import evidence is incomplete or inconsistent."""


class RelationalDialect(str, Enum):
    """Provider-neutral relational capability target."""

    POSTGRESQL_COMPATIBLE = "postgresql_compatible"


def _required_text(value: str, *, field_name: str, error_type=SharedSchemaContractError) -> str:
    if not isinstance(value, str):
        raise error_type(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise error_type(f"{field_name} is required")
    return normalized


def _required_names(values: Iterable[str], *, field_name: str) -> tuple[str, ...]:
    normalized = tuple(_required_text(value, field_name=field_name) for value in values)
    if not normalized:
        raise SharedSchemaContractError(f"{field_name} requires at least one value")
    if len(set(normalized)) != len(normalized):
        raise SharedSchemaContractError(f"{field_name} contains duplicates")
    return normalized


@dataclass(frozen=True)
class ColumnContract:
    name: str
    type_name: str
    nullable: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text(self.name, field_name="column name"))
        object.__setattr__(self, "type_name", _required_text(self.type_name, field_name="type_name"))


@dataclass(frozen=True)
class ForeignKeyContract:
    local_columns: tuple[str, ...]
    referenced_table: str
    referenced_columns: tuple[str, ...]

    def __post_init__(self) -> None:
        local = _required_names(self.local_columns, field_name="local_columns")
        referenced = _required_names(self.referenced_columns, field_name="referenced_columns")
        if len(local) != len(referenced):
            raise SharedSchemaContractError("foreign-key column counts must match")
        object.__setattr__(self, "local_columns", local)
        object.__setattr__(
            self,
            "referenced_table",
            _required_text(self.referenced_table, field_name="referenced_table"),
        )
        object.__setattr__(self, "referenced_columns", referenced)


@dataclass(frozen=True)
class RowSecurityContract:
    """Database-policy contract; this does not install a concrete RLS policy."""

    scope_columns: tuple[str, ...] = TENANT_KEY
    fail_closed: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "scope_columns",
            _required_names(self.scope_columns, field_name="row-security scope_columns"),
        )


@dataclass(frozen=True)
class TableContract:
    name: str
    columns: tuple[ColumnContract, ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[ForeignKeyContract, ...] = ()
    row_security: RowSecurityContract = RowSecurityContract()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text(self.name, field_name="table name"))
        if not self.columns:
            raise SharedSchemaContractError("table requires columns")
        column_names = tuple(column.name for column in self.columns)
        if len(set(column_names)) != len(column_names):
            raise SharedSchemaContractError(f"table {self.name} contains duplicate columns")
        primary_key = _required_names(self.primary_key, field_name="primary_key")
        missing = set(primary_key) - set(column_names)
        if missing:
            raise SharedSchemaContractError(
                f"table {self.name} primary key references missing columns: {sorted(missing)}"
            )
        object.__setattr__(self, "primary_key", primary_key)


@dataclass(frozen=True)
class SharedSchemaContract:
    """Provider-neutral transactional shared-schema descriptor."""

    schema_version: int
    dialect: RelationalDialect
    tables: tuple[TableContract, ...]
    storage_scope: StorageScope = StorageScope.SHARED_CANONICAL
    transactions_required: bool = True
    provider_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.schema_version, int) or self.schema_version <= 0:
            raise SharedSchemaContractError("schema_version must be a positive integer")
        if not isinstance(self.dialect, RelationalDialect):
            raise SharedSchemaContractError("relational dialect is invalid")
        if not self.tables:
            raise SharedSchemaContractError("shared schema requires at least one table")


def validate_shared_schema_contract(contract: SharedSchemaContract) -> SharedSchemaContract:
    """Fail closed unless tenancy is enforced at relational-policy level."""

    if not isinstance(contract, SharedSchemaContract):
        raise SharedSchemaContractError("shared schema contract is required")
    if contract.storage_scope is not StorageScope.SHARED_CANONICAL:
        raise SharedSchemaContractError("shared schema cannot use project-local SQLite storage")
    if contract.dialect is not RelationalDialect.POSTGRESQL_COMPATIBLE:
        raise SharedSchemaContractError("P18.3 requires a PostgreSQL-compatible relational contract")
    if not contract.transactions_required:
        raise SharedSchemaContractError("shared canonical writes require transactional semantics")
    if contract.provider_id is not None:
        raise SharedSchemaContractError("P18.3 remains provider-neutral; provider_id must be unset")

    tables = {table.name: table for table in contract.tables}
    if len(tables) != len(contract.tables):
        raise SharedSchemaContractError("shared schema contains duplicate table names")

    for table in contract.tables:
        column_map = {column.name: column for column in table.columns}
        for tenant_column in TENANT_KEY:
            column = column_map.get(tenant_column)
            if column is None:
                raise TenantConstraintError(
                    f"table {table.name} is missing mandatory tenant column {tenant_column}"
                )
            if column.nullable:
                raise TenantConstraintError(
                    f"table {table.name} tenant column {tenant_column} cannot be nullable"
                )
        if table.primary_key[: len(TENANT_KEY)] != TENANT_KEY:
            raise TenantConstraintError(
                f"table {table.name} primary key must begin with workspace_id/project_id"
            )
        if table.row_security.scope_columns != TENANT_KEY or not table.row_security.fail_closed:
            raise TenantConstraintError(
                f"table {table.name} requires fail-closed workspace/project database policy scope"
            )

        for foreign_key in table.foreign_keys:
            missing_local = set(foreign_key.local_columns) - set(column_map)
            if missing_local:
                raise SharedSchemaContractError(
                    f"table {table.name} foreign key references missing local columns: {sorted(missing_local)}"
                )
            target = tables.get(foreign_key.referenced_table)
            if target is None:
                raise SharedSchemaContractError(
                    f"table {table.name} references unknown table {foreign_key.referenced_table}"
                )
            target_columns = {column.name for column in target.columns}
            missing_target = set(foreign_key.referenced_columns) - target_columns
            if missing_target:
                raise SharedSchemaContractError(
                    f"foreign key target {target.name} lacks columns: {sorted(missing_target)}"
                )
            if (
                foreign_key.local_columns[: len(TENANT_KEY)] != TENANT_KEY
                or foreign_key.referenced_columns[: len(TENANT_KEY)] != TENANT_KEY
            ):
                raise TenantConstraintError(
                    f"foreign key {table.name}->{target.name} must carry workspace_id/project_id"
                )

    return contract


def _tenant_columns() -> tuple[ColumnContract, ...]:
    return (
        ColumnContract("workspace_id", "text"),
        ColumnContract("project_id", "text"),
    )


def build_p18_3_schema_contract() -> SharedSchemaContract:
    """Build the minimum representative schema contract for P18.3 validation.

    These descriptors are not DDL and do not claim to be the final production
    schema. They prove the mandatory tenancy/reference pattern future shared
    canonical object families must follow.
    """

    event = TableContract(
        name="shared_event",
        columns=(*_tenant_columns(), ColumnContract("event_id", "text")),
        primary_key=(*TENANT_KEY, "event_id"),
    )
    claim = TableContract(
        name="shared_semantic_claim",
        columns=(
            *_tenant_columns(),
            ColumnContract("claim_id", "text"),
            ColumnContract("event_id", "text"),
        ),
        primary_key=(*TENANT_KEY, "claim_id"),
        foreign_keys=(
            ForeignKeyContract(
                local_columns=(*TENANT_KEY, "event_id"),
                referenced_table="shared_event",
                referenced_columns=(*TENANT_KEY, "event_id"),
            ),
        ),
    )
    forecast = TableContract(
        name="shared_forecast",
        columns=(
            *_tenant_columns(),
            ColumnContract("forecast_id", "text"),
            ColumnContract("claim_id", "text"),
        ),
        primary_key=(*TENANT_KEY, "forecast_id"),
        foreign_keys=(
            ForeignKeyContract(
                local_columns=(*TENANT_KEY, "claim_id"),
                referenced_table="shared_semantic_claim",
                referenced_columns=(*TENANT_KEY, "claim_id"),
            ),
        ),
    )
    delivery = TableContract(
        name="shared_delivery_intent",
        columns=(
            *_tenant_columns(),
            ColumnContract("delivery_id", "text"),
            ColumnContract("event_id", "text"),
        ),
        primary_key=(*TENANT_KEY, "delivery_id"),
        foreign_keys=(
            ForeignKeyContract(
                local_columns=(*TENANT_KEY, "event_id"),
                referenced_table="shared_event",
                referenced_columns=(*TENANT_KEY, "event_id"),
            ),
        ),
    )
    publication = TableContract(
        name="shared_publication_release",
        columns=(
            *_tenant_columns(),
            ColumnContract("release_id", "text"),
            ColumnContract("claim_id", "text"),
        ),
        primary_key=(*TENANT_KEY, "release_id"),
        foreign_keys=(
            ForeignKeyContract(
                local_columns=(*TENANT_KEY, "claim_id"),
                referenced_table="shared_semantic_claim",
                referenced_columns=(*TENANT_KEY, "claim_id"),
            ),
        ),
    )
    return SharedSchemaContract(
        schema_version=1,
        dialect=RelationalDialect.POSTGRESQL_COMPATIBLE,
        tables=(event, claim, forecast, delivery, publication),
    )


@dataclass(frozen=True)
class SchemaCompatibilityContract:
    """Explicit compatibility statement for a proposed schema transition."""

    prior_readers_supported: bool
    prior_writers_supported: bool
    mixed_version_window_allowed: bool


@dataclass(frozen=True)
class MigrationContract:
    """Logical migration contract; no repository migration number is allocated."""

    contract_id: str
    from_schema_version: int
    to_schema_version: int
    forward_operations: tuple[str, ...]
    rollback_operations: tuple[str, ...]
    compatibility: SchemaCompatibilityContract
    migration_number: int | None = None
    destructive: bool = False
    canonical_cutover: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _required_text(self.contract_id, field_name="contract_id", error_type=MigrationContractError),
        )


def validate_migration_contract(contract: MigrationContract) -> MigrationContract:
    """Validate reversibility/version rules without authorizing a migration."""

    if not isinstance(contract, MigrationContract):
        raise MigrationContractError("migration contract is required")
    if contract.migration_number is not None:
        raise MigrationContractError(
            "P18.3 does not allocate or preauthorize a repository migration number"
        )
    if contract.from_schema_version <= 0 or contract.to_schema_version <= 0:
        raise MigrationContractError("schema versions must be positive")
    if contract.to_schema_version <= contract.from_schema_version:
        raise MigrationContractError("target schema version must advance")
    if not contract.forward_operations:
        raise MigrationContractError("forward operations are required")
    if not contract.rollback_operations:
        raise MigrationContractError("rollback operations are required before validation")
    if any(not str(operation).strip() for operation in contract.forward_operations):
        raise MigrationContractError("forward operations cannot contain blanks")
    if any(not str(operation).strip() for operation in contract.rollback_operations):
        raise MigrationContractError("rollback operations cannot contain blanks")
    if contract.destructive:
        raise MigrationContractError("destructive migration is outside the P18.3 contract boundary")
    if contract.canonical_cutover:
        raise MigrationContractError("migration contract cannot authorize canonical cutover")
    if not isinstance(contract.compatibility, SchemaCompatibilityContract):
        raise MigrationContractError("explicit schema compatibility rules are required")
    return contract


@dataclass(frozen=True)
class ExportManifestContract:
    """Provenance/reconciliation envelope for a future controlled local export."""

    export_id: str
    tenant_context: TenantContext
    source_storage_scope: StorageScope
    source_schema_version: int
    source_database_sha256: str
    row_counts: tuple[tuple[str, int], ...]
    table_checksums: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "export_id",
            _required_text(self.export_id, field_name="export_id", error_type=ReconciliationContractError),
        )
        if not isinstance(self.tenant_context, TenantContext):
            raise ReconciliationContractError("export requires explicit TenantContext")
        if self.source_storage_scope is not StorageScope.PROJECT_LOCAL_SQLITE:
            raise ReconciliationContractError(
                "controlled export source must be the owner-local project SQLite scope"
            )
        if not isinstance(self.source_schema_version, int) or self.source_schema_version <= 0:
            raise ReconciliationContractError("source_schema_version must be positive")
        digest = str(self.source_database_sha256).strip().lower()
        if not _SHA256_RE.fullmatch(digest):
            raise ReconciliationContractError("source_database_sha256 must be a 64-character hex digest")
        object.__setattr__(self, "source_database_sha256", digest)
        object.__setattr__(self, "row_counts", _validate_row_counts(self.row_counts))
        object.__setattr__(self, "table_checksums", _validate_checksums(self.table_checksums))
        if {name for name, _ in self.row_counts} != {name for name, _ in self.table_checksums}:
            raise ReconciliationContractError(
                "row-count and checksum evidence must cover the same tables"
            )


def _validate_row_counts(values: tuple[tuple[str, int], ...]) -> tuple[tuple[str, int], ...]:
    if not values:
        raise ReconciliationContractError("row-count evidence is required")
    normalized: list[tuple[str, int]] = []
    names: set[str] = set()
    for name, count in values:
        table = _required_text(name, field_name="table name", error_type=ReconciliationContractError)
        if table in names:
            raise ReconciliationContractError("duplicate row-count table")
        if not isinstance(count, int) or count < 0:
            raise ReconciliationContractError("row counts must be non-negative integers")
        names.add(table)
        normalized.append((table, count))
    return tuple(normalized)


def _validate_checksums(values: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    if not values:
        raise ReconciliationContractError("table checksum evidence is required")
    normalized: list[tuple[str, str]] = []
    names: set[str] = set()
    for name, digest in values:
        table = _required_text(name, field_name="table name", error_type=ReconciliationContractError)
        checksum = str(digest).strip().lower()
        if table in names:
            raise ReconciliationContractError("duplicate checksum table")
        if not _SHA256_RE.fullmatch(checksum):
            raise ReconciliationContractError("table checksum must be a 64-character hex digest")
        names.add(table)
        normalized.append((table, checksum))
    return tuple(normalized)


@dataclass(frozen=True)
class ImportReconciliationResult:
    tenant_context: TenantContext
    ready_for_shadow_validation: bool
    canonical_cutover_authorized: bool = False


def reconcile_import_evidence(
    *,
    manifest: ExportManifestContract,
    observed_row_counts: tuple[tuple[str, int], ...],
    observed_table_checksums: tuple[tuple[str, str], ...],
) -> ImportReconciliationResult:
    """Compare controlled import evidence without promoting it to canonical state."""

    if not isinstance(manifest, ExportManifestContract):
        raise ReconciliationContractError("export manifest is required")
    rows = _validate_row_counts(observed_row_counts)
    checksums = _validate_checksums(observed_table_checksums)
    if dict(rows) != dict(manifest.row_counts):
        raise ReconciliationContractError("import row counts do not reconcile with export")
    if dict(checksums) != dict(manifest.table_checksums):
        raise ReconciliationContractError("import checksums do not reconcile with export")
    return ImportReconciliationResult(
        tenant_context=manifest.tenant_context,
        ready_for_shadow_validation=True,
        canonical_cutover_authorized=False,
    )
