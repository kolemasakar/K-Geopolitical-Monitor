from kgeopolitical_monitor.research_corroboration_v1 import build_corroboration_report

def obs(source, oid, origin_group, t, lat, lon, mag, claim=None):
    return {"schema_version":"kgm.source.observation.v1","request_id":"req-01",
        "source_id":source,"observation_id":oid,"status":"SUCCESS",
        "observed_at_utc":"2026-10-08T00:00:00Z",
        "published_at_utc":"2026-10-08T00:00:00Z",
        "available_at_utc":"2026-10-08T00:00:00Z",
        "public_url":"https://example.test/"+oid,"summary":oid,"error_code":None,
        "origin_group":origin_group,"claim_signature":claim or "mag-"+str(int(round(mag*10))).zfill(2),
        "event_identity":None,
        "event_parameters":{"kind":"EARTHQUAKE","origin_utc":t,
            "latitude":lat,"longitude":lon,"magnitude":mag}}

def test_same_origin_paths_do_not_double_count_independent_credit():
    items=[
        obs("usgs-earthquake","u1","usgs-neic","2026-10-07T18:15:04Z",54.4775,162.5648,4.8),
        obs("gdacs-events","g1","usgs-neic","2026-10-07T18:15:04Z",54.4775,162.5648,4.8),
        obs("gfz-geofon","f1","gfz-geofon","2026-10-07T18:15:06Z",54.58,162.231,5.2),
    ]
    report=build_corroboration_report(items,max_seconds=30,max_km=50)
    assert len(report)==1
    group=report[0]
    assert group["source_ids"]==["gdacs-events","gfz-geofon","usgs-earthquake"]
    assert group["origin_groups"]==["gfz-geofon","usgs-neic"]
    assert group["origin_assessment"]=="DISTINCT_ORIGIN"
    assert group["independent_origin_credit"] is True
    assert group["factual_verification_credit"] is False

def test_ambiguous_same_source_candidates_deny_credit():
    items=[
        obs("usgs-earthquake","u1","usgs-neic","2026-10-07T18:15:04Z",54.4775,162.5648,4.8),
        obs("gfz-geofon","f1","gfz-geofon","2026-10-07T18:15:06Z",54.58,162.231,5.2),
        obs("gfz-geofon","f2","gfz-geofon","2026-10-07T18:15:07Z",54.57,162.240,5.1),
    ]
    report=build_corroboration_report(items,max_seconds=30,max_km=50)
    assert len(report)==1
    assert report[0]["ambiguous"] is True
    assert report[0]["independent_origin_credit"] is False


def generic(source,oid,origin,event_id,claim):
    return {"schema_version":"kgm.source.observation.v1","request_id":"req-01",
        "source_id":source,"observation_id":oid,"status":"SUCCESS",
        "observed_at_utc":"2026-10-10T12:00:00Z",
        "published_at_utc":"2026-10-10T10:00:00Z",
        "available_at_utc":"2026-10-10T12:00:00Z",
        "public_url":"https://"+source+".example/"+oid,"summary":oid,"error_code":None,
        "origin_group":origin,"claim_signature":claim,"event_identity":event_id,
        "event_descriptor":{"family":"DIPLOMATIC","event_date_utc":"2026-10-10T00:00:00Z",
            "action_key":"MEET","actor_keys":["actor-a","actor-b"],"target_keys":[],
            "subject_key":"subject-a","location_key":"city-a"}}

def test_generic_exact_identity_creates_canonical_corroboration_group():
    items=[generic("source-a","a1","origin-a","geo-diplomatic-event-1","claim-status-1"),
           generic("source-b","b1","origin-b","geo-diplomatic-event-1","claim-status-1")]
    report=build_corroboration_report(items)
    assert len(report)==1
    group=report[0]
    assert group["origin_assessment"]=="DISTINCT_ORIGIN"
    assert group["independent_origin_credit"] is True
    assert group["claim_relation"]=="AGREES"
    assert group["verification_eligibility"]=="ELIGIBLE_FOR_EXPLICIT_VERIFICATION"
    assert group["automatic_verification"] is False
    assert group["factual_verification_credit"] is False

def test_generic_same_origin_does_not_gain_independent_credit():
    items=[generic("source-a","a1","origin-a","geo-diplomatic-event-1","claim-status-1"),
           generic("source-b","b1","origin-a","geo-diplomatic-event-1","claim-status-1")]
    group=build_corroboration_report(items)[0]
    assert group["origin_assessment"]=="SAME_ORIGIN"
    assert group["independent_origin_credit"] is False
    assert group["verification_eligibility"]=="INELIGIBLE"

def test_generic_claim_difference_is_event_only_unresolved():
    items=[generic("source-a","a1","origin-a","geo-diplomatic-event-1","claim-status-1"),
           generic("source-b","b1","origin-b","geo-diplomatic-event-1","claim-status-2")]
    group=build_corroboration_report(items)[0]
    assert group["claim_relation"]=="DIFFERS"
    assert group["verification_eligibility"]=="EVENT_CORROBORATED_CLAIM_UNRESOLVED"
    assert group["automatic_verification"] is False

def test_generic_duplicate_source_member_is_ambiguous_and_denies_credit():
    items=[generic("source-a","a1","origin-a","geo-diplomatic-event-1","claim-status-1"),
           generic("source-a","a2","origin-a","geo-diplomatic-event-1","claim-status-1"),
           generic("source-b","b1","origin-b","geo-diplomatic-event-1","claim-status-1")]
    group=build_corroboration_report(items)[0]
    assert group["ambiguous"] is True
    assert group["independent_origin_credit"] is False
