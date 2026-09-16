"""Event intelligence baseline layer.

Provides domain structures for verified events, updates and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Event:
    event_id: str
    title: str
    confidence: float
    created_at: datetime = field(default_factory=_utc_now)


@dataclass
class EventUpdate:
    event_id: str
    update_text: str
    confidence: float


@dataclass
class Relationship:
    source_id: str
    target_id: str
    relation_type: str
