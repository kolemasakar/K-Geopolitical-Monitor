"""Conservative structured event/claim identities for cross-source correlation.

These identities are correlation aids only. They never grant source
independence or factual verification credit.
"""
from __future__ import annotations
import math
from .research_request_v1 import _utc, _ID

def _hemisphere(value, positive, negative):
    prefix=positive if value>=0 else negative
    return prefix+str(int(round(abs(value)*100))).zfill(4)

def earthquake_identity(*, origin_utc, latitude, longitude):
    origin=_utc(origin_utc)
    for value in (latitude,longitude):
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value):
            raise ValueError("invalid earthquake identity component")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("earthquake identity component out of range")
    key=(
        "eq-"+origin.strftime("%Y%m%dT%H%M%S")+"-"+
        _hemisphere(latitude,"n","s")+"-"+
        _hemisphere(longitude,"e","w")
    )
    if not _ID.fullmatch(key):
        raise ValueError("invalid derived event identity")
    return key

def earthquake_claim_signature(*, magnitude):
    if not isinstance(magnitude,(int,float)) or isinstance(magnitude,bool) or not math.isfinite(magnitude):
        raise ValueError("invalid earthquake magnitude claim")
    if not 0 <= magnitude <= 10:
        raise ValueError("earthquake magnitude claim out of range")
    signature="mag-"+str(int(round(magnitude*10))).zfill(2)
    if not _ID.fullmatch(signature):
        raise ValueError("invalid claim signature")
    return signature
