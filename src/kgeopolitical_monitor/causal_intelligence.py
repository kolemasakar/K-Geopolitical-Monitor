"""Causal relationship baseline for knowledge graph."""

from dataclasses import dataclass


@dataclass
class CausalLink:
    cause: str
    effect: str
    confidence: float


class CausalEngine:
    def __init__(self):
        self.links = []

    def add_link(self, link: CausalLink):
        self.links.append(link)

    def get_effects(self, cause: str):
        return [x for x in self.links if x.cause == cause]
