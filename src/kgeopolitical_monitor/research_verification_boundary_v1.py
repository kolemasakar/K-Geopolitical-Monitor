"""Fail-closed boundary between corroboration and factual verification.

This module determines eligibility only. It never mutates a claim to VERIFIED.
"""
from __future__ import annotations

ELIGIBLE="ELIGIBLE_FOR_EXPLICIT_VERIFICATION"
INELIGIBLE="INELIGIBLE"
EVENT_ONLY="EVENT_CORROBORATED_CLAIM_UNRESOLVED"

def assess_verification_boundary(corroboration):
    if not isinstance(corroboration,dict):
        raise ValueError("corroboration item required")
    required={"origin_assessment","independent_origin_credit","ambiguous",
              "claim_relation","source_ids","origin_groups"}
    if not required <= set(corroboration):
        raise ValueError("incomplete corroboration item")
    blockers=[]
    if corroboration["ambiguous"]:
        blockers.append("AMBIGUOUS_ASSOCIATION")
    if corroboration["origin_assessment"]!="DISTINCT_ORIGIN" or not corroboration["independent_origin_credit"]:
        blockers.append("NO_INDEPENDENT_ORIGIN_CREDIT")
    if not isinstance(corroboration["source_ids"],list) or len(set(corroboration["source_ids"]))<2:
        blockers.append("INSUFFICIENT_SOURCE_PATHS")
    if not isinstance(corroboration["origin_groups"],list) or len(set(corroboration["origin_groups"]))<2:
        blockers.append("INSUFFICIENT_DISTINCT_ORIGINS")
    relation=corroboration["claim_relation"]
    if relation=="DIFFERS":
        return {"verification_eligibility":EVENT_ONLY,
                "verification_blockers":sorted(set(blockers+["CLAIM_DISAGREEMENT"])),
                "automatic_verification":False}
    if relation=="UNKNOWN":
        blockers.append("CLAIM_AGREEMENT_UNKNOWN")
    if blockers:
        return {"verification_eligibility":INELIGIBLE,
                "verification_blockers":sorted(set(blockers)),
                "automatic_verification":False}
    if relation!="AGREES":
        raise ValueError("invalid claim relation")
    return {"verification_eligibility":ELIGIBLE,
            "verification_blockers":[],
            "automatic_verification":False}
