from dataclasses import replace
from datetime import timedelta

import pytest

from kgeopolitical_monitor.rbac_authorization import effective_permissions
from kgeopolitical_monitor.shared_datastore_schema import (
    build_p18_3_schema_contract,
    validate_shared_schema_contract,
)
from kgeopolitical_monitor.shared_repository_concurrency import (
    InMemorySharedRepositoryHarness,
    TenantScopedSharedRepository,
)
from kgeopolitical_monitor.shared_runtime_activation_readiness import (
    ActivationBoundaryEvidence,
    ActivationReadinessError,
    LaunchInfrastructureEvidence,
    P18_8_GATE,
    P18_9_GATE,
    REQUIRED_PHASE_18_GATES,
    Phase18ActivationReadinessInput,
    Phase18GateEvidence,
    ReadinessDomain,
    ReadinessEvidence,
    ReadinessEvidenceState,
    build_provider_neutral_p18_9_matrix,
    evaluate_phase18_activation_readiness,
    validated_predecessor_gate_evidence,
)
from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext
from kgeopolitical_monitor.shared_runtime_recovery import build_p18_7_recovery_plan_contract
from kgeopolitical_monitor.shared_runtime_security import SharedRuntimeSecurityPolicy
from kgeopolitical_monitor.shared_runtime_shadow import (
    InfrastructureObservationState,
    NonProductionShadowCandidate,
)


class EmptyBindingResolver:
    def bindings_for(self, principal):
        return ()


def _input(**overrides):
    values = {
        "predecessor_gates": validated_predecessor_gate_evidence(),
        "matrix_evidence": build_provider_neutral_p18_9_matrix(),
    }
    values.update(overrides)
    return Phase18ActivationReadinessInput(**values)


def _matrix_with(domain: ReadinessDomain, state: ReadinessEvidenceState):
    return tuple(
        replace(item, state=state) if item.domain is domain else item
        for item in build_provider_neutral_p18_9_matrix()
    )


def test_p18_9_provider_neutral_matrix_validates_without_claiming_launch():
    result = evaluate_phase18_activation_readiness(_input())

    assert result.gate == P18_9_GATE
    assert result.phase_matrix_validated is True
    assert result.launch_eligible is False
    assert result.missing_predecessor_gates == ()
    assert result.failed_domains == ()
    assert result.shared_runtime_active is False
    assert result.canonical_cutover_authorized is False
    assert result.migration_033_authorized is False
    assert result.production_live is False
    assert result.factual_verification_authority == "P13.5/P13.6"


def test_p18_9_default_real_infrastructure_observations_remain_fail_closed():
    result = evaluate_phase18_activation_readiness(_input())

    assert set(result.missing_infrastructure_observations) == {
        "network_tls",
        "datastore_private_reachability",
        "off_host_recovery",
        "provider_pitr",
        "real_canary_traffic",
    }
    assert "real_infrastructure_evidence_incomplete" in result.launch_blockers
    assert "explicit_owner_activation_decision_required" in result.launch_blockers
    assert "fresh_launch_time_cutover_gate_required" in result.launch_blockers


def test_p18_9_requires_every_predecessor_gate_through_p18_8():
    assert REQUIRED_PHASE_18_GATES[-1] == P18_8_GATE
    missing = Phase18GateEvidence(validated_gates=REQUIRED_PHASE_18_GATES[:-1])
    result = evaluate_phase18_activation_readiness(_input(predecessor_gates=missing))

    assert result.phase_matrix_validated is False
    assert result.missing_predecessor_gates == (P18_8_GATE,)
    assert "phase_18_validation_matrix_incomplete" in result.launch_blockers


def test_duplicate_predecessor_gate_evidence_fails_closed():
    with pytest.raises(ActivationReadinessError, match="duplicates"):
        Phase18GateEvidence(validated_gates=(P18_8_GATE, P18_8_GATE))


def test_mandatory_readiness_domain_failure_blocks_matrix():
    matrix = _matrix_with(ReadinessDomain.SECURITY, ReadinessEvidenceState.FAIL)
    result = evaluate_phase18_activation_readiness(_input(matrix_evidence=matrix))

    assert result.phase_matrix_validated is False
    assert result.failed_domains == (ReadinessDomain.SECURITY,)
    assert result.launch_eligible is False


def test_mandatory_domain_cannot_be_marked_not_applicable():
    with pytest.raises(ActivationReadinessError, match="mandatory"):
        ReadinessEvidence(
            ReadinessDomain.RECOVERY_ROLLBACK,
            ReadinessEvidenceState.NOT_APPLICABLE,
            "bad-evidence",
            "mandatory control cannot disappear",
        )


def test_matrix_rejects_missing_domain():
    matrix = tuple(
        item
        for item in build_provider_neutral_p18_9_matrix()
        if item.domain is not ReadinessDomain.EPISTEMIC_BOUNDARY
    )
    with pytest.raises(ActivationReadinessError, match="missing domains"):
        _input(matrix_evidence=matrix)


def test_matrix_rejects_duplicate_domain():
    matrix = build_provider_neutral_p18_9_matrix()
    with pytest.raises(ActivationReadinessError, match="exactly one"):
        _input(matrix_evidence=(*matrix, matrix[0]))


def test_provider_cost_evidence_is_conditional_when_no_provider_selected():
    matrix = build_provider_neutral_p18_9_matrix()
    provider = next(item for item in matrix if item.domain is ReadinessDomain.PROVIDER_COST)
    assert provider.state is ReadinessEvidenceState.NOT_APPLICABLE
    assert evaluate_phase18_activation_readiness(_input(matrix_evidence=matrix)).phase_matrix_validated


def test_provider_selection_requires_separate_owner_approval_evidence():
    matrix = build_provider_neutral_p18_9_matrix(
        provider_selection_required=True,
        provider_owner_approval_present=False,
    )
    with pytest.raises(ActivationReadinessError, match="provider/cost"):
        _input(
            matrix_evidence=matrix,
            provider_selection_required=True,
            provider_owner_approval_present=False,
        )


def test_provider_selection_can_be_evidence_complete_without_launching_runtime():
    matrix = build_provider_neutral_p18_9_matrix(
        provider_selection_required=True,
        provider_owner_approval_present=True,
    )
    result = evaluate_phase18_activation_readiness(
        _input(
            matrix_evidence=matrix,
            provider_selection_required=True,
            provider_owner_approval_present=True,
        )
    )
    assert result.phase_matrix_validated is True
    assert result.launch_eligible is False


def test_canary_evidence_is_conditional_without_separate_authorization():
    matrix = build_provider_neutral_p18_9_matrix()
    canary = next(item for item in matrix if item.domain is ReadinessDomain.CANARY)
    assert canary.state is ReadinessEvidenceState.NOT_APPLICABLE


def test_authorized_canary_without_evidence_fails_closed():
    matrix = build_provider_neutral_p18_9_matrix(
        staged_canary_separately_authorized=True,
        staged_canary_evidence_present=False,
    )
    with pytest.raises(ActivationReadinessError, match="canary"):
        _input(
            matrix_evidence=matrix,
            staged_canary_separately_authorized=True,
            staged_canary_evidence_present=False,
        )


def test_authorized_canary_with_evidence_still_does_not_authorize_launch():
    matrix = build_provider_neutral_p18_9_matrix(
        staged_canary_separately_authorized=True,
        staged_canary_evidence_present=True,
    )
    result = evaluate_phase18_activation_readiness(
        _input(
            matrix_evidence=matrix,
            staged_canary_separately_authorized=True,
            staged_canary_evidence_present=True,
        )
    )
    assert result.phase_matrix_validated is True
    assert result.launch_eligible is False


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"owner_local_remains_canonical": False}, "canonical storage"),
        ({"owner_local_independently_operable": False}, "independently operable"),
        ({"shared_runtime_active": True}, "activate shared runtime"),
        ({"canonical_cutover_authorized": True}, "canonical cutover"),
        ({"migration_033_created_or_preauthorized": True}, "migration 033"),
        ({"production_live": True}, "production/live"),
        ({"factual_verification_authority": "P18.9"}, "P13.5/P13.6"),
    ],
)
def test_p18_9_activation_boundary_rejects_scope_escape(kwargs, expected):
    with pytest.raises(ActivationReadinessError, match=expected):
        ActivationBoundaryEvidence(**kwargs)


def test_p18_9_rejects_shared_storage_as_owner_local_canonical_scope():
    with pytest.raises(ActivationReadinessError, match="project-local SQLite"):
        ActivationBoundaryEvidence(
            owner_local_storage_scope=StorageScope.SHARED_CANONICAL,
        )


def test_even_fully_observed_infrastructure_and_owner_decision_cannot_launch_inside_p18_9():
    infrastructure = LaunchInfrastructureEvidence(
        network_tls=InfrastructureObservationState.OBSERVED,
        datastore_private_reachability=InfrastructureObservationState.OBSERVED,
        off_host_recovery=InfrastructureObservationState.OBSERVED,
        provider_pitr=InfrastructureObservationState.OBSERVED,
        real_canary_traffic=InfrastructureObservationState.OBSERVED,
    )
    boundary = ActivationBoundaryEvidence(owner_activation_decision=True)
    result = evaluate_phase18_activation_readiness(
        _input(infrastructure=infrastructure, boundary=boundary)
    )

    assert result.phase_matrix_validated is True
    assert result.missing_infrastructure_observations == ()
    assert result.launch_eligible is False
    assert "fresh_launch_time_cutover_gate_required" in result.launch_blockers
    assert "explicit_owner_activation_decision_required" not in result.launch_blockers


def test_p18_9_composes_representative_prior_phase_contracts_without_external_infrastructure():
    tenant = TenantContext("workspace-p18", "project-p18")

    # P18.2: absent RBAC binding is deny-by-default.
    assert effective_permissions(
        principal=None,
        tenant_context=tenant,
        resolver=EmptyBindingResolver(),
    ) == frozenset()

    # P18.3: the modeled shared schema is provider-neutral and validates.
    schema = build_p18_3_schema_contract()
    assert validate_shared_schema_contract(schema) is schema
    assert schema.provider_id is None

    # P18.4: the repository remains a provider-neutral in-memory contract harness.
    repo = InMemorySharedRepositoryHarness()
    assert isinstance(repo, TenantScopedSharedRepository)
    assert repo.provider_id is None
    assert repo.contract_only is True

    # P18.6: security policy is contract-only, HTTPS/private-datastore by construction.
    security = SharedRuntimeSecurityPolicy(
        application_base_url="https://shared.example.test",
        allowed_egress_hosts=("api.example.test",),
        max_request_bytes=1024,
        max_page_size=100,
        max_requests_per_window=2,
        rate_window=timedelta(minutes=1),
    )
    assert security.contract_only is True
    assert security.network_reachability_observed is False
    assert security.datastore_public_ingress is False

    # P18.7: recovery is provider-neutral and cannot allocate migration 033/cutover.
    recovery = build_p18_7_recovery_plan_contract()
    assert recovery.provider_id is None
    assert recovery.migration_033_authorized is False
    assert recovery.shared_runtime_active is False
    assert recovery.canonical_cutover_authorized is False

    # P18.8: the shadow candidate is read-only/non-canonical/non-production.
    candidate = NonProductionShadowCandidate(
        tenant_context=tenant,
        target_schema=schema,
    )
    assert candidate.read_only is True
    assert candidate.canonical is False
    assert candidate.production_live is False
    assert candidate.provider_id is None
    assert candidate.real_datastore_observed is False
    assert candidate.real_network_tls_observed is False

    result = evaluate_phase18_activation_readiness(_input())
    assert result.phase_matrix_validated is True
    assert result.launch_eligible is False
