from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "implementation" / "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_PLAN.md"


def test_p17_6_canonical_plan_contract_wording_is_preserved_at_closure():
    text = PLAN.read_text(encoding="utf-8")
    required = (
        "publication lifecycle state is not factual-verification state",
        "publication eligibility is not factual-verification status",
        "release receipt proves only that a publication target accepted or recorded a package",
        "P13.5/P13.6 remains the canonical factual-verification path",
        "public field allowlist rather than owner/admin response pass-through",
        "no public HTTP route is required or authorized by this gate",
        "Phase 18 shared/team runtime is not activated or pre-approved by Phase 17",
        "full x64 repository regression passes on the exact readiness closure anchor",
        "full native ARM64 regression passes on the same exact readiness closure anchor",
        "ARM64 host bootstrap, unattended one-tick smoke and systemd contract remain PASS",
    )
    for phrase in required:
        assert phrase in text
