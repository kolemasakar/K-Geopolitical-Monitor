from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_4_gate_and_sequential_transition_are_canonical_or_later():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    implementation = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL.md")
    result = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL_RESULT.md")
    checkpoint = _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED.md")

    for document in (roadmap, readme, plan, implementation, result, checkpoint):
        assert "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED" in document

    assert "P13.4 — Typed Contradiction Model and Resolution Lifecycle\nState: `VALIDATED`" in roadmap
    assert "P13.5 — Verification Policy Engine and Multidimensional Confidence" in roadmap
    assert (
        "P13.5 — Verification Policy Engine and Multidimensional Confidence\nState: `CURRENT / NOT_STARTED`" in roadmap
        or "P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED" in roadmap
    )


def test_p13_4_saved_validation_evidence_is_exact():
    documents = (
        _read("ROADMAP.md"),
        _read("README.md"),
        _read("DATA_MODELS.md"),
        _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"),
        _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL.md"),
        _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL_RESULT.md"),
        _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED.md"),
    )
    for document in documents:
        assert "d4dbb8a8098cef960194935bd94d4640fd719050" in document
        assert "447 passed, 1 warning / SUCCESS" in document
    assert "33594740585" in documents[0] and "100135812629" in documents[0]
    assert "33594740549" in documents[0] and "100135812546" in documents[0]


def test_p13_4_schema_lifecycle_and_evidence_link_contract_are_canonical():
    data_models = _read("DATA_MODELS.md")
    implementation = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL.md")
    result = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL_RESULT.md")
    combined = data_models + implementation + result

    assert "026_semantic_contradiction_model.sql" in combined
    assert "semantic_contradiction_versions" in combined
    assert "semantic_contradiction_evidence_links" in combined
    for token in (
        "OCCURRENCE_EXISTENCE",
        "ATTRIBUTION_RESPONSIBILITY",
        "ACTOR_IDENTITY",
        "QUANTITY_VALUE",
        "TIME",
        "LOCATION",
        "STATUS_OUTCOME",
        "SCOPE_EXTENT",
        "CAUSAL_INTERPRETATION",
        "DETECTED",
        "UNRESOLVED",
        "EVOLVING",
        "RESOLVED",
    ):
        assert token in combined
    assert "current P13.3 evidence relation version" in implementation


def test_p13_4_closure_preserves_truth_confidence_runtime_and_cutover_boundaries():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    implementation = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL.md")
    result = _read("docs/implementation/P13_4_TYPED_CONTRADICTION_MODEL_RESULT.md")

    for document in (roadmap, readme, implementation, result):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document

    combined = (roadmap + readme + implementation + result).lower()
    assert "not automatic" in combined or "does not automatically" in combined
    assert "factual truth" in combined or "factual winner" in combined
    assert "verification" in combined
    assert "factual confidence" in combined
    assert "coverage confidence" in combined
    assert "live" in combined and "cutover" in combined
    assert "left_true" not in combined
    assert "right_true" not in combined
