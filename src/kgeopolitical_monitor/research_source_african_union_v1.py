"""Bounded AU official *single article* parser (research-only, not activated).

An official statement is evidence the African Union issued a statement, not
independent verification of claims contained within it. Dates in AU article URLs
have day-only precision; no exact clock time may be inferred.
"""
from __future__ import annotations
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit
from .research_request_v1 import validate_request, _utc
import hashlib
import re

SOURCE_ID = "african-union-press"
ORIGIN_GROUP = "african-union"
_ALLOWED = {"au.int", "www.au.int"}
_MAX_BYTES = 2_000_000

class _ArticleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tagstack=[]
        self.heading=[]
        self.text=[]
        self.suppress=0
    def handle_starttag(self,tag,attrs):
        self.tagstack.append(tag)
        if tag in {"script","style","noscript"}:
            self.suppress+=1
    def handle_endtag(self,tag):
        if tag in {"script","style","noscript"} and self.suppress:
            self.suppress-=1
        if self.tagstack:
            self.tagstack.pop()
    def handle_data(self,data):
        if self.suppress or not data.strip():
            return
        self.text.append(data)
        if "h1" in self.tagstack:
            self.heading.append(data)

def _parse(raw, public_url):
    if isinstance(raw,bytes):
        if len(raw)>_MAX_BYTES:
            raise ValueError("African Union response exceeds bound")
        html=raw.decode("utf-8","replace")
    elif isinstance(raw,str):
        if len(raw.encode("utf-8"))>_MAX_BYTES:
            raise ValueError("African Union response exceeds bound")
        html=raw
    else:
        raise ValueError("invalid African Union response type")
    path=urlsplit(public_url).path
    match=re.fullmatch(r"/en/pressreleases/(20\d{6})/[a-z0-9-]+/?",path)
    if not match:
        raise ValueError("invalid African Union publication path")
    dt=datetime.strptime(match.group(1),"%Y%m%d").replace(tzinfo=timezone.utc)
    day_text=dt.strftime("%b %-d, %Y")
    parsed=_ArticleHTML()
    parsed.feed(html)
    heading=" ".join(" ".join(parsed.heading).split())
    body=" ".join(" ".join(parsed.text).split())
    if len(heading)<20 or not body or not body.count(heading):
        raise ValueError("African Union article heading missing")
    # Fail closed unless the document visibly contains its human-readable date.
    if day_text.lower() not in body.lower():
        raise ValueError("African Union publication day not corroborated in page")
    return dt.strftime("%Y-%m-%dT00:00:00Z"), heading, body

def fetch(request, *, observed_at_utc, http_get, public_url):
    validate_request(request)
    observed=_utc(observed_at_utc)
    target=urlsplit(public_url)
    if (target.scheme!="https" or target.hostname not in _ALLOWED
            or target.username or target.password or target.fragment or target.port not in (None,443)):
        raise ValueError("invalid African Union provenance")
    try:
        raw=http_get(public_url)
    except (OSError,TimeoutError):
        return [{
            "schema_version":"kgm.source.observation.v1",
            "request_id":request["request_id"],"source_id":SOURCE_ID,
            "observation_id":"au-transport","status":"UNAVAILABLE",
            "observed_at_utc":observed_at_utc,
            "published_at_utc":None,"available_at_utc":None,
            "public_url":None,"summary":None,
            "error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP,
        }]
    published,title,body=_parse(raw,public_url)
    if not (_utc(request["period_start_utc"])<=_utc(published)<=
            _utc(request.get("as_of_utc",request["period_end_utc"]))):
        return []
    oid="au-"+hashlib.sha256(public_url.encode()).hexdigest()[:24]
    if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
        return [{
            "schema_version":"kgm.source.observation.v1",
            "request_id":request["request_id"],"source_id":SOURCE_ID,
            "observation_id":oid,"status":"INVALID",
            "observed_at_utc":observed_at_utc,"published_at_utc":None,
            "available_at_utc":None,"public_url":None,"summary":None,
            "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","origin_group":None,
        }]
    return [{
        "schema_version":"kgm.source.observation.v1",
        "request_id":request["request_id"],"source_id":SOURCE_ID,
        "observation_id":oid,"status":"SUCCESS",
        "observed_at_utc":observed_at_utc,
        "published_at_utc":published, # Day anchor only, never exact clock time.
        "available_at_utc":observed_at_utc,
        "public_url":public_url,"summary":(title+": "+body[body.find(title)+len(title):].strip())[:1000],
        "error_code":None,"origin_group":ORIGIN_GROUP,
    }]
