"""Immutable explicit verification-decision artifacts.

A trusted owner/policy actor may create a decision only against an immutable
typed result artifact. The research worker never calls this module
automatically.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_completion_v1 import _verify, _result
from .research_request_v1 import _ID, _utc

DECISIONS={"VERIFY","REJECT","DEFER"}
SCHEMA="kgm.verification.decision.v1"

def _decision_dir(root, consumer, request_id):
    base=root/"verification"
    if base.is_symlink():
        raise ValueError("symlink verification root denied")
    base.mkdir(mode=0o700,exist_ok=True)
    c=base/consumer
    if c.is_symlink():
        raise ValueError("symlink verification consumer denied")
    c.mkdir(mode=0o700,exist_ok=True)
    r=c/request_id
    if r.is_symlink():
        raise ValueError("symlink verification request denied")
    r.mkdir(mode=0o700,exist_ok=True)
    return r

def validate_decision(decision, *, request, result, result_artifact_sha256,
                      allowed_actors):
    fields={"schema_version","decision_id","request_id","consumer_id","result_id",
            "corroboration_id","decision","decided_at_utc","actor_id",
            "policy_version","rationale","result_artifact_sha256"}
    if not isinstance(decision,dict) or set(decision)!=fields:
        raise ValueError("unapproved verification decision fields")
    if decision["schema_version"]!=SCHEMA:
        raise ValueError("invalid verification decision schema")
    for field in ("decision_id","corroboration_id","actor_id"):
        if not isinstance(decision[field],str) or not _ID.fullmatch(decision[field]):
            raise ValueError("invalid verification decision identity")
    if (decision["request_id"],decision["consumer_id"],decision["result_id"],
        decision["policy_version"]) != (
        request["request_id"],request["consumer_id"],result["result_id"],
        request["policy_version"]):
        raise ValueError("verification decision correlation mismatch")
    decided=_utc(decision["decided_at_utc"])
    if decided < _utc(result["generated_at_utc"]):
        raise ValueError("verification decision predates result")
    if decision["decision"] not in DECISIONS:
        raise ValueError("invalid verification decision")
    if not isinstance(decision["rationale"],str) or not 20<=len(decision["rationale"])<=2000:
        raise ValueError("verification rationale required")
    if not isinstance(allowed_actors,dict) or allowed_actors.get(decision["actor_id"])!=request["policy_version"]:
        raise PermissionError("verification actor denied")
    if decision["result_artifact_sha256"]!=result_artifact_sha256:
        raise ValueError("verification result snapshot mismatch")
    report=result.get("corroboration")
    if not isinstance(report,list):
        raise ValueError("result has no corroboration")
    matches=[x for x in report if x.get("corroboration_id")==decision["corroboration_id"]]
    if len(matches)!=1:
        raise ValueError("corroboration target missing/ambiguous")
    target=matches[0]
    if decision["decision"]=="VERIFY":
        if target.get("verification_eligibility")!="ELIGIBLE_FOR_EXPLICIT_VERIFICATION":
            raise ValueError("corroboration not eligible for verification")
        if target.get("verification_blockers"):
            raise ValueError("verification blockers present")
        if target.get("ambiguous") or not target.get("independent_origin_credit"):
            raise ValueError("verification prerequisites not met")
        if target.get("claim_relation")!="AGREES":
            raise ValueError("claim agreement required")
    return decision

def publish_decision(root, consumer, request_id, decision, *,
                     allowed_consumers, allowed_actors):
    root=initialize(root)
    fd=_lock(root)
    try:
        _,saved=_verify(root,consumer,request_id,allowed_consumers)
        artifact=_result(root,consumer,request_id,saved)
        validate_decision(decision,request=saved["request"],result=artifact["result"],
                          result_artifact_sha256=artifact["sha256"],
                          allowed_actors=allowed_actors)
        target=_decision_dir(root,consumer,request_id)/(decision["decision_id"]+".json")
        payload={"decision":decision}
        payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
        encoded=canonical_bytes(payload)
        if target.is_symlink():
            raise ValueError("symlink verification decision denied")
        if target.exists():
            if target.read_bytes()!=encoded:
                raise ValueError("immutable verification decision conflict")
        else:
            atomic_replace(target,encoded)
        return payload
    finally:
        os.close(fd)

def effective_verification(decision_artifact):
    if not isinstance(decision_artifact,dict) or set(decision_artifact)!={"decision","sha256"}:
        raise ValueError("invalid verification artifact")
    expected=hashlib.sha256(canonical_bytes({"decision":decision_artifact["decision"]})).hexdigest()
    if decision_artifact["sha256"]!=expected:
        raise ValueError("verification artifact integrity mismatch")
    action=decision_artifact["decision"]["decision"]
    return "VERIFIED" if action=="VERIFY" else ("DISPUTED" if action=="REJECT" else "UNVERIFIED")
