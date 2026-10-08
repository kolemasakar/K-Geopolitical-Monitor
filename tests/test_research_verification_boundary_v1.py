import pytest
from kgeopolitical_monitor.research_verification_boundary_v1 import (
    assess_verification_boundary, ELIGIBLE, INELIGIBLE, EVENT_ONLY)

def base():
    return {"origin_assessment":"DISTINCT_ORIGIN",
            "independent_origin_credit":True,
            "ambiguous":False,
            "claim_relation":"AGREES",
            "source_ids":["source-a","source-b"],
            "origin_groups":["origin-a","origin-b"]}

def test_distinct_origin_agreement_is_only_explicit_verification_eligible():
    r=assess_verification_boundary(base())
    assert r["verification_eligibility"]==ELIGIBLE
    assert r["verification_blockers"]==[]
    assert r["automatic_verification"] is False

def test_claim_disagreement_is_event_only_not_verified():
    x=base(); x["claim_relation"]="DIFFERS"
    r=assess_verification_boundary(x)
    assert r["verification_eligibility"]==EVENT_ONLY
    assert "CLAIM_DISAGREEMENT" in r["verification_blockers"]
    assert r["automatic_verification"] is False

def test_same_origin_is_ineligible():
    x=base(); x["origin_assessment"]="SAME_ORIGIN"; x["independent_origin_credit"]=False
    x["origin_groups"]=["origin-a"]
    r=assess_verification_boundary(x)
    assert r["verification_eligibility"]==INELIGIBLE
    assert "NO_INDEPENDENT_ORIGIN_CREDIT" in r["verification_blockers"]

def test_ambiguity_is_ineligible():
    x=base(); x["ambiguous"]=True; x["independent_origin_credit"]=False
    r=assess_verification_boundary(x)
    assert r["verification_eligibility"]==INELIGIBLE
    assert "AMBIGUOUS_ASSOCIATION" in r["verification_blockers"]

def test_unknown_claim_agreement_is_ineligible():
    x=base(); x["claim_relation"]="UNKNOWN"
    r=assess_verification_boundary(x)
    assert r["verification_eligibility"]==INELIGIBLE
    assert "CLAIM_AGREEMENT_UNKNOWN" in r["verification_blockers"]
