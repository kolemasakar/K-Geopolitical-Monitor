import copy
import pytest
from kgeopolitical_monitor.research_verification_revision_v1 import (
    publish_revision, effective_revision_verification)
from test_research_verification_decision_v1 import completed, decision, ACTORS
from kgeopolitical_monitor.research_verification_decision_v1 import publish_decision
from test_research_completion_v1 import POLICY

def initial_verified(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact)
    published=publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    return artifact,d,published

def revision(artifact, prior, action="REVOKE", rid="rev-01", supersedes="verify-01"):
    return {"schema_version":"kgm.verification.revision.v1",
        "revision_id":rid,"request_id":"req-01","consumer_id":"ktrader",
        "result_id":artifact["result"]["result_id"],"corroboration_id":"corr-1",
        "supersedes_id":supersedes,"supersedes_sha256":prior["sha256"],
        "action":action,"decided_at_utc":"2026-09-28T12:06:00Z",
        "actor_id":"owner","policy_version":"review-v1",
        "rationale":"Later evidence requires an explicit verification lineage revision.",
        "result_artifact_sha256":artifact["sha256"]}

def test_verified_decision_can_be_revoked_without_deleting_history(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    r=revision(artifact,prior,"REVOKE")
    published=publish_revision(tmp_path,"ktrader","req-01",r,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert effective_revision_verification(published)=="UNVERIFIED"
    assert (tmp_path/"verification/ktrader/req-01/verify-01.json").is_file()
    assert (tmp_path/"verification/ktrader/req-01/revisions/rev-01.json").is_file()
    assert publish_revision(tmp_path,"ktrader","req-01",r,
        allowed_consumers=POLICY,allowed_actors=ACTORS)==published

def test_lineage_can_reverify_after_revocation(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    revoke=publish_revision(tmp_path,"ktrader","req-01",revision(artifact,prior,"REVOKE"),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r2=revision(artifact,revoke,"VERIFY",rid="rev-02",supersedes="rev-01")
    r2["decided_at_utc"]="2026-09-28T12:07:00Z"
    published=publish_revision(tmp_path,"ktrader","req-01",r2,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert effective_revision_verification(published)=="VERIFIED"

def test_revision_fork_from_same_prior_is_denied(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    publish_revision(tmp_path,"ktrader","req-01",revision(artifact,prior,"REVOKE"),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    fork=revision(artifact,prior,"REJECT",rid="rev-fork")
    with pytest.raises(ValueError,match="lineage fork denied"):
        publish_revision(tmp_path,"ktrader","req-01",fork,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_wrong_prior_hash_is_denied(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    r=revision(artifact,prior); r["supersedes_sha256"]="0"*64
    with pytest.raises(ValueError,match="superseded verification hash mismatch"):
        publish_revision(tmp_path,"ktrader","req-01",r,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_non_monotonic_revision_is_denied(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    r=revision(artifact,prior); r["decided_at_utc"]="2026-09-28T12:05:00Z"
    with pytest.raises(ValueError,match="non-monotonic"):
        publish_revision(tmp_path,"ktrader","req-01",r,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_revoke_requires_current_verified_state(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    reject=revision(artifact,prior,"REJECT")
    first=publish_revision(tmp_path,"ktrader","req-01",reject,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r2=revision(artifact,first,"REVOKE",rid="rev-02",supersedes="rev-01")
    r2["decided_at_utc"]="2026-09-28T12:07:00Z"
    with pytest.raises(ValueError,match="only verified lineage"):
        publish_revision(tmp_path,"ktrader","req-01",r2,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_conflicting_revision_replay_is_denied(tmp_path):
    artifact,_,prior=initial_verified(tmp_path)
    r=revision(artifact,prior)
    publish_revision(tmp_path,"ktrader","req-01",r,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    changed=copy.deepcopy(r); changed["rationale"]="A different revision rationale that is long enough."
    with pytest.raises(ValueError,match="immutable verification revision conflict"):
        publish_revision(tmp_path,"ktrader","req-01",changed,
            allowed_consumers=POLICY,allowed_actors=ACTORS)
