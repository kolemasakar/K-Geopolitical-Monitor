from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_1_gate_and_later_sequential_progress_are_canonical():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    result = _read("docs/implementation/P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_RESULT.md")
    checkpoint = _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED.md")

    for document in (roadmap, readme, plan, result, checkpoint):
        assert "P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED" in document

    assert "P13.1 — Structured Semantic Claim Model\nState: `VALIDATED`" in roadmap
    assert "P13.2 — Provenance / Underlying-Origin Relation Model\nState: `VALIDATED`" in roadmap
    assert "P13.3 — Evidence Relation and Independence Assessment\nState: `CURRENT / NOT_STARTED`" in roadmap
    assert "P13.2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED" in readme
    assert "P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED" in plan


def test_p13_1_saved_validation_evidence_is_exact():
    documents = (
        _read("ROADMAP.md"),
        _read("README.md"),
        _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"),
        _read("docs/implementation/P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL.md"),
        _read("docs/implementation/P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_RESULT.md"),
        _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED.md"),
    )
    for document in documents:
        assert "69c3282077ad8dd90ef239c0594be56f9363bfe5" in document
        assert "408 passed, 1 warning / SUCCESS" in document
    assert "33555804493" in documents[0] and "100016206225" in documents[0]
    assert "33555804396" in documents[0] and "100016205406" in documents[0]


def test_p13_1_closure_preserves_scope_and_truth_boundaries():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    data_models = _read("DATA_MODELS.md")
    result = _read("docs/implementation/P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_RESULT.md")

    for document in (roadmap, readme, data_models, result):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document

    assert "semantic extraction confidence is not factual verification confidence" in roadmap
    assert "publisher/publication is not automatically the underlying origin" in roadmap
    assert "different publisher/domain/language" in readme
    assert "provenance / underlying-origin relations — P13.2" in result
    assert "verification policy engine or multidimensional factual confidence — P13.5" in result
    assert "no live analytical cutover" in result.lower()


def test_p13_1_schema_boundary_remains_explicit_in_canonical_docs():
    data_models = _read("DATA_MODELS.md")
    result = _read("docs/implementation/P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_RESULT.md")

    for token in (
        "underlying_origin",
        "independence_state",
        "evidence_relation",
        "contradiction_state",
        "verification_state",
        "factual_confidence",
        "coverage_confidence",
    ):
        assert token in data_models
        assert token in result

    assert "semantic_claim_versions" in data_models
    assert "semantic_claim_links" in data_models
    assert "association records only" in result
