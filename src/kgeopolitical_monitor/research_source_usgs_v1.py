"""Bounded public/free USGS earthquake owner-pilot source adapter.

Official U.S. Geological Survey FDSN event API. Transport is injected.
"""
from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
from .research_request_v1 import validate_request, _utc
from .research_event_identity_v1 import earthquake_identity, earthquake_claim_signature

BASE="https://earthquake.usgs.gov/fdsnws/event/1/query"
SOURCE_ID="usgs-earthquake"

def _iso(value):
    return _utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")

def _epoch_ms_utc(value):
    if not isinstance(value,(int,float)):
        raise ValueError("invalid USGS updated timestamp")
    return datetime.fromtimestamp(value/1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_query(request, *, min_magnitude=4.5):
    validate_request(request)
    if not isinstance(min_magnitude,(int,float)) or isinstance(min_magnitude,bool) or not 0 <= min_magnitude <= 10:
        raise ValueError("invalid USGS minimum magnitude")
    end=request.get("as_of_utc",request["period_end_utc"])
    params={"format":"geojson","starttime":_iso(request["period_start_utc"]),
            "endtime":_iso(end),"limit":min(request["max_results"],50),
            "orderby":"time","minmagnitude":min_magnitude}
    return BASE+"?"+urlencode(params)

def fetch(request, *, observed_at_utc, http_get, min_magnitude=4.5):
    validate_request(request); _utc(observed_at_utc)
    try:
        payload=http_get(build_query(request,min_magnitude=min_magnitude))
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":"usgs-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
          "public_url":None,"summary":None,"error_code":"TRANSPORT_UNAVAILABLE","event_identity":None,"claim_signature":None,"origin_group":"usgs-neic","event_parameters":None}]
    features=payload.get("features") if isinstance(payload,dict) else None
    if not isinstance(features,list):
        raise ValueError("invalid USGS response")
    out=[]
    for feature in features[:min(request["max_results"],50)]:
        if not isinstance(feature,dict) or not isinstance(feature.get("properties"),dict):
            raise ValueError("invalid USGS feature")
        props=feature["properties"]; fid=feature.get("id")
        title=props.get("title"); url=props.get("url")
        geometry=feature.get("geometry")
        if not isinstance(fid,str) or not fid or not isinstance(title,str) or not title.strip():
            raise ValueError("invalid USGS event identity")
        if not isinstance(url,str) or urlparse(url).scheme!="https":
            raise ValueError("invalid USGS provenance")
        published=_epoch_ms_utc(props.get("updated"))
        origin=_epoch_ms_utc(props.get("time"))
        if not isinstance(geometry,dict) or geometry.get("type")!="Point":
            raise ValueError("invalid USGS geometry")
        coordinates=geometry.get("coordinates")
        if not isinstance(coordinates,list) or len(coordinates)<2:
            raise ValueError("invalid USGS coordinates")
        magnitude=props.get("mag")
        event_identity=earthquake_identity(origin_utc=origin,latitude=coordinates[1],
                                            longitude=coordinates[0])
        claim_signature=earthquake_claim_signature(magnitude=magnitude)
        event_parameters={"kind":"EARTHQUAKE","origin_utc":origin,
                          "latitude":coordinates[1],"longitude":coordinates[0],
                          "magnitude":magnitude}
        if request["mode"]=="HISTORICAL_AS_OF" and _utc(observed_at_utc)>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"usgs-"+fid,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
              "public_url":None,"summary":None,"error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","event_identity":None,"claim_signature":None,"origin_group":"usgs-neic","event_parameters":None})
        else:
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"usgs-"+fid,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":published,
              "available_at_utc":observed_at_utc,"public_url":url,"summary":title[:1000],
              "error_code":None,"event_identity":event_identity,"claim_signature":claim_signature,"origin_group":"usgs-neic","event_parameters":event_parameters})
    return out
