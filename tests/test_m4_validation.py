from datetime import datetime, timedelta

from src.kgeopolitical_monitor.causal_intelligence import CausalEngine, CausalLink
from src.kgeopolitical_monitor.intelligence_query import IntelligenceQuery
from src.kgeopolitical_monitor.knowledge_graph import KnowledgeEdge, KnowledgeGraph, KnowledgeNode
from src.kgeopolitical_monitor.knowledge_repository import KnowledgeRepository, KnowledgeSnapshot
from src.kgeopolitical_monitor.relationship_engine import RelationshipEngine, RelationshipSignal
from src.kgeopolitical_monitor.temporal_graph import TemporalGraphAnalyzer, TemporalRelation


def test_m4_graph_and_relationship_contract():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode("ukraine", "country", {"region": "Europe"}))
    graph.add_node(KnowledgeNode("eu", "organization", {"region": "Europe"}))
    graph.add_edge(KnowledgeEdge("ukraine", "eu", "cooperation", 0.8))

    assert set(graph.nodes) == {"ukraine", "eu"}
    assert len(graph.edges) == 1

    engine = RelationshipEngine()
    assert engine.score(RelationshipSignal("ukraine", "eu", "cooperation", 0.8)) == 0.8
    assert engine.score(RelationshipSignal("a", "b", "test", 1.5)) == 1.0
    assert engine.score(RelationshipSignal("a", "b", "test", -0.5)) == 0.0


def test_m4_graph_persistence_contract():
    repository = KnowledgeRepository()
    snapshot_1 = KnowledgeSnapshot(version=1, nodes={"a": {"type": "country"}}, edges=[])
    snapshot_2 = KnowledgeSnapshot(
        version=2,
        nodes={"a": {"type": "country"}, "b": {"type": "organization"}},
        edges=[{"source": "a", "target": "b", "relation": "supports"}],
    )

    assert repository.save(snapshot_1) == 1
    assert repository.save(snapshot_2) == 2
    assert repository.latest() == snapshot_2


def test_m4_causal_and_temporal_contract():
    causal = CausalEngine()
    causal.add_link(CausalLink("event-a", "event-b", 0.9))
    causal.add_link(CausalLink("event-b", "event-c", 0.7))

    query = IntelligenceQuery(causal_engine=causal)
    chain = query.trace_causal_chain("event-a")
    assert [(link.cause, link.effect) for link in chain] == [
        ("event-a", "event-b"),
        ("event-b", "event-c"),
    ]

    temporal = TemporalGraphAnalyzer()
    start = datetime(2026, 8, 24, 0, 0, 0)
    temporal.add_relation(TemporalRelation("a", "b", "influence", start, 0.4))
    temporal.add_relation(
        TemporalRelation("a", "b", "influence", start + timedelta(hours=1), 0.75)
    )

    assert len(temporal.history("a")) == 2
    assert abs(temporal.influence_change("a") - 0.35) < 1e-12


def test_m4_query_and_explainability_contract():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode("ukraine", "country", {"region": "Europe"}))
    graph.add_node(KnowledgeNode("eu", "organization", {"region": "Europe"}))
    graph.add_edge(KnowledgeEdge("ukraine", "eu", "cooperation", 0.8))

    query = IntelligenceQuery(graph=graph)

    entity_result = query.query("ukraine")
    assert any(getattr(item, "node_id", None) == "ukraine" for item in entity_result.findings)
    assert any(getattr(item, "relation", None) == "cooperation" for item in entity_result.findings)
    assert entity_result.confidence == 1.0

    relation_result = query.query("cooperation")
    assert len(relation_result.findings) == 1
    assert relation_result.findings[0].relation == "cooperation"
    assert relation_result.confidence == 0.8

    explanation = query.build_explanation("ukraine")
    assert explanation["query"] == "ukraine"
    assert explanation["confidence"] == 1.0
    assert {item["type"] for item in explanation["evidence"]} == {"node", "edge"}
