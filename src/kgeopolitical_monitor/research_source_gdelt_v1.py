"""Bounded GDELT DOC 2.0 owner-pilot adapter.

Public/free/read-only HTTPS only. No credentials, paid fallback, daemon or
automatic scheduling. Network transport is injected for deterministic tests.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, urlparse
from .research_request_v1 import validate_request, _utc
from .research_source_cooldown_v1 import check_cooldown, record_cooldown

BASE = "https://api.gdeltproject.org/api/v2/doc/doc"
SOURCE_ID = "gdelt-doc-v2"
RETRYABLE = {"RATE_LIMITED", "TRANSPORT_UNAVAILABLE"}
MAX_ATTEMPTS = 2

def _stamp(value):
    return _utc(value).strftime("%Y%m%d%H%M%S")

def build_query(request, *, query):
    validate_request(request)
    if not isinstance(query, str) or not 1 <= len(query) <= 256:
        raise ValueError("invalid GDELT query")
    end = request.get("as_of_utc", request["period_end_utc"])
    params={"query":query,"mode":"artlist","format":"json","sort":"datedesc",
            "maxrecords":min(request["max_results"], 50),
            "startdatetime":_stamp(request["period_start_utc"]),
            "enddatetime":_stamp(end)}
    return BASE+"?"+urlencode(params)

def normalize_article(request, article, *, observed_at_utc, ordinal):
    validate_request(request); _utc(observed_at_utc)
    if not isinstance(article, dict):
        raise ValueError("invalid GDELT article")
    url=article.get("url"); title=article.get("title"); seen=article.get("seendate")
    if not isinstance(url,str) or urlparse(url).scheme!="https":
        raise ValueError("non-HTTPS GDELT article")
    if not isinstance(title,str) or not title.strip():
        raise ValueError("missing GDELT title")
    if not isinstance(seen,str):
        raise ValueError("missing GDELT publication timestamp")
    try:
        published=datetime.strptime(seen,"%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid GDELT publication timestamp") from exc
    published_at=published.strftime("%Y-%m-%dT%H:%M:%SZ")
    # observed_at is the first availability fact KGM itself can attest.
    # Never backdate it to GDELT's publication timestamp.
    available_at=observed_at_utc
    status="SUCCESS"
    if request["mode"]=="HISTORICAL_AS_OF" and _utc(available_at)>_utc(request["as_of_utc"]):
        status="INVALID"
        return {"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
            "source_id":SOURCE_ID,"observation_id":f"gdelt-{ordinal:03d}","status":status,
            "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
            "public_url":None,"summary":None,"error_code":"HISTORICAL_AVAILABILITY_UNPROVEN"}
    return {"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
        "source_id":SOURCE_ID,"observation_id":f"gdelt-{ordinal:03d}","status":status,
        "observed_at_utc":observed_at_utc,"published_at_utc":published_at,
        "available_at_utc":available_at,"public_url":url,"summary":title[:1000],
        "error_code":None}

def fetch(request, *, query, observed_at_utc, http_get, sleep=lambda _: None,
          max_attempts=MAX_ATTEMPTS, cooldown_root=None, cooldown_seconds=300):
    url=build_query(request,query=query)
    observed=_utc(observed_at_utc)
    if type(max_attempts) is not int or not 1 <= max_attempts <= MAX_ATTEMPTS:
        raise ValueError("invalid GDELT attempt bound")
    if type(cooldown_seconds) is not int or not 1 <= cooldown_seconds <= 3600:
        raise ValueError("invalid GDELT cooldown bound")
    if cooldown_root is not None:
        saved=check_cooldown(cooldown_root,SOURCE_ID,observed_at_utc=observed_at_utc)
        if saved is not None:
            return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
                "source_id":SOURCE_ID,"observation_id":"gdelt-cooldown","status":"UNAVAILABLE",
                "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
                "public_url":None,"summary":None,"error_code":saved["reason"]}]
    payload=None; code=None
    for attempt in range(max_attempts):
        try:
            payload=http_get(url); code=None; break
        except (TimeoutError, OSError) as exc:
            code="RATE_LIMITED" if getattr(exc, "code", None)==429 else "TRANSPORT_UNAVAILABLE"
            if attempt + 1 < max_attempts:
                sleep(2 ** attempt)
    if code is not None:
        if cooldown_root is not None:
            until=(observed+timedelta(seconds=cooldown_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
            record_cooldown(cooldown_root,SOURCE_ID,until_utc=until,reason=code)
        return [{"schema_version":"kgm.source.observation.v1","request_id":request["request_id"],
            "source_id":SOURCE_ID,"observation_id":"gdelt-transport","status":"UNAVAILABLE",
            "observed_at_utc":observed_at_utc,"published_at_utc":None,"available_at_utc":None,
            "public_url":None,"summary":None,"error_code":code}]
    if not isinstance(payload,dict) or not isinstance(payload.get("articles"),list):
        raise ValueError("invalid GDELT response")
    return [normalize_article(request,a,observed_at_utc=observed_at_utc,ordinal=i+1)
            for i,a in enumerate(payload["articles"][:min(request["max_results"],50)])]
