from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "implementation" / "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"
RESULT = ROOT / "docs" / "implementation" / "P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_RESULT.md"
CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-01_P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_0_plan_declares_additive_compatibility_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    assert "P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED" in plan
    assert "creates **no database migration**" in plan
    assert "additive migrations only" in plan
    for legacy in ("`claims`", "`evidence`", "`live_analysis_claims`", "`live_analysis_evidence`"):
        assert legacy in plan
    assert "must link to legacy/live objects rather than silently overwrite" in plan


def test_p13_0_forbids_headline_and_count_shortcuts():
    plan = PLAN.read_text(encoding="utf-8").lower()
    assert "semantic claim is not identified solely by a headline" in plan
    assert "evidence count is `>= 2`" in plan
    assert "two domains/hosts are different" in plan
    assert "same statement appears in multiple languages" in plan
    assert "different source, host, domain, publisher or language is not sufficient proof of independence" in plan


def test_p13_0_provenance_and_independence_are_explicit():
    plan = PLAN.read_text(encoding="utf-8")
    for text in (
        "publisher / publication",
        "cited or quoted source",
        "asserted underlying origin",
        "wire/syndication origin",
        "unresolved or mixed origin",
        "INDEPENDENT",
        "NOT_INDEPENDENT",
        "UNKNOWN",
    ):
        assert text in plan
    assert "Unknown independence cannot be promoted to independent" in plan


def test_p13_0_evidence_relations_and_contradictions_are_typed():
    plan = PLAN.read_text(encoding="utf-8")
    for relation in (
        "SUPPORTS",
        "CONTRADICTS",
        "QUALIFIES",
        "CONTEXT_ONLY",
        "ATTRIBUTION_ONLY",
        "DUPLICATE_OR_SAME_ORIGIN",
    ):
        assert relation in plan
    for dimension in (
        "occurrence/existence",
        "attribution/responsibility",
        "quantity/value",
        "time",
        "location",
        "status/outcome",
    ):
        assert dimension in plan


def test_p13_0_separates_extraction_confidence_truth_and_coverage():
    plan = PLAN.read_text(encoding="utf-8").lower()
    assert "semantic extraction confidence is not factual verification confidence" in plan
    assert "coverage confidence remains separate and cannot promote factual verification confidence" in plan
    assert "model output may propose structured objects; policy validates and records them" in plan


def test_p13_0_canonical_state_and_sequencing_survive_later_progress():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    data_models = _read("DATA_MODELS.md")
    source_policy = _read("SOURCE_POLICY.md")

    assert "Phase 13 — Semantic Verification and Provenance Intelligence" in roadmap
    assert (
        "State: `APPROVED / ACTIVE_ENGINEERING_PHASE`" in roadmap
        or "State: `CLOSURE_CANDIDATE / AWAITING_EXACT_HEAD_REGRESSION`" in roadmap
        or "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED" in roadmap
    )
    for section in (
        "P13.0 — Semantic Verification Architecture Contract\nState: `VALIDATED`",
        "P13.1 — Structured Semantic Claim Model\nState: `VALIDATED`",
        "P13.2 — Provenance / Underlying-Origin Relation Model\nState: `VALIDATED`",
        "P13.3 — Evidence Relation and Independence Assessment\nState: `VALIDATED`",
        "P13.4 — Typed Contradiction Model and Resolution Lifecycle\nState: `VALIDATED`",
    ):
        assert section in roadmap
    assert "P13.5 — Verification Policy Engine and Multidimensional Confidence" in roadmap
    assert "P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED" in readme
    assert "Phase 13 semantic model v2 architecture: `P13.0_VALIDATED`" in data_models
    assert "P13.0 semantic verification architecture contract: `VALIDATED`" in source_policy
    assert "Phase 14 — Owner Operational Intelligence Activation\nState: `APPROVED_SEQUENTIAL / NOT_STARTED`" in roadmap
    assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in roadmap


def test_p13_0_preserves_runtime_and_truth_boundaries():
    for path in (
        "docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md",
        "ROADMAP.md",
        "README.md",
    ):
        doc = _read(path)
        assert "Production/live operational status: NOT_OPERATIONAL" in doc
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in doc

    plan = PLAN.read_text(encoding="utf-8").lower()
    assert "publisher/domain identity is not automatically underlying-origin identity" in plan
    assert "does not create independent corroboration" in plan
    assert "are not truth operators" in plan
    assert "graph inference and forecast probability cannot promote factual verification" in plan
    assert "`global` remains scope, not proof of exhaustive coverage" in plan


def test_p13_0_validation_evidence_is_saved_exactly():
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")
    for exact in (
        "4422fae5e2a4546585a43237d2124f466c457543",
        "33554568574",
        "100012110127",
        "33554568570",
        "100012110488",
        "399 passed, 1 warning / SUCCESS",
    ):
        assert exact in result
        assert exact in checkpoint
    assert "P13.1_STRUCTURED_SEMANTIC_CLAIM_MODEL / CURRENT_NOT_STARTED" in checkpoint


def test_p13_0_closure_allows_validated_sequential_phase13_progress():
    roadmap = _read("ROADMAP.md")
    plan = PLAN.read_text(encoding="utf-8")
    for section in (
        "P13.1 — Structured Semantic Claim Model\nState: `VALIDATED`",
        "P13.2 — Provenance / Underlying-Origin Relation Model\nState: `VALIDATED`",
        "P13.3 — Evidence Relation and Independence Assessment\nState: `VALIDATED`",
        "P13.4 — Typed Contradiction Model and Resolution Lifecycle\nState: `VALIDATED`",
    ):
        assert section in roadmap
    assert "P13_5_VERIFICATION_POLICY_CONFIDENCE_VALIDATED" in roadmap
    assert "P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix" in roadmap
    assert (
        "current engineering activity: `P13.5_VERIFICATION_POLICY_CONFIDENCE`" in roadmap
        or "current engineering activity: `P13.6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX`" in roadmap
        or "current engineering activity: `PHASE_13_CANONICAL_CLOSURE_VALIDATION`" in roadmap
        or "PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED" in roadmap
    )
    assert "P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED" in plan
    assert "P13.6 must be implemented, validated and saved before Phase 13 is closed" in plan
