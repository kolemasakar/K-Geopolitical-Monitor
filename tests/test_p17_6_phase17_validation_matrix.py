from pathlib import Path

from kgeopolitical_monitor.owner_publication_readiness import (
    OWNER_PUBLICATION_READINESS_BOUNDARY,
    P17_5_GATE,
    P17_5_MIGRATION,
)
from kgeopolitical_monitor.publication_target import (
    P17_4_GATE,
    P17_4_MIGRATION,
    PUBLICATION_TARGET_BOUNDARY,
)
from kgeopolitical_monitor.release_manifest import P17_3_GATE, P17_3_MIGRATION


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "implementation" / "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_PLAN.md"
MATRIX = ROOT / "docs" / "implementation" / "P17_6_VALIDATION_MATRIX.md"
MIGRATIONS = ROOT / "migrations"
BACKEND_API = ROOT / "src" / "kgeopolitical_monitor" / "backend_action_api.py"


def test_p17_6_matrix_defines_validated_readiness_gate_and_separate_activation_gate():
    text = MATRIX.read_text(encoding="utf-8")
    assert "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED" in text
    assert "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION" in text
    assert "VALIDATED_READY / NOT_ACTIVATED" in text
    assert "daca1240cb1f99267795b39ddf7da32eb4fa9ec0" in text
    assert "716 passed, 2 warnings / SUCCESS" in text


def test_p17_6_plan_has_p17_0_through_p17_6_validated():
    text = PLAN.read_text(encoding="utf-8")
    headings = (
        "### P17.0 — Controlled Publication Architecture and Safety Contract",
        "### P17.1 — Deterministic Publication Eligibility Policy",
        "### P17.2 — Public-Safe Projection and Redaction",
        "### P17.3 — Release Manifest, Provenance and Reproducibility",
        "### P17.4 — Provider-Neutral Local/Test Publication Target",
        "### P17.5 — Owner Publication Readiness Projection and Approval Gate",
        "### P17.6 — Phase 17 Validation Matrix / Strategic Readiness Closure",
    )
    for heading in headings:
        section = text.split(heading, 1)[1].split("### P17.", 1)[0]
        assert "State: `VALIDATED`" in section


def test_p17_6_prior_gate_constants_and_no_migration_contracts_are_exact():
    assert P17_3_GATE == "P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED"
    assert P17_3_MIGRATION == "NONE"
    assert P17_4_GATE == "P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED"
    assert P17_4_MIGRATION == "NONE"
    assert P17_5_GATE == "P17_5_OWNER_PUBLICATION_READINESS_PROJECTION_VALIDATED"
    assert P17_5_MIGRATION == "NONE"
    assert not list(MIGRATIONS.glob("033*"))


def test_p17_6_publication_target_and_owner_projection_remain_non_operational():
    target = PUBLICATION_TARGET_BOUNDARY
    assert target.runtime_storage == "PROJECT_LOCAL_ONLY"
    assert target.target_mode == "LOCAL_TEST_ONLY"
    assert target.external_targets == "NOT_ACTIVATED"
    assert target.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert target.production_live == "NOT_OPERATIONAL"
    assert target.public_sharing == "NOT_ACTIVE"
    assert target.paid_providers == "NONE_APPROVED"
    assert target.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"

    owner = OWNER_PUBLICATION_READINESS_BOUNDARY
    assert owner.visibility == "PROJECT_LOCAL_OWNER_READ_ONLY"
    assert owner.publication_activation == "NOT_AUTHORIZED"
    assert owner.public_ingress == "NOT_APPROVED_NOT_DEPLOYED"
    assert owner.backend_https == "NOT_DEPLOYED"
    assert owner.public_gpt_action == "NOT_CONNECTED_NOT_APPROVED"
    assert owner.owner_execution == "DISABLED"
    assert owner.production_live == "NOT_OPERATIONAL"
    assert owner.public_sharing == "NOT_ACTIVE"
    assert owner.paid_providers == "NONE_APPROVED"
    assert owner.activation_gate == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"


def test_p17_6_matrix_records_all_permanent_readiness_boundaries():
    text = MATRIX.read_text(encoding="utf-8")
    required = (
        "Publisher/publication identity is not underlying-origin proof",
        "Publication eligibility cannot promote factual verification",
        "Public-safe redaction/data minimization occurs before export/target boundary",
        "Exact reproducibility/history is never reconstructed",
        "deterministic local/in-memory/test only",
        "No Phase 17 shadow truth store exists",
        "Migration `033` remains uncreated and not pre-authorized",
        "`PROJECT_LOCAL_ONLY`",
        "`BLOCKED`",
        "`PRODUCTION_LIVE = NOT_OPERATIONAL`",
        "`NOT_CONNECTED_NOT_APPROVED`",
        "`NOT_ACTIVE`",
        "`NONE_APPROVED`",
        "Phase 18 shared/team runtime is not activated or pre-approved",
    )
    for item in required:
        assert item in text


def test_p17_6_matrix_preserves_exact_subphase_validation_anchors():
    text = MATRIX.read_text(encoding="utf-8")
    for anchor in (
        "e7281428cc226c4f68223f3b89503a3aa47a92fa",
        "3b26863f622b5db3cc07cda156f4ea7b2be9d889",
        "8f2e920fd727597286ec691d49c74dd600df35bd",
        "85453a38bacfcb64c69be4d1b671152f6a54849c",
        "36548f79cf254621646fa2e2bf863b70944754d2",
        "69010a348cd35fd0b2361c9b32c5baa9428c5816",
        "daca1240cb1f99267795b39ddf7da32eb4fa9ec0",
    ):
        assert anchor in text


def test_p17_6_owner_readiness_projection_is_not_exposed_by_existing_backend_action_api():
    if BACKEND_API.exists():
        source = BACKEND_API.read_text(encoding="utf-8")
        assert "owner_publication_readiness" not in source
        assert "publication_target" not in source


def test_p17_6_closure_records_dual_architecture_and_arm_host_checks():
    text = MATRIX.read_text(encoding="utf-8")
    assert "full x64 repository regression" in text
    assert "full native ARM64 repository regression on the same exact commit" in text
    assert "native architecture check `aarch64`: PASS" in text
    assert "ARM64 host bootstrap: PASS" in text
    assert "ARM64 unattended one-tick smoke with no execution side effect: PASS" in text
    assert "ARM64 systemd contract: PASS" in text
    assert "33937240088" in text and "101227433133" in text
    assert "33937240097" in text and "101227433249" in text

def test_p17_6_current_account_capability_blocker_is_canonical_and_non_promotional():
    decision = ROOT / "docs" / "decisions" / "PHASE_17_CURRENT_ACCOUNT_PUBLICATION_CAPABILITY_BOUNDARY_2026-09-05.md"
    result = ROOT / "docs" / "implementation" / "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_RESULT.md"
    checkpoint = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-05_PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED_READY.md"
    for path in (PLAN, MATRIX, decision, result, checkpoint):
        text = path.read_text(encoding="utf-8")
        assert "PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY" in text
    matrix_text = MATRIX.read_text(encoding="utf-8")
    assert "Current account external-publication capability is `UNAVAILABLE`" in matrix_text
    assert "blocks real publication independently of owner approval" in matrix_text
