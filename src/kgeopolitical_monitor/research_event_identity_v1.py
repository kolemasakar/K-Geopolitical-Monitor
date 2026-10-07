"""Conservative structured event identities for cross-source correlation.

Identity is evidence-correlation only. It does not grant source independence or
factual verification credit.
"""
from __future__ import annotations
import math
from .research_request_v1 import _utc, _ID

def _hemisphere(value, positive, negative):
    prefix=positive if value>=0 else negative
    return prefix+str(int(round(abs(value)*100))).zfill(4)

def earthquake_identity(*, origin_utc, latitude, longitude, magnitude):
    origin=_utc(origin_utc)
    for value in (latitude,longitude,magnitude):
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value):
            raise ValueError("invalid earthquake identity component")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180 or not 0 <= magnitude <= 10:
        raise ValueError("earthquake identity component out of range")
    key=(
        "eq-"+origin.strftime("%Y%m%dT%H%M")+"-"+
        _hemisphere(latitude,"n","s")+"-"+
        _hemisphere(longitude,"e","w")+"-m"+
        str(int(round(magnitude*10))).zfill(2)
    )
    if not _ID.fullmatch(key):
        raise ValueError("invalid derived event identity")
    return key
