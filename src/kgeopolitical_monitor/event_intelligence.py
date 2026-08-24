"""Event intelligence baseline layer.

Provides domain structures for verified events, updates and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Event:
    event_id: str
    title: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)


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
