"""Conservative generic event/claim identity families for geopolitical research.

Generic identities are derived only from explicit controlled descriptors. This
module performs no NLP, synonym inference or fuzzy semantic matching.
"""
from __future__ import annotations
import hashlib
from .research_request_v1 import _ID, _utc
from .research_storage_v1 import canonical_bytes

EVENT_FAMILIES={"POLITICAL","DIPLOMATIC","MILITARY","ECONOMIC"}
ACTIONS={"ANNOUNCE","ADOPT","APPROVE","REJECT","IMPOSE","LIFT","MEET",
         "SIGN","RATIFY","VOTE","APPOINT","RESIGN","DEPLOY","WITHDRAW",
         "STRIKE","SANCTION","NEGOTIATE","AGREE","STATEMENT","OTHER"}
CLAIM_TYPES={"STATUS","DECISION","POSITION","QUANTITY","DATE","ACTOR",
             "TARGET","LOCATION","OUTCOME","OTHER"}

def _key(value, field):
    if not isinstance(value,str) or not _ID.fullmatch(value):
        raise ValueError("invalid "+field)
    return value.lower()

def _keys(values, field, *, allow_empty=False):
    if not isinstance(values,list) or (not values and not allow_empty) or len(values)>20:
        raise ValueError("invalid "+field)
    normalized=sorted({_key(x,field) for x in values})
    if len(normalized)!=len(values):
        raise ValueError("duplicate "+field)
    return normalized

def validate_generic_event_descriptor(desc):
    fields={"family","event_date_utc","action_key","actor_keys",
            "target_keys","subject_key","location_key"}
    if not isinstance(desc,dict) or set(desc)!=fields:
        raise ValueError("invalid generic event descriptor")
    family=desc["family"]
    if family not in EVENT_FAMILIES:
        raise ValueError("invalid generic event family")
    dt=_utc(desc["event_date_utc"])
    if desc["event_date_utc"]!=dt.strftime("%Y-%m-%dT00:00:00Z"):
        raise ValueError("generic event date must be UTC day boundary")
    action=desc["action_key"]
    if action not in ACTIONS:
        raise ValueError("invalid generic action key")
    actors=_keys(desc["actor_keys"],"actor key")
    targets=_keys(desc["target_keys"],"target key",allow_empty=True)
    subject=_key(desc["subject_key"],"subject key")
    location=None if desc["location_key"] is None else _key(desc["location_key"],"location key")
    return {"family":family,"event_date_utc":desc["event_date_utc"],
            "action_key":action,"actor_keys":actors,"target_keys":targets,
            "subject_key":subject,"location_key":location}

def generic_event_identity(desc):
    canonical=validate_generic_event_descriptor(desc)
    digest=hashlib.sha256(canonical_bytes(canonical)).hexdigest()[:32]
    identity="geo-"+canonical["family"].lower()+"-"+canonical["event_date_utc"][:10].replace("-","")+"-"+digest
    if not _ID.fullmatch(identity):
        raise ValueError("invalid generic event identity")
    return identity

def validate_generic_claim_descriptor(desc):
    fields={"claim_type","value_keys","unit_key"}
    if not isinstance(desc,dict) or set(desc)!=fields:
        raise ValueError("invalid generic claim descriptor")
    ctype=desc["claim_type"]
    if ctype not in CLAIM_TYPES:
        raise ValueError("invalid generic claim type")
    values=_keys(desc["value_keys"],"claim value")
    unit=None if desc["unit_key"] is None else _key(desc["unit_key"],"claim unit")
    return {"claim_type":ctype,"value_keys":values,"unit_key":unit}

def generic_claim_signature(desc):
    canonical=validate_generic_claim_descriptor(desc)
    digest=hashlib.sha256(canonical_bytes(canonical)).hexdigest()[:32]
    signature="claim-"+canonical["claim_type"].lower()+"-"+digest
    if not _ID.fullmatch(signature):
        raise ValueError("invalid generic claim signature")
    return signature
