"""Typed source-portfolio policy for policy-bound research execution."""
from __future__ import annotations
import hashlib
from .research_request_v1 import validate_request, _ID
from .research_storage_v1 import canonical_bytes

SCHEMA="kgm.source.policy.v1"

def validate_source_policy(request, policy):
    validate_request(request)
    fields={"schema_version","consumer_id","policy_version",
            "required_source_ids","optional_source_ids","max_observations"}
    if not isinstance(policy,dict) or set(policy)!=fields:
        raise ValueError("unapproved source policy fields")
    if policy["schema_version"]!=SCHEMA:
        raise ValueError("invalid source policy schema")
    if (policy["consumer_id"],policy["policy_version"]) != (
        request["consumer_id"],request["policy_version"]):
        raise ValueError("source policy/request mismatch")
    required=policy["required_source_ids"]; optional=policy["optional_source_ids"]
    if not isinstance(required,list) or not 1<=len(required)<=50:
        raise ValueError("required source portfolio missing/unbounded")
    if not isinstance(optional,list) or len(optional)>50:
        raise ValueError("optional source portfolio unbounded")
    for values in (required,optional):
        if len(values)!=len(set(values)):
            raise ValueError("duplicate source id in policy")
        if any(not isinstance(x,str) or not _ID.fullmatch(x) for x in values):
            raise ValueError("invalid source id in policy")
    if set(required)&set(optional):
        raise ValueError("required/optional source overlap")
    if type(policy["max_observations"]) is not int or not 1<=policy["max_observations"]<=100:
        raise ValueError("invalid source observation bound")
    return policy

def source_policy_digest(request, policy):
    validate_source_policy(request,policy)
    return hashlib.sha256(canonical_bytes(policy)).hexdigest()

def validate_adapter_mapping(request, policy, adapters):
    validate_source_policy(request,policy)
    if not isinstance(adapters,dict) or not adapters:
        raise ValueError("adapter mapping required")
    if any(not isinstance(k,str) or not _ID.fullmatch(k) or not callable(v)
           for k,v in adapters.items()):
        raise ValueError("invalid adapter mapping")
    keys=set(adapters)
    required=set(policy["required_source_ids"])
    allowed=required|set(policy["optional_source_ids"])
    missing=sorted(required-keys)
    if missing:
        raise ValueError("required source adapter missing: "+",".join(missing))
    unknown=sorted(keys-allowed)
    if unknown:
        raise ValueError("unapproved source adapter: "+",".join(unknown))
    if len(keys)>100:
        raise ValueError("adapter mapping unbounded")
    return adapters
