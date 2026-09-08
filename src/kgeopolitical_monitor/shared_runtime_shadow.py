"""P18.8 provider-neutral non-production shadow and canary-readiness contracts.

This module models an isolated, read-only shared-runtime candidate without
provisioning a datastore, selecting a provider, creating migration 033,
activating shared runtime, or changing the owner-local SQLite canonical runtime.

Real provider/network/TLS/PITR/off-host observations are never synthesized here.
They remain explicit external evidence for a separately approved infrastructure
step and the Phase 18 final readiness matrix.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Any, Iterable, Mapping

from .shared_datastore_schema import (
    ExportManifestContract,
    SharedSchemaContract,
    validate_shared_schema_contract,
)
from .shared_runtime_contract import StorageScope, TenantContext


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

P18_4_GATE = "P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED"
P18_6_GATE = "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED"
P18_7_GATE = "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED"


class ShadowContractError(RuntimeError):
    """Base error for P18.8 shadow/canary contract violations."""


class ShadowImportError(ShadowContractError, ValueError):
    """Raised when controlled import evidence is incomplete or unsafe."""


class ShadowComparisonError(ShadowContractError, ValueError):
    """Raised when shadow comparison evidence is malformed or ambiguous."""


class ProviderDecisionError(ShadowContractError, ValueError):
    """Raised when provider/spend boundaries are crossed without owner approval."""


class CanaryBoundaryError(ShadowContractError, ValueError):
    """Raised when a canary design attempts activation, writes, or auto-promotion."""


class MismatchKind(str, Enum):
    TENANT = "tenant"
    SCHEMA = "schema"
    ROW_COUNT = "row_count"
    TABLE_CONTENT = "table_content"
    SEMANTIC_PROJECTION = "semantic_projection"
    INVARIANT = "invariant"


class InfrastructureObservationState(str, Enum):
    NOT_OBSERVED = "not_observed"
    OBSERVED = "observed"


_FATAL_MISMATCH_KINDS = frozenset(
    {MismatchKind.TENANT, MismatchKind.SCHEMA, MismatchKind.INVARIANT}
)
_BUDGETABLE_MISMATCH_KINDS = frozenset(
    {
        MismatchKind.ROW_COUNT,
        MismatchKind.TABLE_CONTENT,
        MismatchKind.SEMANTIC_PROJECTION,
    }
)


def _required_text(value: str, *, field_name: str, error_type=ShadowContractError) -> str:
    if not isinstance(value, str):
        raise error_type(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise error_type(f"{field_name} is required")
    return normalized


def _digest(value: str, *, field_name: str, error_type=ShadowComparisonError) -> str:
    normalized = _required_text(value, field_name=field_name, error_type=error_type).lower()
    if not _SHA256_RE.fullmatch(normalized):
        raise error_type(f"{field_name} must be a 64-character SHA-256 hex digest")
    return normalized


def _canonical_json(value: Mapping[str, Any]) -> str:
    if not isinstance(value, Mapping):
        raise ShadowImportError("record payload must be a mapping")
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ShadowImportError("record payload must be canonical-JSON serializable") from exc


def _table_digest(records: Iterable["ShadowRecord"]) -> str:
    material = "\n".join(
        f"{record.object_id}\x1f{record.payload_sha256}\x1f{record.semantic_sha256}"
        for record in sorted(records, key=lambda item: item.object_id)
    )
    return sha256(material.encode("utf-8")).hexdigest()


def _semantic_table_digest(records: Iterable["ShadowRecord"]) -> str:
    material = "\n".join(
        f"{record.object_id}\x1f{record.semantic_sha256}"
        for record in sorted(records, key=lambda item: item.object_id)
    )
    return sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ShadowRecord:
    """Immutable tenant-scoped row snapshot used only for shadow validation."""

    tenant_context: TenantContext
    table_name: str
    object_id: str
    payload_json: str
    payload_sha256: str
    semantic_sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise ShadowImportError("shadow record requires explicit TenantContext")
        object.__setattr__(
            self,
            "table_name",
            _required_text(self.table_name, field_name="table_name", error_type=ShadowImportError),
        )
        object.__setattr__(
            self,
            "object_id",
            _required_text(self.object_id, field_name="object_id", error_type=ShadowImportError),
        )
        payload_json = _required_text(
            self.payload_json,
            field_name="payload_json",
            error_type=ShadowImportError,
        )
        try:
            parsed = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise ShadowImportError("payload_json must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ShadowImportError("payload_json must encode a JSON object")
        canonical = _canonical_json(parsed)
        if canonical != payload_json:
            raise ShadowImportError("payload_json must use canonical JSON encoding")
        expected_payload = sha256(canonical.encode("utf-8")).hexdigest()
        payload_digest = _digest(
            self.payload_sha256,
            field_name="payload_sha256",
            error_type=ShadowImportError,
        )
        if payload_digest != expected_payload:
            raise ShadowImportError("payload_sha256 does not match payload_json")
        object.__setattr__(self, "payload_sha256", payload_digest)
        object.__setattr__(
            self,
            "semantic_sha256",
            _digest(
                self.semantic_sha256,
                field_name="semantic_sha256",
                error_type=ShadowImportError,
            ),
        )

    @classmethod
    def from_payload(
        cls,
        *,
        tenant_context: TenantContext,
        table_name: str,
        object_id: str,
        payload: Mapping[str, Any],
        semantic_projection: Mapping[str, Any] | None = None,
    ) -> "ShadowRecord":
        payload_json = _canonical_json(payload)
        semantic_json = _canonical_json(
            semantic_projection if semantic_projection is not None else payload
        )
        return cls(
            tenant_context=tenant_context,
            table_name=table_name,
            object_id=object_id,
            payload_json=payload_json,
            payload_sha256=sha256(payload_json.encode("utf-8")).hexdigest(),
            semantic_sha256=sha256(semantic_json.encode("utf-8")).hexdigest(),
        )


@dataclass(frozen=True)
class ShadowSnapshotEvidence:
    tenant_context: TenantContext
    schema_version: int
    row_counts: tuple[tuple[str, int], ...]
    table_checksums: tuple[tuple[str, str], ...]
    semantic_checksums: tuple[tuple[str, str], ...]
    invariant_failures: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_context, TenantContext):
            raise ShadowComparisonError("snapshot evidence requires TenantContext")
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
            or self.schema_version <= 0
        ):
            raise ShadowComparisonError("schema_version must be a positive integer")
        object.__setattr__(self, "row_counts", _normalized_counts(self.row_counts))
        object.__setattr__(
            self,
            "table_checksums",
            _normalized_digests(self.table_checksums, "table_checksums"),
        )
        object.__setattr__(
            self,
            "semantic_checksums",
            _normalized_digests(self.semantic_checksums, "semantic_checksums"),
        )
        names = {name for name, _ in self.row_counts}
        if names != {name for name, _ in self.table_checksums}:
            raise ShadowComparisonError("row counts and table checksums must cover identical tables")
        if names != {name for name, _ in self.semantic_checksums}:
            raise ShadowComparisonError("row counts and semantic checksums must cover identical tables")
        failures = tuple(
            _required_text(value, field_name="invariant failure", error_type=ShadowComparisonError)
            for value in self.invariant_failures
        )
        if len(set(failures)) != len(failures):
            raise ShadowComparisonError("invariant failures cannot contain duplicates")
        object.__setattr__(self, "invariant_failures", tuple(sorted(failures)))


def _normalized_counts(values: tuple[tuple[str, int], ...]) -> tuple[tuple[str, int], ...]:
    if not values:
        raise ShadowComparisonError("row-count evidence is required")
    result: list[tuple[str, int]] = []
    seen: set[str] = set()
    for name, count in values:
        table = _required_text(name, field_name="table name", error_type=ShadowComparisonError)
        if table in seen:
            raise ShadowComparisonError("duplicate row-count table")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ShadowComparisonError("row counts must be non-negative integers")
        seen.add(table)
        result.append((table, count))
    return tuple(sorted(result))


def _normalized_digests(
    values: tuple[tuple[str, str], ...],
    field_name: str,
) -> tuple[tuple[str, str], ...]:
    if not values:
        raise ShadowComparisonError(f"{field_name} evidence is required")
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name, digest in values:
        table = _required_text(name, field_name="table name", error_type=ShadowComparisonError)
        if table in seen:
            raise ShadowComparisonError(f"duplicate {field_name} table")
        seen.add(table)
        result.append((table, _digest(digest, field_name=field_name)))
    return tuple(sorted(result))


def snapshot_from_records(
    *,
    tenant_context: TenantContext,
    schema_version: int,
    records: tuple[ShadowRecord, ...],
    invariant_failures: tuple[str, ...] = (),
) -> ShadowSnapshotEvidence:
    if not isinstance(tenant_context, TenantContext):
        raise ShadowImportError("shadow snapshot requires explicit TenantContext")
    if not records:
        raise ShadowImportError("shadow snapshot requires at least one record")
    identities: set[tuple[str, str]] = set()
    grouped: dict[str, list[ShadowRecord]] = {}
    for record in records:
        if not isinstance(record, ShadowRecord):
            raise ShadowImportError("records must be ShadowRecord instances")
        if record.tenant_context != tenant_context:
            raise ShadowImportError("mixed-tenant shadow records are forbidden")
        identity = (record.table_name, record.object_id)
        if identity in identities:
            raise ShadowImportError("duplicate shadow object identity")
        identities.add(identity)
        grouped.setdefault(record.table_name, []).append(record)
    row_counts = tuple(sorted((name, len(items)) for name, items in grouped.items()))
    table_checksums = tuple(sorted((name, _table_digest(items)) for name, items in grouped.items()))
    semantic_checksums = tuple(
        sorted((name, _semantic_table_digest(items)) for name, items in grouped.items())
    )
    return ShadowSnapshotEvidence(
        tenant_context=tenant_context,
        schema_version=schema_version,
        row_counts=row_counts,
        table_checksums=table_checksums,
        semantic_checksums=semantic_checksums,
        invariant_failures=invariant_failures,
    )


@dataclass(frozen=True)
class ControlledShadowPackage:
    """Provenance-bound owner-local export prepared for isolated shadow loading."""

    manifest: ExportManifestContract
    target_schema: SharedSchemaContract
    records: tuple[ShadowRecord, ...]
    source_snapshot: ShadowSnapshotEvidence
    canonical_cutover_authorized: bool = field(default=False, init=False)
    shared_runtime_activation_authorized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, ExportManifestContract):
            raise ShadowImportError("controlled shadow package requires ExportManifestContract")
        try:
            validate_shared_schema_contract(self.target_schema)
        except Exception as exc:
            raise ShadowImportError("target shared schema contract is invalid") from exc
        if self.target_schema.provider_id is not None:
            raise ShadowImportError("provider-neutral P18.8 package cannot select a provider")
        if self.source_snapshot.tenant_context != self.manifest.tenant_context:
            raise ShadowImportError("source snapshot tenant does not match export manifest")
        if self.source_snapshot.schema_version != self.manifest.source_schema_version:
            raise ShadowImportError("source snapshot schema version does not match export manifest")
        if dict(self.source_snapshot.row_counts) != dict(self.manifest.row_counts):
            raise ShadowImportError("source snapshot row counts do not match export manifest")
        if dict(self.source_snapshot.table_checksums) != dict(self.manifest.table_checksums):
            raise ShadowImportError("source snapshot checksums do not match export manifest")
        if not self.records:
            raise ShadowImportError("controlled shadow package requires records")

        allowed_tables = {table.name for table in self.target_schema.tables}
        record_tables = {record.table_name for record in self.records}
        snapshot_tables = {name for name, _ in self.source_snapshot.row_counts}
        unknown_tables = (record_tables | snapshot_tables) - allowed_tables
        if unknown_tables:
            raise ShadowImportError(
                "shadow package contains tables outside the approved target schema: "
                + ", ".join(sorted(unknown_tables))
            )

        rebuilt = snapshot_from_records(
            tenant_context=self.manifest.tenant_context,
            schema_version=self.manifest.source_schema_version,
            records=self.records,
            invariant_failures=self.source_snapshot.invariant_failures,
        )
        if rebuilt != self.source_snapshot:
            raise ShadowImportError("records do not reconcile to source snapshot evidence")


class NonProductionShadowCandidate:
    """Isolated read-only candidate. It is never canonical and exposes no write API."""

    provider_id = None
    environment = "non_production_contract_harness"
    read_only = True
    canonical = False
    production_live = False
    real_datastore_observed = False
    real_network_tls_observed = False
    canonical_cutover_authorized = False
    shared_runtime_activation_authorized = False

    def __init__(self, *, tenant_context: TenantContext, target_schema: SharedSchemaContract) -> None:
        if not isinstance(tenant_context, TenantContext):
            raise ShadowImportError("candidate requires explicit TenantContext")
        try:
            validate_shared_schema_contract(target_schema)
        except Exception as exc:
            raise ShadowImportError("candidate target schema is invalid") from exc
        if target_schema.provider_id is not None:
            raise ShadowImportError("candidate must remain provider-neutral")
        self._tenant_context = tenant_context
        self._target_schema = target_schema
        self._records: tuple[ShadowRecord, ...] = ()
        self._loaded = False

    @property
    def tenant_context(self) -> TenantContext:
        return self._tenant_context

    @property
    def target_schema(self) -> SharedSchemaContract:
        return self._target_schema

    def load_controlled_package(self, package: ControlledShadowPackage) -> ShadowSnapshotEvidence:
        if self._loaded:
            raise ShadowImportError("shadow candidate already contains an import; overwrite is forbidden")
        if not isinstance(package, ControlledShadowPackage):
            raise ShadowImportError("ControlledShadowPackage is required")
        if package.manifest.tenant_context != self._tenant_context:
            raise ShadowImportError("cross-tenant shadow import is forbidden")
        if package.target_schema != self._target_schema:
            raise ShadowImportError("shadow package target schema differs from candidate schema")
        self._records = tuple(package.records)
        self._loaded = True
        return self.observe()

    def observe(self) -> ShadowSnapshotEvidence:
        if not self._loaded:
            raise ShadowComparisonError("shadow candidate has not been loaded")
        return snapshot_from_records(
            tenant_context=self._tenant_context,
            schema_version=self._target_schema.schema_version,
            records=self._records,
        )

    def read_table(self, table_name: str) -> tuple[ShadowRecord, ...]:
        if not self._loaded:
            raise ShadowComparisonError("shadow candidate has not been loaded")
        name = _required_text(table_name, field_name="table_name", error_type=ShadowComparisonError)
        allowed_tables = {table.name for table in self._target_schema.tables}
        if name not in allowed_tables:
            raise ShadowComparisonError(
                "read request references a table outside the approved target schema"
            )
        return tuple(record for record in self._records if record.table_name == name)


@dataclass(frozen=True)
class ShadowMismatch:
    kind: MismatchKind
    subject: str
    expected: str
    observed: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, MismatchKind):
            raise ShadowComparisonError("mismatch kind is invalid")
        for field_name in ("subject", "expected", "observed"):
            object.__setattr__(
                self,
                field_name,
                _required_text(
                    getattr(self, field_name),
                    field_name=field_name,
                    error_type=ShadowComparisonError,
                ),
            )


@dataclass(frozen=True)
class ShadowMismatchBudget:
    """Explicit allowance for non-fatal comparison drift only.

    Tenant, schema and invariant mismatches are never budgetable.
    """

    max_total_mismatches: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.max_total_mismatches, int) or isinstance(self.max_total_mismatches, bool):
            raise ShadowComparisonError("max_total_mismatches must be an integer")
        if self.max_total_mismatches < 0:
            raise ShadowComparisonError("max_total_mismatches cannot be negative")


@dataclass(frozen=True)
class ShadowReconciliationReport:
    tenant_context: TenantContext
    mismatches: tuple[ShadowMismatch, ...]
    mismatch_budget: ShadowMismatchBudget
    within_budget: bool
    exact_match: bool
    ready_for_read_only_canary_design: bool
    fatal_mismatch_present: bool
    budgetable_mismatch_count: int
    canonical_cutover_authorized: bool = field(default=False, init=False)
    shared_runtime_activation_authorized: bool = field(default=False, init=False)
    factual_verification_authority: bool = field(default=False, init=False)


def compare_shadow_snapshots(
    *,
    expected: ShadowSnapshotEvidence,
    observed: ShadowSnapshotEvidence,
    budget: ShadowMismatchBudget = ShadowMismatchBudget(),
) -> ShadowReconciliationReport:
    if not isinstance(expected, ShadowSnapshotEvidence) or not isinstance(observed, ShadowSnapshotEvidence):
        raise ShadowComparisonError("expected and observed snapshot evidence are required")
    if not isinstance(budget, ShadowMismatchBudget):
        raise ShadowComparisonError("ShadowMismatchBudget is required")

    mismatches: list[ShadowMismatch] = []
    if expected.tenant_context != observed.tenant_context:
        mismatches.append(
            ShadowMismatch(
                MismatchKind.TENANT,
                "tenant_context",
                repr(expected.tenant_context),
                repr(observed.tenant_context),
            )
        )
    if expected.schema_version != observed.schema_version:
        mismatches.append(
            ShadowMismatch(
                MismatchKind.SCHEMA,
                "schema_version",
                str(expected.schema_version),
                str(observed.schema_version),
            )
        )

    _compare_mapping(
        kind=MismatchKind.ROW_COUNT,
        expected=dict(expected.row_counts),
        observed=dict(observed.row_counts),
        mismatches=mismatches,
    )
    _compare_mapping(
        kind=MismatchKind.TABLE_CONTENT,
        expected=dict(expected.table_checksums),
        observed=dict(observed.table_checksums),
        mismatches=mismatches,
    )
    _compare_mapping(
        kind=MismatchKind.SEMANTIC_PROJECTION,
        expected=dict(expected.semantic_checksums),
        observed=dict(observed.semantic_checksums),
        mismatches=mismatches,
    )

    for failure in sorted(set(expected.invariant_failures) | set(observed.invariant_failures)):
        mismatches.append(
            ShadowMismatch(
                MismatchKind.INVARIANT,
                failure,
                "clear",
                (
                    f"source={'present' if failure in expected.invariant_failures else 'absent'},"
                    f"shadow={'present' if failure in observed.invariant_failures else 'absent'}"
                ),
            )
        )

    mismatch_tuple = tuple(mismatches)
    fatal_mismatch_present = any(item.kind in _FATAL_MISMATCH_KINDS for item in mismatch_tuple)
    budgetable_mismatch_count = sum(
        item.kind in _BUDGETABLE_MISMATCH_KINDS for item in mismatch_tuple
    )
    within_budget = (
        not fatal_mismatch_present
        and budgetable_mismatch_count <= budget.max_total_mismatches
    )
    exact_match = not mismatch_tuple
    ready = (
        within_budget
        and not fatal_mismatch_present
        and expected.tenant_context == observed.tenant_context
        and expected.schema_version == observed.schema_version
        and not expected.invariant_failures
        and not observed.invariant_failures
    )
    return ShadowReconciliationReport(
        tenant_context=expected.tenant_context,
        mismatches=mismatch_tuple,
        mismatch_budget=budget,
        within_budget=within_budget,
        exact_match=exact_match,
        ready_for_read_only_canary_design=ready,
        fatal_mismatch_present=fatal_mismatch_present,
        budgetable_mismatch_count=budgetable_mismatch_count,
    )


def _compare_mapping(
    *,
    kind: MismatchKind,
    expected: Mapping[str, Any],
    observed: Mapping[str, Any],
    mismatches: list[ShadowMismatch],
) -> None:
    for key in sorted(set(expected) | set(observed)):
        left = expected.get(key, "<missing>")
        right = observed.get(key, "<missing>")
        if left != right:
            mismatches.append(ShadowMismatch(kind, key, str(left), str(right)))


@dataclass(frozen=True)
class Phase18ContractEvidence:
    """References validated P18 controls without claiming infrastructure probes."""

    concurrency_gate: str = P18_4_GATE
    security_gate: str = P18_6_GATE
    recovery_gate: str = P18_7_GATE
    network_tls: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    datastore_reachability: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    off_host_recovery: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    provider_pitr: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED

    def __post_init__(self) -> None:
        if self.concurrency_gate != P18_4_GATE:
            raise ShadowContractError("P18.4 concurrency evidence gate is required")
        if self.security_gate != P18_6_GATE:
            raise ShadowContractError("P18.6 security evidence gate is required")
        if self.recovery_gate != P18_7_GATE:
            raise ShadowContractError("P18.7 recovery evidence gate is required")
        for name in ("network_tls", "datastore_reachability", "off_host_recovery", "provider_pitr"):
            if not isinstance(getattr(self, name), InfrastructureObservationState):
                raise ShadowContractError(f"{name} observation state is invalid")

    @property
    def contract_evidence_complete(self) -> bool:
        return True

    @property
    def real_infrastructure_observed(self) -> bool:
        return any(
            state is InfrastructureObservationState.OBSERVED
            for state in (
                self.network_tls,
                self.datastore_reachability,
                self.off_host_recovery,
                self.provider_pitr,
            )
        )


@dataclass(frozen=True)
class ProviderCostOption:
    option_id: str
    monthly_fixed_cost: float
    variable_cost_basis: str
    security_summary: str
    exit_path: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "option_id",
            _required_text(self.option_id, field_name="option_id", error_type=ProviderDecisionError),
        )
        if (
            not isinstance(self.monthly_fixed_cost, (int, float))
            or isinstance(self.monthly_fixed_cost, bool)
            or self.monthly_fixed_cost < 0
        ):
            raise ProviderDecisionError("monthly_fixed_cost must be non-negative")
        object.__setattr__(self, "monthly_fixed_cost", float(self.monthly_fixed_cost))
        for name in ("variable_cost_basis", "security_summary", "exit_path"):
            object.__setattr__(
                self,
                name,
                _required_text(getattr(self, name), field_name=name, error_type=ProviderDecisionError),
            )


@dataclass(frozen=True)
class ProviderCostGate:
    """Separate provider/spend decision boundary."""

    external_infrastructure_required: bool = False
    options: tuple[ProviderCostOption, ...] = ()
    selected_option_id: str | None = None
    owner_approval_id: str | None = field(default=None, repr=False)
    paid_provider_commitment_authorized: bool = False

    def __post_init__(self) -> None:
        if any(not isinstance(option, ProviderCostOption) for option in self.options):
            raise ProviderDecisionError("provider options must be ProviderCostOption instances")
        if len({option.option_id for option in self.options}) != len(self.options):
            raise ProviderDecisionError("provider option ids must be unique")
        if self.external_infrastructure_required and len(self.options) < 2:
            raise ProviderDecisionError("external infrastructure requires comparison of at least two options")
        if self.selected_option_id is not None:
            selected = _required_text(
                self.selected_option_id,
                field_name="selected_option_id",
                error_type=ProviderDecisionError,
            )
            if selected not in {option.option_id for option in self.options}:
                raise ProviderDecisionError("selected provider option was not evaluated")
            if not self.owner_approval_id or not str(self.owner_approval_id).strip():
                raise ProviderDecisionError("provider selection requires separate explicit owner approval")
            object.__setattr__(self, "selected_option_id", selected)
            object.__setattr__(self, "owner_approval_id", str(self.owner_approval_id).strip())
        if self.paid_provider_commitment_authorized:
            if self.selected_option_id is None or not self.owner_approval_id:
                raise ProviderDecisionError("paid commitment requires approved provider selection")

    @property
    def comparison_complete(self) -> bool:
        return (not self.external_infrastructure_required) or len(self.options) >= 2

    @property
    def provider_selected(self) -> bool:
        return self.selected_option_id is not None


@dataclass(frozen=True)
class CanaryStage:
    observation_percent: int
    read_only: bool = True
    writes_enabled: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.observation_percent, int) or isinstance(self.observation_percent, bool):
            raise CanaryBoundaryError("observation_percent must be an integer")
        if self.observation_percent <= 0 or self.observation_percent > 100:
            raise CanaryBoundaryError("observation_percent must be between 1 and 100")
        if not self.read_only or self.writes_enabled:
            raise CanaryBoundaryError("P18.8 canary stages must remain read-only")


@dataclass(frozen=True)
class CanaryReadinessPlan:
    stages: tuple[CanaryStage, ...]
    automatic_promotion: bool = False
    canonical_cutover_authorized: bool = False
    shared_runtime_activation_authorized: bool = False
    production_live_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.stages:
            raise CanaryBoundaryError("canary design requires at least one stage")
        if any(not isinstance(stage, CanaryStage) for stage in self.stages):
            raise CanaryBoundaryError("canary stages must be CanaryStage instances")
        percentages = tuple(stage.observation_percent for stage in self.stages)
        if percentages != tuple(sorted(set(percentages))):
            raise CanaryBoundaryError("canary observation stages must be unique and increasing")
        if self.automatic_promotion:
            raise CanaryBoundaryError("automatic canary promotion is forbidden")
        if self.canonical_cutover_authorized:
            raise CanaryBoundaryError("P18.8 cannot authorize canonical cutover")
        if self.shared_runtime_activation_authorized:
            raise CanaryBoundaryError("P18.8 cannot activate shared runtime")
        if self.production_live_authorized:
            raise CanaryBoundaryError("P18.8 cannot authorize production/live")


def build_default_read_only_canary_plan() -> CanaryReadinessPlan:
    return CanaryReadinessPlan(
        stages=(CanaryStage(1), CanaryStage(5), CanaryStage(25), CanaryStage(100))
    )


@dataclass(frozen=True)
class P18_8ReadinessEvidence:
    reconciliation: ShadowReconciliationReport
    controls: Phase18ContractEvidence
    provider_gate: ProviderCostGate
    canary_plan: CanaryReadinessPlan
    owner_local_remains_canonical: bool = True
    shared_runtime_active: bool = False
    migration_033_created_or_authorized: bool = False
    production_live: bool = False
    factual_verification_authority: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.reconciliation, ShadowReconciliationReport):
            raise ShadowContractError("reconciliation evidence is required")
        if not isinstance(self.controls, Phase18ContractEvidence):
            raise ShadowContractError("Phase 18 control evidence is required")
        if not isinstance(self.provider_gate, ProviderCostGate):
            raise ShadowContractError("provider/cost gate evidence is required")
        if not isinstance(self.canary_plan, CanaryReadinessPlan):
            raise ShadowContractError("canary readiness plan is required")
        if not self.owner_local_remains_canonical:
            raise ShadowContractError("owner-local SQLite must remain canonical through P18.8")
        if self.shared_runtime_active:
            raise ShadowContractError("P18.8 validation cannot activate shared runtime")
        if self.migration_033_created_or_authorized:
            raise ShadowContractError("P18.8 cannot create or preauthorize migration 033")
        if self.production_live:
            raise ShadowContractError("P18.8 cannot authorize production/live")
        if not self.reconciliation.within_budget:
            raise ShadowContractError(
                "shadow mismatches exceed the explicit acceptance budget or include a fatal tenant/schema/invariant mismatch"
            )
        if not self.reconciliation.ready_for_read_only_canary_design:
            raise ShadowContractError("shadow reconciliation is not safe for read-only canary design")
        if not self.controls.contract_evidence_complete:
            raise ShadowContractError("required prior Phase 18 control evidence is incomplete")
        if not self.provider_gate.comparison_complete:
            raise ShadowContractError("provider/cost comparison gate is incomplete")
        if self.provider_gate.paid_provider_commitment_authorized:
            raise ShadowContractError("P18.8 readiness evidence cannot itself authorize paid commitment")

    @property
    def ready_for_p18_9_validation_matrix(self) -> bool:
        return True

    @property
    def real_infrastructure_observation_complete(self) -> bool:
        return all(
            state is InfrastructureObservationState.OBSERVED
            for state in (
                self.controls.network_tls,
                self.controls.datastore_reachability,
                self.controls.off_host_recovery,
                self.controls.provider_pitr,
            )
        )

    @property
    def canonical_storage_scope(self) -> StorageScope:
        return StorageScope.PROJECT_LOCAL_SQLITE
