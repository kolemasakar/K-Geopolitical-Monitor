import pytest
from kgeopolitical_monitor.research_event_identity_v1 import earthquake_identity, earthquake_claim_signature
from kgeopolitical_monitor.research_source_adapter_v1 import validate_source_observation
from test_research_request_v1 import sample

def test_event_identity_is_stable_across_magnitude_revision():
    a=earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=54.4775,longitude=162.5648)
    b=earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=54.4775,longitude=162.5648)
    assert a==b=="eq-20261007T181504-n5448-e16256"
    assert earthquake_claim_signature(magnitude=4.8)=="mag-48"
    assert earthquake_claim_signature(magnitude=4.9)=="mag-49"

def test_claim_signature_requires_event_identity():
    req=sample()
    item={"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
          "source_id":"source-a","observation_id":"obs-1","status":"SUCCESS",
          "observed_at_utc":"2026-09-28T12:00:00Z",
          "published_at_utc":"2026-09-02T11:00:00Z",
          "available_at_utc":"2026-09-02T11:30:00Z",
          "public_url":"https://example.test/item","summary":"claim","error_code":None,
          "claim_signature":"mag-50"}
    with pytest.raises(ValueError,match="requires event identity"):
        validate_source_observation(req,item)

def test_identity_range_validation_is_fail_closed():
    with pytest.raises(ValueError,match="out of range"):
        earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=91,longitude=10)
