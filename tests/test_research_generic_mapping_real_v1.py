from kgeopolitical_monitor.research_generic_mapping_v1 import correlate_explicit_facts

EVENT={"family":"DIPLOMATIC","event_date_utc":"2026-09-24T00:00:00Z",
       "action_key":"MEET",
       "actor_keys":["nato-secgen-mark-rutte","president-ukraine-volodymyr-zelenskyy"],
       "target_keys":[],"subject_key":"ukraine-nato-bilateral-meeting",
       "location_key":"new-york-us"}
CLAIM={"claim_type":"STATUS","value_keys":["meeting-held"],"unit_key":None}

def facts():
    return [
      {"schema_version":"kgm.research.generic-mapping.v1",
       "source_id":"nato-news","origin_group":"nato","source_fact_id":"nato-20260924-zelenskyy-rutte",
       "public_url":"https://www.nato.int/en/news-and-events/articles/news/2026/09/25/nato-secretary-general-joins-world-leaders-in-new-york-during-unga-commemorates-25th-anniversary-of-911-attacks",
       "event_descriptor":EVENT,"claim_descriptor":CLAIM},
      {"schema_version":"kgm.research.generic-mapping.v1",
       "source_id":"president-ua-official","origin_group":"president-ukraine",
       "source_fact_id":"president-ua-20260924-rutte",
       "public_url":"https://www.president.gov.ua/en/news/volodimir-zelenskij-i-mark-ryutte-obgovorili-zabezpechennya-106565",
       "event_descriptor":EVENT,"claim_descriptor":CLAIM}
    ]

def test_real_official_nato_ukraine_presidency_pair_maps_same_event():
    result=correlate_explicit_facts(facts())
    assert result["event_match"] is True
    assert result["claim_match"] is True
    assert result["independent_origin_candidate"] is True
    assert result["source_ids"]==["nato-news","president-ua-official"]
    assert result["origin_groups"]==["nato","president-ukraine"]

def test_real_pair_mapping_is_fail_closed_on_different_event_day():
    items=facts()
    changed=dict(items[1])
    changed["event_descriptor"]=dict(EVENT)
    changed["event_descriptor"]["event_date_utc"]="2026-09-25T00:00:00Z"
    items[1]=changed
    result=correlate_explicit_facts(items)
    assert result["event_match"] is False
    assert result["event_identity"] is None

def test_real_pair_mapping_does_not_convert_origin_candidate_to_verification():
    result=correlate_explicit_facts(facts())
    assert "verification" not in result
    assert "factual_verification_credit" not in result
