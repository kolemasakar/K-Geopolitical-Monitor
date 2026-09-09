import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/a2_3_logical_recovery_proof.py"
WORKFLOW = ROOT / ".github/workflows/a2-3-backup-restore-rollback.yml"
STATE = ROOT / "docs/state/CURRENT_PROJECT_STATE.json"


def test_a2_3_recovery_script_is_disposable_and_provider_credential_free() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    folded = text.casefold()

    assert 'db_prefix = "kgm_a2_3_"' in folded
    assert '"pg_dump"' in text
    assert '"pg_restore"' in text
    assert "finally:" in text
    assert "_drop_database(RESTORE_DB)" in text
    assert "_drop_database(SOURCE_DB)" in text
    assert "dump_path.unlink(missing_ok=True)" in text

    # The synthetic adapter legitimately accepts a field named database_url.
    # What A2.3 must never embed is a Railway endpoint, provider secret name, or
    # live preflight credential/configuration surface.
    for forbidden in (
        "railway.internal",
        "railway_public_domain",
        "probe_bearer_token",
        "kgm-preflight-postgres",
        "kgm_preflight_database_url",
        "kgm_preflight_bearer_token",
        "railway_token",
    ):
        assert forbidden not in folded

    for required_synthetic_env in ("PGHOST", "PGPORT", "PGUSER", "PGPASSWORD"):
        assert f'_required_env("{required_synthetic_env}")' in text


def test_a2_3_recovery_proof_preserves_rls_and_role_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "relrowsecurity" in text
    assert "relforcerowsecurity" in text
    assert "kgm_preflight_tenant_isolation" in text
    assert "rolbypassrls" in text
    assert 'restored["rls"] != (True, True)' in text
    assert 'restored["role"] != (False, False, False, False, False, False)' in text
    assert "_assert_restored_rls_isolation()" in text


def test_a2_3_workflow_uses_ephemeral_postgres_and_owner_local_runtime() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "image: postgres:16-alpine" in text
    assert "logical-recovery:" in text
    assert "owner-local-rollback:" in text
    assert "a2_3_logical_recovery_proof.py" in text
    assert "kgeopolitical_monitor.unattended_runner" in text
    assert "PRAGMA integrity_check" in text
    assert "A2_3_OWNER_LOCAL_ROLLBACK=PASS" in text


def test_a2_3_does_not_relax_activation_or_migration_033_gates() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))

    assert state["roadmap"]["state_sync_version"] == "4.34"
    assert state["activation_gates"]["phase18_activation"] == (
        "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    )
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert state["phase18_p18_9"]["launch_eligible"] is False
    assert state["phase18_p18_9"]["activation_state"] == "NOT_AUTHORIZED"
