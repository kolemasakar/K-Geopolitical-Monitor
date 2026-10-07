"""Deterministic owner-pilot worker over the canonical durable workflow.

Adapters are injected callables. This module performs no network access.
"""
from __future__ import annotations
import hashlib
from .research_source_adapter_v1 import normalize_observations
from .research_typed_workflow_v1 import begin_processing, publish_and_complete
from .research_storage_v1 import canonical_bytes

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
        if len(observations) > 100:
            raise ValueError("unbounded adapter observations")
    normalized=normalize_observations(request, observations)
    usable=[x for x in normalized if x["status"] in {"SUCCESS","PARTIAL"}]
    unhealthy=[x for x in normalized if x["status"] in {"PARTIAL","UNAVAILABLE","INVALID"}]
    records=[]
    for item in usable[:request["max_results"]]:
        records.append({"record_id":item["observation_id"],"kind":"CLAIM_EVENT",
            "summary":item["summary"],"verification":"UNVERIFIED",
            "evidence":[{k:item[k] for k in ("source_id","public_url","published_at_utc","available_at_utc")}],
            "contradictions":[],"revision_of":None,"forecast":None})
    complete = bool(records) and not unhealthy
    status="COMPLETE" if complete else "PARTIAL"
    result={"schema_version":"kgm.research.result.v1","request_id":request_id,
        "consumer_id":consumer,
        "result_id":"result-"+hashlib.sha256(canonical_bytes(normalized)).hexdigest()[:24],
        "generated_at_utc":completed_at_utc,"producer_snapshot_id":producer_snapshot_id,
        "policy_version":request["policy_version"],"research_status":status,
        "coverage":"COMPLETE" if complete else "PARTIAL",
        "source_health":"HEALTHY" if complete else ("DEGRADED" if records else "UNAVAILABLE"),
        "records":records}
    return publish_and_complete(root, consumer, request_id, result,
                                allowed_consumers=allowed_consumers,
                                at_utc=completed_at_utc)
