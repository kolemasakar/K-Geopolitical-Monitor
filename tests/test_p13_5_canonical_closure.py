from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "implementation" / "P13_5_VERIFICATION_POLICY_CONFIDENCE_RESULT.md"
CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-04_P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "P13_5_VERIFICATION_POLICY_CONFIDENCE.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_5_gate_and_transition_to_p13_6_are_canonical():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    implementation = IMPLEMENTATION.read_text(encoding="utf-8")
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    for document in (roadmap, readme, plan, implementation, result, checkpoint):
        assert "P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED" in document
    assert "P13.5 — Verification Policy Engine and Multidimensional Confidence\nState: `VALIDATED`" in roadmap
    assert "P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix\nState: `CURRENT / NOT_STARTED`" in roadmap
    assert "P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX" in readme


def test_p13_5_validation_evidence_is_exact_and_saved():
    documents = (
        _read("ROADMAP.md"),
        _read("README.md"),
        _read("DATA_MODELS.md"),
        _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"),
        IMPLEMENTATION.read_text(encoding="utf-8"),
        RESULT.read_text(encoding="utf-8"),
        CHECKPOINT.read_text(encoding="utf-8"),
    )
    for document in documents:
        assert "0f0d746c538dc5ce8f010fb80f8afbe00685414a" in document
        assert "475 passed, 2 warnings / SUCCESS" in document
    assert "33849149736" in documents[0] and "100947736040" in documents[0]
    assert "33849149742" in documents[0] and "100947736318" in documents[0]


def test_p13_5_policy_and_confidence_boundaries_remain_explicit():
    combined = "\n".join(
        [
            _read("ROADMAP.md"),
            _read("README.md"),
            _read("DATA_MODELS.md"),
            IMPLEMENTATION.read_text(encoding="utf-8"),
            RESULT.read_text(encoding="utf-8"),
        ]
    ).lower()
    assert "count-only" in combined
    assert "independent" in combined and "supports" in combined
    assert "multidimensional" in combined
    assert "no canonical scalar" in combined or "no single canonical factual-confidence scalar" in combined
    assert "coverage" in combined and "cannot promote" in combined
    assert "official" in combined and "not automatically" in combined


def test_p13_5_preserves_legacy_runtime_and_cutover_boundaries():
    readme = _read("README.md")
    result = RESULT.read_text(encoding="utf-8")
    implementation = IMPLEMENTATION.read_text(encoding="utf-8")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")

    for document in (readme, result, implementation, plan):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document
    combined = (readme + result + implementation + plan).lower()
    assert "verification.py" in combined
    assert "confidence_engine.py" in combined
    assert "compatibility" in combined
    assert "p13.6" in combined and "cutover" in combined
    assert "paid providers" in combined
