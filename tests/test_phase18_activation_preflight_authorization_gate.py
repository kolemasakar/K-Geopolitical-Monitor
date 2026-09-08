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
A0_DECISION_PATH = (
    ROOT
    / "docs"
    / "decisions"
    / "PHASE_18_ACTIVATION_A0_RENDER_DISPOSABLE_PROVIDER_DECISION_2026-09-08.md"
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
A0_VALIDATED_CHECKPOINT_PATH = (
    ROOT
    / "docs"
    / "checkpoints"
    / "PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_A0_VALIDATED_A1_ADAPTER_IN_PROGRESS.md"
)
A1_BLOCKER_CHECKPOINT_PATH = (
    ROOT
    / "docs"
    / "checkpoints"
    / "PROJECT_CHECKPOINT_2026-09-08_PHASE_18_ACTIVATION_A1_BLOCKED_RENDER_FREE_DB_QUOTA.md"
)
MIGRATIONS_PATH = ROOT / "migrations"


READINESS_GATE = "PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED"
PREFLIGHT_AUTH = "PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES"
ACTIVE_NO = "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
A0_GATE = "PHASE_18_SHARED_RUNTIME_PROVIDER_TOPOLOGY_DECISION_READY"
A1_GATE = "PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED"


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
    checkpoint = _text(A1_BLOCKER_CHECKPOINT_PATH)

    for text in (decision, plan, checkpoint):
        assert ACTIVE_NO in text
        assert "P18_9_LAUNCH_ELIGIBLE = FALSE" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text
        assert "NOT_OPERATIONAL" in text

    assert "does **not** authorize" in decision
    assert "A5 — Explicit Owner Activation / Cutover Decision" in plan


def test_a0_history_and_validated_free_render_decision_are_consistent():
    authorization = _text(DECISION_PATH)
    original_checkpoint = _text(CHECKPOINT_PATH)
    a0_decision = _text(A0_DECISION_PATH)
    plan = _text(PLAN_PATH)
    a0_checkpoint = _text(A0_VALIDATED_CHECKPOINT_PATH)

    assert "A0 — Provider / Topology / Cost Decision" in authorization
    assert "A0 — Provider / Topology / Cost Decision" in plan
    assert A0_GATE in authorization
    assert A0_GATE in plan
    assert A0_GATE in original_checkpoint

    # Historical authorization/checkpoint preserve the pre-confirmation state.
    assert "RENDER_WORKSPACE_SELECTION = PENDING_EXPLICIT_OWNER_CONFIRMATION" in original_checkpoint

    # The later A0 decision remains narrow: only a free disposable Render candidate.
    assert "A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY" in a0_decision
    assert "A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY" in plan
    assert "A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY" in a0_checkpoint
    assert "RENDER_WORKSPACE_SELECTION = OWNER_CONFIRMED_MY_WORKSPACE" in plan
    assert "PAID_PROVIDERS = NONE_APPROVED" in a0_decision


def test_a1_records_real_render_free_database_quota_blocker_without_claiming_gate():
    plan = _text(PLAN_PATH)
    checkpoint = _text(A1_BLOCKER_CHECKPOINT_PATH)

    for text in (plan, checkpoint):
        assert "A1 = BLOCKED_ON_RENDER_FREE_DB_QUOTA" in text
        assert "A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED" in text
        assert "RENDER_FREE_DB_QUOTA = EXHAUSTED_BY_EXISTING_NON_KGM_RESOURCE" in text
        assert "KGM_POSTGRES_CREATED = NO" in text
        assert "EXISTING_NON_KGM_DATABASE_REUSE = FORBIDDEN" in text
        assert "PAID_RENDER_DATABASE = NOT_AUTHORIZED" in text
        assert "PROVIDER_PIVOT = NOT_AUTHORIZED" in text

    assert A1_GATE in plan
    assert "PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO" in checkpoint
    assert "A1_TARGET_GATE = NOT_SATISFIED" in checkpoint
    assert "kgm-shared-runtime-preflight" in checkpoint
    assert "placeholder" in checkpoint.casefold()
    assert "1131 passed" in checkpoint
    assert "aarch64" in checkpoint


def test_a1_failed_shell_is_not_a_backend_https_or_production_activation_claim():
    state = _state()
    checkpoint = _text(A1_BLOCKER_CHECKPOINT_PATH)

    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert "The shell is **not operational**" in checkpoint
    assert "No A2 live-security/network/recovery claims" in checkpoint


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
