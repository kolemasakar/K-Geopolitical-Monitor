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
