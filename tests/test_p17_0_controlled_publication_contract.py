from pathlib import Path

from kgeopolitical_monitor.controlled_publication_contract import (
    CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION,
    P17_0_GATE,
    PUBLICATION_ELIGIBILITY_STATES,
    PUBLICATION_TARGET_STATES,
    controlled_publication_architecture_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "kgeopolitical_monitor" / "controlled_publication_contract.py"


def test_p17_0_contract_identity_and_gate_are_exact():
    contract = controlled_publication_architecture_contract()
    assert CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION == "KGM_CONTROLLED_PUBLICATION_ARCHITECTURE_V1"
    assert P17_0_GATE == "P17_0_CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT_VALIDATED"
    assert contract["version"] == CONTROLLED_PUBLICATION_ARCHITECTURE_VERSION
    assert contract["gate"] == P17_0_GATE
    assert contract["phase"] == "P17.0"
    assert contract["status"] == "ARCHITECTURE_BASELINE"


def test_p17_0_entities_and_separation_chain_are_complete():
    contract = controlled_publication_architecture_contract()
    entities = contract["entities"]
    assert set(entities) == {
        "canonical_intelligence_state",
        "publication_eligibility",
        "public_safe_projection",
        "release_manifest",
        "publication_package",
        "publication_target_attempt",
        "release_receipt",
    }
    assert contract["separation_chain"] == (
        "CANONICAL_INTELLIGENCE_STATE",
        "PUBLICATION_ELIGIBILITY",
        "PUBLIC_SAFE_PROJECTION",
        "RELEASE_MANIFEST",
        "PUBLICATION_PACKAGE",
        "LOCAL_TEST_PUBLICATION_TARGET",
        "RELEASE_RECEIPT",
    )
    assert PUBLICATION_ELIGIBILITY_STATES == ("PENDING", "ELIGIBLE", "BLOCKED")
    assert PUBLICATION_TARGET_STATES == ("PREPARED", "ACCEPTED", "FAILED")


def test_p17_0_publication_is_non_promotional_to_truth_and_origin():
    contract = controlled_publication_architecture_contract()
    rules = " ".join(contract["publication_truth_contract"]["rules"])
    invariants = " ".join(contract["epistemic_invariants"])

    assert "derived presentation layer, not canonical truth state" in rules
    assert "not automatically the underlying origin" in rules
    assert "not factual-verification state" in rules
    assert "cannot promote factual verification" in rules
    assert "not event evidence, independent corroboration or truth operators" in rules
    assert "P13.5" in rules and "P13.6" in rules
    assert "Publisher/publication identity is not underlying-origin proof" in invariants


def test_p17_0_public_safe_projection_is_allowlist_fail_closed_and_redacted():
    contract = controlled_publication_architecture_contract()
    boundary = contract["public_safe_projection_boundary"]
    rules = " ".join(boundary["rules"])
    forbidden = set(boundary["forbidden_public_payload_classes"])

    assert boundary["mode"] == "STRICT_ALLOWLIST_FAIL_CLOSED"
    assert "before any export or publication-target boundary" in rules
    assert "Missing, stale, ambiguous or non-public-safe canonical references fail closed" in rules
    assert "Owner/admin API responses are not public payload pass-throughs" in rules
    assert {
        "SECRETS",
        "AUTHENTICATION_MATERIAL",
        "OWNER_ADMIN_TOKENS",
        "PRIVATE_DATABASE_PATHS",
        "RAW_OPERATOR_FEEDBACK",
        "UNNECESSARY_RUNTIME_METADATA",
        "NON_PUBLIC_OPERATIONAL_DIAGNOSTICS",
    } <= forbidden


def test_p17_0_reproducibility_contract_forbids_reconstructed_exact_history():
    contract = controlled_publication_architecture_contract()
    rules = " ".join(contract["reproducibility_contract"]["rules"])

    assert "only from persisted instrumentation" in rules
    assert "NOT_INSTRUMENTED" in rules
    assert "never labeled exact" in rules
    assert "cannot invent missing instrumentation" in rules


def test_p17_0_target_contract_is_local_test_only_and_non_operational():
    contract = controlled_publication_architecture_contract()
    target = contract["publication_target_contract"]
    rules = " ".join(target["rules"])

    assert target["mode"] == "LOCAL_TEST_ONLY"
    assert "no real network publication" in rules
    assert "GPT Store target is enabled by P17.0" in rules
    assert "isolated from monitoring and canonical analytical persistence" in rules
    assert "Target receipts are publication evidence only" in rules
    assert "later explicit owner activation decision" in rules


def test_p17_0_historical_e8_boundary_remains_non_active():
    boundary = controlled_publication_architecture_contract()["historical_e8_boundary"]
    assert boundary == {
        "owner_only_publication_readiness": "APPROVED",
        "external_sharing": "NOT_ACTIVE",
        "public_action": "NOT_APPROVED",
        "public_backend": "NOT_DEPLOYED",
        "public_gpt": "NOT_PUBLISHED",
        "owner_api_public_reuse": "FORBIDDEN",
        "admin_dashboard_public_reuse": "FORBIDDEN",
        "platform_requirements": "REVALIDATE_AT_ACTUAL_LAUNCH_GATE",
    }


def test_p17_0_readiness_and_activation_are_separate():
    contract = controlled_publication_architecture_contract()
    activation = contract["activation_contract"]
    assert activation["readiness_gate"] == "PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED"
    assert activation["activation_gate"] == "PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION"
    assert activation["readiness_may_reach"] == "VALIDATED_READY / NOT_ACTIVATED"
    assert activation["actual_publication"] == "NOT_AUTHORIZED_BY_P17_0"


def test_p17_0_runtime_security_boundary_remains_closed():
    boundary = controlled_publication_architecture_contract()["runtime_security_boundary"]
    assert boundary["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert boundary["mixed_shared_canonical_runtime"] == "BLOCKED"
    assert boundary["production_live"] == "NOT_OPERATIONAL"
    assert boundary["public_ingress"] == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary["private_gpt_action"] == "NOT_CONNECTED"
    assert boundary["backend_https"] == "NOT_DEPLOYED"
    assert boundary["admin_dashboard"] == "NOT_DEPLOYED"
    assert boundary["public_sharing"] == "NOT_ACTIVE"
    assert boundary["paid_providers"] == "NONE_APPROVED"
    assert boundary["owner_execution"] == "DISABLED"
    assert boundary["external_publication_activation"] == "NOT_AUTHORIZED_BY_P17_0"


def test_p17_0_compatibility_has_no_migration_and_no_phase18_activation():
    compatibility = controlled_publication_architecture_contract()["compatibility"]
    assert compatibility["migration_033"] == "NONE_FOR_P17_0"
    assert compatibility["canonical_verification"] == "P13_5_THROUGH_P13_6_UNCHANGED"
    assert compatibility["phase_14_owner_activation"] == "UNCHANGED_OWNER_DECISION_REQUIRED"
    assert compatibility["phase_18_shared_runtime"] == "NOT_ACTIVATED_NEW_ARCHITECTURE_APPROVAL_REQUIRED"


def test_p17_0_contract_is_detached_and_module_is_non_operational():
    first = controlled_publication_architecture_contract()
    second = controlled_publication_architecture_contract()
    first["runtime_security_boundary"]["public_sharing"] = "MUTATED_TEST_VALUE"
    assert second["runtime_security_boundary"]["public_sharing"] == "NOT_ACTIVE"

    source = CONTRACT_PATH.read_text(encoding="utf-8")
    for forbidden_runtime_dependency in ("FastAPI", "uvicorn", "requests", "httpx", "socket"):
        assert forbidden_runtime_dependency not in source
