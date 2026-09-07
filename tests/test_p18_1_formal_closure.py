import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_1_IDENTITY_TENANT_CONTEXT_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED.md"
ROADMAP_PATH = ROOT / "ROADMAP.md"
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_18_SHARED_TEAM_RUNTIME_IMPLEMENTATION_PLAN.md"
MIGRATIONS_DIR = ROOT / "migrations"


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_p18_1_machine_state_is_formally_validated_and_p18_2_is_ready():
    state = _state()

    assert _version_tuple(state["roadmap"]["state_sync_version"]) >= (4, 26)
    assert state["roadmap"]["current_position"] == "PHASE_18_P18_1_VALIDATED_P18_2_READY_GATE"
    assert "P18_0_VALIDATED" in state["phases"]["18"]
    assert "P18_1_VALIDATED" in state["phases"]["18"]
    assert "P18_2_READY" in state["phases"]["18"]
    assert state["phases"]["18"].endswith("/ NOT_ACTIVATED")

    p18_1 = state["phase18_p18_1"]
    assert p18_1["state"] == "VALIDATED"
    assert p18_1["gate"] == "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED"
    assert p18_1["implementation_anchor"] == "01abc4f6be77c856e24497ad77c58ab052bb89e2"
    assert p18_1["pr_number"] == 15
    assert p18_1["pr_x64_run_id"] == 34124158186
    assert p18_1["x64_run_id"] == 34124491945
    assert p18_1["arm64_run_id"] == 34124491899
    assert p18_1["test_count"] == 776
    assert p18_1["next_gate"] == "P18_2_RBAC_OWNER_GATE_ENFORCEMENT_VALIDATED"
    assert p18_1["p18_2_state"] == "READY_TO_BEGIN"


def test_p18_1_closure_preserves_activation_storage_provider_and_migration_boundaries():
    state = _state()

    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))


def test_p18_1_result_and_checkpoint_record_exact_validation_evidence():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")

    for text in (result, checkpoint):
        assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in text
        assert "01abc4f6be77c856e24497ad77c58ab052bb89e2" in text
        assert "34124158186" in text
        assert "34124491945" in text
        assert "34124491899" in text
        assert "776 passed" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text


def test_roadmap_and_plan_converge_on_p18_1_validated_p18_2_ready():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    version_line = next(line for line in roadmap.splitlines() if line.startswith("Version: "))

    assert _version_tuple(version_line.removeprefix("Version: ")) >= (4, 26)
    for text in (roadmap, plan):
        assert "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED" in text
        assert "P18.1" in text and "VALIDATED" in text
        assert "P18.2" in text and "READY_TO_BEGIN" in text
        assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in text
        assert "033" in text


def test_p18_0_historical_closure_evidence_remains_immutable_in_current_state():
    p18_0 = _state()["phase18_p18_0"]

    assert p18_0["state"] == "VALIDATED"
    assert p18_0["implementation_anchor"] == "6a932c1572fc8136a372bbef35be926adf5248fd"
    assert p18_0["x64_run_id"] == 34118505375
    assert p18_0["arm64_run_id"] == 34118505353
    assert p18_0["test_count"] == 749
    assert p18_0["next_gate"] == "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED"
    assert p18_0["p18_1_state"] == "READY_TO_BEGIN"
