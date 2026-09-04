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


def test_phase14_validated_ready_state_is_synchronized():
    roadmap = _text("ROADMAP.md")
    readme = _text("README.md")
    checkpoint = _text(
        "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY.md"
    )

    assert "Version: 4.18" in roadmap
    assert "PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY" in roadmap
    assert "VALIDATED_READY / NOT_ACTIVATED" in roadmap
    assert "PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY / VALIDATED_READY / NOT_ACTIVATED" in checkpoint
    assert "PHASE_14_VALIDATED_READY / NOT_ACTIVATED" in readme


def test_phase14_closure_evidence_is_exact_and_saved():
    documents = "\n".join(
        [
            _text("ROADMAP.md"),
            _text("README.md"),
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_PLAN.md"),
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_RESULT.md"),
            _text("docs/implementation/P14_6_VALIDATION_MATRIX.md"),
            _text(
                "docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY.md"
            ),
        ]
    )
    for token in (
        "43a26aee7ed677dafd46eb91c510d0e724d558c2",
        "33873131265",
        "101023637949",
        "33873131300",
        "101023638027",
        "510 passed, 2 warnings / SUCCESS",
    ):
        assert token in documents


def test_phase14_validated_readiness_does_not_grant_operational_activation():
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


def test_phase14_introduced_no_migration_028_but_p15_1_may_do_so_later():
    phase14_documents = "\n".join(
        [
            _text("docs/implementation/PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_RESULT.md"),
            _text("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY.md"),
            _text("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_POST_PHASE_14_TRANSITION_READY.md"),
        ]
    )
    assert "migration `028`: `NONE`" in phase14_documents or "No migration `028` is introduced" in phase14_documents

    migration_028 = ROOT / "migrations" / "028_forecast_outcome_assessment_history.sql"
    if migration_028.exists():
        assert "Phase 15.1" in migration_028.read_text(encoding="utf-8")
