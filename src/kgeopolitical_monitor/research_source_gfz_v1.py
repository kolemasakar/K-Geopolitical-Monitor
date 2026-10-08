"""Bounded public/free GFZ GEOFON FDSN earthquake owner-pilot adapter."""
from __future__ import annotations
from urllib.parse import urlencode
from .research_request_v1 import validate_request, _utc
from .research_event_identity_v1 import earthquake_identity, earthquake_claim_signature

BASE="https://geofon.gfz-potsdam.de/fdsnws/event/1/query"
SOURCE_ID="gfz-geofon"
ORIGIN_GROUP="gfz-geofon"

def _iso(value):
    return _utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")

def build_query(request, *, min_magnitude=4.5):
    validate_request(request)
    if not isinstance(min_magnitude,(int,float)) or isinstance(min_magnitude,bool) or not 0 <= min_magnitude <= 10:
        raise ValueError("invalid GFZ minimum magnitude")
    end=request.get("as_of_utc",request["period_end_utc"])
    params={"format":"text","starttime":_iso(request["period_start_utc"]),
            "endtime":_iso(end),"limit":min(request["max_results"],50),
            "orderby":"time","minmagnitude":min_magnitude}
    return BASE+"?"+urlencode(params)

def _parse(text):
    if not isinstance(text,str):
        raise ValueError("invalid GFZ response")
    lines=[x for x in text.splitlines() if x.strip()]
    if not lines or not lines[0].startswith("#EventID|Time|Latitude|Longitude|"):
        raise ValueError("invalid GFZ header")
    out=[]
    for line in lines[1:]:
        parts=line.split("|")
        if len(parts)<14:
            raise ValueError("invalid GFZ row")
        out.append(parts)
    return out

def fetch(request, *, observed_at_utc, http_get, min_magnitude=4.5):
    validate_request(request); _utc(observed_at_utc)
    try:
        text=http_get(build_query(request,min_magnitude=min_magnitude))
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":"gfz-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
          "public_url":None,"summary":None,"error_code":"TRANSPORT_UNAVAILABLE",
          "event_identity":None,"claim_signature":None,"origin_group":ORIGIN_GROUP,
          "event_parameters":None}]
    rows=_parse(text)
    out=[]
    for parts in rows[:min(request["max_results"],50)]:
        event_id,time_s,lat_s,lon_s,depth_s,author,catalog,contributor,contributor_id,magtype,mag_s,magauthor,region,eventtype=parts[:14]
        if not event_id or eventtype.lower()!="earthquake":
            continue
        origin=time_s if time_s.endswith("Z") else time_s+"Z"
        _utc(origin)
        try:
            lat=float(lat_s); lon=float(lon_s); mag=float(mag_s)
        except ValueError as exc:
            raise ValueError("invalid GFZ numeric field") from exc
        identity=earthquake_identity(origin_utc=origin,latitude=lat,longitude=lon)
        signature=earthquake_claim_signature(magnitude=mag)
        public=BASE+"?"+urlencode({"format":"text","eventid":event_id})
        params={"kind":"EARTHQUAKE","origin_utc":origin,
                "latitude":lat,"longitude":lon,"magnitude":mag}
        summary=f"M {mag:.1f} - {region.strip() or 'GFZ earthquake'}"
        if request["mode"]=="HISTORICAL_AS_OF" and _utc(observed_at_utc)>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"gfz-"+event_id,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
              "public_url":None,"summary":None,"error_code":"HISTORICAL_AVAILABILITY_UNPROVEN",
              "event_identity":None,"claim_signature":None,"origin_group":ORIGIN_GROUP,
              "event_parameters":None})
        else:
            # The text endpoint has no publication-update field. Use KGM's first
            # observed availability as a conservative non-backdated publication boundary.
            out.append({"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
              "source_id":SOURCE_ID,"observation_id":"gfz-"+event_id,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":observed_at_utc,
              "available_at_utc":observed_at_utc,"public_url":public,"summary":summary[:1000],
              "error_code":None,"event_identity":identity,"claim_signature":signature,
              "origin_group":ORIGIN_GROUP,"event_parameters":params})
    return out
