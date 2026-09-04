from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "implementation" / "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_RESULT.md"
CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-04_PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase13_final_gate_is_canonical_and_exactly_evidenced():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    matrix = _read("docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md")
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")
    for document in (roadmap, readme, matrix, result, checkpoint):
        assert "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED" in document
        assert "7e49f790a36f596cdb8ed3d7d6e17f5ace2787be" in document
        assert "33861302915" in document and "100986128743" in document
        assert "33861302926" in document and "100986128780" in document
        assert "497 passed, 2 warnings / SUCCESS" in document
    assert "Phase 13 — Semantic Verification and Provenance Intelligence\nState: `VALIDATED`" in roadmap
    assert "P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix\nState: `VALIDATED`" in roadmap


def test_phase13_final_gate_preserves_all_package_gates():
    combined = "\n".join((
        _read("ROADMAP.md"),
        _read("README.md"),
        _read("docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md"),
        RESULT.read_text(encoding="utf-8"),
        CHECKPOINT.read_text(encoding="utf-8"),
    ))
    for gate in (
        "P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED",
        "P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED",
        "P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED",
        "P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED",
        "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED",
        "P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED",
        "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED",
    ):
        assert gate in combined


def test_phase13_final_gate_preserves_epistemic_boundaries():
    combined = "\n".join((
        _read("ROADMAP.md"), _read("README.md"), _read("DATA_MODELS.md"),
        _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"),
        RESULT.read_text(encoding="utf-8"),
    )).lower()
    assert "publisher/publication is not automatically the underlying origin" in combined
    assert "does not create independent corroboration" in combined
    assert "count-only" in combined
    assert "independent" in combined and "supports" in combined
    assert "multidimensional" in combined
    assert "no canonical" in combined and "scalar" in combined
    assert "coverage confidence cannot promote factual verification confidence" in combined
    assert "migration 028" in combined and "none" in combined
    assert "not_instrumented" in combined


def test_phase13_final_gate_does_not_activate_phase14_or_production():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")
    for document in (roadmap, readme, checkpoint):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document
        assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in document
    assert "Phase 14 — Owner Operational Intelligence Activation\nState: `APPROVED_SEQUENTIAL / NOT_STARTED`" in roadmap
    assert "paid providers: `NONE_APPROVED`" in roadmap or "paid providers: `NONE_APPROVED`" in readme
