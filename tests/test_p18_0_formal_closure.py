import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "docs" / "state" / "CURRENT_PROJECT_STATE.json"
RESULT_PATH = ROOT / "docs" / "implementation" / "P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_RESULT.md"
CHECKPOINT_PATH = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-07_P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED.md"
ROADMAP_PATH = ROOT / "ROADMAP.md"
MIGRATIONS_DIR = ROOT / "migrations"


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_p18_0_machine_state_remains_formally_validated_after_later_progression():
    state = _state()

    assert _version_tuple(state["roadmap"]["state_sync_version"]) >= (4, 25)
    assert state["roadmap"]["current_position"].startswith("PHASE_18_")
    assert "P18_0_VALIDATED" in state["phases"]["18"]
    assert "/ NOT_ACTIVATED" in state["phases"]["18"]

    # phase18_p18_0 is historical closure evidence and must not be rewritten
    # merely because later P18.x gates progress.
    p18_0 = state["phase18_p18_0"]
    assert p18_0["state"] == "VALIDATED"
    assert p18_0["gate"] == "P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED"
    assert p18_0["implementation_anchor"] == "6a932c1572fc8136a372bbef35be926adf5248fd"
    assert p18_0["x64_run_id"] == 34118505375
    assert p18_0["arm64_run_id"] == 34118505353
    assert p18_0["test_count"] == 749
    assert p18_0["next_gate"] == "P18_1_IDENTITY_TENANT_CONTEXT_VALIDATED"
    assert p18_0["p18_1_state"] == "READY_TO_BEGIN"


def test_p18_0_closure_preserves_activation_storage_provider_and_migration_boundaries():
    state = _state()

    assert state["activation_gates"]["phase18_activation"] == "PHASE_18_SHARED_RUNTIME_ACTIVE = NO"
    assert state["runtime"]["storage"] == "PROJECT_LOCAL_ONLY"
    assert state["runtime"]["mixed_shared_runtime"] == "BLOCKED"
    assert state["runtime"]["production_live"] == "NOT_OPERATIONAL"
    assert state["runtime"]["paid_providers"] == "NONE_APPROVED"
    assert state["runtime"]["backend_https"] == "NOT_DEPLOYED"
    assert state["migrations"]["033"] == "NOT_CREATED / NOT_PREAUTHORIZED"
    assert not any(path.name.startswith("033_") for path in MIGRATIONS_DIR.glob("*.sql"))


def test_p18_0_result_and_checkpoint_record_exact_validation_evidence():
    result = RESULT_PATH.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")

    for text in (result, checkpoint):
        assert "P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED" in text
        assert "6a932c1572fc8136a372bbef35be926adf5248fd" in text
        assert "34118505375" in text
        assert "34118505353" in text
        assert "749 passed" in text
        assert "PROJECT_LOCAL_ONLY" in text
        assert "NOT_CREATED / NOT_PREAUTHORIZED" in text
        assert "NONE_APPROVED" in text


def test_roadmap_keeps_p18_0_validation_while_later_phase18_gates_advance():
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    version_line = next(
        line for line in roadmap.splitlines() if line.startswith("Version: ")
    )

    assert _version_tuple(version_line.removeprefix("Version: ")) >= (4, 25)
    assert "P18_0_SHARED_RUNTIME_CONTRACT_FOUNDATION_VALIDATED" in roadmap
    assert "P18.0: `VALIDATED`" in roadmap
    assert "PHASE_18_SHARED_RUNTIME_ACTIVE = NO" in roadmap
    assert "migration `033`" in roadmap.lower() or "Migration `033`" in roadmap
