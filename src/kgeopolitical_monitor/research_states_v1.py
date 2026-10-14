"""Canonical durable research lifecycle state constants."""
TRANSITIONS = {
    "RECEIVED": {"ACCEPTED", "FAILED", "EXPIRED"},
    "ACCEPTED": {"PROCESSING", "FAILED", "EXPIRED"},
    "PROCESSING": {"COMPLETE", "PARTIAL", "FAILED", "EXPIRED"},
    "COMPLETE": set(), "PARTIAL": set(), "FAILED": set(), "EXPIRED": set(),
}
