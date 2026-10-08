"""Canonical public/free Consilium RSS owner-pilot source adapter.

Official Council of the EU / European Council press-release RSS. Transport is
injected; no credentials, paid fallback or write-back.
"""
from __future__ import annotations
import hashlib
import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from datetime import datetime, timezone
from .research_request_v1 import validate_request, _utc

SOURCE_ID="consilium-press-releases"
ORIGIN_GROUP="consilium-eu-council"
FEED_URL="https://www.consilium.europa.eu/en/rss/pressreleases.ashx"

def _clean(value):
    text=re.sub(r"<[^>]+>"," ",value or "")
    return " ".join(html.unescape(text).split())

def _published(value):
    try:
        dt=parsedate_to_datetime(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError("invalid Consilium publication timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("naive Consilium publication timestamp")
    return dt.astimezone(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch(request, *, observed_at_utc, http_get, query=None):
    validate_request(request); observed=_utc(observed_at_utc)
    if query is not None and (not isinstance(query,str) or not 1<=len(query)<=256):
        raise ValueError("invalid Consilium query")
    try:
        payload=http_get(FEED_URL)
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":"consilium-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,
          "available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP}]
    if isinstance(payload,bytes):
        raw=payload
    elif isinstance(payload,str):
        raw=payload.encode("utf-8")
    else:
        raise ValueError("invalid Consilium response type")
    if len(raw)>2_000_000:
        raise ValueError("Consilium response exceeds bound")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("invalid Consilium XML") from exc
    terms=[x for x in re.split(r"\s+",query.lower().strip()) if x] if query else []
    start=_utc(request["period_start_utc"])
    end=_utc(request.get("as_of_utc",request["period_end_utc"]))
    out=[]
    for entry in root.findall(".//item"):
        title=_clean(entry.findtext("title") or "")
        description=_clean(entry.findtext("description") or "")
        link=(entry.findtext("link") or "").strip()
        pub=(entry.findtext("pubDate") or "").strip()
        if not title or not link or not pub:
            continue
        if urlparse(link).scheme!="https":
            raise ValueError("invalid Consilium provenance")
        searchable=(title+" "+description).lower()
        if terms and not all(term in searchable for term in terms):
            continue
        published=_published(pub)
        published_dt=_utc(published)
        if published_dt<start or published_dt>end:
            continue
        oid="consilium-"+hashlib.sha256(link.encode("utf-8")).hexdigest()[:24]
        if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,
              "available_at_utc":None,"public_url":None,"summary":None,
              "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN",
              "origin_group":None})
        else:
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":published,
              "available_at_utc":observed_at_utc,"public_url":link,
              "summary":(description or title)[:1000],"error_code":None,
              "origin_group":ORIGIN_GROUP})
        if len(out)>=min(request["max_results"],50):
            break
    return out
