"""Evidence and verification domain models."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Evidence:
    id: str
    source_id: str
    claim: str
    reliability: str
    created_at: datetime

@dataclass
class Claim:
    id: str
    event_id: str
    text: str
    status: str = "UNVERIFIED"
