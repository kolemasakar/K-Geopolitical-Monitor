import pytest
from kgeopolitical_monitor.research_generic_mapping_profile_v1 import apply_mapping_profile
from kgeopolitical_monitor.research_generic_identity_v1 import generic_event_identity,generic_claim_signature

PROFILE={"source_id":"source-a",
 "required_phrases":["mihai popsoi","radmila shekerinska"],
 "event_descriptor":{"family":"DIPLOMATIC","event_date_utc":"2026-10-08T00:00:00Z",
   "action_key":"MEET","actor_keys":["moldova-dpm-mfa-mihai-popsoi","nato-dsg-radmila-shekerinska"],
   "target_keys":[],"subject_key":"nato-moldova-bilateral-meeting","location_key":"chisinau-moldova"},
 "claim_descriptor":{"claim_type":"STATUS","value_keys":["meeting-held"],"unit_key":None}}

def obs():
    return {"source_id":"source-a","observation_id":"obs-1"}

def test_strict_profile_attaches_only_on_required_phrases():
    item,matched=apply_mapping_profile(obs(),"Mihai Popsoi met Radmila Shekerinska.",PROFILE)
    assert matched is True
    assert item["event_identity"]==generic_event_identity(PROFILE["event_descriptor"])
    assert item["claim_signature"]==generic_claim_signature(PROFILE["claim_descriptor"])

def test_strict_profile_does_not_map_when_phrase_missing():
    item,matched=apply_mapping_profile(obs(),"Mihai Popsoi held a meeting.",PROFILE)
    assert matched is False
    assert "event_identity" not in item

def test_profile_source_binding_is_fail_closed():
    bad=dict(PROFILE); bad["source_id"]="other"
    with pytest.raises(ValueError,match="source mismatch"):
        apply_mapping_profile(obs(),"Mihai Popsoi Radmila Shekerinska",bad)
