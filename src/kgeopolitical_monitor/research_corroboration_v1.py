"""Bounded event-level corroboration metadata for owner-pilot typed results.

Association and origin-level independence are kept separate from factual
verification. One physical event yields at most one independence credit.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from .research_event_association_v1 import associate_earthquakes
from .research_origin_assessment_v1 import assess_origin_groups
from .research_storage_v1 import canonical_bytes
from .research_verification_boundary_v1 import assess_verification_boundary


def _generic_corroboration_groups(observations,max_groups):
    usable=[x for x in observations if isinstance(x,dict) and
            x.get("status") in {"SUCCESS","PARTIAL"} and
            isinstance(x.get("event_descriptor"),dict) and
            isinstance(x.get("event_identity"),str)]
    groups=defaultdict(list)
    for item in usable:
        groups[item["event_identity"]].append(item)
    report=[]
    for identity,members in sorted(groups.items()):
        source_ids=sorted({x["source_id"] for x in members})
        if len(source_ids)<2:
            continue
        if len(report)>=max_groups:
            raise ValueError("corroboration group bound exceeded")
        ordered=sorted(members,key=lambda x:(x["source_id"],x["observation_id"]))
        duplicate_source=len(source_ids)!=len(ordered)
        origin=assess_origin_groups(ordered)
        signatures=[x.get("claim_signature") for x in ordered]
        claim_relation=("UNKNOWN" if any(x is None for x in signatures)
                        else ("AGREES" if len(set(signatures))==1 else "DIFFERS"))
        member_refs=[{"source_id":x["source_id"],"observation_id":x["observation_id"],
                      "origin_group":x.get("origin_group"),
                      "claim_signature":x.get("claim_signature")} for x in ordered]
        seed={"event_identity":identity,
              "members":[(x["source_id"],x["observation_id"]) for x in ordered]}
        cid="corr-"+hashlib.sha256(canonical_bytes(seed)).hexdigest()[:24]
        item={"corroboration_id":cid,"members":member_refs,
              "source_ids":source_ids,"max_delta_seconds":0.0,
              "max_distance_km":0.0,"claim_relation":claim_relation,
              "origin_assessment":origin["assessment"],
              "origin_groups":origin["origin_groups"],
              "independent_origin_credit":bool(origin["independent_origin_credit"] and not duplicate_source),
              "ambiguous":duplicate_source,"factual_verification_credit":False}
        item.update(assess_verification_boundary(item))
        report.append(item)
    return report

def build_corroboration_report(observations, *, max_groups=100,
                               max_seconds=30, max_km=50):
    if not isinstance(observations,list):
        raise ValueError("observation list required")
    usable=[x for x in observations if isinstance(x,dict) and
            x.get("status") in {"SUCCESS","PARTIAL"} and
            isinstance(x.get("event_parameters"),dict)]
    n=len(usable)
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb:
            parent[rb]=ra

    edges=[]
    per_other_source=defaultdict(int)
    for i,left in enumerate(usable):
        for j in range(i+1,n):
            right=usable[j]
            if left["source_id"]==right["source_id"]:
                continue
            assoc=associate_earthquakes(left,right,max_seconds=max_seconds,max_km=max_km)
            if not assoc["match"]:
                continue
            union(i,j)
            edges.append((i,j,assoc))
            per_other_source[(i,right["source_id"])]+=1
            per_other_source[(j,left["source_id"])]+=1

    components=defaultdict(list)
    for i in range(n):
        components[find(i)].append(i)

    edge_by_root=defaultdict(list)
    for i,j,assoc in edges:
        edge_by_root[find(i)].append((i,j,assoc))

    report=[]
    for root,members_idx in components.items():
        source_ids=sorted({usable[i]["source_id"] for i in members_idx})
        if len(source_ids)<2:
            continue
        if len(report)>=max_groups:
            raise ValueError("corroboration group bound exceeded")
        members=[usable[i] for i in sorted(members_idx,key=lambda k:(usable[k]["source_id"],usable[k]["observation_id"]))]
        ambiguous=any(per_other_source[(i,other)]>1
                      for i in members_idx
                      for other in source_ids
                      if other!=usable[i]["source_id"])
        origin=assess_origin_groups(members)
        signatures=[x.get("claim_signature") for x in members]
        claim_relation=("UNKNOWN" if any(x is None for x in signatures)
                        else ("AGREES" if len(set(signatures))==1 else "DIFFERS"))
        component_edges=edge_by_root[root]
        max_dt=max((x[2]["delta_seconds"] for x in component_edges),default=0.0)
        max_km_seen=max((x[2]["distance_km"] for x in component_edges),default=0.0)
        member_refs=[{"source_id":x["source_id"],"observation_id":x["observation_id"],
                      "origin_group":x.get("origin_group"),
                      "claim_signature":x.get("claim_signature")} for x in members]
        seed={"members":[(x["source_id"],x["observation_id"]) for x in members]}
        cid="corr-"+hashlib.sha256(canonical_bytes(seed)).hexdigest()[:24]
        item={"corroboration_id":cid,"members":member_refs,
            "source_ids":source_ids,"max_delta_seconds":round(max_dt,3),
            "max_distance_km":round(max_km_seen,3),"claim_relation":claim_relation,
            "origin_assessment":origin["assessment"],
            "origin_groups":origin["origin_groups"],
            "independent_origin_credit":bool(origin["independent_origin_credit"] and not ambiguous),
            "ambiguous":ambiguous,"factual_verification_credit":False}
        item.update(assess_verification_boundary(item))
        report.append(item)
    remaining=max_groups-len(report)
    if remaining<0:
        raise ValueError("corroboration group bound exceeded")
    report.extend(_generic_corroboration_groups(observations,remaining))
    if len(report)>max_groups:
        raise ValueError("corroboration group bound exceeded")
    report.sort(key=lambda x:x["corroboration_id"])
    return report
