"""Timeline processing baseline."""

from dataclasses import dataclass
from typing import List


@dataclass
class TimelinePoint:
    event_id: str
    timestamp: str


class TimelineEngine:
    def build(self, events: List[TimelinePoint]) -> List[TimelinePoint]:
        return sorted(events, key=lambda item: item.timestamp)
