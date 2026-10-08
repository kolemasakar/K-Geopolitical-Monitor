"""Deterministic owner-pilot worker over the canonical durable workflow.

Adapters are injected callables. This module performs no network access.
Cross-source correlation is allowed only through explicit structured
event_identity metadata. Correlation never grants independence or verification.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from .research_source_adapter_v1 import normalize_observations
from .research_typed_workflow_v1 import begin_processing, publish_and_complete
from .research_storage_v1 import canonical_bytes
from .research_corroboration_v1 import build_corroboration_report

_EVIDENCE_FIELDS=("source_id","public_url","published_at_utc","available_at_utc")

def _evidence(item):
    return {k:item[k] for k in _EVIDENCE_FIELDS}

def _unique_evidence(group):
    seen=set(); evidence=[]
    for item in sorted(group,key=lambda x:(x["source_id"],x["observation_id"])):
        ev=_evidence(item); key=tuple(ev[k] for k in _EVIDENCE_FIELDS)
        if key not in seen:
            seen.add(key); evidence.append(ev)
    return evidence[:20]

def _source_local_record_id(item, native_counts):
    native=item["observation_id"]
    if native_counts[native]==1:
        return native
    return "obs-"+hashlib.sha256(canonical_bytes({
        "source_id":item["source_id"],"observation_id":native
    })).hexdigest()[:24]

def _build_records(usable):
    """Build event records before applying result-budget selection.

    Shared structured event_identity identifies one event. Matching claim
    signatures merge provenance even when source wording differs. Distinct
    non-null claim signatures for the same event become explicit DISPUTED
    records. Without structured event_identity, source-native IDs remain local.
    """
    native_counts=defaultdict(int)
    for item in usable:
        native_counts[item["observation_id"]]+=1

    groups=defaultdict(list)
    for item in usable:
        identity=item.get("event_identity")
        key=("event",identity) if identity is not None else (
            "source",item["source_id"],item["observation_id"])
        groups[key].append(item)

    records=[]; disagreement=False
    for key in sorted(groups):
        group=groups[key]
        if key[0]=="source":
            item=group[0]
            records.append({"record_id":_source_local_record_id(item,native_counts),
                "kind":"CLAIM_EVENT","summary":item["summary"],
                "verification":"UNVERIFIED","evidence":[_evidence(item)],
                "contradictions":[],"revision_of":None,"forecast":None})
            continue

        identity=key[1]
        signatures={item.get("claim_signature") for item in group
                    if item.get("claim_signature") is not None}
        if len(signatures)<=1:
            representative=sorted(group,key=lambda x:(x["source_id"],x["observation_id"]))[0]
            records.append({"record_id":identity,"kind":"CLAIM_EVENT",
                "summary":representative["summary"],"verification":"UNVERIFIED",
                "evidence":_unique_evidence(group),"contradictions":[],
                "revision_of":None,"forecast":None})
            continue

        disagreement=True
        ids=[]
        ordered=sorted(group,key=lambda x:(x["source_id"],x["observation_id"]))
        for item in ordered:
            rid="dispute-"+hashlib.sha256(canonical_bytes({
                "source_id":item["source_id"],"observation_id":item["observation_id"],
                "event_identity":identity,"claim_signature":item.get("claim_signature")
            })).hexdigest()[:24]
            ids.append(rid)
        for item,rid in zip(ordered,ids):
            records.append({"record_id":rid,"kind":"CLAIM_EVENT",
                "summary":item["summary"],"verification":"DISPUTED",
                "evidence":[_evidence(item)],
                "contradictions":[x for x in ids if x!=rid][:20],
                "revision_of":None,"forecast":None})
    return records,disagreement

def _select_records(records,budget):
    """Bounded deterministic selection that maximizes source representation."""
    remaining=sorted(records,key=lambda r:r["record_id"])
    selected=[]; seen_sources=set()
    while remaining and len(selected)<budget:
        def rank(record):
            sources={e["source_id"] for e in record["evidence"]}
            return (-len(sources-seen_sources),record["record_id"])
        best=min(remaining,key=rank)
        remaining.remove(best); selected.append(best)
        seen_sources.update(e["source_id"] for e in best["evidence"])
    return selected

def execute_deterministic(root, consumer, request_id, *, request, allowed_consumers,
                          adapters, processing_at_utc, completed_at_utc,
                          producer_snapshot_id="deterministic-worker-v1"):
    begin_processing(root,consumer,request_id,allowed_consumers=allowed_consumers,
                     at_utc=processing_at_utc)
    observations=[]
    for adapter in adapters:
        produced=adapter(dict(request))
        if isinstance(produced,list):
            observations.extend(produced)
        else:
            observations.append(produced)
        if len(observations)>100:
            raise ValueError("unbounded adapter observations")
    normalized=normalize_observations(request,observations)
    corroboration=build_corroboration_report(normalized)
    usable=[x for x in normalized if x["status"] in {"SUCCESS","PARTIAL"}]
    unhealthy=[x for x in normalized if x["status"] in {"PARTIAL","UNAVAILABLE","INVALID"}]
    all_records,disagreement=_build_records(usable)
    records=_select_records(all_records,request["max_results"])
    complete=bool(records) and not unhealthy and not disagreement
    status="COMPLETE" if complete else "PARTIAL"
    result={"schema_version":"kgm.research.result.v2","request_id":request_id,
        "consumer_id":consumer,
        "result_id":"result-"+hashlib.sha256(canonical_bytes({"observations":normalized,"corroboration":corroboration})).hexdigest()[:24],
        "generated_at_utc":completed_at_utc,"producer_snapshot_id":producer_snapshot_id,
        "policy_version":request["policy_version"],"research_status":status,
        "coverage":"COMPLETE" if complete else "PARTIAL",
        "source_health":"HEALTHY" if complete else ("DEGRADED" if records else "UNAVAILABLE"),
        "records":records,"corroboration":corroboration}
    return publish_and_complete(root,consumer,request_id,result,
                                allowed_consumers=allowed_consumers,
                                at_utc=completed_at_utc)
