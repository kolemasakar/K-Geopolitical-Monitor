"""Strict source-text mapping profiles for generic geopolitical identities.

Profiles attach descriptors only when every source-specific required phrase is
present in normalized source text. No fuzzy matching or NLP inference.
"""
from __future__ import annotations
import copy
import re
from .research_generic_identity_v1 import (
    validate_generic_event_descriptor, generic_event_identity,
    validate_generic_claim_descriptor, generic_claim_signature)

def _norm(value):
    if not isinstance(value,str):
        raise ValueError("mapping source text required")
    return " ".join(value.casefold().split())

def validate_mapping_profile(profile, *, source_id):
    fields={"source_id","required_phrases","event_descriptor","claim_descriptor"}
    if not isinstance(profile,dict) or set(profile)!=fields:
        raise ValueError("invalid mapping profile")
    if profile["source_id"]!=source_id:
        raise ValueError("mapping profile source mismatch")
    phrases=profile["required_phrases"]
    if not isinstance(phrases,list) or not 1<=len(phrases)<=20:
        raise ValueError("invalid mapping required phrases")
    normalized=[]
    for phrase in phrases:
        p=_norm(phrase)
        if not 2<=len(p)<=200:
            raise ValueError("invalid mapping required phrase")
        normalized.append(p)
    if len(set(normalized))!=len(normalized):
        raise ValueError("duplicate mapping required phrase")
    validate_generic_event_descriptor(profile["event_descriptor"])
    validate_generic_claim_descriptor(profile["claim_descriptor"])
    return profile

def apply_mapping_profile(observation, source_text, profile):
    if not isinstance(observation,dict):
        raise ValueError("observation required")
    source_id=observation.get("source_id")
    validate_mapping_profile(profile,source_id=source_id)
    text=_norm(source_text)
    missing=[p for p in profile["required_phrases"] if _norm(p) not in text]
    if missing:
        return dict(observation),False
    out=copy.deepcopy(observation)
    out["event_descriptor"]=copy.deepcopy(profile["event_descriptor"])
    out["claim_descriptor"]=copy.deepcopy(profile["claim_descriptor"])
    out["event_identity"]=generic_event_identity(out["event_descriptor"])
    out["claim_signature"]=generic_claim_signature(out["claim_descriptor"])
    return out,True
