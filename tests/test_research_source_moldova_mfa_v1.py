from kgeopolitical_monitor.research_source_moldova_mfa_v1 import fetch
from test_research_request_v1 import sample

HTML="""<html><body>
<span property="dc:date dc:created" content="2026-10-08T16:17:15+03:00" datatype="xsd:dateTime">Thu, 08/10/2026 - 16:17</span>
<div class="field field-name-body field-type-text-with-summary field-label-hidden">
<div class="field-items"><div class="field-item even" property="content:encoded">
<p>08 octombrie 2026, Chișinău – Viceprim-ministrul Mihai Popșoi a avut o întrevedere cu secretarul general adjunct al NATO, Radmila Shekerinska.</p>
<p>Discuțiile au vizat parteneriatul dintre Republica Moldova și NATO.</p>
</div></div></div>
</body></html>"""

URL="https://www.mfa.gov.md/ro/content/test-event"
EVENT={"family":"DIPLOMATIC","event_date_utc":"2026-10-08T00:00:00Z",
       "action_key":"MEET","actor_keys":["moldova-dpm-mfa-mihai-popsoi","nato-dsg-radmila-shekerinska"],
       "target_keys":[],"subject_key":"nato-moldova-bilateral-meeting","location_key":"chisinau-moldova"}
CLAIM={"claim_type":"STATUS","value_keys":["meeting-held"],"unit_key":None}
PROFILE={"source_id":"moldova-mfa",
         "required_phrases":["mihai popșoi","radmila shekerinska"],
         "event_descriptor":EVENT,"claim_descriptor":CLAIM}

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc")
    r["period_start_utc"]="2026-10-08T00:00:00Z"
    r["period_end_utc"]="2026-10-09T23:59:59Z"
    return r

def test_moldova_mfa_page_normalizes_and_maps():
    items=fetch(current(),observed_at_utc="2026-10-08T14:00:00Z",
                http_get=lambda _:HTML,public_url=URL,mapping_profile=PROFILE)
    assert len(items)==1
    x=items[0]
    assert x["source_id"]=="moldova-mfa"
    assert x["origin_group"]=="moldova-mfa"
    assert x["published_at_utc"]=="2026-10-08T13:17:15Z"
    assert x["event_descriptor"]==EVENT
    assert x["claim_descriptor"]==CLAIM
    assert x["event_identity"].startswith("geo-diplomatic-20261008-")

def test_moldova_mfa_historical_live_backdating_denied():
    r=current(); r["mode"]="HISTORICAL_AS_OF"
    r["period_end_utc"]="2026-10-08T13:30:00Z"
    r["as_of_utc"]="2026-10-08T13:30:00Z"
    r["requested_at_utc"]="2026-10-08T14:00:00Z"
    items=fetch(r,observed_at_utc="2026-10-08T14:00:00Z",
                http_get=lambda _:HTML,public_url=URL)
    assert items[0]["status"]=="INVALID"
    assert items[0]["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_moldova_mfa_host_is_allowlisted():
    import pytest
    with pytest.raises(ValueError,match="provenance"):
        fetch(current(),observed_at_utc="2026-10-08T14:00:00Z",
              http_get=lambda _:HTML,public_url="https://example.com/x")
