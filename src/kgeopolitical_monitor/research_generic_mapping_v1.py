"""Auditable mapping of explicit official-source facts into generic identities.

This layer accepts only already-extracted structured facts. It does not perform
NLP, synonym inference, fuzzy matching, or source-independence assessment.
"""
from __future__ import annotations
from .research_request_v1 import _ID, _utc
from .research_generic_identity_v1 import (
    validate_generic_event_descriptor, generic_event_identity,
    validate_generic_claim_descriptor, generic_claim_signature)

SCHEMA="kgm.research.generic-mapping.v1"

def map_explicit_fact(fact):
    fields={"schema_version","source_id","origin_group","public_url",
            "event_descriptor","claim_descriptor","source_fact_id"}
    if not isinstance(fact,dict) or set(fact)!=fields:
        raise ValueError("unapproved explicit mapping fields")
    if fact["schema_version"]!=SCHEMA:
        raise ValueError("invalid explicit mapping schema")
    for field in ("source_id","origin_group","source_fact_id"):
        if not isinstance(fact[field],str) or not _ID.fullmatch(fact[field]):
            raise ValueError("invalid explicit mapping identity")
    url=fact["public_url"]
    if not isinstance(url,str) or not url.startswith("https://") or len(url)>2048:
        raise ValueError("invalid explicit mapping provenance")
    event=validate_generic_event_descriptor(fact["event_descriptor"])
    claim=validate_generic_claim_descriptor(fact["claim_descriptor"])
    return {"source_id":fact["source_id"],"origin_group":fact["origin_group"],
            "source_fact_id":fact["source_fact_id"],"public_url":url,
            "event_descriptor":event,"claim_descriptor":claim,
            "event_identity":generic_event_identity(event),
            "claim_signature":generic_claim_signature(claim)}

def correlate_explicit_facts(facts):
    if not isinstance(facts,list) or not 2<=len(facts)<=20:
        raise ValueError("explicit mapping fact batch required")
    mapped=[map_explicit_fact(x) for x in facts]
    event_ids={x["event_identity"] for x in mapped}
    claim_sigs={x["claim_signature"] for x in mapped}
    source_ids={x["source_id"] for x in mapped}
    origin_groups={x["origin_group"] for x in mapped}
    if len(source_ids)!=len(mapped):
        raise ValueError("duplicate source in explicit mapping batch")
    return {"event_match":len(event_ids)==1,
            "claim_match":len(claim_sigs)==1,
            "independent_origin_candidate":len(origin_groups)>=2,
            "event_identity":next(iter(event_ids)) if len(event_ids)==1 else None,
            "claim_signature":next(iter(claim_sigs)) if len(claim_sigs)==1 else None,
            "source_ids":sorted(source_ids),"origin_groups":sorted(origin_groups),
            "mapped_facts":mapped}
