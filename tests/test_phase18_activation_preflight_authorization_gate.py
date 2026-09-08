import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
DECISION_PATH = (
    ROOT
    / "docs"
    / "decisions"
    / "PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZATION_2026-09-08.md"
)
PLAN_PATH = (
    ROOT
    / "docs"
    / "implementation"
    / "PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_PLAN.md"
)
CHECKPOINT_PATH = (
    ROOT
    / "docs"
    / "checkpoints"
    / "PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_PREFLIGHT_A0_IN_PROGRESS.md"
)
MIGRATIONS_PATH = ROOT / "migrations"


READINESS_GATE = "PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED"
PREFLIGHT_AUTH = "PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES"
ACTIVE_NO = "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
A0_GATE = "PHASE_18_SHARED_RUNTIME_PROVIDER_TOPOLOGY_DECISION_READY"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _state() -> dict:
    return json.loads(_text(STATE_PATH))


def test_activation_preflight_is_separate_from_phase18_readiness_and_activation():
    decision = _text(DECISION_PATH)
    plan = _text(PLAN_PATH)
    checkpoint = _text(CHECKPOINT_PATH)
    state = _state()

    assert READINESS_GATE in decision
    assert READINESS_GATE in plan
    assert PREFLIGHT_AUTH in decision
    assert PREFLIGHT_AUTH in plan
    assert PREFLIGHT_AUTH in checkpoint

    # The strategic roadmap/machine state remains the validated P18.9 closure
    # until the separate activation workstream reaches a formal synchronization gate.
    assert state["roadmap"]["state_sync_version"] == "4.34"
    assert state["roadmap"]["current_position"] == (
        "PHASE_18_P18_9_VALIDATED_ACTIVATION_OWNER_GATE"
    )
    assert state["activation_gates"]["phase18_readiness"] == READINESS_GATE
    assert state["activation_gates"]["phase18_activation"] == ACTIVE_NO


def test_preflight_authorization_never_implies_launch_or_cutover_authorization():
    decision = _text(DECISION_PATH)
    plan = _text(PLAN_PATH)
    checkpoint = _text(CHECKPOINT_PATH)

    for text in (decision, plan, checkpoint):
        assert ACTIVE_NO in text
        assert "P18_9_LAUNCH_ELIGIBLE = FALSE" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text

    assert "does **not** authorize" in decision
    assert "A5 — Explicit Owner Activation / Cutover Decision" in plan
    assert "A5 =" not in checkpoint or "A5 = NOT_AUTHORIZED" in checkpoint


def test_a0_is_provider_decision_only_and_render_candidate_remains_uncreated():
    decision = _text(DECISION_PATH)
    plan = _text(PLAN_PATH)
    checkpoint = _text(CHECKPOINT_PATH)

    assert "A0 — Provider / Topology / Cost Decision" in decision
    assert "A0 — Provider / Topology / Cost Decision" in plan
    assert A0_GATE in decision
    assert A0_GATE in plan
    assert A0_GATE in checkpoint

    assert "RENDER_FRANKFURT_DISPOSABLE_NONPROD" in plan
    assert "RENDER_WORKSPACE_SELECTION = PENDING_EXPLICIT_OWNER_CONFIRMATION" in plan
    assert "RENDER_WORKSPACE_SELECTION = PENDING_EXPLICIT_OWNER_CONFIRMATION" in checkpoint
    assert "No Render resource has been created" in plan
    assert "no Render resource has been created" in checkpoint


def test_canonical_runtime_provider_and_migration_boundaries_remain_fail_closed():
    state = _state()

    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_PATH.glob("*.sql"))


def test_activation_workstream_does_not_create_p18_10():
    decision = _text(DECISION_PATH)
    plan = _text(PLAN_PATH)

    assert "does not create a P18.10" in decision
    assert "There is no P18.10" in plan
    assert "A0 — Provider / Topology / Cost Decision" in plan
    assert "A1 — Concrete Non-Production Launch Candidate" in plan
    assert "A2 — Live Security / Network / Recovery Observation" in plan
    assert "A3 — Migration / Reconciliation / Shadow / Canary Evidence" in plan
    assert "A4 — Fresh Exact-Head Launch Validation" in plan
    assert "A5 — Explicit Owner Activation / Cutover Decision" in plan
