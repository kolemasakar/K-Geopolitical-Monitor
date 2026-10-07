"""Deterministic owner-pilot worker over the canonical durable workflow.

Adapters are injected callables. This module performs no network access.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from .research_source_adapter_v1 import normalize_observations
from .research_typed_workflow_v1 import begin_processing, publish_and_complete
from .research_storage_v1 import canonical_bytes

_EVIDENCE_FIELDS=("source_id","public_url","published_at_utc","available_at_utc")

def _evidence(item):
    return {k:item[k] for k in _EVIDENCE_FIELDS}

def _balanced_usable(usable, budget):
    """Deterministically prevent one healthy source from monopolizing results."""
    by_source=defaultdict(list)
    for item in usable:
        by_source[item["source_id"]].append(item)
    for items in by_source.values():
        items.sort(key=lambda x:(x["observation_id"],x["summary"]))
    sources=sorted(by_source)
    selected=[]; index=0
    while len(selected)<budget:
        progressed=False
        for source in sources:
            if index<len(by_source[source]):
                selected.append(by_source[source][index]); progressed=True
                if len(selected)>=budget:
                    break
        if not progressed:
            break
        index+=1
    return selected

def _build_records(usable, max_results):
    """Conservative cross-source correlation by shared observation_id.

    Same observation_id + same summary => one deduplicated record with merged
    provenance. Same observation_id + differing summary => separate DISPUTED
    records linked as contradictions. Different observation_ids are never
    heuristically merged.
    """
    groups=defaultdict(list)
    for item in usable:
        groups[item["observation_id"]].append(item)
    records=[]; disagreement=False
    for observation_id in sorted(groups):
        group=groups[observation_id]
        summaries={item["summary"] for item in group}
        if len(summaries)==1:
            seen=set(); evidence=[]
            for item in group:
                ev=_evidence(item)
                key=tuple(ev[k] for k in _EVIDENCE_FIELDS)
                if key not in seen:
                    seen.add(key); evidence.append(ev)
            records.append({"record_id":observation_id,"kind":"CLAIM_EVENT",
                "summary":group[0]["summary"],"verification":"UNVERIFIED",
                "evidence":evidence[:20],"contradictions":[],"revision_of":None,
                "forecast":None})
        else:
            disagreement=True
            ids=[]
            for item in group:
                rid="dispute-"+hashlib.sha256(canonical_bytes({
                    "source_id":item["source_id"],"observation_id":observation_id,
                    "summary":item["summary"]})).hexdigest()[:24]
                ids.append(rid)
            for item,rid in zip(group,ids):
                records.append({"record_id":rid,"kind":"CLAIM_EVENT",
                    "summary":item["summary"],"verification":"DISPUTED",
                    "evidence":[_evidence(item)],
                    "contradictions":[x for x in ids if x!=rid][:20],
                    "revision_of":None,"forecast":None})
        if len(records)>=max_results:
            break
    return records[:max_results],disagreement

def execute_deterministic(root, consumer, request_id, *, request, allowed_consumers,
                          adapters, processing_at_utc, completed_at_utc,
                          producer_snapshot_id="deterministic-worker-v1"):
    begin_processing(root, consumer, request_id, allowed_consumers=allowed_consumers,
                     at_utc=processing_at_utc)
    observations=[]
    for adapter in adapters:
        produced=adapter(dict(request))
        if isinstance(produced, list):
            observations.extend(produced)
        else:
            observations.append(produced)
        if len(observations)>100:
            raise ValueError("unbounded adapter observations")
    normalized=normalize_observations(request,observations)
    usable=[x for x in normalized if x["status"] in {"SUCCESS","PARTIAL"}]
    unhealthy=[x for x in normalized if x["status"] in {"PARTIAL","UNAVAILABLE","INVALID"}]
    balanced=_balanced_usable(usable,request["max_results"])
    records,disagreement=_build_records(balanced,request["max_results"])
    complete=bool(records) and not unhealthy and not disagreement
    status="COMPLETE" if complete else "PARTIAL"
    result={"schema_version":"kgm.research.result.v1","request_id":request_id,
        "consumer_id":consumer,
        "result_id":"result-"+hashlib.sha256(canonical_bytes(normalized)).hexdigest()[:24],
        "generated_at_utc":completed_at_utc,"producer_snapshot_id":producer_snapshot_id,
        "policy_version":request["policy_version"],"research_status":status,
        "coverage":"COMPLETE" if complete else "PARTIAL",
        "source_health":"HEALTHY" if complete else ("DEGRADED" if records else "UNAVAILABLE"),
        "records":records}
    return publish_and_complete(root,consumer,request_id,result,
                                allowed_consumers=allowed_consumers,
                                at_utc=completed_at_utc)
