"""Canonical public/free ECB RSS owner-pilot source adapter.

Official European Central Bank press/news RSS. Transport is injected; no
credentials, paid fallback or write-back.
"""
from __future__ import annotations
import hashlib
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit
from .research_request_v1 import validate_request, _utc

SOURCE_ID="ecb-press"
ORIGIN_GROUP="ecb"
FEED_URL="https://www.ecb.europa.eu/rss/press.html"

def _published(value):
    try:
        dt=parsedate_to_datetime(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError("invalid ECB publication timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("naive ECB publication timestamp")
    return dt.astimezone(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch(request, *, observed_at_utc, http_get, query=None):
    validate_request(request); observed=_utc(observed_at_utc)
    if query is not None and (not isinstance(query,str) or not 1<=len(query)<=256):
        raise ValueError("invalid ECB query")
    try:
        payload=http_get(FEED_URL)
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":"ecb-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,
          "available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP}]
    if isinstance(payload,bytes):
        raw=payload
    elif isinstance(payload,str):
        raw=payload.encode("utf-8")
    else:
        raise ValueError("invalid ECB response type")
    if len(raw)>2_000_000:
        raise ValueError("ECB response exceeds bound")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("invalid ECB XML") from exc

    terms=[x for x in re.split(r"\s+",query.lower().strip()) if x] if query else []
    start=_utc(request["period_start_utc"])
    end=_utc(request.get("as_of_utc",request["period_end_utc"]))
    out=[]
    for entry in root.findall(".//item"):
        title=" ".join((entry.findtext("title") or "").split())
        link=(entry.findtext("link") or "").strip()
        pub=(entry.findtext("pubDate") or "").strip()
        if not title or not link or not pub:
            continue
        parsed=urlsplit(link)
        if parsed.scheme!="https" or parsed.hostname not in {"www.ecb.europa.eu","ecb.europa.eu"}:
            raise ValueError("invalid ECB provenance")
        if terms and not all(term in title.lower() for term in terms):
            continue
        published=_published(pub); published_dt=_utc(published)
        if published_dt<start or published_dt>end:
            continue
        oid="ecb-"+hashlib.sha256(link.encode("utf-8")).hexdigest()[:24]
        if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,
              "available_at_utc":None,"public_url":None,"summary":None,
              "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","origin_group":None})
        else:
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":published,
              "available_at_utc":observed_at_utc,"public_url":link,
              "summary":title[:1000],"error_code":None,
              "origin_group":ORIGIN_GROUP})
        if len(out)>=min(request["max_results"],50):
            break
    return out
