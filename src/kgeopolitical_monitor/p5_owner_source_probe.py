"""Owner-only P5.4 public-source reachability probe. Never writes raw content.

Executes three fixed allowlisted public HTTPS GETs with strict size/time/request
budgets and no redirects. No production DB, scheduler or consumer dispatch.
NOT an end-to-end geopolitical research/report engine.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from .on_demand_source_policy import RestrictedSourcePolicy, RestrictedSourceTransport


SOURCE_ENDPOINTS = (
    ("gdacs-rss", "https://www.gdacs.org/xml/rss.xml", "xml"),
    ("consilium-rss", "https://www.consilium.europa.eu/en/rss/pressreleases.ashx", "xml"),
    ("gdelt-doc2", "https://api.gdeltproject.org/api/v2/doc/doc", "json"),
)


def probe_sources(*, transport=None, term="earthquake"):
    if not isinstance(term, str) or not (1 <= len(term) <= 80) or any(ord(c) < 32 for c in term):
        raise ValueError("invalid bounded public probe term")
    if transport is None:
        transport = RestrictedSourceTransport(RestrictedSourcePolicy(
            max_requests=3, timeout_seconds=7, max_bytes_per_response=512_000
        ))
    checked = []
    for source_id, url, fmt in SOURCE_ENDPOINTS:
        query_url = url
        if source_id == "gdelt-doc2":
            query_url += "?" + urlencode({
                "query": term, "mode": "artlist", "format": "json",
                "maxrecords": "5", "timespan": "24h", "sort": "datedesc",
            })
        try:
            response = transport.get(query_url, headers={"Accept":
                "application/json" if fmt == "json" else "application/xml, text/xml"})
            if fmt == "xml":
                root = ET.fromstring(response.body)
                if root.tag not in ("rss", "{http://www.w3.org/2005/Atom}feed"):
                    raise ValueError("unrecognized feed root")
                if root.tag == "rss":
                    records = len(root.findall("./channel/item"))
                else:
                    records = len(root.findall("{http://www.w3.org/2005/Atom}entry"))
            else:
                payload = json.loads(response.body.decode("utf-8"))
                articles = payload.get("articles") if isinstance(payload, dict) else None
                if not isinstance(articles, list):
                    raise ValueError("GDELT article list unavailable")
                records = len(articles)
            checked.append({"source": source_id, "result": "PARSE_OK",
                            "item_count": records, "error_class": None})
        except Exception as exc:
            # No raw exception string, redirects, URLs or response body in logs.
            checked.append({"source": source_id, "result": "FAILED",
                            "item_count": None, "error_class": type(exc).__name__})
    return {
        "format": "KGM_P5_4_OWNER_PUBLIC_SOURCE_PROBE_V1",
        "mode": "ON_DEMAND_ONLY",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_results": checked,
        "success_count": sum(x["result"] == "PARSE_OK" for x in checked),
        "failure_count": sum(x["result"] == "FAILED" for x in checked),
        "provenance_validated": False,
        "primary_claims_verified": False,
        "raw_data_persisted": False,
        "report_sent": False,
    }


def main():
    result = probe_sources(term=os.environ.get("KGM_PROBE_TERM", "earthquake"))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
