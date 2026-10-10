import pytest
from kgeopolitical_monitor.research_generic_identity_v1 import (
    generic_event_identity, generic_claim_signature,
    validate_generic_event_descriptor, validate_generic_claim_descriptor)
from kgeopolitical_monitor.research_source_adapter_v1 import validate_source_observation
from test_research_request_v1 import sample

def event_desc():
    return {"family":"DIPLOMATIC","event_date_utc":"2026-10-10T00:00:00Z",
            "action_key":"ADOPT","actor_keys":["eu-council"],
            "target_keys":["russia"],"subject_key":"sanctions-package",
            "location_key":"brussels"}

def claim_desc():
    return {"claim_type":"DECISION","value_keys":["adopted"],
            "unit_key":None}

def test_generic_event_identity_is_order_stable():
    a=event_desc()
    b=event_desc(); b["actor_keys"]=["eu-council"]; b["target_keys"]=["russia"]
    assert generic_event_identity(a)==generic_event_identity(b)
    assert generic_event_identity(a).startswith("geo-diplomatic-20261010-")

def test_generic_claim_signature_is_typed_and_stable():
    sig=generic_claim_signature(claim_desc())
    assert sig.startswith("claim-decision-")
    assert sig==generic_claim_signature(claim_desc())

def test_generic_descriptor_rejects_non_day_boundary():
    d=event_desc(); d["event_date_utc"]="2026-10-10T12:00:00Z"
    with pytest.raises(ValueError,match="day boundary"):
        validate_generic_event_descriptor(d)

def test_generic_descriptor_binding_is_enforced_by_source_contract():
    req=sample()
    ed=event_desc(); cd=claim_desc()
    item={"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
          "source_id":"official-a","observation_id":"obs-1","status":"SUCCESS",
          "observed_at_utc":"2026-09-28T12:00:00Z",
          "published_at_utc":"2026-09-02T11:00:00Z",
          "available_at_utc":"2026-09-02T11:30:00Z",
          "public_url":"https://example.test/item","summary":"Council adopts sanctions",
          "error_code":None,"event_identity":generic_event_identity(ed),
          "claim_signature":generic_claim_signature(cd),
          "event_descriptor":ed,"claim_descriptor":cd}
    assert validate_source_observation(req,item) is item
    item["event_identity"]="geo-diplomatic-bad"
    with pytest.raises(ValueError,match="identity mismatch"):
        validate_source_observation(req,item)
