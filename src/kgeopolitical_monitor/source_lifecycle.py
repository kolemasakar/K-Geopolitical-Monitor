"""Source lifecycle management baseline."""

from enum import Enum


class SourceState(str, Enum):
    DISCOVERED = "DISCOVERED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    ARCHIVED = "ARCHIVED"
    RESTORED = "RESTORED"


class SourceLifecycleManager:
    def transition(self, current: SourceState, event: str) -> SourceState:
        transitions = {
            (SourceState.DISCOVERED, "activate"): SourceState.ACTIVE,
            (SourceState.ACTIVE, "degrade"): SourceState.DEGRADED,
            (SourceState.DEGRADED, "archive"): SourceState.ARCHIVED,
            (SourceState.ARCHIVED, "restore"): SourceState.RESTORED,
        }
        return transitions.get((current, event), current)
