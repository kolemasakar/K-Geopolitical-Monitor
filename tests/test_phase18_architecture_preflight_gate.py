import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
PREFLIGHT_PATH = (
    ROOT
    / "docs"
    / "implementation"
    / "PHASE_18_SHARED_TEAM_RUNTIME_ARCHITECTURE_PREFLIGHT.md"
)
DECISION_PATH = (
    ROOT
    / "docs"
    / "decisions"
    / "PHASE_18_ARCHITECTURE_APPROVAL_GATE_2026-09-07.md"
)


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_phase18_remains_conditional_and_unapproved():
    state = _state()

    assert state["phases"]["18"] == "CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED"
    assert (
        state["activation_gates"]["phase18"]
        == "PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL"
    )
    assert (
        state["roadmap"]["current_position"]
        == "POST_PHASE_17_PRE_PHASE_18_ARCHITECTURE_GATE"
    )


def test_preflight_is_not_implementation_authorization():
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    decision = DECISION_PATH.read_text(encoding="utf-8")

    for text in (preflight, decision):
        assert "PHASE_18_NEW_ARCHITECTURE_APPROVAL = PENDING_OWNER_DECISION" in text
        assert "PHASE_18_IMPLEMENTATION_AUTHORIZED = NO" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "MIGRATION_033" in text or "migration `033`" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text

    assert "PHASE_18_ARCHITECTURE_PREFLIGHT = COMPLETE" in preflight
    assert "DECISION = PENDING_OWNER_APPROVAL" in decision


def test_existing_project_local_runtime_boundary_remains_authoritative():
    state = _state()
    runtime = state["runtime"]
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert runtime["storage"] == "PROJECT_LOCAL_ONLY"
    assert runtime["mixed_shared_runtime"] == "BLOCKED"
    assert runtime["production_live"] == "NOT_OPERATIONAL"
    assert runtime["paid_providers"] == "NONE_APPROVED"

    assert "project-local SQLite" in preflight
    assert "must **not** be implemented" in preflight
    assert "shared/network filesystem" in preflight
    assert "existing local canonical SQLite store in place" in preflight


def test_phase18_preflight_does_not_create_or_preauthorize_migration_033():
    state = _state()
    migration_state = state["migrations"]["033"]
    migrations = ROOT / "migrations"

    assert migration_state == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in migrations.glob("*.sql"))


def test_phase18_architecture_requires_tenancy_authz_dr_and_rollback_contracts():
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")

    required_markers = (
        "workspace_id",
        "project_id",
        "NO_CROSS_TENANT_CANONICAL_ACCESS_WITHOUT_EXPLICIT_AUTHORIZED_CONTRACT",
        "Authentication and RBAC",
        "deny-by-default",
        "idempotency key",
        "optimistic concurrency",
        "transactional outbox",
        "Threat Model Baseline",
        "Backup, Disaster Recovery and Rollback",
        "clean-environment restore",
        "staged migration",
        "NO_GO_PENDING_EXPLICIT_OWNER_ARCHITECTURE_APPROVAL",
    )

    for marker in required_markers:
        assert marker in preflight
