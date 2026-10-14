"""Conservative earthquake association across independent origins."""
from __future__ import annotations
import math
from .research_request_v1 import _utc

def _distance_km(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,[a["latitude"],a["longitude"],b["latitude"],b["longitude"]])
    dlat=lat2-lat1; dlon=lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371.0*2*math.asin(min(1.0,math.sqrt(h)))

def associate_earthquakes(a,b,*,max_seconds=30,max_km=50):
    pa=a.get("event_parameters"); pb=b.get("event_parameters")
    if not isinstance(pa,dict) or not isinstance(pb,dict):
        return {"match":False,"reason":"MISSING_PARAMETERS"}
    if pa.get("kind")!="EARTHQUAKE" or pb.get("kind")!="EARTHQUAKE":
        return {"match":False,"reason":"UNSUPPORTED_KIND"}
    dt=abs((_utc(pa["origin_utc"])-_utc(pb["origin_utc"])).total_seconds())
    km=_distance_km(pa,pb)
    match=dt<=max_seconds and km<=max_km
    return {"match":match,"reason":"MATCH" if match else "OUTSIDE_TOLERANCE",
            "delta_seconds":dt,"distance_km":km}
