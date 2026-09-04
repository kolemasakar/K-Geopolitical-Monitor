from pathlib import Path

from kgeopolitical_monitor.owner_operational_intelligence import (
    OWNER_OPERATIONAL_ACTIVATION,
    PHASE_14_GATE,
    PRODUCTION_LIVE,
    RUNTIME_STORAGE,
)


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase14_closure_candidate_state_is_synchronized():
    roadmap = _text("ROADMAP.md")
    readme = _text("README.md")
    checkpoint = _text(
        "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY.md"
    )

    assert "Version: 4.17" in roadmap
    assert "Phase 14: `CLOSURE_CANDIDATE / EXACT_HEAD_VALIDATION_PENDING / OWNER_DECISION_REQUIRED`" in roadmap
    assert "PHASE_14_CLOSURE_CANDIDATE / EXACT_HEAD_VALIDATION_PENDING" in checkpoint
    assert "PHASE_14_CLOSURE_CANDIDATE" in readme


def test_phase14_closure_candidate_does_not_grant_operational_activation():
    documents = "\n".join(
        [
            _text("ROADMAP.md"),
            _text("README.md"),
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_PLAN.md"),
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_RESULT.md"),
            _text(
                "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY.md"
            ),
        ]
    )
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in documents
    assert "PRODUCTION_LIVE = NOT_OPERATIONAL" in documents
    assert "PROJECT_LOCAL_ONLY" in documents
    assert "NONE_APPROVED" in documents


def test_phase14_owner_runtime_contract_remains_pre_activation():
    assert PHASE_14_GATE == "PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY"
    assert OWNER_OPERATIONAL_ACTIVATION == "OWNER_DECISION_REQUIRED"
    assert PRODUCTION_LIVE == "NOT_OPERATIONAL"
    assert RUNTIME_STORAGE == "PROJECT_LOCAL_ONLY"


def test_phase14_introduces_no_migration_028():
    migrations = ROOT / "migrations"
    assert not any(path.name.startswith("028") for path in migrations.iterdir())
