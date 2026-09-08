from dataclasses import replace
from hashlib import sha256

import pytest

from kgeopolitical_monitor.shared_datastore_schema import (
    ExportManifestContract,
    build_p18_3_schema_contract,
)
from kgeopolitical_monitor.shared_runtime_contract import StorageScope, TenantContext
from kgeopolitical_monitor.shared_runtime_shadow import (
    CanaryBoundaryError,
    CanaryReadinessPlan,
    CanaryStage,
    ControlledShadowPackage,
    InfrastructureObservationState,
    MismatchKind,
    NonProductionShadowCandidate,
    P18_4_GATE,
    P18_6_GATE,
    P18_7_GATE,
    P18_8ReadinessEvidence,
    Phase18ContractEvidence,
    ProviderCostGate,
    ProviderCostOption,
    ProviderDecisionError,
    ShadowComparisonError,
    ShadowContractError,
    ShadowImportError,
    ShadowMismatchBudget,
    ShadowRecord,
    ShadowSnapshotEvidence,
    build_default_read_only_canary_plan,
    compare_shadow_snapshots,
    snapshot_from_records,
)


def _tenant(name: str = "alpha") -> TenantContext:
    return TenantContext(workspace_id=f"workspace-{name}", project_id=f"project-{name}")


def _records(tenant: TenantContext | None = None) -> tuple[ShadowRecord, ...]:
    tenant = tenant or _tenant()
    return (
        ShadowRecord.from_payload(
            tenant_context=tenant,
            table_name="shared_event",
            object_id="event-1",
            payload={"event_id": "event-1", "title": "Synthetic event"},
            semantic_projection={"event_id": "event-1", "meaning": "synthetic"},
        ),
        ShadowRecord.from_payload(
            tenant_context=tenant,
            table_name="shared_semantic_claim",
            object_id="claim-1",
            payload={"claim_id": "claim-1", "event_id": "event-1", "text": "Synthetic claim"},
            semantic_projection={"claim_id": "claim-1", "meaning": "synthetic-claim"},
        ),
    )


def _source_snapshot(
    tenant: TenantContext | None = None,
    records: tuple[ShadowRecord, ...] | None = None,
) -> ShadowSnapshotEvidence:
    tenant = tenant or _tenant()
    records = records or _records(tenant)
    return snapshot_from_records(
        tenant_context=tenant,
        schema_version=32,
        records=records,
    )


def _manifest(
    tenant: TenantContext | None = None,
    records: tuple[ShadowRecord, ...] | None = None,
) -> ExportManifestContract:
    tenant = tenant or _tenant()
    records = records or _records(tenant)
    snapshot = _source_snapshot(tenant, records)
    return ExportManifestContract(
        export_id="shadow-export-1",
        tenant_context=tenant,
        source_storage_scope=StorageScope.PROJECT_LOCAL_SQLITE,
        source_schema_version=32,
        source_database_sha256=sha256(b"synthetic-owner-local-db").hexdigest(),
        row_counts=snapshot.row_counts,
        table_checksums=snapshot.table_checksums,
    )


def _package(
    tenant: TenantContext | None = None,
    records: tuple[ShadowRecord, ...] | None = None,
) -> ControlledShadowPackage:
    tenant = tenant or _tenant()
    records = records or _records(tenant)
    return ControlledShadowPackage(
        manifest=_manifest(tenant, records),
        target_schema=build_p18_3_schema_contract(),
        records=records,
        source_snapshot=_source_snapshot(tenant, records),
    )


def _expected_target_snapshot(package: ControlledShadowPackage) -> ShadowSnapshotEvidence:
    return snapshot_from_records(
        tenant_context=package.manifest.tenant_context,
        schema_version=package.target_schema.schema_version,
        records=package.records,
    )


def _exact_reconciliation():
    package = _package()
    candidate = NonProductionShadowCandidate(
        tenant_context=package.manifest.tenant_context,
        target_schema=package.target_schema,
    )
    observed = candidate.load_controlled_package(package)
    return compare_shadow_snapshots(
        expected=_expected_target_snapshot(package),
        observed=observed,
    )


def _readiness(report=None, provider_gate=None):
    return P18_8ReadinessEvidence(
        reconciliation=report or _exact_reconciliation(),
        controls=Phase18ContractEvidence(),
        provider_gate=provider_gate or ProviderCostGate(),
        canary_plan=build_default_read_only_canary_plan(),
    )


def test_shadow_record_canonicalizes_payload_and_binds_digest():
    record = ShadowRecord.from_payload(
        tenant_context=_tenant(),
        table_name="shared_event",
        object_id="event-1",
        payload={"z": 2, "a": 1},
    )
    assert record.payload_json == '{"a":1,"z":2}'
    assert record.payload_sha256 == sha256(record.payload_json.encode()).hexdigest()


def test_shadow_record_rejects_noncanonical_payload_json():
    canonical = '{"a":1}'
    with pytest.raises(ShadowImportError, match="canonical JSON"):
        ShadowRecord(
            tenant_context=_tenant(),
            table_name="shared_event",
            object_id="event-1",
            payload_json='{ "a": 1 }',
            payload_sha256=sha256(canonical.encode()).hexdigest(),
            semantic_sha256=sha256(canonical.encode()).hexdigest(),
        )


def test_shadow_record_rejects_payload_digest_substitution():
    record = _records()[0]
    with pytest.raises(ShadowImportError, match="does not match"):
        replace(record, payload_sha256="0" * 64)


def test_snapshot_rejects_mixed_tenant_rows():
    records = (_records(_tenant("alpha"))[0], _records(_tenant("beta"))[0])
    with pytest.raises(ShadowImportError, match="mixed-tenant"):
        snapshot_from_records(tenant_context=_tenant("alpha"), schema_version=1, records=records)


def test_snapshot_rejects_duplicate_object_identity():
    record = _records()[0]
    with pytest.raises(ShadowImportError, match="duplicate shadow object identity"):
        snapshot_from_records(
            tenant_context=_tenant(),
            schema_version=1,
            records=(record, record),
        )


def test_source_snapshot_has_row_content_and_semantic_evidence():
    snapshot = _source_snapshot()
    assert dict(snapshot.row_counts) == {"shared_event": 1, "shared_semantic_claim": 1}
    assert set(dict(snapshot.table_checksums)) == {"shared_event", "shared_semantic_claim"}
    assert set(dict(snapshot.semantic_checksums)) == {"shared_event", "shared_semantic_claim"}


def test_controlled_package_requires_owner_local_provenance_and_no_activation():
    package = _package()
    assert package.manifest.source_storage_scope is StorageScope.PROJECT_LOCAL_SQLITE
    assert package.canonical_cutover_authorized is False
    assert package.shared_runtime_activation_authorized is False


def test_controlled_package_rejects_manifest_row_count_mismatch():
    package = _package()
    broken_manifest = replace(
        package.manifest,
        row_counts=(("shared_event", 99), ("shared_semantic_claim", 1)),
    )
    with pytest.raises(ShadowImportError, match="row counts"):
        ControlledShadowPackage(
            manifest=broken_manifest,
            target_schema=package.target_schema,
            records=package.records,
            source_snapshot=package.source_snapshot,
        )


def test_controlled_package_rejects_cross_tenant_snapshot():
    package = _package()
    other_records = _records(_tenant("beta"))
    other_snapshot = _source_snapshot(_tenant("beta"), other_records)
    with pytest.raises(ShadowImportError, match="tenant"):
        ControlledShadowPackage(
            manifest=package.manifest,
            target_schema=package.target_schema,
            records=package.records,
            source_snapshot=other_snapshot,
        )


def test_controlled_package_rejects_table_outside_approved_target_schema():
    tenant = _tenant()
    records = (
        ShadowRecord.from_payload(
            tenant_context=tenant,
            table_name="unapproved_shadow_table",
            object_id="row-1",
            payload={"id": "row-1"},
        ),
    )
    snapshot = _source_snapshot(tenant, records)
    manifest = _manifest(tenant, records)
    with pytest.raises(ShadowImportError, match="outside the approved target schema"):
        ControlledShadowPackage(
            manifest=manifest,
            target_schema=build_p18_3_schema_contract(),
            records=records,
            source_snapshot=snapshot,
        )


def test_candidate_is_nonproduction_read_only_provider_neutral_and_not_canonical():
    package = _package()
    candidate = NonProductionShadowCandidate(
        tenant_context=package.manifest.tenant_context,
        target_schema=package.target_schema,
    )
    assert candidate.environment == "non_production_contract_harness"
    assert candidate.read_only is True
    assert candidate.canonical is False
    assert candidate.production_live is False
    assert candidate.provider_id is None
    assert candidate.real_datastore_observed is False
    assert candidate.real_network_tls_observed is False
    assert candidate.canonical_cutover_authorized is False
    assert candidate.shared_runtime_activation_authorized is False
    assert not hasattr(candidate, "write")


def test_candidate_loads_once_and_supports_read_only_observation():
    package = _package()
    candidate = NonProductionShadowCandidate(
        tenant_context=package.manifest.tenant_context,
        target_schema=package.target_schema,
    )
    observed = candidate.load_controlled_package(package)
    assert observed.tenant_context == package.manifest.tenant_context
    assert observed.schema_version == package.target_schema.schema_version
    assert len(candidate.read_table("shared_event")) == 1
    with pytest.raises(ShadowImportError, match="overwrite"):
        candidate.load_controlled_package(package)


def test_candidate_rejects_cross_tenant_import():
    package = _package(_tenant("alpha"))
    candidate = NonProductionShadowCandidate(
        tenant_context=_tenant("beta"),
        target_schema=package.target_schema,
    )
    with pytest.raises(ShadowImportError, match="cross-tenant"):
        candidate.load_controlled_package(package)


def test_candidate_rejects_read_of_table_outside_schema():
    package = _package()
    candidate = NonProductionShadowCandidate(
        tenant_context=package.manifest.tenant_context,
        target_schema=package.target_schema,
    )
    candidate.load_controlled_package(package)
    with pytest.raises(ShadowComparisonError, match="outside the approved target schema"):
        candidate.read_table("unapproved_shadow_table")


def test_exact_shadow_reconciliation_passes_zero_budget():
    report = _exact_reconciliation()
    assert report.mismatches == ()
    assert report.exact_match is True
    assert report.within_budget is True
    assert report.ready_for_read_only_canary_design is True
    assert report.fatal_mismatch_present is False
    assert report.budgetable_mismatch_count == 0
    assert report.canonical_cutover_authorized is False
    assert report.shared_runtime_activation_authorized is False
    assert report.factual_verification_authority is False


def test_row_count_mismatch_fails_zero_budget_and_can_be_explicitly_bounded():
    expected = _expected_target_snapshot(_package())
    observed = replace(
        expected,
        row_counts=(("shared_event", 2), ("shared_semantic_claim", 1)),
    )
    strict = compare_shadow_snapshots(expected=expected, observed=observed)
    bounded = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=1),
    )
    assert strict.within_budget is False
    assert bounded.within_budget is True
    assert bounded.ready_for_read_only_canary_design is True
    assert bounded.exact_match is False
    assert bounded.budgetable_mismatch_count == 1
    assert any(item.kind is MismatchKind.ROW_COUNT for item in bounded.mismatches)


def test_content_and_semantic_mismatches_are_budgetable_but_explicit():
    expected = _expected_target_snapshot(_package())
    content = dict(expected.table_checksums)
    semantic = dict(expected.semantic_checksums)
    content["shared_event"] = "0" * 64
    semantic["shared_semantic_claim"] = "f" * 64
    observed = replace(
        expected,
        table_checksums=tuple(sorted(content.items())),
        semantic_checksums=tuple(sorted(semantic.items())),
    )
    report = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=2),
    )
    assert report.within_budget is True
    assert report.budgetable_mismatch_count == 2
    assert {item.kind for item in report.mismatches} == {
        MismatchKind.TABLE_CONTENT,
        MismatchKind.SEMANTIC_PROJECTION,
    }


@pytest.mark.parametrize("kind", ["tenant", "schema", "invariant"])
def test_tenant_schema_and_invariant_mismatches_are_fatal_regardless_of_budget(kind):
    expected = _expected_target_snapshot(_package())
    if kind == "tenant":
        observed = replace(expected, tenant_context=_tenant("beta"))
        expected_kind = MismatchKind.TENANT
    elif kind == "schema":
        observed = replace(expected, schema_version=expected.schema_version + 1)
        expected_kind = MismatchKind.SCHEMA
    else:
        observed = replace(expected, invariant_failures=("foreign-key-invariant",))
        expected_kind = MismatchKind.INVARIANT
    report = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=999),
    )
    assert any(item.kind is expected_kind for item in report.mismatches)
    assert report.fatal_mismatch_present is True
    assert report.within_budget is False
    assert report.ready_for_read_only_canary_design is False


def test_invariant_failure_is_fatal_even_when_present_on_both_snapshots():
    expected = replace(
        _expected_target_snapshot(_package()),
        invariant_failures=("tenant-policy-invariant",),
    )
    observed = replace(expected)
    report = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=999),
    )
    assert report.fatal_mismatch_present is True
    assert report.ready_for_read_only_canary_design is False


def test_negative_mismatch_budget_is_rejected():
    with pytest.raises(ShadowComparisonError, match="negative"):
        ShadowMismatchBudget(max_total_mismatches=-1)


def test_prior_phase_contract_evidence_is_explicit_without_fake_infrastructure():
    evidence = Phase18ContractEvidence()
    assert evidence.concurrency_gate == P18_4_GATE
    assert evidence.security_gate == P18_6_GATE
    assert evidence.recovery_gate == P18_7_GATE
    assert evidence.contract_evidence_complete is True
    assert evidence.real_infrastructure_observed is False
    assert evidence.network_tls is InfrastructureObservationState.NOT_OBSERVED
    assert evidence.datastore_reachability is InfrastructureObservationState.NOT_OBSERVED
    assert evidence.off_host_recovery is InfrastructureObservationState.NOT_OBSERVED
    assert evidence.provider_pitr is InfrastructureObservationState.NOT_OBSERVED


def test_wrong_prior_phase_gate_reference_fails_closed():
    with pytest.raises(ShadowContractError, match="P18.6"):
        Phase18ContractEvidence(security_gate="wrong-gate")


def test_provider_gate_stays_neutral_when_external_infrastructure_not_required():
    gate = ProviderCostGate()
    assert gate.external_infrastructure_required is False
    assert gate.comparison_complete is True
    assert gate.provider_selected is False
    assert gate.paid_provider_commitment_authorized is False


def test_external_infrastructure_requires_multiple_cost_options():
    one = ProviderCostOption(
        option_id="candidate-a",
        monthly_fixed_cost=10,
        variable_cost_basis="synthetic unit basis",
        security_summary="synthetic comparison metadata",
        exit_path="export and delete",
    )
    with pytest.raises(ProviderDecisionError, match="at least two"):
        ProviderCostGate(external_infrastructure_required=True, options=(one,))


def test_provider_selection_without_owner_approval_is_rejected():
    options = (
        ProviderCostOption("candidate-a", 10, "basis-a", "security-a", "exit-a"),
        ProviderCostOption("candidate-b", 20, "basis-b", "security-b", "exit-b"),
    )
    with pytest.raises(ProviderDecisionError, match="owner approval"):
        ProviderCostGate(
            external_infrastructure_required=True,
            options=options,
            selected_option_id="candidate-a",
        )


def test_paid_commitment_without_approved_selection_is_rejected():
    with pytest.raises(ProviderDecisionError, match="approved provider selection"):
        ProviderCostGate(paid_provider_commitment_authorized=True)


def test_default_canary_plan_is_read_only_staged_and_nonpromoting():
    plan = build_default_read_only_canary_plan()
    assert [stage.observation_percent for stage in plan.stages] == [1, 5, 25, 100]
    assert all(stage.read_only and not stage.writes_enabled for stage in plan.stages)
    assert plan.automatic_promotion is False
    assert plan.canonical_cutover_authorized is False
    assert plan.shared_runtime_activation_authorized is False
    assert plan.production_live_authorized is False


def test_write_enabled_canary_stage_is_rejected():
    with pytest.raises(CanaryBoundaryError, match="read-only"):
        CanaryStage(5, read_only=False, writes_enabled=True)


def test_automatic_canary_promotion_is_rejected():
    with pytest.raises(CanaryBoundaryError, match="automatic"):
        CanaryReadinessPlan(stages=(CanaryStage(5),), automatic_promotion=True)


def test_canary_cutover_activation_or_production_is_rejected():
    with pytest.raises(CanaryBoundaryError, match="cutover"):
        CanaryReadinessPlan(stages=(CanaryStage(5),), canonical_cutover_authorized=True)
    with pytest.raises(CanaryBoundaryError, match="activate"):
        CanaryReadinessPlan(stages=(CanaryStage(5),), shared_runtime_activation_authorized=True)
    with pytest.raises(CanaryBoundaryError, match="production/live"):
        CanaryReadinessPlan(stages=(CanaryStage(5),), production_live_authorized=True)


def test_p18_8_readiness_is_contract_ready_without_fabricating_real_infrastructure():
    evidence = _readiness()
    assert evidence.ready_for_p18_9_validation_matrix is True
    assert evidence.real_infrastructure_observation_complete is False
    assert evidence.owner_local_remains_canonical is True
    assert evidence.canonical_storage_scope is StorageScope.PROJECT_LOCAL_SQLITE
    assert evidence.shared_runtime_active is False
    assert evidence.migration_033_created_or_authorized is False
    assert evidence.production_live is False
    assert evidence.factual_verification_authority is False


def test_p18_8_readiness_accepts_only_bounded_nonfatal_mismatch():
    expected = _expected_target_snapshot(_package())
    observed = replace(
        expected,
        row_counts=(("shared_event", 2), ("shared_semantic_claim", 1)),
    )
    report = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=1),
    )
    assert _readiness(report=report).ready_for_p18_9_validation_matrix is True


def test_p18_8_readiness_rejects_fatal_schema_mismatch_even_with_large_budget():
    expected = _expected_target_snapshot(_package())
    observed = replace(expected, schema_version=expected.schema_version + 1)
    report = compare_shadow_snapshots(
        expected=expected,
        observed=observed,
        budget=ShadowMismatchBudget(max_total_mismatches=999),
    )
    with pytest.raises(ShadowContractError, match="fatal tenant/schema/invariant"):
        _readiness(report=report)


def test_p18_8_readiness_cannot_create_migration_033_or_activate_shared_runtime():
    kwargs = dict(
        reconciliation=_exact_reconciliation(),
        controls=Phase18ContractEvidence(),
        provider_gate=ProviderCostGate(),
        canary_plan=build_default_read_only_canary_plan(),
    )
    with pytest.raises(ShadowContractError, match="migration 033"):
        P18_8ReadinessEvidence(**kwargs, migration_033_created_or_authorized=True)
    with pytest.raises(ShadowContractError, match="activate shared runtime"):
        P18_8ReadinessEvidence(**kwargs, shared_runtime_active=True)


def test_p18_8_readiness_cannot_change_owner_local_canonical_or_production_status():
    kwargs = dict(
        reconciliation=_exact_reconciliation(),
        controls=Phase18ContractEvidence(),
        provider_gate=ProviderCostGate(),
        canary_plan=build_default_read_only_canary_plan(),
    )
    with pytest.raises(ShadowContractError, match="owner-local SQLite"):
        P18_8ReadinessEvidence(**kwargs, owner_local_remains_canonical=False)
    with pytest.raises(ShadowContractError, match="production/live"):
        P18_8ReadinessEvidence(**kwargs, production_live=True)


def test_p18_8_readiness_cannot_itself_authorize_paid_provider_commitment():
    options = (
        ProviderCostOption("candidate-a", 10, "basis-a", "security-a", "exit-a"),
        ProviderCostOption("candidate-b", 20, "basis-b", "security-b", "exit-b"),
    )
    approved_gate = ProviderCostGate(
        external_infrastructure_required=True,
        options=options,
        selected_option_id="candidate-a",
        owner_approval_id="synthetic-owner-approval-evidence",
        paid_provider_commitment_authorized=True,
    )
    with pytest.raises(ShadowContractError, match="paid commitment"):
        _readiness(provider_gate=approved_gate)
