import hashlib
import json
import pytest
from kgeopolitical_monitor.research_storage_v1 import canonical_bytes
from kgeopolitical_monitor.research_verification_resolver_v1 import resolve_verification_state
from kgeopolitical_monitor.research_verification_basis_v1 import publish_basis
from kgeopolitical_monitor.research_verification_revision_v2 import publish_revision_v2
from kgeopolitical_monitor.research_verification_decision_v1 import publish_decision
from test_research_verification_decision_v1 import completed, decision, ACTORS
from test_research_verification_basis_v1 import basis, revision_v2
from test_research_completion_v1 import POLICY

def initial(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact)
    prior=publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    return artifact,prior

def test_resolver_follows_evidence_bound_revoke_and_reverify(tmp_path):
    artifact,prior=initial(tmp_path)
    adverse=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    revoked=publish_revision_v2(tmp_path,"ktrader","req-01",
        revision_v2(artifact,prior,adverse),allowed_consumers=POLICY,allowed_actors=ACTORS)
    state=resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")
    assert state["effective_verification"]=="UNVERIFIED"
    assert state["head_artifact_id"]=="rev2-01"
    assert state["evidence_bound_lineage"] is True
    confirmation_basis=basis(artifact,basis_id="basis-02",basis_type="CONFIRMATION",
                             created="2026-09-28T12:08:00Z")
    confirmation_basis["evidence_refs"][0]["reference_id"]="evidence-02"
    confirmation_basis["evidence_refs"][0]["observed_at_utc"]="2026-09-28T12:07:30Z"
    confirmation=publish_basis(tmp_path,"ktrader","req-01",confirmation_basis,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r2=revision_v2(artifact,revoked,confirmation,action="VERIFY",rid="rev2-02",
                   supersedes="rev2-01",decided="2026-09-28T12:09:00Z")
    publish_revision_v2(tmp_path,"ktrader","req-01",r2,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    state=resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")
    assert state["effective_verification"]=="VERIFIED"
    assert [x["id"] for x in state["lineage"]]==["verify-01","rev2-01","rev2-02"]
    assert state["effective_state_stale"] is False

def test_unapplied_post_head_basis_marks_effective_state_stale(tmp_path):
    artifact,_=initial(tmp_path)
    pending=basis(artifact,basis_id="basis-pending",basis_type="CONTRADICTION",
                  created="2026-09-28T12:06:00Z")
    publish_basis(tmp_path,"ktrader","req-01",pending,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    state=resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")
    assert state["effective_verification"]=="VERIFIED"
    assert state["effective_state_stale"] is True
    assert [x["basis_id"] for x in state["post_head_basis"]]==["basis-pending"]

def test_multiple_root_decisions_are_fail_closed(tmp_path):
    artifact,_=initial(tmp_path)
    d=decision(artifact); d["decision_id"]="verify-02"
    d["decided_at_utc"]="2026-09-28T12:06:00Z"
    publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    with pytest.raises(ValueError,match="exactly one root"):
        resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")

def test_resolver_detects_fork_even_if_files_are_manually_corrupted(tmp_path):
    artifact,prior=initial(tmp_path)
    adverse=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r=revision_v2(artifact,prior,adverse)
    publish_revision_v2(tmp_path,"ktrader","req-01",r,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    fork=dict(r); fork["revision_id"]="rev2-fork"; fork["decided_at_utc"]="2026-09-28T12:08:00Z"
    payload={"revision":fork}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    path=tmp_path/"verification/ktrader/req-01/revisions/rev2-fork.json"
    path.write_bytes(canonical_bytes(payload))
    with pytest.raises(ValueError,match="fork detected"):
        resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")

def test_resolver_detects_missing_link(tmp_path):
    artifact,prior=initial(tmp_path)
    adverse=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r=revision_v2(artifact,prior,adverse)
    r["revision_id"]="orphan-rev"; r["supersedes_id"]="missing-parent"
    payload={"revision":r}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    directory=tmp_path/"verification/ktrader/req-01/revisions"; directory.mkdir(exist_ok=True)
    (directory/"orphan-rev.json").write_bytes(canonical_bytes(payload))
    with pytest.raises(ValueError,match="missing superseded artifact"):
        resolve_verification_state(tmp_path,"ktrader","req-01","corr-1")
