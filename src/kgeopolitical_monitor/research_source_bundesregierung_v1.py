"""Public/free German Federal Government single-page owner-pilot source adapter."""
from __future__ import annotations
import hashlib, html, re
from datetime import datetime, timezone
from urllib.parse import urlsplit
from .research_request_v1 import validate_request,_utc
from .research_generic_mapping_profile_v1 import apply_mapping_profile

SOURCE_ID="germany-federal-government"
ORIGIN_GROUP="germany-federal-government"
_ALLOWED={"www.bundesregierung.de","bundesregierung.de"}

def _clean(raw):
    if isinstance(raw,bytes): text=raw.decode("utf-8","ignore")
    elif isinstance(raw,str): text=raw
    else: raise ValueError("invalid Bundesregierung response type")
    if len(text)>2_000_000: raise ValueError("Bundesregierung response exceeds bound")
    m=re.search(r'<time[^>]+datetime=["\']([^"\']+)["\']',text,re.I)
    if not m: raise ValueError("Bundesregierung publication timestamp missing")
    dt=datetime.fromisoformat(m.group(1).replace("Z","+00:00"))
    if dt.tzinfo is None: raise ValueError("naive Bundesregierung publication timestamp")
    pub=dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",text,flags=re.I|re.S)
    body=re.sub(r"<[^>]+>"," ",body)
    body=" ".join(html.unescape(body).split())
    return pub,body

def fetch(request,*,observed_at_utc,http_get,public_url,mapping_profile=None):
    validate_request(request); observed=_utc(observed_at_utc)
    p=urlsplit(public_url)
    if p.scheme!="https" or p.hostname not in _ALLOWED or p.username or p.password or p.fragment:
        raise ValueError("invalid Bundesregierung provenance")
    try: raw=http_get(public_url)
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":"bundes-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
          "public_url":None,"summary":None,"error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP}]
    published,body=_clean(raw)
    if not (_utc(request["period_start_utc"])<=_utc(published)<=_utc(request.get("as_of_utc",request["period_end_utc"]))): return []
    oid="bundes-"+hashlib.sha256(public_url.encode()).hexdigest()[:24]
    if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
          "source_id":SOURCE_ID,"observation_id":oid,"status":"INVALID","observed_at_utc":observed_at_utc,
          "published_at_utc":None,"available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","origin_group":None}]
    item={"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
      "source_id":SOURCE_ID,"observation_id":oid,"status":"SUCCESS","observed_at_utc":observed_at_utc,
      "published_at_utc":published,"available_at_utc":observed_at_utc,"public_url":public_url,
      "summary":body[:1000],"error_code":None,"origin_group":ORIGIN_GROUP}
    if mapping_profile is not None: item,_=apply_mapping_profile(item,body,mapping_profile)
    return [item]
