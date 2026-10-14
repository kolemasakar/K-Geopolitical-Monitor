"""Fail-closed underlying-origin assessment for correlated source observations.

Origin groups are explicit provenance metadata only. UNKNOWN never earns
independence credit. Equal origin groups explicitly deny independence credit.
"""
from __future__ import annotations
from .research_request_v1 import _ID

UNKNOWN="UNKNOWN"
SAME_ORIGIN="SAME_ORIGIN"
DISTINCT_ORIGIN="DISTINCT_ORIGIN"

def validate_origin_group(value):
    if value is None:
        return None
    if not isinstance(value,str) or not _ID.fullmatch(value):
        raise ValueError("invalid origin group")
    return value

def assess_origin_groups(observations):
    if not isinstance(observations,list) or not observations:
        raise ValueError("observations required")
    groups=[]
    for item in observations:
        if not isinstance(item,dict):
            raise ValueError("invalid observation")
        group=validate_origin_group(item.get("origin_group"))
        if group is None:
            return {"assessment":UNKNOWN,"independent_origin_credit":False,
                    "origin_groups":[]}
        groups.append(group)
    unique=sorted(set(groups))
    if len(unique)==1:
        return {"assessment":SAME_ORIGIN,"independent_origin_credit":False,
                "origin_groups":unique}
    return {"assessment":DISTINCT_ORIGIN,"independent_origin_credit":True,
            "origin_groups":unique}
