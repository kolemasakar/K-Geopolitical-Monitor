"""Source discovery baseline.

Detects and registers potential new information sources.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class DiscoveredSource:
    name: str
    source_type: str
    region: str
    status: str = "candidate"


class SourceDiscovery:
    def discover(self, candidates: List[DiscoveredSource]) -> List[DiscoveredSource]:
        return candidates
