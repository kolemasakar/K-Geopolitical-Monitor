from dataclasses import dataclass
from datetime import datetime


@dataclass
class Source:
    source_id: str
    name: str
    reliability_level: int | None = None


@dataclass
class RawItem:
    item_id: str
    source_id: str
    collected_at: datetime


@dataclass
class Event:
    event_id: str
    title: str
    status: str = "DETECTED"
