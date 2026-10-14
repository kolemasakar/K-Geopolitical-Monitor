import pytest
from kgeopolitical_monitor.research_event_identity_v1 import earthquake_identity, earthquake_claim_signature

def test_event_identity_is_stable_across_magnitude_revision():
    a=earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=54.4775,longitude=162.5648)
    b=earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=54.4775,longitude=162.5648)
    assert a==b=="eq-20261007T181504-n5448-e16256"
    assert earthquake_claim_signature(magnitude=4.8)=="mag-48"
    assert earthquake_claim_signature(magnitude=4.9)=="mag-49"

def test_identity_range_validation_is_fail_closed():
    with pytest.raises(ValueError,match="out of range"):
        earthquake_identity(origin_utc="2026-10-07T18:15:04Z",latitude=91,longitude=10)
