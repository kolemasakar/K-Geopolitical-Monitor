from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs" / "implementation" / "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_PLAN.md"
ROADMAP_PATH = ROOT / "ROADMAP.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase17_plan_identity_baseline_and_activation_gate_are_explicit():
    plan = _text(PLAN_PATH)
    roadmap = _text(ROADMAP_PATH)

    assert "# Phase 17 — Controlled External Publication Readiness" in plan
    # v4.20 is the historical planning basis; the current synchronized roadmap may advance.
    assert "ROADMAP basis: `v4.20`" in plan
    assert "Strategic phase state: `VALIDATED_READY / NOT_ACTIVATED`" in plan
    assert "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED" in plan
    assert "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION" in plan
    assert "P17_CONTROLLED_PUBLICATION_READINESS_PLAN_VALIDATED" in plan
    assert "DEFINED -> VALIDATED_PLAN -> IN_PROGRESS -> COMPLETE / VALIDATED_READY / NOT_ACTIVATED" in plan

    assert "Version: 4.21" in roadmap
    assert "Phase 17 — Controlled External Publication Readiness" in roadmap
    assert "VALIDATED_READY / NOT_ACTIVATED" in roadmap
    assert "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED" in roadmap
    assert "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION" in roadmap


def test_phase17_plan_preserves_historical_e8_non_activation_boundary():
    plan = _text(PLAN_PATH)
    for token in (
        "E8_EXTERNAL_SHARING = NOT_ACTIVE",
        "E8_PUBLIC_ACTION = NOT_APPROVED",
        "E8_PUBLIC_BACKEND = NOT_DEPLOYED",
        "E8_PUBLIC_GPT = NOT_PUBLISHED",
        "owner E3 Action API and E5 admin dashboard are not public contracts",
        "Any actual launch gate must revalidate then-current platform eligibility and publication requirements",
    ):
        assert token in plan


def test_phase17_plan_sequence_is_complete_and_ordered():
    plan = _text(PLAN_PATH)
    headings = [
        "### P17.0 — Controlled Publication Architecture and Safety Contract",
        "### P17.1 — Deterministic Publication Eligibility Policy",
        "### P17.2 — Public-Safe Projection and Redaction",
        "### P17.3 — Release Manifest, Provenance and Reproducibility",
        "### P17.4 — Provider-Neutral Local/Test Publication Target",
        "### P17.5 — Owner Publication Readiness Projection and Approval Gate",
        "### P17.6 — Phase 17 Validation Matrix / Strategic Readiness Closure",
    ]
    positions = [plan.index(heading) for heading in headings]
    assert positions == sorted(positions)
    for heading in headings:
        section = plan.split(heading, 1)[1].split("### P17.", 1)[0]
        assert "State: `VALIDATED`" in section


def test_phase17_plan_separates_publication_from_truth_and_origin():
    plan = _text(PLAN_PATH)
    required = (
        "publication is a derived presentation layer, not canonical truth state",
        "publisher/publication identity is not automatically the underlying origin",
        "publication lifecycle state is not factual-verification state",
        "publication eligibility is not factual-verification status",
        "release receipt proves only that a publication target accepted or recorded a package",
        "P13.5/P13.6 remains the canonical factual-verification path",
    )
    for phrase in required:
        assert phrase in plan


def test_phase17_plan_requires_public_safe_redaction_and_fail_closed_projection():
    plan = _text(PLAN_PATH)
    required = (
        "public-safe redaction and data minimization occur before any export or publication-target boundary",
        "raw operator feedback",
        "private database paths",
        "missing, stale, ambiguous or non-public-safe canonical references fail closed",
        "public field allowlist rather than owner/admin response pass-through",
        "no public HTTP route is required or authorized by this gate",
    )
    for phrase in required:
        assert phrase in plan


def test_phase17_plan_does_not_pre_authorize_migration_or_real_public_target():
    plan = _text(PLAN_PATH)
    assert "P17.0 introduces no migration: `NONE_FOR_P17_0`" in plan
    assert "Migration `033` is not pre-authorized by this plan" in plan
    assert "local/in-memory/test sink only" in plan
    assert "canonical automated tests perform no real network publication" in plan
    assert "any real target/provider requires a separate explicit owner activation decision" in plan
    assert "paid providers remain forbidden unless separately approved" in plan


def test_phase17_plan_preserves_runtime_security_and_phase18_boundaries():
    plan = _text(PLAN_PATH)
    for token in (
        "runtime storage remains `PROJECT_LOCAL_ONLY`",
        "mixed/shared canonical runtime remains `BLOCKED`",
        "`PRODUCTION_LIVE = NOT_OPERATIONAL`",
        "private GPT Action remains `NOT_CONNECTED`",
        "backend HTTPS remains `NOT_DEPLOYED`",
        "public sharing remains `NOT_ACTIVE`",
        "paid providers remain `NONE_APPROVED`",
        "Phase 18 shared/team runtime is not activated or pre-approved by Phase 17",
    ):
        assert token in plan


def test_phase17_readiness_closure_remains_distinct_from_publication_activation():
    plan = _text(PLAN_PATH)
    assert "Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`" in plan
    assert "Activation gate remains: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`" in plan
    assert "VALIDATED_READY / NOT_ACTIVATED" in plan
    assert "It must not set publication/sharing to active" in plan
    assert "Actual publication requires a later explicit owner decision" in plan


def test_phase17_plan_records_exact_dual_architecture_closure_validation():
    plan = _text(PLAN_PATH)
    assert "full x64 repository regression passes on the exact readiness closure anchor" in plan
    assert "full native ARM64 regression passes on the same exact readiness closure anchor" in plan
    assert "ARM64 host bootstrap, unattended one-tick smoke and systemd contract remain PASS" in plan
    assert "No P17 subphase is promoted from implemented to validated solely because code exists" in plan
    assert "daca1240cb1f99267795b39ddf7da32eb4fa9ec0" in plan
    assert "33937240088" in plan and "101227433133" in plan
    assert "33937240097" in plan and "101227433249" in plan
    assert "716 passed, 2 warnings / SUCCESS" in plan
