"""Bounded public/free USGS earthquake owner-pilot source adapter.

Official U.S. Geological Survey FDSN event API. Transport is injected.
"""
from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
from .research_request_v1 import validate_request, _utc

BASE="https://earthquake.usgs.gov/fdsnws/event/1/query"
SOURCE_ID="usgs-earthquake"

def _iso(value):
    return _utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")

def _epoch_ms_utc(value):
    if not isinstance(value,(int,float)):
        raise ValueError("invalid USGS updated timestamp")
    return datetime.fromtimestamp(value/1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_query(request):
    validate_request(request)
    end=request.get("as_of_utc",request["period_end_utc"])
    params={"format":"geojson","starttime":_iso(request["period_start_utc"]),
            "endtime":_iso(end),"limit":min(request["max_results"],50),
            "orderby":"time"}
    return BASE+"?"+urlencode(params)

def fetch(request, *, observed_at_utc, http_get):
    validate_request(request); _utc(observed_at_utc)
    try:
        payload=http_get(build_query(request))
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":"usgs-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
          "public_url":None,"summary":None,"error_code":"TRANSPORT_UNAVAILABLE"}]
    features=payload.get("features") if isinstance(payload,dict) else None
    if not isinstance(features,list):
        raise ValueError("invalid USGS response")
    out=[]
    for feature in features[:min(request["max_results"],50)]:
        if not isinstance(feature,dict) or not isinstance(feature.get("properties"),dict):
            raise ValueError("invalid USGS feature")
        props=feature["properties"]; fid=feature.get("id")
        title=props.get("title"); url=props.get("url")
        if not isinstance(fid,str) or not fid or not isinstance(title,str) or not title.strip():
            raise ValueError("invalid USGS event identity")
        if not isinstance(url,str) or urlparse(url).scheme!="https":
            raise ValueError("invalid USGS provenance")
        published=_epoch_ms_utc(props.get("updated"))
        if request["mode"]=="HISTORICAL_AS_OF" and _utc(observed_at_utc)>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"usgs-"+fid,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
              "public_url":None,"summary":None,"error_code":"HISTORICAL_AVAILABILITY_UNPROVEN"})
        else:
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"usgs-"+fid,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":published,
              "available_at_utc":observed_at_utc,"public_url":url,"summary":title[:1000],
              "error_code":None})
    return out
