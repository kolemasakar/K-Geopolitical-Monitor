import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.identity_tenant_context import (
    HumanIdentity,
    IdentityKind,
    ServiceIdentity,
)
from kgeopolitical_monitor.rbac_authorization import (
    AccessDeniedError,
    Permission,
    Role,
    RoleBinding,
)
from kgeopolitical_monitor.shared_audit_outbox import (
    InMemoryAuditedOutboxRepositoryHarness,
    InMemoryIdempotentSideEffectConsumerHarness,
    MutationAuditMetadata,
    OutboxMessageNotFoundError,
    OutboxState,
    SecurityMutationAuditRecord,
    SideEffectDeliveryConflictError,
    SideEffectIntent,
    SideEffectKind,
    TransactionalOutboxMessage,
)
from kgeopolitical_monitor.shared_repository_concurrency import (
    IdempotencyConflictError,
    VersionConflictError,
    WriteCommand,
)
from kgeopolitical_monitor.shared_runtime_contract import TenantContext


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


class BindingResolver:
    def __init__(self, *bindings: RoleBinding):
        self.bindings = bindings

    def bindings_for(self, principal):
        return self.bindings


def now() -> datetime:
    return datetime(2026, 9, 7, 18, 0, tzinfo=timezone.utc)


def human(subject: str = "human-owner") -> HumanIdentity:
    issued = now() - timedelta(minutes=5)
    return HumanIdentity(
        subject_id=subject,
        issuer="test-issuer",
        session_id=f"session-{subject}",
        issued_at=issued,
        expires_at=issued + timedelta(minutes=30),
    )


def service(service_id: str = "outbox-worker") -> ServiceIdentity:
    issued = now() - timedelta(minutes=5)
    return ServiceIdentity(
        service_id=service_id,
        issuer="test-issuer",
        session_id=f"session-{service_id}",
        issued_at=issued,
        expires_at=issued + timedelta(minutes=30),
    )


def context(workspace: str = "workspace-a", project: str = "project-1") -> TenantContext:
    return TenantContext(workspace_id=workspace, project_id=project)


def human_binding(
    principal: HumanIdentity,
    *,
    workspace: str = "workspace-a",
    project: str | None = None,
    role: Role = Role.OWNER,
) -> RoleBinding:
    return RoleBinding(
        identity_kind=IdentityKind.HUMAN,
        principal_id=principal.principal_id,
        workspace_id=workspace,
        project_id=project,
        role=role,
    )


def service_binding(
    principal: ServiceIdentity,
    *,
    workspace: str = "workspace-a",
    project: str = "project-1",
) -> RoleBinding:
    return RoleBinding(
        identity_kind=IdentityKind.SERVICE,
        principal_id=principal.principal_id,
        workspace_id=workspace,
        project_id=project,
        role=Role.SERVICE,
        service_permissions=(Permission.SERVICE_EXECUTE,),
    )


def command(
    *,
    object_id: str = "obj-1",
    payload=None,
    key: str = "idem-1",
    expected: int = 0,
) -> WriteCommand:
    return WriteCommand(
        object_type="event",
        object_id=object_id,
        payload={"value": 1} if payload is None else payload,
        idempotency_key=key,
        expected_version=expected,
    )


def metadata(
    *,
    action: str = "event.update",
    correlation_id: str = "corr-1",
    request_id: str = "req-1",
) -> MutationAuditMetadata:
    return MutationAuditMetadata(
        action=action,
        correlation_id=correlation_id,
        request_id=request_id,
        occurred_at=now(),
        causation_id="cause-1",
    )


def intent(
    *,
    kind: SideEffectKind = SideEffectKind.DELIVERY,
    payload=None,
    destination: str = "public-safe-target-1",
) -> SideEffectIntent:
    return SideEffectIntent(
        kind=kind,
        channel="provider-neutral-test",
        destination_ref=destination,
        payload={"summary": "safe"} if payload is None else payload,
    )


def owner_repo(
    repo=None,
    *,
    subject: str = "human-owner",
    workspace: str = "workspace-a",
    project: str = "project-1",
):
    principal = human(subject)
    resolver = BindingResolver(
        human_binding(principal, workspace=workspace, project=None, role=Role.OWNER)
    )
    return principal, resolver, repo or InMemoryAuditedOutboxRepositoryHarness()


def test_p18_5_harness_is_provider_neutral_contract_only():
    repo = InMemoryAuditedOutboxRepositoryHarness()
    consumer = InMemoryIdempotentSideEffectConsumerHarness()
    assert repo.provider_id is None
    assert repo.persistent is False
    assert repo.contract_only is True
    assert consumer.provider_id is None
    assert consumer.persistent is False
    assert consumer.contract_only is True
    assert repo.contract_counts() == (0, 0, 0, 0)


def test_canonical_mutation_always_appends_security_audit_record():
    principal, resolver, repo = owner_repo()
    result = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    audits = repo.list_audit_records(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
    )
    assert result.record.version == 1
    assert repo.contract_counts() == (1, 1, 1, 0)
    assert len(audits) == 1
    audit = audits[0]
    assert audit.actor_kind is IdentityKind.HUMAN
    assert audit.actor_id == principal.principal_id
    assert audit.actor_session_id == principal.session_id
    assert audit.action == "event.update"
    assert audit.object_type == "event"
    assert audit.object_id == "obj-1"
    assert audit.object_version == 1
    assert audit.command_fingerprint == command().fingerprint
    assert audit.correlation_id == "corr-1"
    assert audit.request_id == "req-1"
    assert audit.factual_verification_authority is False


def test_canonical_mutation_and_outbox_intent_commit_together():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    messages = repo.list_outbox_messages(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
    )
    assert repo.contract_counts() == (1, 1, 1, 1)
    assert len(messages) == 1
    message = messages[0]
    assert message.state is OutboxState.PENDING
    assert message.object_id == "obj-1"
    assert message.object_version == 1
    assert message.kind is SideEffectKind.DELIVERY
    assert message.payload == {"summary": "safe"}
    assert message.factual_verification_authority is False


def test_process_failure_before_commit_cannot_diverge_canonical_audit_or_outbox():
    def fail():
        raise RuntimeError("simulated pre-commit process failure")

    repo = InMemoryAuditedOutboxRepositoryHarness(before_commit_hook=fail)
    principal, resolver, _ = owner_repo(repo)
    with pytest.raises(RuntimeError, match="pre-commit"):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(),
            audit_metadata=metadata(),
            side_effect=intent(),
        )
    assert repo.contract_counts() == (0, 0, 0, 0)


def test_version_conflict_publishes_no_new_audit_or_outbox():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    with pytest.raises(VersionConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(key="idem-stale", expected=0, payload={"value": 2}),
            audit_metadata=metadata(request_id="req-stale"),
            side_effect=intent(),
        )
    assert repo.contract_counts() == (1, 1, 1, 0)


def test_exact_retry_replays_without_duplicate_audit_or_outbox():
    principal, resolver, repo = owner_repo()
    cmd = command()
    first = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=cmd,
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    replay = repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=cmd,
        audit_metadata=metadata(request_id="req-retry"),
        side_effect=intent(),
    )
    assert first.replayed is False
    assert replay.replayed is True
    assert replay.record.version == 1
    assert repo.contract_counts() == (1, 1, 1, 1)


def test_retry_key_cannot_change_side_effect_intent():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(payload={"summary": "one"}),
    )
    with pytest.raises(IdempotencyConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(),
            audit_metadata=metadata(request_id="req-2"),
            side_effect=intent(payload={"summary": "two"}),
        )
    assert repo.contract_counts() == (1, 1, 1, 1)


def test_retry_key_cannot_change_audit_action_or_actor():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(action="event.update"),
    )
    with pytest.raises(IdempotencyConflictError):
        repo.write(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            command=command(),
            audit_metadata=metadata(action="event.publish", request_id="req-2"),
        )

    other = human("other-owner")
    other_resolver = BindingResolver(human_binding(other))
    with pytest.raises(IdempotencyConflictError):
        repo.write(
            principal=other,
            tenant_context=context(),
            role_bindings=other_resolver,
            command=command(),
            audit_metadata=metadata(request_id="req-3"),
        )
    assert repo.contract_counts() == (1, 1, 1, 0)


def test_same_retry_key_in_distinct_tenants_remains_isolated():
    repo = InMemoryAuditedOutboxRepositoryHarness()
    principal = human()
    resolver = BindingResolver(
        human_binding(principal, workspace="workspace-a"),
        human_binding(principal, workspace="workspace-b"),
    )
    for workspace in ("workspace-a", "workspace-b"):
        repo.write(
            principal=principal,
            tenant_context=context(workspace, "project-1"),
            role_bindings=resolver,
            command=command(key="same-key"),
            audit_metadata=metadata(correlation_id=f"corr-{workspace}"),
            side_effect=intent(destination=f"target-{workspace}"),
        )
    assert repo.contract_counts() == (2, 2, 2, 2)


def test_audit_and_outbox_reads_are_exact_tenant_scoped():
    repo = InMemoryAuditedOutboxRepositoryHarness()
    principal = human()
    resolver = BindingResolver(
        human_binding(principal, workspace="workspace-a"),
        human_binding(principal, workspace="workspace-b"),
    )
    repo.write(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
        command=command(object_id="a", key="a"),
        audit_metadata=metadata(correlation_id="corr-a"),
        side_effect=intent(destination="target-a"),
    )
    repo.write(
        principal=principal,
        tenant_context=context("workspace-b", "project-1"),
        role_bindings=resolver,
        command=command(object_id="b", key="b"),
        audit_metadata=metadata(correlation_id="corr-b"),
        side_effect=intent(destination="target-b"),
    )
    a_audits = repo.list_audit_records(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
    )
    a_outbox = repo.list_outbox_messages(
        principal=principal,
        tenant_context=context("workspace-a", "project-1"),
        role_bindings=resolver,
    )
    assert [record.object_id for record in a_audits] == ["a"]
    assert [message.object_id for message in a_outbox] == ["a"]


def test_audit_records_are_frozen_append_only_values():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
    )
    audit = repo.list_audit_records(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
    )[0]
    assert isinstance(audit, SecurityMutationAuditRecord)
    with pytest.raises(FrozenInstanceError):
        audit.action = "tampered"


def test_side_effect_intent_snapshots_payload_before_caller_mutation():
    payload = {"nested": {"value": 1}}
    item = intent(payload=payload)
    fingerprint = item.fingerprint
    payload["nested"]["value"] = 999
    assert json.loads(item.payload_json) == {"nested": {"value": 1}}
    assert item.fingerprint == fingerprint


def test_dispatch_requires_explicit_service_execute_scope():
    principal, resolver, repo = owner_repo()
    repo.write(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    outbox_id = repo.list_outbox_messages(
        principal=principal,
        tenant_context=context(),
        role_bindings=resolver,
    )[0].outbox_id
    with pytest.raises(AccessDeniedError):
        repo.dispatch_outbox_message(
            principal=principal,
            tenant_context=context(),
            role_bindings=resolver,
            outbox_id=outbox_id,
            consumer=InMemoryIdempotentSideEffectConsumerHarness(),
        )


def test_successful_dispatch_performs_one_effect_and_marks_delivered():
    owner, owner_resolver, repo = owner_repo()
    repo.write(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    message = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    worker = service()
    worker_resolver = BindingResolver(service_binding(worker))
    consumer = InMemoryIdempotentSideEffectConsumerHarness()
    receipt = repo.dispatch_outbox_message(
        principal=worker,
        tenant_context=context(),
        role_bindings=worker_resolver,
        outbox_id=message.outbox_id,
        consumer=consumer,
    )
    assert receipt.replayed is False
    assert receipt.factual_verification_authority is False
    assert consumer.effect_count == 1
    delivered = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    assert delivered.state is OutboxState.DELIVERED
    assert delivered.delivered_receipt_ref == receipt.receipt_ref


def test_post_effect_process_failure_retries_without_duplicate_external_effect():
    owner, owner_resolver, repo = owner_repo()
    repo.write(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    message = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    worker = service()
    worker_resolver = BindingResolver(service_binding(worker))
    consumer = InMemoryIdempotentSideEffectConsumerHarness()

    def fail_after_effect():
        raise RuntimeError("simulated process loss after external effect")

    with pytest.raises(RuntimeError, match="after external effect"):
        repo.dispatch_outbox_message(
            principal=worker,
            tenant_context=context(),
            role_bindings=worker_resolver,
            outbox_id=message.outbox_id,
            consumer=consumer,
            after_consumer_hook=fail_after_effect,
        )
    assert consumer.effect_count == 1

    still_pending = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    assert still_pending.state is OutboxState.PENDING

    replay = repo.dispatch_outbox_message(
        principal=worker,
        tenant_context=context(),
        role_bindings=worker_resolver,
        outbox_id=message.outbox_id,
        consumer=consumer,
    )
    assert replay.replayed is True
    assert consumer.effect_count == 1
    delivered = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    assert delivered.state is OutboxState.DELIVERED


def test_concurrent_dispatchers_share_stable_delivery_key_and_do_not_duplicate_effect():
    owner, owner_resolver, repo = owner_repo()
    repo.write(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    message = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    worker = service()
    worker_resolver = BindingResolver(service_binding(worker))
    consumer = InMemoryIdempotentSideEffectConsumerHarness()

    def dispatch(_):
        return repo.dispatch_outbox_message(
            principal=worker,
            tenant_context=context(),
            role_bindings=worker_resolver,
            outbox_id=message.outbox_id,
            consumer=consumer,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(dispatch, (1, 2)))

    assert consumer.effect_count == 1
    assert {receipt.receipt_ref for receipt in receipts} == {receipts[0].receipt_ref}
    assert any(receipt.replayed for receipt in receipts)


def test_dispatch_cannot_cross_tenant_scope_even_with_valid_worker_elsewhere():
    owner, owner_resolver, repo = owner_repo()
    repo.write(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(),
    )
    message = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    worker = service()
    other_resolver = BindingResolver(
        service_binding(worker, workspace="workspace-b", project="project-1")
    )
    with pytest.raises(OutboxMessageNotFoundError):
        repo.dispatch_outbox_message(
            principal=worker,
            tenant_context=context("workspace-b", "project-1"),
            role_bindings=other_resolver,
            outbox_id=message.outbox_id,
            consumer=InMemoryIdempotentSideEffectConsumerHarness(),
        )


def test_consumer_rejects_same_delivery_key_with_different_content():
    context_value = context()
    message = TransactionalOutboxMessage(
        outbox_id="outbox-1",
        tenant_context=context_value,
        kind=SideEffectKind.DELIVERY,
        channel="test",
        destination_ref="target",
        payload_json='{"value":1}',
        payload_fingerprint="48208f9428d64634bd8e28ff345bf0eab60d53c18fa2fbdb0b9bc1e84df2b5f6",
        delivery_idempotency_key="stable-key",
        object_type="event",
        object_id="obj-1",
        object_version=1,
        correlation_id="corr",
        created_at=now(),
    )
    changed = TransactionalOutboxMessage(
        outbox_id="outbox-2",
        tenant_context=context_value,
        kind=SideEffectKind.DELIVERY,
        channel="test",
        destination_ref="other-target",
        payload_json='{"value":1}',
        payload_fingerprint="48208f9428d64634bd8e28ff345bf0eab60d53c18fa2fbdb0b9bc1e84df2b5f6",
        delivery_idempotency_key="stable-key",
        object_type="event",
        object_id="obj-1",
        object_version=1,
        correlation_id="corr",
        created_at=now(),
    )
    consumer = InMemoryIdempotentSideEffectConsumerHarness()
    consumer.deliver(message)
    with pytest.raises(SideEffectDeliveryConflictError):
        consumer.deliver(changed)
    assert consumer.effect_count == 1


@pytest.mark.parametrize("kind", [SideEffectKind.DELIVERY, SideEffectKind.PUBLICATION])
def test_delivery_and_publication_lifecycle_evidence_is_truth_neutral(kind):
    owner, owner_resolver, repo = owner_repo()
    repo.write(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
        command=command(),
        audit_metadata=metadata(),
        side_effect=intent(kind=kind),
    )
    message = repo.list_outbox_messages(
        principal=owner,
        tenant_context=context(),
        role_bindings=owner_resolver,
    )[0]
    worker = service()
    worker_resolver = BindingResolver(service_binding(worker))
    receipt = repo.dispatch_outbox_message(
        principal=worker,
        tenant_context=context(),
        role_bindings=worker_resolver,
        outbox_id=message.outbox_id,
        consumer=InMemoryIdempotentSideEffectConsumerHarness(),
    )
    assert message.factual_verification_authority is False
    assert receipt.factual_verification_authority is False
    assert not hasattr(message, "verification_status")
    assert not hasattr(receipt, "verification_status")


def test_p18_5_contract_preserves_runtime_provider_migration_and_truth_boundaries():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    version_parts = state["roadmap"]["state_sync_version"].split(".")
    assert int(version_parts[0]) == 4
    assert int(version_parts[1]) >= 29
    assert "P18_4_VALIDATED" in state["phases"]["18"]
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["verification_authority"] == "P13.5/P13.6"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert list((ROOT / "migrations").glob("033_*.sql")) == []
