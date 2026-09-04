from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "implementation" / "P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md"
RESULT = ROOT / "docs" / "implementation" / "P13_6_LIVE_COMPATIBILITY_CUTOVER_RESULT.md"
CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-04_P13_6_IMPLEMENTATION_VALIDATED.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_p13_6_saved_evidence_matches_validated_candidate():
    matrix = _read(MATRIX)
    result = _read(RESULT)
    checkpoint = _read(CHECKPOINT)
    for document in (matrix, result, checkpoint):
        assert "3b8d75d05168561898ba3fa592d0d7bdad5a5dd4" in document
        assert "33857212159" in document and "100973174656" in document
        assert "33857212157" in document and "100973174256" in document
        assert "489 passed, 2 warnings / SUCCESS" in document
    assert "native `aarch64`" in matrix
    assert "native `aarch64`" in result
    assert "native `aarch64`" in checkpoint


def test_p13_6_validation_matrix_preserves_complete_phase13_chain():
    matrix = _read(MATRIX)
    for gate in (
        "P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED",
        "P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED",
        "P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED",
        "P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED",
        "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED",
        "P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED",
    ):
        assert gate in matrix
    for anchor in (
        "4422fae5e2a4546585a43237d2124f466c457543",
        "69c3282077ad8dd90ef239c0594be56f9363bfe5",
        "6cd37a334b122ae5de2b4cb6272f9cc222f1f174",
        "9023dc22d36525b4dc9babbf21d97d184a1c110e",
        "f771ce0154e24b2218b309d8b3e6b880b408a146",
        "d2e80fe8a1bd998ca422be1e1001744be0e9e6e3",
    ):
        assert anchor in matrix


def test_p13_6_saved_boundary_has_no_parallel_migration_or_legacy_truth_promotion():
    combined = (_read(MATRIX) + _read(RESULT) + _read(CHECKPOINT)).lower()
    assert "no database migration" in combined or "migration 028: `none`" in combined
    assert "origin_host" in combined
    assert "independent_origin_count" in combined
    assert "scalar confidence" in combined
    assert "never" in combined or "not" in combined
    assert "not_instrumented" in combined
    assert "never reconstructed" in combined or "not reconstructed" in combined


def test_p13_6_evidence_save_does_not_prematurely_grant_strategic_gate():
    matrix = _read(MATRIX)
    result = _read(RESULT)
    checkpoint = _read(CHECKPOINT)
    assert "PENDING_CANONICAL_CLOSURE" in matrix
    assert "PENDING_CANONICAL_CLOSURE" in result
    assert "NOT_YET_GRANTED" in checkpoint
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in matrix
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in checkpoint
    for document in (matrix, result, checkpoint):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document
