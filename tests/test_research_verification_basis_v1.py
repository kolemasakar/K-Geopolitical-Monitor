import hashlib
import pytest
from kgeopolitical_monitor.research_verification_basis_v1 import publish_basis
from kgeopolitical_monitor.research_verification_revision_v2 import publish_revision_v2
from kgeopolitical_monitor.research_verification_decision_v1 import publish_decision
from test_research_verification_decision_v1 import completed, decision, ACTORS
from test_research_completion_v1 import POLICY

def initial_verified(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact)
    prior=publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    return artifact,prior

def basis(artifact, basis_id="basis-01", basis_type="CONTRADICTION",
          created="2026-09-28T12:06:00Z"):
    digest=hashlib.sha256(b"explicit evidence snapshot").hexdigest()
    return {"schema_version":"kgm.verification.basis.v1",
        "basis_id":basis_id,"request_id":"req-01","consumer_id":"ktrader",
        "result_id":artifact["result"]["result_id"],"corroboration_id":"corr-1",
        "basis_type":basis_type,"created_at_utc":created,
        "actor_id":"owner","policy_version":"review-v1",
        "rationale":"Explicit evidence basis for a later verification state change.",
        "result_artifact_sha256":artifact["sha256"],
        "evidence_refs":[{"reference_id":"evidence-01","source_id":"source-c",
            "public_url":"https://example.test/new-evidence",
            "observed_at_utc":"2026-09-28T12:05:30Z",
            "content_sha256":digest,
            "summary":"A bounded immutable digest of the new evidence snapshot."}]}

def revision_v2(artifact, prior, basis_artifact, action="REVOKE",
                rid="rev2-01", supersedes="verify-01", decided="2026-09-28T12:07:00Z"):
    return {"schema_version":"kgm.verification.revision.v2",
        "revision_id":rid,"request_id":"req-01","consumer_id":"ktrader",
        "result_id":artifact["result"]["result_id"],"corroboration_id":"corr-1",
        "supersedes_id":supersedes,"supersedes_sha256":prior["sha256"],
        "action":action,"decided_at_utc":decided,"actor_id":"owner",
        "policy_version":"review-v1",
        "rationale":"Evidence-bound explicit verification lineage update after new evidence review.",
        "result_artifact_sha256":artifact["sha256"],
        "basis_id":basis_artifact["basis"]["basis_id"],
        "basis_sha256":basis_artifact["sha256"]}

def test_revoke_requires_immutable_adverse_evidence_basis(tmp_path):
    artifact,prior=initial_verified(tmp_path)
    b=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r=revision_v2(artifact,prior,b)
    published=publish_revision_v2(tmp_path,"ktrader","req-01",r,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert published["revision"]["basis_sha256"]==b["sha256"]
    assert published["revision"]["action"]=="REVOKE"

def test_confirmation_basis_cannot_revoke_verified_lineage(tmp_path):
    artifact,prior=initial_verified(tmp_path)
    b=publish_basis(tmp_path,"ktrader","req-01",
        basis(artifact,basis_type="CONFIRMATION"),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r=revision_v2(artifact,prior,b)
    with pytest.raises(ValueError,match="adverse evidence basis"):
        publish_revision_v2(tmp_path,"ktrader","req-01",r,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_wrong_basis_hash_is_denied(tmp_path):
    artifact,prior=initial_verified(tmp_path)
    b=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r=revision_v2(artifact,prior,b); r["basis_sha256"]="0"*64
    with pytest.raises(ValueError,match="basis hash mismatch"):
        publish_revision_v2(tmp_path,"ktrader","req-01",r,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_basis_cannot_reference_future_evidence(tmp_path):
    artifact,_=initial_verified(tmp_path)
    b=basis(artifact)
    b["evidence_refs"][0]["observed_at_utc"]="2026-09-28T12:06:30Z"
    with pytest.raises(ValueError,match="evidence from future"):
        publish_basis(tmp_path,"ktrader","req-01",b,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_reverify_after_revocation_requires_new_confirmation_basis(tmp_path):
    artifact,prior=initial_verified(tmp_path)
    adverse=publish_basis(tmp_path,"ktrader","req-01",basis(artifact),
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    revoked=publish_revision_v2(tmp_path,"ktrader","req-01",
        revision_v2(artifact,prior,adverse),allowed_consumers=POLICY,allowed_actors=ACTORS)
    confirmation_basis=basis(artifact,basis_id="basis-02",basis_type="CONFIRMATION",
                             created="2026-09-28T12:08:00Z")
    confirmation_basis["evidence_refs"][0]["reference_id"]="evidence-02"
    confirmation_basis["evidence_refs"][0]["observed_at_utc"]="2026-09-28T12:07:30Z"
    confirmation=publish_basis(tmp_path,"ktrader","req-01",confirmation_basis,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    r2=revision_v2(artifact,revoked,confirmation,action="VERIFY",rid="rev2-02",
                   supersedes="rev2-01",decided="2026-09-28T12:09:00Z")
    published=publish_revision_v2(tmp_path,"ktrader","req-01",r2,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert published["revision"]["action"]=="VERIFY"

def test_basis_artifact_is_immutable(tmp_path):
    artifact,_=initial_verified(tmp_path)
    b=basis(artifact)
    first=publish_basis(tmp_path,"ktrader","req-01",b,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    changed=dict(b); changed["rationale"]="A different evidence basis rationale that is long enough."
    with pytest.raises(ValueError,match="immutable verification basis conflict"):
        publish_basis(tmp_path,"ktrader","req-01",changed,
            allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert first["basis"]["basis_id"]=="basis-01"
