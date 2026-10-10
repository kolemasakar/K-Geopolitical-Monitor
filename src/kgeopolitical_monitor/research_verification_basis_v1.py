"""Immutable evidence-basis artifacts for verification state changes."""
from __future__ import annotations
import hashlib
import json
import os
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_completion_v1 import _verify, _result
from .research_request_v1 import _ID, _utc

SCHEMA="kgm.verification.basis.v1"
BASIS_TYPES={"CONFIRMATION","CONTRADICTION","CORRECTION","SOURCE_REVISION"}

def _basis_dir(root, consumer, request_id):
    base=root/"verification"/consumer/request_id
    if base.is_symlink() or not base.is_dir():
        raise ValueError("verification request directory missing")
    path=base/"basis"
    if path.is_symlink():
        raise ValueError("symlink verification basis denied")
    path.mkdir(mode=0o700,exist_ok=True)
    return path

def validate_basis(basis, *, request, result, result_artifact_sha256, allowed_actors):
    fields={"schema_version","basis_id","request_id","consumer_id","result_id",
            "corroboration_id","basis_type","created_at_utc","actor_id",
            "policy_version","rationale","result_artifact_sha256","evidence_refs"}
    if not isinstance(basis,dict) or set(basis)!=fields:
        raise ValueError("unapproved verification basis fields")
    if basis["schema_version"]!=SCHEMA:
        raise ValueError("invalid verification basis schema")
    for field in ("basis_id","corroboration_id","actor_id"):
        if not isinstance(basis[field],str) or not _ID.fullmatch(basis[field]):
            raise ValueError("invalid verification basis identity")
    if (basis["request_id"],basis["consumer_id"],basis["result_id"],basis["policy_version"]) != (
        request["request_id"],request["consumer_id"],result["result_id"],request["policy_version"]):
        raise ValueError("verification basis correlation mismatch")
    created=_utc(basis["created_at_utc"])
    if created < _utc(result["generated_at_utc"]):
        raise ValueError("verification basis predates result")
    if basis["basis_type"] not in BASIS_TYPES:
        raise ValueError("invalid verification basis type")
    if not isinstance(basis["rationale"],str) or not 20<=len(basis["rationale"])<=2000:
        raise ValueError("verification basis rationale required")
    if basis["result_artifact_sha256"]!=result_artifact_sha256:
        raise ValueError("verification basis result snapshot mismatch")
    if not isinstance(allowed_actors,dict) or allowed_actors.get(basis["actor_id"])!=request["policy_version"]:
        raise PermissionError("verification basis actor denied")
    report=result.get("corroboration")
    if not isinstance(report,list) or len([x for x in report if x.get("corroboration_id")==basis["corroboration_id"]])!=1:
        raise ValueError("verification basis corroboration target missing")
    refs=basis["evidence_refs"]
    if not isinstance(refs,list) or not 1<=len(refs)<=20:
        raise ValueError("verification basis evidence required")
    ref_fields={"reference_id","source_id","public_url","observed_at_utc",
                "content_sha256","summary"}
    seen=set()
    for ref in refs:
        if not isinstance(ref,dict) or set(ref)!=ref_fields:
            raise ValueError("invalid verification basis evidence reference")
        if not isinstance(ref["reference_id"],str) or not _ID.fullmatch(ref["reference_id"]) or ref["reference_id"] in seen:
            raise ValueError("invalid/duplicate verification basis reference")
        seen.add(ref["reference_id"])
        if not isinstance(ref["source_id"],str) or not _ID.fullmatch(ref["source_id"]):
            raise ValueError("invalid verification basis source")
        if not isinstance(ref["public_url"],str) or not ref["public_url"].startswith("https://") or len(ref["public_url"])>2048:
            raise ValueError("invalid verification basis URL")
        observed=_utc(ref["observed_at_utc"])
        if observed>created:
            raise ValueError("verification basis evidence from future")
        digest=ref["content_sha256"]
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid verification basis content digest")
        if not isinstance(ref["summary"],str) or not 1<=len(ref["summary"])<=1000:
            raise ValueError("invalid verification basis summary")
    return basis

def publish_basis(root, consumer, request_id, basis, *,
                  allowed_consumers, allowed_actors):
    root=initialize(root)
    fd=_lock(root)
    try:
        _,saved=_verify(root,consumer,request_id,allowed_consumers)
        artifact=_result(root,consumer,request_id,saved)
        validate_basis(basis,request=saved["request"],result=artifact["result"],
                       result_artifact_sha256=artifact["sha256"],
                       allowed_actors=allowed_actors)
        target=_basis_dir(root,consumer,request_id)/(basis["basis_id"]+".json")
        payload={"basis":basis}
        payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
        encoded=canonical_bytes(payload)
        if target.is_symlink():
            raise ValueError("symlink verification basis denied")
        if target.exists():
            if target.read_bytes()!=encoded:
                raise ValueError("immutable verification basis conflict")
        else:
            atomic_replace(target,encoded)
        return payload
    finally:
        os.close(fd)

def load_basis(root, consumer, request_id, basis_id):
    if not isinstance(basis_id,str) or not _ID.fullmatch(basis_id):
        raise ValueError("invalid verification basis identity")
    path=root/"verification"/consumer/request_id/"basis"/(basis_id+".json")
    if path.is_symlink() or not path.is_file():
        raise ValueError("verification basis artifact missing")
    artifact=json.loads(path.read_bytes())
    if not isinstance(artifact,dict) or set(artifact)!={"basis","sha256"}:
        raise ValueError("invalid verification basis artifact")
    expected=hashlib.sha256(canonical_bytes({"basis":artifact["basis"]})).hexdigest()
    if artifact["sha256"]!=expected:
        raise ValueError("verification basis integrity mismatch")
    return artifact
