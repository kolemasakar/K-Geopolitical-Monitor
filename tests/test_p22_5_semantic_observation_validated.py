import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"docs/evidence/P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED_2026-09-19.json"
STATE=ROOT/"docs/state/CURRENT_PROJECT_STATE.json"
RESULT=ROOT/"docs/implementation/P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED_RESULT.md"
CHECKPOINT=ROOT/"docs/checkpoints/PROJECT_CHECKPOINT_2026-09-19_P22_5_SEMANTIC_CORPUS_VERIFICATION_OBSERVATION_VALIDATED.md"

def _json(p): return json.loads(p.read_text(encoding="utf-8"))

def test_p22_5_post_bridge_exact_cohort_is_canonical_and_fail_closed():
    x=_json(E)
    assert x["canonical_code_sha"]=="a4dfeee3765116e6b2c261413129b7329f754202"
    assert x["legacy_analysis"]["claim_count"]==28
    assert x["canonical_semantic"]["semantic_claim_versions"]==28
    assert x["canonical_semantic"]["semantic_claim_links"]==56
    assert x["canonical_semantic"]["semantic_evidence_relation_versions"]==28
    assert x["canonical_semantic"]["semantic_verification_decision_versions"]==28
    assert x["verification_distribution"]=={
        "DETECTED":28,
        "PARTLY_VERIFIED":0,
        "VERIFIED":0,
        "DISPUTED":0,
        "UNVERIFIABLE":0,
    }
    assert x["evidence_distribution"]["ATTRIBUTION_ONLY"]==28
    assert x["canonical_semantic"]["semantic_independence_assessment_versions"]==0
    assert x["provenance_observation"]["automatic_factual_independence_credit"]==0
    assert x["database_integrity"]=="ok"

def test_p22_5_does_not_promote_legacy_truth_and_opens_only_p22_6():
    x=_json(E); s=_json(STATE)
    assert x["p13_6_compatibility"]["LINKED_WITH_DECISION"]==28
    assert x["p13_6_compatibility"]["legacy_status_promoted_count"]==0
    assert x["p13_6_compatibility"]["legacy_confidence_promoted_count"]==0
    assert x["verification_authority"]=="P13.5/P13.6"
    major, minor = map(int, s["roadmap"]["state_sync_version"].split("."))
    assert major == 4 and minor >= 56
    assert s["roadmap"]["current_position"].startswith("PHASE_22_")
    assert s["phase22"]["p22_5_state"]=="VALIDATED_WITH_ALL_CLAIMS_DETECTED_AND_UNDERLYING_ORIGIN_UNRESOLVED"
    assert s["phase22"]["next_gate"] in {"P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED", "P22_7_OWNER_UTILITY_QUALITY_OBSERVATION_VALIDATED", "PHASE_22_OPERATIONAL_EVIDENCE_HIGH_PRIORITY_COVERAGE_VALIDATED"}
    assert s["phase22"]["persistent_owner_operation"]=="NOT_ACTIVATED"
    assert s["runtime"]["production_live"]=="NOT_OPERATIONAL"
    assert RESULT.exists() and CHECKPOINT.exists()
