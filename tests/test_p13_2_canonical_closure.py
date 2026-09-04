from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_2_historical_gate_survives_later_sequential_progress():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    result = _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_RESULT.md")
    checkpoint = _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED.md")

    for document in (roadmap, readme, plan, result, checkpoint):
        assert "P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED" in document

    assert "P13.2 — Provenance / Underlying-Origin Relation Model\nState: `VALIDATED`" in roadmap
    for later_gate in (
        "P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED",
        "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED",
    ):
        assert later_gate in roadmap
        assert later_gate in readme
        assert later_gate in plan


def test_p13_2_saved_validation_evidence_remains_exact_in_authoritative_records():
    documents = (
        _read("ROADMAP.md"),
        _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL.md"),
        _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_RESULT.md"),
        _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED.md"),
    )
    for document in documents:
        assert "6cd37a334b122ae5de2b4cb6272f9cc222f1f174" in document
        assert "420 passed, 1 warning / SUCCESS" in document
    assert "33558425194" in documents[0] and "100024835794" in documents[0]
    assert "33558425252" in documents[0] and "100024836399" in documents[0]


def test_p13_2_closure_preserves_epistemic_and_runtime_boundaries():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    result = _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_RESULT.md")

    for document in (roadmap, readme, result):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document

    assert "publisher/publication is not automatically the underlying origin" in roadmap
    assert "do not create independent corroboration" in result
    assert "does not establish that a claim is true" in result
    assert "no live analytical cutover occurred" in result.lower()


def test_p13_2_scope_stops_before_later_semantic_packages():
    result = _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_RESULT.md")
    implementation = _read("docs/implementation/P13_2_PROVENANCE_ORIGIN_RELATION_MODEL.md")
    combined = (result + implementation).lower()

    for token in (
        "evidentiary independence",
        "contradiction",
        "verification",
        "factual confidence",
        "p13.3",
        "p13.4",
        "p13.5",
        "p13.6",
    ):
        assert token in combined
