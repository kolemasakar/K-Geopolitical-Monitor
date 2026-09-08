"""P18.9 Phase 18 validation matrix and activation-readiness contract.

This module composes provider-neutral evidence from P18.0-P18.8. It can prove
that the Phase 18 validation matrix is complete without claiming that a real
shared datastore, TLS boundary, off-host recovery path, provider, migration,
canary traffic, canonical cutover, or production activation exists.

``phase_matrix_validated`` is deliberately distinct from ``launch_eligible``.
P18.9 may validate the matrix while launch remains blocked by unobserved real
infrastructure and the separate owner launch/cutover decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .shared_runtime_contract import StorageScope
from .shared_runtime_shadow import InfrastructureObservationState


P18_0_GATE = "P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED"
P18_1_GATE = "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED"
P18_2_GATE = "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED"
P18_3_GATE = "P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED"
P18_4_GATE = "P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED"
P18_5_GATE = "P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED"
P18_6_GATE = "P18_6_SHARED_RUNTIME_SECURITY_CONTROLS_VALIDATED"
P18_7_GATE = "P18_7_SHARED_RUNTIME_BACKUP_DR_ROLLBACK_VALIDATED"
P18_8_GATE = "P18_8_NONPROD_SHADOW_CANARY_READINESS_VALIDATED"
P18_9_GATE = "PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED"
P13_TRUTH_AUTHORITY = "P13.5/P13.6"

REQUIRED_PHASE_18_GATES = (
    P18_0_GATE,
    P18_1_GATE,
    P18_2_GATE,
    P18_3_GATE,
    P18_4_GATE,
    P18_5_GATE,
    P18_6_GATE,
    P18_7_GATE,
    P18_8_GATE,
)


class ActivationReadinessError(RuntimeError):
    """Base fail-closed error for malformed P18.9 readiness evidence."""


class ReadinessDomain(str, Enum):
    TENANCY_RBAC = "tenancy_rbac"
    MIGRATION = "migration"
    CONCURRENCY_IDEMPOTENCY_OUTBOX = "concurrency_idempotency_outbox"
    SECURITY = "security"
    RECOVERY_ROLLBACK = "recovery_rollback"
    OWNER_LOCAL_COMPATIBILITY = "owner_local_compatibility"
    PROVIDER_COST = "provider_cost"
    CANARY = "canary"
    EPISTEMIC_BOUNDARY = "epistemic_boundary"


class ReadinessEvidenceState(str, Enum):
    PASS = "pass"
    NOT_APPLICABLE = "not_applicable"
    FAIL = "fail"


_REQUIRED_DOMAINS = frozenset(ReadinessDomain)
_CONDITIONAL_DOMAINS = frozenset(
    {ReadinessDomain.PROVIDER_COST, ReadinessDomain.CANARY}
)


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ActivationReadinessError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ActivationReadinessError(f"{field_name} is required")
    return normalized


@dataclass(frozen=True)
class ReadinessEvidence:
    """One explicit P18.9 validation-matrix finding."""

    domain: ReadinessDomain
    state: ReadinessEvidenceState
    evidence_id: str
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.domain, ReadinessDomain):
            raise ActivationReadinessError("readiness domain is invalid")
        if not isinstance(self.state, ReadinessEvidenceState):
            raise ActivationReadinessError("readiness evidence state is invalid")
        object.__setattr__(
            self,
            "evidence_id",
            _required_text(self.evidence_id, field_name="evidence_id"),
        )
        object.__setattr__(
            self,
            "detail",
            _required_text(self.detail, field_name="detail"),
        )
        if (
            self.state is ReadinessEvidenceState.NOT_APPLICABLE
            and self.domain not in _CONDITIONAL_DOMAINS
        ):
            raise ActivationReadinessError(
                f"{self.domain.value} is mandatory and cannot be not_applicable"
            )


@dataclass(frozen=True)
class Phase18GateEvidence:
    """Validated predecessor gates required before P18.9 can pass."""

    validated_gates: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized = tuple(
            _required_text(value, field_name="validated gate")
            for value in self.validated_gates
        )
        if len(set(normalized)) != len(normalized):
            raise ActivationReadinessError(
                "validated predecessor gates cannot contain duplicates"
            )
        object.__setattr__(self, "validated_gates", normalized)

    @property
    def missing_required_gates(self) -> tuple[str, ...]:
        present = set(self.validated_gates)
        return tuple(gate for gate in REQUIRED_PHASE_18_GATES if gate not in present)

    @property
    def complete(self) -> bool:
        return not self.missing_required_gates


@dataclass(frozen=True)
class LaunchInfrastructureEvidence:
    """Observed launch-time evidence; P18.9 never synthesizes these observations."""

    network_tls: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    datastore_private_reachability: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    off_host_recovery: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    provider_pitr: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED
    real_canary_traffic: InfrastructureObservationState = InfrastructureObservationState.NOT_OBSERVED

    def __post_init__(self) -> None:
        for field_name in (
            "network_tls",
            "datastore_private_reachability",
            "off_host_recovery",
            "provider_pitr",
            "real_canary_traffic",
        ):
            if not isinstance(getattr(self, field_name), InfrastructureObservationState):
                raise ActivationReadinessError(
                    f"{field_name} observation state is invalid"
                )

    @property
    def complete(self) -> bool:
        return not self.missing

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(
            name
            for name in (
                "network_tls",
                "datastore_private_reachability",
                "off_host_recovery",
                "provider_pitr",
                "real_canary_traffic",
            )
            if getattr(self, name) is not InfrastructureObservationState.OBSERVED
        )


@dataclass(frozen=True)
class ActivationBoundaryEvidence:
    """Strategic boundary P18.9 must preserve."""

    owner_local_storage_scope: StorageScope = StorageScope.PROJECT_LOCAL_SQLITE
    owner_local_remains_canonical: bool = True
    owner_local_independently_operable: bool = True
    shared_runtime_active: bool = False
    canonical_cutover_authorized: bool = False
    migration_033_created_or_preauthorized: bool = False
    production_live: bool = False
    owner_activation_decision: bool = False
    factual_verification_authority: str = P13_TRUTH_AUTHORITY

    def __post_init__(self) -> None:
        if self.owner_local_storage_scope is not StorageScope.PROJECT_LOCAL_SQLITE:
            raise ActivationReadinessError(
                "owner-local canonical storage must remain project-local SQLite"
            )
        if not self.owner_local_remains_canonical:
            raise ActivationReadinessError(
                "P18.9 cannot replace owner-local canonical storage"
            )
        if not self.owner_local_independently_operable:
            raise ActivationReadinessError(
                "owner-local runtime must remain independently operable"
            )
        if self.shared_runtime_active:
            raise ActivationReadinessError("P18.9 cannot activate shared runtime")
        if self.canonical_cutover_authorized:
            raise ActivationReadinessError("P18.9 cannot authorize canonical cutover")
        if self.migration_033_created_or_preauthorized:
            raise ActivationReadinessError(
                "P18.9 cannot create or preauthorize migration 033"
            )
        if self.production_live:
            raise ActivationReadinessError("P18.9 cannot authorize production/live")
        authority = _required_text(
            self.factual_verification_authority,
            field_name="factual_verification_authority",
        )
        if authority != P13_TRUTH_AUTHORITY:
            raise ActivationReadinessError(
                "P18.9 cannot change P13.5/P13.6 factual-verification authority"
            )
        object.__setattr__(self, "factual_verification_authority", authority)


@dataclass(frozen=True)
class Phase18ActivationReadinessResult:
    gate: str
    phase_matrix_validated: bool
    launch_eligible: bool
    missing_predecessor_gates: tuple[str, ...]
    failed_domains: tuple[ReadinessDomain, ...]
    missing_infrastructure_observations: tuple[str, ...]
    launch_blockers: tuple[str, ...]
    shared_runtime_active: bool = field(default=False, init=False)
    canonical_cutover_authorized: bool = field(default=False, init=False)
    migration_033_authorized: bool = field(default=False, init=False)
    production_live: bool = field(default=False, init=False)
    factual_verification_authority: str = field(
        default=P13_TRUTH_AUTHORITY,
        init=False,
    )


@dataclass(frozen=True)
class Phase18ActivationReadinessInput:
    predecessor_gates: Phase18GateEvidence
    matrix_evidence: tuple[ReadinessEvidence, ...]
    infrastructure: LaunchInfrastructureEvidence = LaunchInfrastructureEvidence()
    boundary: ActivationBoundaryEvidence = ActivationBoundaryEvidence()
    provider_selection_required: bool = False
    provider_owner_approval_present: bool = False
    staged_canary_separately_authorized: bool = False
    staged_canary_evidence_present: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.predecessor_gates, Phase18GateEvidence):
            raise ActivationReadinessError("predecessor gate evidence is required")
        if any(not isinstance(item, ReadinessEvidence) for item in self.matrix_evidence):
            raise ActivationReadinessError(
                "matrix evidence must contain ReadinessEvidence items"
            )
        if not isinstance(self.infrastructure, LaunchInfrastructureEvidence):
            raise ActivationReadinessError("launch infrastructure evidence is required")
        if not isinstance(self.boundary, ActivationBoundaryEvidence):
            raise ActivationReadinessError("activation boundary evidence is required")

        domains = tuple(item.domain for item in self.matrix_evidence)
        if len(set(domains)) != len(domains):
            raise ActivationReadinessError(
                "P18.9 matrix must contain exactly one finding per domain"
            )
        missing_domains = _REQUIRED_DOMAINS - set(domains)
        if missing_domains:
            raise ActivationReadinessError(
                "P18.9 matrix is incomplete; missing domains: "
                + ", ".join(sorted(domain.value for domain in missing_domains))
            )

        provider = _domain_item(self.matrix_evidence, ReadinessDomain.PROVIDER_COST)
        if self.provider_selection_required:
            if provider.state is not ReadinessEvidenceState.PASS:
                raise ActivationReadinessError(
                    "required provider/cost decision evidence must pass"
                )
            if not self.provider_owner_approval_present:
                raise ActivationReadinessError(
                    "provider selection requires separate owner approval evidence"
                )
        elif provider.state not in {
            ReadinessEvidenceState.PASS,
            ReadinessEvidenceState.NOT_APPLICABLE,
        }:
            raise ActivationReadinessError(
                "provider/cost evidence cannot fail in a validated matrix"
            )

        canary = _domain_item(self.matrix_evidence, ReadinessDomain.CANARY)
        if self.staged_canary_separately_authorized:
            if not self.staged_canary_evidence_present:
                raise ActivationReadinessError(
                    "authorized staged canary requires evidence"
                )
            if canary.state is not ReadinessEvidenceState.PASS:
                raise ActivationReadinessError(
                    "authorized staged canary evidence must pass"
                )
        elif canary.state not in {
            ReadinessEvidenceState.PASS,
            ReadinessEvidenceState.NOT_APPLICABLE,
        }:
            raise ActivationReadinessError(
                "non-authorized canary evidence cannot fail a validated matrix"
            )


def _domain_item(
    items: tuple[ReadinessEvidence, ...],
    domain: ReadinessDomain,
) -> ReadinessEvidence:
    return next(item for item in items if item.domain is domain)


def evaluate_phase18_activation_readiness(
    evidence: Phase18ActivationReadinessInput,
) -> Phase18ActivationReadinessResult:
    """Evaluate P18.9 matrix readiness while keeping launch authorization separate."""

    if not isinstance(evidence, Phase18ActivationReadinessInput):
        raise ActivationReadinessError("Phase18ActivationReadinessInput is required")

    failed_domains = tuple(
        item.domain
        for item in evidence.matrix_evidence
        if item.state is ReadinessEvidenceState.FAIL
    )
    missing_gates = evidence.predecessor_gates.missing_required_gates

    core_domains = _REQUIRED_DOMAINS - _CONDITIONAL_DOMAINS
    core_pass = all(
        _domain_item(evidence.matrix_evidence, domain).state
        is ReadinessEvidenceState.PASS
        for domain in core_domains
    )
    provider = _domain_item(evidence.matrix_evidence, ReadinessDomain.PROVIDER_COST)
    provider_ready = (
        provider.state is ReadinessEvidenceState.PASS
        if evidence.provider_selection_required
        else provider.state
        in {ReadinessEvidenceState.PASS, ReadinessEvidenceState.NOT_APPLICABLE}
    )
    canary = _domain_item(evidence.matrix_evidence, ReadinessDomain.CANARY)
    canary_ready = (
        canary.state is ReadinessEvidenceState.PASS
        and evidence.staged_canary_evidence_present
        if evidence.staged_canary_separately_authorized
        else canary.state
        in {ReadinessEvidenceState.PASS, ReadinessEvidenceState.NOT_APPLICABLE}
    )

    phase_matrix_validated = (
        not missing_gates
        and not failed_domains
        and core_pass
        and provider_ready
        and canary_ready
        and evidence.boundary.owner_local_remains_canonical
        and evidence.boundary.owner_local_independently_operable
        and not evidence.boundary.shared_runtime_active
        and not evidence.boundary.canonical_cutover_authorized
        and not evidence.boundary.migration_033_created_or_preauthorized
        and not evidence.boundary.production_live
    )

    launch_blockers: list[str] = []
    if not phase_matrix_validated:
        launch_blockers.append("phase_18_validation_matrix_incomplete")
    if not evidence.infrastructure.complete:
        launch_blockers.append("real_infrastructure_evidence_incomplete")
    if not evidence.boundary.owner_activation_decision:
        launch_blockers.append("explicit_owner_activation_decision_required")
    launch_blockers.append("fresh_launch_time_cutover_gate_required")

    # P18.9 is a readiness gate, not the launch gate. Its own boundary forbids
    # canonical-cutover authorization, so launch eligibility is always false.
    return Phase18ActivationReadinessResult(
        gate=P18_9_GATE,
        phase_matrix_validated=phase_matrix_validated,
        launch_eligible=False,
        missing_predecessor_gates=missing_gates,
        failed_domains=failed_domains,
        missing_infrastructure_observations=evidence.infrastructure.missing,
        launch_blockers=tuple(launch_blockers),
    )


def validated_predecessor_gate_evidence() -> Phase18GateEvidence:
    """Return the validated P18.0-P18.8 predecessor gate set."""

    return Phase18GateEvidence(validated_gates=REQUIRED_PHASE_18_GATES)


def build_provider_neutral_p18_9_matrix(
    *,
    provider_selection_required: bool = False,
    provider_owner_approval_present: bool = False,
    staged_canary_separately_authorized: bool = False,
    staged_canary_evidence_present: bool = False,
) -> tuple[ReadinessEvidence, ...]:
    """Build the canonical provider-neutral P18.9 contract-evidence matrix."""

    if provider_selection_required and not provider_owner_approval_present:
        provider_state = ReadinessEvidenceState.FAIL
    elif provider_selection_required:
        provider_state = ReadinessEvidenceState.PASS
    else:
        provider_state = ReadinessEvidenceState.NOT_APPLICABLE

    if staged_canary_separately_authorized and not staged_canary_evidence_present:
        canary_state = ReadinessEvidenceState.FAIL
    elif staged_canary_separately_authorized:
        canary_state = ReadinessEvidenceState.PASS
    else:
        canary_state = ReadinessEvidenceState.NOT_APPLICABLE

    return (
        ReadinessEvidence(
            ReadinessDomain.TENANCY_RBAC,
            ReadinessEvidenceState.PASS,
            "p18.1+p18.2-negative-matrix",
            "explicit tenant context, cross-tenant denial and deny-by-default RBAC validated",
        ),
        ReadinessEvidence(
            ReadinessDomain.MIGRATION,
            ReadinessEvidenceState.PASS,
            "p18.3-forward-rollback-contract",
            "provider-neutral forward/rollback contract validated; migration 033 remains unallocated",
        ),
        ReadinessEvidence(
            ReadinessDomain.CONCURRENCY_IDEMPOTENCY_OUTBOX,
            ReadinessEvidenceState.PASS,
            "p18.4+p18.5-concurrency-outbox",
            "tenant-scoped concurrency, idempotency, audit and transactional outbox contracts validated",
        ),
        ReadinessEvidence(
            ReadinessDomain.SECURITY,
            ReadinessEvidenceState.PASS,
            "p18.6-threat-matrix",
            "security/threat-model controls validated without inventing infrastructure observations",
        ),
        ReadinessEvidence(
            ReadinessDomain.RECOVERY_ROLLBACK,
            ReadinessEvidenceState.PASS,
            "p18.7-clean-restore-rollback",
            "clean-target restore, tenant safety, measured RPO/RTO and owner-local rollback validated",
        ),
        ReadinessEvidence(
            ReadinessDomain.OWNER_LOCAL_COMPATIBILITY,
            ReadinessEvidenceState.PASS,
            "owner-local-exact-regression",
            "owner-local SQLite remains canonical, independently operable and regression-tested",
        ),
        ReadinessEvidence(
            ReadinessDomain.PROVIDER_COST,
            provider_state,
            "p18.8-provider-cost-gate",
            (
                "separate owner-approved provider/cost evidence present"
                if provider_state is ReadinessEvidenceState.PASS
                else "provider selection/spend not requested; conditional evidence not applicable"
            ),
        ),
        ReadinessEvidence(
            ReadinessDomain.CANARY,
            canary_state,
            "p18.8-read-only-canary",
            (
                "separately authorized staged-canary evidence present"
                if canary_state is ReadinessEvidenceState.PASS
                else "staged canary not separately authorized; conditional evidence not applicable"
            ),
        ),
        ReadinessEvidence(
            ReadinessDomain.EPISTEMIC_BOUNDARY,
            ReadinessEvidenceState.PASS,
            "p13.5+p13.6-truth-authority",
            "readiness evidence cannot promote audit/delivery/publication state to factual truth",
        ),
    )
