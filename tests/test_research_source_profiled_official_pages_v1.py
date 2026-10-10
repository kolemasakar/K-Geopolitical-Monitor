import pytest
from kgeopolitical_monitor.research_source_govuk_v1 import fetch as gov_fetch
from kgeopolitical_monitor.research_source_bundesregierung_v1 import fetch as de_fetch
from kgeopolitical_monitor.research_source_elysee_v1 import fetch as fr_fetch
from test_research_request_v1 import sample

GOV='''<html><script type="application/ld+json">{"datePublished":"2026-10-08T14:36:40+01:00"}</script><body>Prime Minister Andy Burnham and Federal Chancellor Friedrich Merz finalised the ratification of the Kensington Treaty through the official exchange of documents.</body></html>'''
DE='''<html><time datetime="2026-10-08T13:30:00Z">8 October 2026</time><body>Prime Minister Andy Burnham and Federal Chancellor Friedrich Merz finalised the ratification of the Kensington Treaty through the official exchange of documents.</body></html>'''
FR='''<html><script type="application/ld+json">{"datePublished":"2026-10-02"}</script><body>G7 Leaders agreed coordinated measures to stabilize immediate energy supplies and strengthen global energy systems.</body></html>'''

EVENT={"family":"POLITICAL","event_date_utc":"2026-10-08T00:00:00Z","action_key":"RATIFY",
"actor_keys":["germany-federal-government","uk-government"],"target_keys":[],
"subject_key":"kensington-treaty","location_key":"berlin-germany"}
CLAIM={"claim_type":"STATUS","value_keys":["ratification-completed"],"unit_key":None}

def current():
    r=sample();r["mode"]="CURRENT";r.pop("as_of_utc")
    r["period_start_utc"]="2026-10-01T00:00:00Z";r["period_end_utc"]="2026-10-10T23:59:59Z"
    return r

def profile(source):
    return {"source_id":source,"required_phrases":["friedrich merz","kensington treaty","ratification"],
            "event_descriptor":EVENT,"claim_descriptor":CLAIM}

def test_govuk_profiled_page():
    x=gov_fetch(current(),observed_at_utc="2026-10-10T12:00:00Z",http_get=lambda _:GOV,
        public_url="https://www.gov.uk/government/news/test",mapping_profile=profile("govuk-official"))[0]
    assert x["published_at_utc"]=="2026-10-08T13:36:40Z"
    assert x["event_descriptor"]==EVENT

def test_bundesregierung_profiled_page():
    x=de_fetch(current(),observed_at_utc="2026-10-10T12:00:00Z",http_get=lambda _:DE,
        public_url="https://www.bundesregierung.de/breg-en/news/test",mapping_profile=profile("germany-federal-government"))[0]
    assert x["published_at_utc"]=="2026-10-08T13:30:00Z"
    assert x["event_descriptor"]==EVENT

def test_elysee_profiled_page():
    event={"family":"ECONOMIC","event_date_utc":"2026-10-02T00:00:00Z","action_key":"AGREE",
      "actor_keys":["g7-leaders"],"target_keys":[],"subject_key":"global-energy-security-market-stability","location_key":None}
    claim={"claim_type":"STATUS","value_keys":["coordinated-measures-agreed"],"unit_key":None}
    p={"source_id":"france-presidency","required_phrases":["g7 leaders","coordinated measures","energy"],
       "event_descriptor":event,"claim_descriptor":claim}
    x=fr_fetch(current(),observed_at_utc="2026-10-10T12:00:00Z",http_get=lambda _:FR,
        public_url="https://www.elysee.fr/G7evian/2026/10/02/test",mapping_profile=p)[0]
    assert x["origin_group"]=="france-presidency"
    assert x["event_descriptor"]["family"]=="ECONOMIC"
