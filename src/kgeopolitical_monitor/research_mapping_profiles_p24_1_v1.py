"""Explicit owner-pilot mapping profiles for one documented UK-Germany event.

These are opt-in, source-bound profiles, not automatic extraction nor verified
truth. A match means text contains required phrases, NOT that the treaty claim
has been independently proven or that the source is trustworthy.
"""
from __future__ import annotations

from copy import deepcopy

EVENT = {
    "family": "POLITICAL",
    "event_date_utc": "2026-10-08T00:00:00Z",
    "action_key": "RATIFY",
    "actor_keys": ["germany-federal-government", "uk-government"],
    "target_keys": [],
    "subject_key": "kensington-treaty",
    "location_key": "berlin-germany",
}
CLAIM = {
    "claim_type": "STATUS",
    "value_keys": ["ratification-completed"],
    "unit_key": None,
}

# Source anchors directly inspected, 2026-10-13. Germany has only a date
# granularity; gov.uk published_at includes explicit timezone/clock time.
SOURCE_URLS = {
    "govuk-official": (
        "https://www.gov.uk/government/news/"
        "joint-uk-germany-statement-berlin-8-october-2026"
    ),
    "germany-federal-government": (
        "https://www.bundesregierung.de/breg-en/news/"
        "chancellor-merz-uk-pm-burnham-2456444"
    ),
}
REQUIRED_PHRASES = {
    "govuk-official": ("friedrich merz", "kensington treaty", "ratification"),
    "germany-federal-government": (
        "friedrich merz", "kensington treaty", "ratification",
    ),
}


def get_ratification_profile(source_id):
    """Return source-bound deep copy; unknown sources fail closed."""
    if source_id not in SOURCE_URLS:
        raise ValueError("unapproved ratification source profile")
    return {
        "source_id": source_id,
        "required_phrases": list(REQUIRED_PHRASES[source_id]),
        "event_descriptor": deepcopy(EVENT),
        "claim_descriptor": deepcopy(CLAIM),
    }
