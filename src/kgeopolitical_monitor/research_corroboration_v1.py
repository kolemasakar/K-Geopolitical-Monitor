"""Bounded cross-source corroboration metadata for owner-pilot typed results.

Association and origin-level independence are kept separate from factual
verification. This module never upgrades a claim to VERIFIED.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from .research_event_association_v1 import associate_earthquakes
from .research_origin_assessment_v1 import assess_origin_groups
from .research_storage_v1 import canonical_bytes

def build_corroboration_report(observations, *, max_pairs=200,
                               max_seconds=30, max_km=50):
    if not isinstance(observations,list):
        raise ValueError("observation list required")
    usable=[x for x in observations if isinstance(x,dict) and
            x.get("status") in {"SUCCESS","PARTIAL"} and
            isinstance(x.get("event_parameters"),dict)]
    candidates=[]
    per_other_source=defaultdict(int)
    for i,left in enumerate(usable):
        for right in usable[i+1:]:
            if left["source_id"]==right["source_id"]:
                continue
            assoc=associate_earthquakes(left,right,max_seconds=max_seconds,max_km=max_km)
            if not assoc["match"]:
                continue
            candidates.append((left,right,assoc))
            per_other_source[(left["source_id"],left["observation_id"],right["source_id"])]+=1
            per_other_source[(right["source_id"],right["observation_id"],left["source_id"])]+=1
            if len(candidates)>max_pairs:
                raise ValueError("corroboration pair bound exceeded")
    report=[]
    for left,right,assoc in candidates:
        ambiguous=(per_other_source[(left["source_id"],left["observation_id"],right["source_id"])]>1 or
                   per_other_source[(right["source_id"],right["observation_id"],left["source_id"])]>1)
        origin=assess_origin_groups([left,right])
        ls,rs=left.get("claim_signature"),right.get("claim_signature")
        claim_relation="UNKNOWN" if ls is None or rs is None else ("AGREES" if ls==rs else "DIFFERS")
        seed={"left_source_id":left["source_id"],"left_observation_id":left["observation_id"],
              "right_source_id":right["source_id"],"right_observation_id":right["observation_id"]}
        pair_id="corr-"+hashlib.sha256(canonical_bytes(seed)).hexdigest()[:24]
        report.append({"pair_id":pair_id,**seed,
            "delta_seconds":round(assoc["delta_seconds"],3),
            "distance_km":round(assoc["distance_km"],3),
            "claim_relation":claim_relation,
            "origin_assessment":origin["assessment"],
            "origin_groups":origin["origin_groups"],
            "independent_origin_credit":bool(origin["independent_origin_credit"] and not ambiguous),
            "ambiguous":ambiguous,
            "factual_verification_credit":False})
    report.sort(key=lambda x:x["pair_id"])
    return report
