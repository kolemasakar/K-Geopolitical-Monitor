"""Canonical public/free NATO news owner-pilot source adapter.

Uses NATO's public listing JSON endpoint for official news. Transport is
injected; no credentials, paid fallback or write-back.
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlencode, urljoin, urlsplit
from .research_request_v1 import validate_request, _utc

SOURCE_ID="nato-news"
ORIGIN_GROUP="nato"
BASE="https://www.nato.int"
SEARCH_ENDPOINT=(BASE+
 "/content/nato/en/news-and-events/articles/news/jcr:content/root/container/"
 "general_search.search.json")
ALLOWED_TAGS={
 "deterrence-and-defence":"nato:theme/deterrence-and-defence",
 "operations-and-missions":"nato:theme/operations-and-missions",
 "partnerships-and-cooperation":"nato:theme/partnerships-and-cooperation",
}

def build_query(request, *, theme="deterrence-and-defence", search_text=""):
    validate_request(request)
    if theme not in ALLOWED_TAGS:
        raise ValueError("invalid NATO theme")
    if not isinstance(search_text,str) or len(search_text)>256:
        raise ValueError("invalid NATO search text")
    start=_utc(request["period_start_utc"]).strftime("%Y-%m-%dT00:00:00.000Z")
    end=_utc(request.get("as_of_utc",request["period_end_utc"])).strftime("%Y-%m-%dT23:59:59.999Z")
    params={"searchText":search_text,"searchType":"wcm","sortBy":"dateDesc",
            "pageSize":min(request["max_results"],50),"page":1,"urlTags":"",
            "selectedTagsFilter":ALLOWED_TAGS[theme],"languages":"en",
            "startDate":start,"endDate":end}
    return SEARCH_ENDPOINT+"?"+urlencode(params)

def _page_day(value):
    if not isinstance(value,str):
        raise ValueError("invalid NATO page date")
    try:
        return datetime.strptime(value,"%d %B %Y").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid NATO page date") from exc

def fetch(request, *, observed_at_utc, http_get,
          theme="deterrence-and-defence", search_text=""):
    validate_request(request); observed=_utc(observed_at_utc)
    try:
        payload=http_get(build_query(request,theme=theme,search_text=search_text))
    except (TimeoutError,OSError):
        return [{"schema_version":"kgm.source.observation.v1",
          "request_id":request["request_id"],"source_id":SOURCE_ID,
          "observation_id":"nato-transport","status":"UNAVAILABLE",
          "observed_at_utc":observed_at_utc,"published_at_utc":None,
          "available_at_utc":None,"public_url":None,"summary":None,
          "error_code":"TRANSPORT_UNAVAILABLE","origin_group":ORIGIN_GROUP}]
    pages=payload.get("pages") if isinstance(payload,dict) else None
    if not isinstance(pages,list) or len(pages)>50:
        raise ValueError("invalid NATO response")
    start=_utc(request["period_start_utc"]).date()
    end=_utc(request.get("as_of_utc",request["period_end_utc"])).date()
    out=[]
    for page in pages[:min(request["max_results"],50)]:
        if not isinstance(page,dict):
            raise ValueError("invalid NATO page")
        title=page.get("title"); description=page.get("description")
        link=page.get("link"); page_date=page.get("pageDate")
        if not isinstance(title,str) or not title.strip() or not isinstance(link,str):
            raise ValueError("invalid NATO item")
        day=_page_day(page_date)
        if day.date()<start or day.date()>end:
            continue
        public=urljoin(BASE,link)
        parsed=urlsplit(public)
        if parsed.scheme!="https" or parsed.hostname not in {"www.nato.int","nato.int"}:
            raise ValueError("invalid NATO provenance")
        oid="nato-"+hashlib.sha256(public.encode("utf-8")).hexdigest()[:24]
        if request["mode"]=="HISTORICAL_AS_OF" and observed>_utc(request["as_of_utc"]):
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"INVALID",
              "observed_at_utc":observed_at_utc,"published_at_utc":None,
              "available_at_utc":None,"public_url":None,"summary":None,
              "error_code":"HISTORICAL_AVAILABILITY_UNPROVEN","origin_group":None})
        else:
            summary=(" ".join(description.split()) if isinstance(description,str) and description.strip()
                     else " ".join(title.split()))
            # NATO listing exposes only the publication day, not a trustworthy
            # exact publication time. First KGM observation is the conservative
            # publication/availability boundary.
            out.append({"schema_version":"kgm.source.observation.v1",
              "request_id":request["request_id"],"source_id":SOURCE_ID,
              "observation_id":oid,"status":"SUCCESS",
              "observed_at_utc":observed_at_utc,"published_at_utc":observed_at_utc,
              "available_at_utc":observed_at_utc,"public_url":public,
              "summary":summary[:1000],"error_code":None,
              "origin_group":ORIGIN_GROUP})
    return out
