import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"docs/evidence/P22_5_SEMANTIC_CORPUS_OBSERVATION_2026-09-19.json"
STATE=ROOT/"docs/state/CURRENT_PROJECT_STATE.json"

def _json(p): return json.loads(p.read_text(encoding="utf-8"))

def test_p22_5_observation_records_real_collection_but_zero_canonical_semantic_corpus():
    x=_json(E)
    assert x["canonical_base_sha"]=="eabd9ed98cfa3e266fdee5933f69bed2d459b83b"
    assert x["collection"]=={"status":"COMPLETED","item_count":28,"source_success_count":2,"source_failure_count":0,"failures":[]}
    assert x["legacy_analysis"]["claim_count"]==28
    assert x["legacy_analysis"]["status_distribution"]=={"DETECTED":28}
    assert x["canonical_semantic"]=={
      "semantic_claim_versions":0,
      "semantic_claim_links":0,
      "semantic_evidence_relation_versions":0,
      "semantic_factual_confidence_versions":0,
      "semantic_verification_decision_versions":0,
    }
    assert x["canonical_semantic_corpus_observed"] is False

def test_p22_5_gap_does_not_promote_legacy_state_or_open_p22_6():
    x=_json(E); s=_json(STATE)
    assert x["decision"]=="BLOCKED_ON_CANONICAL_SEMANTIC_INGESTION_GAP"
    assert x["verification_yield_impact"]=="NOT_OBSERVED"
    assert x["verification_authority"]=="P13.5/P13.6"
    assert s["phase22"]["p22_5_state"] in {"BLOCKED_ON_CANONICAL_SEMANTIC_INGESTION_GAP", "VALIDATED_WITH_ALL_CLAIMS_DETECTED_AND_UNDERLYING_ORIGIN_UNRESOLVED"}
    assert s["phase22"]["next_gate"] in {"P22_5_CANONICAL_SEMANTIC_INGESTION_BRIDGE_IMPLEMENTATION", "P22_6_DOWNSTREAM_INTELLIGENCE_IMPACT_VALIDATED"}
    assert s["phase22"]["persistent_owner_operation"]=="NOT_ACTIVATED"
    assert s["runtime"]["production_live"]=="NOT_OPERATIONAL"
