import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    ROOT
    / "docs"
    / "implementation"
    / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
)
AUTHORIZATION_PATH = (
    ROOT
    / "docs"
    / "decisions"
    / "PHASE_18_IMPLEMENTATION_AUTHORIZATION_GATE_2026-09-07.md"
)
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_phase18_owner_implementation_authorization_is_recorded_without_starting_p18_0():
    plan = _text(PLAN_PATH)
    gate = _text(AUTHORIZATION_PATH)
    state = _state()

    assert "PHASE_18_NEW_ARCHITECTURE_APPROVAL = APPROVED_BY_OWNER" in plan
    assert "PHASE_18_IMPLEMENTATION_PLANNING_AUTHORIZED = YES" in plan
    assert "PHASE_18_IMPLEMENTATION_AUTHORIZED = YES" in plan
    assert "P18_0 = PLANNED / NOT_STARTED" in plan

    assert "Status: APPROVED_BY_OWNER_FOR_PHASE_18_IMPLEMENTATION" in gate
    assert "DECISION = APPROVED_BY_OWNER_FOR_PHASE_18_IMPLEMENTATION" in gate
    assert "PHASE_18_IMPLEMENTATION_AUTHORIZED = YES" in gate
    assert "P18_0 = PLANNED / NOT_STARTED" in gate

    assert (
        state["activation_gates"]["phase18_architecture"]
        == "PHASE_18_NEW_ARCHITECTURE_APPROVAL = APPROVED_BY_OWNER"
    )
    assert (
        state["activation_gates"]["phase18_planning"]
        == "PHASE_18_IMPLEMENTATION_PLANNING_AUTHORIZED = YES"
    )
    assert (
        state["activation_gates"]["phase18_implementation"]
        == "PHASE_18_IMPLEMENTATION_AUTHORIZED = YES"
    )
    assert (
        state["activation_gates"]["phase18_activation"]
        == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    )
    assert (
        state["roadmap"]["current_position"]
        == "PHASE_18_IMPLEMENTATION_AUTHORIZED_P18_0_READY_GATE"
    )


def test_phase18_plan_sequence_is_complete_ordered_and_not_started():
    plan = _text(PLAN_PATH)
    headings = (
        "### P18.0 — Shared Runtime Contract Foundation and Test Harness",
        "### P18.1 — Identity and Authenticated Tenant Context Foundation",
        "### P18.2 — RBAC and Owner-Only Strategic Gate Enforcement",
        "### P18.3 — Shared Datastore Schema and Migration Contract",
        "### P18.4 — Tenant-Scoped Repository, Write, Idempotency and Concurrency Layer",
        "### P18.5 — Audit, Transactional Outbox and Side-Effect Isolation",
        "### P18.6 — Shared Runtime Security and Secrets Controls",
        "### P18.7 — Backup, Disaster Recovery and Rollback",
        "### P18.8 — Non-Production Shadow, Provider/Cost Gate and Canary Readiness",
        "### P18.9 — Phase 18 Validation Matrix and Shared Runtime Activation Readiness",
    )
    positions = [plan.index(heading) for heading in headings]
    assert positions == sorted(positions)

    for index, heading in enumerate(headings):
        section = plan.split(heading, 1)[1]
        if index + 1 < len(headings):
            section = section.split(headings[index + 1], 1)[0]
        assert "State: `PLANNED / NOT_STARTED`" in section
        assert "Gate: `" in section


def test_phase18_plan_preserves_tenancy_authz_concurrency_security_and_dr_contracts():
    plan = _text(PLAN_PATH)
    required = (
        "workspace_id",
        "project_id",
        "deny-by-default",
        "OWNER",
        "ADMIN",
        "ANALYST",
        "VIEWER",
        "SERVICE",
        "idempotency",
        "optimistic concurrency",
        "transactional outbox",
        "HTTPS-only",
        "non-public canonical datastore ingress",
        "clean-environment restore",
        "rollback",
        "owner-only SQLite runtime remains independently operable",
    )
    for marker in required:
        assert marker in plan


def test_phase18_implementation_authorization_does_not_create_or_preauthorize_migration_033():
    plan = _text(PLAN_PATH)
    gate = _text(AUTHORIZATION_PATH)
    state = _state()
    migrations = ROOT / "migrations"

    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in migrations.glob("*.sql"))
    assert "MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED" in plan
    assert "does **not** allocate, create or preauthorize migration `033`" in plan
    assert "migration `033` creation or execution merely because Phase 18 implementation is authorized" in gate


def test_phase18_plan_preserves_current_runtime_and_provider_boundaries():
    plan = _text(PLAN_PATH)
    gate = _text(AUTHORIZATION_PATH)
    runtime = _state()["runtime"]

    assert runtime["storage"] == "PROJECT_LOCAL_ONLY"
    assert runtime["mixed_shared_runtime"] == "BLOCKED"
    assert runtime["production_live"] == "NOT_OPERATIONAL"
    assert runtime["paid_providers"] == "NONE_APPROVED"

    for text in (plan, gate):
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text

    assert "provider selection and spending remain separate owner decisions" in plan
    assert "owner-only project-local SQLite remains canonical" in plan


def test_phase18_plan_keeps_final_activation_separate_from_implementation():
    plan = _text(PLAN_PATH)
    gate = _text(AUTHORIZATION_PATH)

    assert "P18.9 validation means **activation readiness only**" in plan
    assert "Final activation requires a separate explicit owner activation decision" in plan
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = YES" in plan
    assert "does **not** authorize" in gate
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = YES" in gate
    assert "canonical cutover from the owner-only project-local runtime" in gate
