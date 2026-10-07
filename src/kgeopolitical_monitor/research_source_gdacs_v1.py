"""Bounded public/free GDACS owner-pilot source adapter.

GDACS is UN/European Commission disaster-awareness data. Transport is injected.
"""
from __future__ import annotations
from urllib.parse import urlencode
from .research_request_v1 import validate_request, _utc

BASE="https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
SOURCE_ID="gdacs-events"\n\ndef _gdacs_utc(value):\n    if not isinstance(value,str): raise ValueError("invalid GDACS timestamp")\n    candidate=value if value.endswith("Z") else value+"Z"\n    _utc(candidate)\n    return candidate

def build_query(request, *, eventlist="EQ;TC;FL;VO;DR;WF"):
    validate_request(request)
    if not isinstance(eventlist,str) or not eventlist:
        raise ValueError("invalid GDACS event scope")
    start=_utc(request["period_start_utc"]).date().isoformat()
    end=_utc(request["period_end_utc"]).date().isoformat()
    return BASE+"?"+urlencode({"eventlist":eventlist,"fromdate":start,"todate":end,
                               "alertlevel":"red;orange;green"})

def fetch(request, *, observed_at_utc, http_get, eventlist="EQ;TC;FL;VO;DR;WF"):
    _utc(observed_at_utc); url=build_query(request,eventlist=eventlist)
    try: payload=http_get(url)
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":"gdacs-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
          "public_url":None,"summary":None,"error_code":"TRANSPORT_UNAVAILABLE"}]
    features=payload.get("features") if isinstance(payload,dict) else None
    if not isinstance(features,list): raise ValueError("invalid GDACS response")
    out=[]
    for n,feature in enumerate(features[:request["max_results"]],1):
        p=feature.get("properties",{}) if isinstance(feature,dict) else {}
        title=p.get("name") or p.get("description") or p.get("eventname")
        published=_gdacs_utc(p.get("datemodified") or p.get("fromdate"))
        if not isinstance(title,str) or not title.strip():
            raise ValueError("invalid GDACS event")
        # GDACS API date variants are normalized by the live transport wrapper;
        # canonical adapter receives UTC-Z timestamps only.
        _utc(published)
        eventid=str(p.get("eventid","unknown"))
        eventtype=str(p.get("eventtype","event"))
        public=f"https://www.gdacs.org/resources.aspx?eventid={eventid}&eventtype={eventtype}"
        status="SUCCESS"
        if request["mode"]=="HISTORICAL_AS_OF" and _utc(observed_at_utc)>_utc(request["as_of_utc"]):
            status="INVALID"
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":f"gdacs-{n:03d}","status":status,
              "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
              "public_url":None,"summary":None,"error_code":"HISTORICAL_AVAILABILITY_UNPROVEN"})
        else:
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":f"gdacs-{n:03d}","status":status,
              "observed_at_utc":observed_at_utc,"published_at_utc":published,
              "available_at_utc":observed_at_utc,"public_url":public,"summary":title[:1000],
              "error_code":None})
    return out
