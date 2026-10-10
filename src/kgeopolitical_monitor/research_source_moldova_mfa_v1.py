"""Public/free Moldova MFA single-page owner-pilot adapter.

Fetches one allowlisted official MFA article URL and optionally applies a strict
generic mapping profile. No credentials, paid fallback, or write-back.
"""
from __future__ import annotations
import hashlib
import html
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit
from .research_request_v1 import validate_request, _utc
from .research_generic_mapping_profile_v1 import apply_mapping_profile

SOURCE_ID="moldova-mfa"
ORIGIN_GROUP="moldova-mfa"
_ALLOWED_HOSTS={"mfa.gov.md","www.mfa.gov.md"}

def _clean_html(value):
    text=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",value,flags=re.I|re.S)
    text=re.sub(r"<[^>]+>"," ",text)
    return " ".join(html.unescape(text).split())

def _parse_page(raw):
    if isinstance(raw,bytes):
        text=raw.decode("utf-8","ignore")
    elif isinstance(raw,str):
        text=raw
    else:
        raise ValueError("invalid Moldova MFA response type")
    if len(text)>2_000_000:
        raise ValueError("Moldova MFA response exceeds bound")
    match=re.search(
        r'property=["\']dc:date dc:created["\'][^>]*content=["\']([^"\']+)["\']',
        text,re.I)
    if not match:
        raise ValueError("Moldova MFA publication timestamp missing")
    try:
        dt=datetime.fromisoformat(match.group(1))
    except ValueError as exc:
        raise ValueError("invalid Moldova MFA publication timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("naive Moldova MFA publication timestamp")
    published=dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body_match=re.search(
        r'field-name-body[^>]*>.*?<div class=["\']field-item even["\'][^>]*>(.*?)</div>\s*</div>\s*</div>',
        text,re.I|re.S)
    if not body_match:
        raise ValueError("Moldova MFA body missing")
    body=_clean_html(body_match.group(1))
    if not body:
        raise ValueError("Moldova MFA body empty")
    return published,body

def fetch(request, *, observed_at_utc, http_get, public_url, mapping_profile=None):
    validate_request(request); observed=_utc(observed_at_utc)
    parsed=urlsplit(public_url)
    if (parsed.scheme!="https" or parsed.hostname not in _ALLOWED_HOSTS or
        parsed.username is not None or parsed.password is not None or parsed.fragment):
        raise ValueError("invalid Moldova MFA provenance")
    try:
        raw=http_get(public_url)
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":"mfa-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,
          "available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP}]
    published,body=_parse_page(raw)
    if not (_utc(request["period_start_utc"])<=_utc(published)<=
            _utc(request.get("as_of_utc",request["period_end_utc"]))):
        return []
    oid="mfa-"+hashlib.sha256(public_url.encode("utf-8")).hexdigest()[:24]
    if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
        return [{"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":oid,"status":"INVALID",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,
          "available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","origin_group":None}]
    item={"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":oid,"status":"SUCCESS",
          "observed_at_utc":observed_at_utc,"published_at_utc":published,
          "available_at_utc":observed_at_utc,"public_url":public_url,
          "summary":body[:1000],"error_code":None,"origin_group":ORIGIN_GROUP}
    if mapping_profile is not None:
        item,_=apply_mapping_profile(item,body,mapping_profile)
    return [item]
