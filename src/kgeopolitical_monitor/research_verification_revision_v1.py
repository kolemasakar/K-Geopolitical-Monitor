"""Immutable verification revision/revocation lineage.

Revisions never delete or rewrite earlier verification artifacts. Each revision
supersedes exactly one prior lineage artifact and branching is denied.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_completion_v1 import _verify, _result
from .research_request_v1 import _ID, _utc
from .research_verification_decision_v1 import effective_verification

SCHEMA="kgm.verification.revision.v1"
ACTIONS={"VERIFY","REJECT","DEFER","REVOKE"}

def _verification_request_dir(root, consumer, request_id):
    path=root/"verification"/consumer/request_id
    if path.is_symlink() or not path.is_dir():
        raise ValueError("verification request directory missing")
    return path

def _revisions_dir(root, consumer, request_id):
    base=_verification_request_dir(root,consumer,request_id)
    path=base/"revisions"
    if path.is_symlink():
        raise ValueError("symlink verification revisions denied")
    path.mkdir(mode=0o700,exist_ok=True)
    return path

def _read_json_artifact(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("verification lineage artifact missing")
    return json.loads(path.read_bytes())

def _load_prior(root, consumer, request_id, artifact_id):
    if not isinstance(artifact_id,str) or not _ID.fullmatch(artifact_id):
        raise ValueError("invalid superseded artifact identity")
    base=_verification_request_dir(root,consumer,request_id)
    decision_path=base/(artifact_id+".json")
    if decision_path.is_file() and not decision_path.is_symlink():
        artifact=_read_json_artifact(decision_path)
        status=effective_verification(artifact)
        d=artifact["decision"]
        return {"kind":"decision","id":d["decision_id"],"sha256":artifact["sha256"],
                "request_id":d["request_id"],"consumer_id":d["consumer_id"],
                "result_id":d["result_id"],"corroboration_id":d["corroboration_id"],
                "policy_version":d["policy_version"],"at_utc":d["decided_at_utc"],
                "effective_verification":status}
    revision_path=base/"revisions"/(artifact_id+".json")
    if revision_path.is_file() and not revision_path.is_symlink():
        artifact=_read_json_artifact(revision_path)
        if not isinstance(artifact,dict) or set(artifact)!={"revision","sha256"}:
            raise ValueError("invalid verification revision artifact")
        expected=hashlib.sha256(canonical_bytes({"revision":artifact["revision"]})).hexdigest()
        if artifact["sha256"]!=expected:
            raise ValueError("verification revision integrity mismatch")
        r=artifact["revision"]
        status=("VERIFIED" if r["action"]=="VERIFY" else
                "DISPUTED" if r["action"]=="REJECT" else "UNVERIFIED")
        return {"kind":"revision","id":r["revision_id"],"sha256":artifact["sha256"],
                "request_id":r["request_id"],"consumer_id":r["consumer_id"],
                "result_id":r["result_id"],"corroboration_id":r["corroboration_id"],
                "policy_version":r["policy_version"],"at_utc":r["decided_at_utc"],
                "effective_verification":status}
    raise ValueError("superseded verification artifact not found")

def _target_corroboration(result, corroboration_id):
    report=result.get("corroboration")
    if not isinstance(report,list):
        raise ValueError("result has no corroboration")
    matches=[x for x in report if x.get("corroboration_id")==corroboration_id]
    if len(matches)!=1:
        raise ValueError("corroboration target missing/ambiguous")
    return matches[0]

def validate_revision(revision, *, request, result, result_artifact_sha256,
                      prior, allowed_actors):
    fields={"schema_version","revision_id","request_id","consumer_id","result_id",
            "corroboration_id","supersedes_id","supersedes_sha256","action",
            "decided_at_utc","actor_id","policy_version","rationale",
            "result_artifact_sha256"}
    if not isinstance(revision,dict) or set(revision)!=fields:
        raise ValueError("unapproved verification revision fields")
    if revision["schema_version"]!=SCHEMA:
        raise ValueError("invalid verification revision schema")
    for field in ("revision_id","corroboration_id","supersedes_id","actor_id"):
        if not isinstance(revision[field],str) or not _ID.fullmatch(revision[field]):
            raise ValueError("invalid verification revision identity")
    if revision["revision_id"]==revision["supersedes_id"]:
        raise ValueError("verification lineage self-reference")
    if revision["action"] not in ACTIONS:
        raise ValueError("invalid verification revision action")
    if (revision["request_id"],revision["consumer_id"],revision["result_id"],
        revision["policy_version"]) != (
        request["request_id"],request["consumer_id"],result["result_id"],
        request["policy_version"]):
        raise ValueError("verification revision correlation mismatch")
    if (prior["request_id"],prior["consumer_id"],prior["result_id"],
        prior["corroboration_id"],prior["policy_version"]) != (
        revision["request_id"],revision["consumer_id"],revision["result_id"],
        revision["corroboration_id"],revision["policy_version"]):
        raise ValueError("verification lineage target mismatch")
    if revision["supersedes_sha256"]!=prior["sha256"]:
        raise ValueError("superseded verification hash mismatch")
    if revision["result_artifact_sha256"]!=result_artifact_sha256:
        raise ValueError("verification revision result snapshot mismatch")
    decided=_utc(revision["decided_at_utc"])
    if decided <= _utc(prior["at_utc"]):
        raise ValueError("non-monotonic verification revision")
    if not isinstance(revision["rationale"],str) or not 20<=len(revision["rationale"])<=2000:
        raise ValueError("verification revision rationale required")
    if not isinstance(allowed_actors,dict) or allowed_actors.get(revision["actor_id"])!=request["policy_version"]:
        raise PermissionError("verification revision actor denied")
    target=_target_corroboration(result,revision["corroboration_id"])
    if revision["action"]=="VERIFY":
        if target.get("verification_eligibility")!="ELIGIBLE_FOR_EXPLICIT_VERIFICATION":
            raise ValueError("corroboration not eligible for verification")
        if target.get("verification_blockers") or target.get("ambiguous") or not target.get("independent_origin_credit") or target.get("claim_relation")!="AGREES":
            raise ValueError("verification prerequisites not met")
    if revision["action"]=="REVOKE" and prior["effective_verification"]!="VERIFIED":
        raise ValueError("only verified lineage can be revoked")
    return revision

def publish_revision(root, consumer, request_id, revision, *,
                     allowed_consumers, allowed_actors):
    root=initialize(root)
    fd=_lock(root)
    try:
        _,saved=_verify(root,consumer,request_id,allowed_consumers)
        artifact=_result(root,consumer,request_id,saved)
        prior=_load_prior(root,consumer,request_id,revision.get("supersedes_id"))
        validate_revision(revision,request=saved["request"],result=artifact["result"],
                          result_artifact_sha256=artifact["sha256"],prior=prior,
                          allowed_actors=allowed_actors)
        directory=_revisions_dir(root,consumer,request_id)
        target=directory/(revision["revision_id"]+".json")
        payload={"revision":revision}
        payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
        encoded=canonical_bytes(payload)
        if target.is_symlink():
            raise ValueError("symlink verification revision denied")
        if target.exists():
            if target.read_bytes()!=encoded:
                raise ValueError("immutable verification revision conflict")
            return payload
        for path in directory.glob("*.json"):
            if path.is_symlink() or not path.is_file():
                raise ValueError("invalid verification revision entry")
            existing=json.loads(path.read_bytes())
            if isinstance(existing,dict) and isinstance(existing.get("revision"),dict):
                if existing["revision"].get("supersedes_id")==revision["supersedes_id"]:
                    raise ValueError("verification lineage fork denied")
        atomic_replace(target,encoded)
        return payload
    finally:
        os.close(fd)

def effective_revision_verification(revision_artifact):
    if not isinstance(revision_artifact,dict) or set(revision_artifact)!={"revision","sha256"}:
        raise ValueError("invalid verification revision artifact")
    expected=hashlib.sha256(canonical_bytes({"revision":revision_artifact["revision"]})).hexdigest()
    if revision_artifact["sha256"]!=expected:
        raise ValueError("verification revision integrity mismatch")
    action=revision_artifact["revision"]["action"]
    return "VERIFIED" if action=="VERIFY" else ("DISPUTED" if action=="REJECT" else "UNVERIFIED")
