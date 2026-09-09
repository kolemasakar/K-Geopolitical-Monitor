import json
from pathlib import Path

from kgeopolitical_monitor.shared_runtime_shadow import (
    CanaryReadinessPlan,
    CanaryStage,
    MismatchKind,
    ShadowMismatchBudget,
    ShadowRecord,
    compare_shadow_snapshots,
    snapshot_from_records,
)
from kgeopolitical_monitor.shared_runtime_contract import TenantContext

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "scripts" / "a3_shadow_reconciliation_proof.py"
CANARY = ROOT / "scripts" / "a3_live_railway_canary.py"
WORKFLOW = ROOT / ".github" / "workflows" / "a3-shadow-reconciliation-canary.yml"
STATE = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


def _record(object_id: str) -> ShadowRecord:
    tenant = TenantContext(workspace_id="workspace-alpha", project_id="project-alpha")
    return ShadowRecord.from_payload(
        tenant_context=tenant,
        table_name="shared_event",
        object_id=object_id,
        payload={"id": object_id},
    )


def test_a3_mismatch_threshold_is_deterministic_and_fail_closed():
    tenant = TenantContext(workspace_id="workspace-alpha", project_id="project-alpha")
    expected = snapshot_from_records(tenant_context=tenant, schema_version=32, records=(_record("a"), _record("b")))
    observed = snapshot_from_records(tenant_context=tenant, schema_version=32, records=(_record("a"),))
    report = compare_shadow_snapshots(expected=expected, observed=observed, budget=ShadowMismatchBudget(2))
    assert tuple(item.kind for item in report.mismatches) == (
        MismatchKind.ROW_COUNT,
        MismatchKind.TABLE_CONTENT,
        MismatchKind.SEMANTIC_PROJECTION,
    )
    assert report.within_budget is False
    assert report.exact_match is False
    assert report.canonical_cutover_authorized is False
    assert report.shared_runtime_activation_authorized is False


def test_a3_canary_plan_never_promotes_or_activates():
    plan = CanaryReadinessPlan(stages=(CanaryStage(1), CanaryStage(5), CanaryStage(25), CanaryStage(100)))
    assert plan.automatic_promotion is False
    assert plan.canonical_cutover_authorized is False
    assert plan.shared_runtime_activation_authorized is False
    assert plan.production_live_authorized is False


def test_a3_proof_is_disposable_synthetic_and_has_retry_outbox_rls_contracts():
    text = PROOF.read_text(encoding="utf-8").casefold()
    for required in (
        "synthetic_data_only",
        "on conflict do nothing",
        "shadow_outbox",
        "force row level security",
        "nobypassrls",
        "set transaction read only",
        "a3_ephemeral_cleanup=pass",
    ):
        assert required in text
    for forbidden in ("migration_033 = created", "shared_runtime_active = yes", "production_live = true"):
        assert forbidden not in text


def test_a3_live_canary_requires_noncanonical_health_and_no_credentials():
    text = CANARY.read_text(encoding="utf-8").casefold()
    assert '"canonical"' in text
    assert '"production_live"' in text
    assert '"shared_runtime_active"' in text
    assert "alternate_tenant_visible_rows" in text
    assert "data_plane_reconciliation=not_evidenced" in text
    for forbidden in ("bearer_token", "database_url", "railway.internal", "pgpassword"):
        assert forbidden not in text


def test_a3_workflow_uses_ephemeral_postgres_and_credential_free_live_canary():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "image: postgres:16" in text
    assert "python scripts/a3_shadow_reconciliation_proof.py" in text
    assert "python scripts/a3_live_railway_canary.py" in text


def test_a3_does_not_change_frozen_activation_state():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    assert state["roadmap"]["state_sync_version"] == "4.34"
    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
