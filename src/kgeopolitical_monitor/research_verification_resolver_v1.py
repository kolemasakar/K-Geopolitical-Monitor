"""Deterministic resolution of effective verification state from immutable lineage."""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from .research_storage_v1 import canonical_bytes
from .research_request_v1 import _ID, _utc
from .research_verification_decision_v1 import effective_verification
from .research_verification_basis_v1 import load_basis

def _read_json(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("verification lineage entry missing")
    return json.loads(path.read_bytes())

def _decision_node(path):
    artifact=_read_json(path)
    status=effective_verification(artifact)
    d=artifact["decision"]
    return {"id":d["decision_id"],"kind":"decision","sha256":artifact["sha256"],
            "request_id":d["request_id"],"consumer_id":d["consumer_id"],
            "result_id":d["result_id"],"corroboration_id":d["corroboration_id"],
            "policy_version":d["policy_version"],"at_utc":d["decided_at_utc"],
            "action":d["decision"],"effective_verification":status,
            "supersedes_id":None,"basis_id":None,"basis_sha256":None,
            "evidence_bound":True}

def _revision_node(path):
    artifact=_read_json(path)
    if not isinstance(artifact,dict) or set(artifact)!={"revision","sha256"}:
        raise ValueError("invalid verification revision artifact")
    expected=hashlib.sha256(canonical_bytes({"revision":artifact["revision"]})).hexdigest()
    if artifact["sha256"]!=expected:
        raise ValueError("verification revision integrity mismatch")
    r=artifact["revision"]
    schema=r.get("schema_version")
    if schema not in {"kgm.verification.revision.v1","kgm.verification.revision.v2"}:
        raise ValueError("unsupported verification revision schema")
    status="VERIFIED" if r["action"]=="VERIFY" else ("DISPUTED" if r["action"]=="REJECT" else "UNVERIFIED")
    return {"id":r["revision_id"],"kind":"revision","sha256":artifact["sha256"],
            "request_id":r["request_id"],"consumer_id":r["consumer_id"],
            "result_id":r["result_id"],"corroboration_id":r["corroboration_id"],
            "policy_version":r["policy_version"],"at_utc":r["decided_at_utc"],
            "action":r["action"],"effective_verification":status,
            "supersedes_id":r["supersedes_id"],
            "basis_id":r.get("basis_id"),"basis_sha256":r.get("basis_sha256"),
            "evidence_bound":schema=="kgm.verification.revision.v2"}

def resolve_verification_state(root, consumer, request_id, corroboration_id):
    if not all(isinstance(x,str) and _ID.fullmatch(x) for x in (consumer,request_id,corroboration_id)):
        raise ValueError("invalid verification resolution identity")
    base=root/"verification"/consumer/request_id
    if base.is_symlink() or not base.is_dir():
        raise ValueError("verification request directory missing")

    nodes={}
    decision_paths=sorted(p for p in base.glob("*.json") if p.is_file() and not p.is_symlink())
    revision_dir=base/"revisions"
    revision_paths=[]
    if revision_dir.exists():
        if revision_dir.is_symlink() or not revision_dir.is_dir():
            raise ValueError("invalid verification revisions directory")
        revision_paths=sorted(p for p in revision_dir.glob("*.json") if p.is_file() and not p.is_symlink())

    for path in decision_paths:
        node=_decision_node(path)
        if node["corroboration_id"]!=corroboration_id:
            continue
        if node["id"] in nodes:
            raise ValueError("duplicate verification lineage identity")
        nodes[node["id"]]=node
    for path in revision_paths:
        node=_revision_node(path)
        if node["corroboration_id"]!=corroboration_id:
            continue
        if node["id"] in nodes:
            raise ValueError("duplicate verification lineage identity")
        nodes[node["id"]]=node

    if not nodes:
        raise ValueError("verification lineage target absent")

    roots=[n for n in nodes.values() if n["kind"]=="decision"]
    if len(roots)!=1:
        raise ValueError("verification lineage requires exactly one root decision")
    root_node=roots[0]

    children=defaultdict(list)
    for node in nodes.values():
        if node["kind"]=="revision":
            parent=node["supersedes_id"]
            if parent not in nodes:
                raise ValueError("verification lineage missing superseded artifact")
            parent_node=nodes[parent]
            if (node["request_id"],node["consumer_id"],node["result_id"],
                node["corroboration_id"],node["policy_version"]) != (
                parent_node["request_id"],parent_node["consumer_id"],parent_node["result_id"],
                parent_node["corroboration_id"],parent_node["policy_version"]):
                raise ValueError("verification lineage correlation mismatch")
            if _utc(node["at_utc"])<=_utc(parent_node["at_utc"]):
                raise ValueError("verification lineage non-monotonic")
            children[parent].append(node["id"])
            if len(children[parent])>1:
                raise ValueError("verification lineage fork detected")
            if node["evidence_bound"]:
                basis=load_basis(root,consumer,request_id,node["basis_id"])
                if basis["sha256"]!=node["basis_sha256"]:
                    raise ValueError("verification lineage basis hash mismatch")
                b=basis["basis"]
                if (b["request_id"],b["consumer_id"],b["result_id"],b["corroboration_id"],
                    b["policy_version"]) != (
                    node["request_id"],node["consumer_id"],node["result_id"],
                    node["corroboration_id"],node["policy_version"]):
                    raise ValueError("verification lineage basis target mismatch")
                if _utc(b["created_at_utc"])>_utc(node["at_utc"]):
                    raise ValueError("verification lineage revision predates basis")

    lineage=[]
    seen=set()
    current=root_node
    while True:
        if current["id"] in seen:
            raise ValueError("verification lineage cycle detected")
        seen.add(current["id"])
        lineage.append(current)
        next_ids=children.get(current["id"],[])
        if not next_ids:
            break
        current=nodes[next_ids[0]]

    if len(seen)!=len(nodes):
        raise ValueError("verification lineage disconnected artifacts")

    applied_basis={n["basis_id"] for n in lineage if n["basis_id"] is not None}
    all_basis=[]
    basis_dir=base/"basis"
    if basis_dir.exists():
        if basis_dir.is_symlink() or not basis_dir.is_dir():
            raise ValueError("invalid verification basis directory")
        for path in sorted(p for p in basis_dir.glob("*.json") if p.is_file() and not p.is_symlink()):
            artifact=_read_json(path)
            if not isinstance(artifact,dict) or set(artifact)!={"basis","sha256"}:
                raise ValueError("invalid verification basis artifact")
            expected=hashlib.sha256(canonical_bytes({"basis":artifact["basis"]})).hexdigest()
            if artifact["sha256"]!=expected:
                raise ValueError("verification basis integrity mismatch")
            b=artifact["basis"]
            if b.get("corroboration_id")==corroboration_id:
                all_basis.append({"basis_id":b["basis_id"],"created_at_utc":b["created_at_utc"],
                                  "basis_type":b["basis_type"],"sha256":artifact["sha256"]})
    unapplied=[b for b in all_basis if b["basis_id"] not in applied_basis]
    post_head=[b for b in unapplied if _utc(b["created_at_utc"])>_utc(current["at_utc"])]

    return {"corroboration_id":corroboration_id,
            "root_decision_id":root_node["id"],
            "head_artifact_id":current["id"],
            "head_kind":current["kind"],
            "effective_verification":current["effective_verification"],
            "lineage":[{"id":n["id"],"kind":n["kind"],"action":n["action"],
                        "at_utc":n["at_utc"],"sha256":n["sha256"],
                        "basis_id":n["basis_id"],"evidence_bound":n["evidence_bound"]}
                       for n in lineage],
            "evidence_bound_lineage":all(n["evidence_bound"] for n in lineage),
            "unapplied_basis":unapplied,
            "post_head_basis":post_head,
            "effective_state_stale":bool(post_head)}
