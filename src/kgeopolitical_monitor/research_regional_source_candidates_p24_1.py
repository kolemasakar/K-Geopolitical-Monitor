"""P24.1 read-only candidate inventory, NOT an enabled data-source adapter.

Publisher attribution, verified transport, verified parsing and independent
claim corroboration are separate stages. None are granted by this catalog.
"""
from __future__ import annotations
from copy import deepcopy
from urllib.parse import urlsplit

_CANDIDATES = {
    "african-union-press": {
        "region": "AFRICA",
        "origin_group": "african-union",
        "entry_url": "https://www.au.int/en/happening/pressreleases",
        "publisher_type": "INTERGOVERNMENTAL",
        "languages_observed": ["en"],
        "transport": "HTTP_200_OBSERVED",
    },
    "asean-news": {
        "region": "ASIA",
        "origin_group": "asean-secretariat",
        "entry_url": "https://asean.org/category/news/",
        "publisher_type": "INTERGOVERNMENTAL",
        "languages_observed": ["en"],
        "transport": "REDIRECT_307_NOT_RESOLVED",
    },
    "gcc-secretariat-news": {
        "region": "MIDDLE_EAST",
        "origin_group": "gcc-secretariat",
        "entry_url": "https://gcc-sg.org/en/MediaCenter/News/Pages/default.aspx",
        "publisher_type": "INTERGOVERNMENTAL",
        "languages_observed": ["en"],
        "transport": "HTTP_200_OBSERVED",
    },
    "oas-press": {
        "region": "AMERICAS",
        "origin_group": "oas-general-secretariat",
        "entry_url": "https://www.oas.org/en/media_center/press_releases.asp",
        "publisher_type": "INTERGOVERNMENTAL",
        "languages_observed": ["en"],
        "transport": "HTTP_403_OBSERVED",
    },
}

def regional_source_candidates():
    """Return defensive copy of discovery-only records."""
    return deepcopy(_CANDIDATES)

def validated_candidate(source_id):
    """Restrict to known source identity; never imply a successful parse."""
    if source_id not in _CANDIDATES:
        raise ValueError("unapproved regional source candidate")
    item=deepcopy(_CANDIDATES[source_id])
    u=urlsplit(item["entry_url"])
    if u.scheme!="https" or not u.hostname or u.username or u.password or u.fragment:
        raise ValueError("invalid regional source candidate provenance")
    item["source_id"]=source_id
    item["adapter_enabled"]=False
    item["parsing_validated"]=False
    item["factual_verification_credit"]=False
    item["source_independence_credit"]=False
    return item
