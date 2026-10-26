"""Privacy-safe, bounded source failure taxonomy for on-demand probe results.

Never emit raw exception strings, URLs, source content, tokens or redirects.
"""
from __future__ import annotations

import re


def classify_attempt(*, status: str, item_count: int, error: str | None) -> dict[str, object]:
    if status == "SUCCESS":
        return {
            "diagnostic": "MATCHED_ITEMS" if item_count > 0 else "ZERO_MATCHES_OR_EMPTY_FEED",
            "http_status": None,
            "retry_guidance": "NONE",
        }
    raw = (error or "").strip().lower()
    match = re.fullmatch(r"source_http_status_(\d{3})", raw)
    if match:
        code = int(match.group(1))
        retry = "MANUAL_BACKOFF_ONLY" if code in (408, 429, 500, 502, 503, 504) else "REVIEW_ENDPOINT"
        return {"diagnostic": "HTTP_RESPONSE_FAILURE", "http_status": code,
                "retry_guidance": retry}
    network_kinds = {
        "source_network_timeout": "NETWORK_TIMEOUT",
        "source_network_dns_failure": "NETWORK_DNS_FAILURE",
        "source_network_tls_failure": "NETWORK_TLS_FAILURE",
        "source_network_connect_failure": "NETWORK_CONNECT_FAILURE",
    }
    if raw in network_kinds:
        return {"diagnostic": network_kinds[raw], "http_status": None,
                "retry_guidance": "MANUAL_BACKOFF_ONLY" if raw.endswith("timeout")
                else "MANUAL_INVESTIGATION"}
    if "source network failure" in raw or "source_network_failure" in raw:
        return {"diagnostic": "NETWORK_FAILURE", "http_status": None,
                "retry_guidance": "MANUAL_BACKOFF_ONLY"}
    if "source redirect refused" in raw:
        return {"diagnostic": "REDIRECT_REFUSED", "http_status": None,
                "retry_guidance": "REVIEW_ENDPOINT"}
    if "source response exceeds configured bound" in raw:
        return {"diagnostic": "SIZE_LIMIT_EXCEEDED", "http_status": None,
                "retry_guidance": "REVIEW_LIMIT"}
    if "gdelt response" in raw or "gdelt article list" in raw or "articles list" in raw:
        return {"diagnostic": "GDELT_PAYLOAD_SCHEMA", "http_status": None,
                "retry_guidance": "REVIEW_PARSER"}
    if "gdacs rss" in raw or "consilium rss" in raw or "not valid xml" in raw:
        return {"diagnostic": "RSS_PAYLOAD_SCHEMA", "http_status": None,
                "retry_guidance": "REVIEW_PARSER"}
    return {"diagnostic": "UNKNOWN_FAILURE", "http_status": None,
            "retry_guidance": "MANUAL_INVESTIGATION"}
