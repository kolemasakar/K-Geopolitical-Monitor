import sqlite3
from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.advanced_graph import (
    ACTIVE,
    CONTEXT,
    SUPPORTS,
    GraphEdge,
    GraphEdgeEvidence,
    GraphNode,
    SQLiteAdvancedGraphRepository,
    graph_edge_id,
    graph_node_id,
    project_m4_knowledge_graph,
)
from kgeopolitical_monitor.knowledge_graph import KnowledgeEdge, KnowledgeGraph, KnowledgeNode


NOW = datetime(2026, 8, 26, 13, 0, tzinfo=timezone.utc)


def test_durable_graph_nodes_edges_and_evidence_survive_restart(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)

    ukraine = GraphNode.from_canonical(
        "ACTOR",
        "ukraine",
        "ACTOR",
        "Ukraine",
        attributes={"actor_type": "COUNTRY"},
        created_at=NOW,
    )
    eu = GraphNode.from_canonical(
        "ACTOR",
        "eu",
        "ACTOR",
        "European Union",
        attributes={"actor_type": "ORGANIZATION"},
        created_at=NOW,
    )
    repo.save_node(ukraine)
    repo.save_node(eu)

    edge = GraphEdge.between(
        ukraine.node_id,
        eu.node_id,
        "cooperation",
        "POLITICAL",
        0.8,
        "Persisted M11 relationship baseline.",
        observed_at=NOW,
        valid_from=NOW,
    )
    repo.save_edge(edge)
    repo.add_edge_evidence(
        GraphEdgeEvidence(edge.edge_id, "finding:f-1", SUPPORTS, NOW)
    )

    restarted = SQLiteAdvancedGraphRepository(db)
    loaded_ukraine = restarted.get_node_by_canonical("actor", "ukraine")
    loaded_edge = restarted.get_edge(edge.edge_id)
    evidence = restarted.list_edge_evidence(edge.edge_id)

    assert loaded_ukraine is not None
    assert loaded_ukraine.node_id == ukraine.node_id
    assert loaded_ukraine.attributes == {"actor_type": "COUNTRY"}
    assert loaded_edge is not None
    assert loaded_edge.relation_type == "COOPERATION"
    assert loaded_edge.relation_class == "POLITICAL"
    assert loaded_edge.status == ACTIVE
    assert loaded_edge.valid_from == NOW
    assert [(item.evidence_ref, item.evidence_role) for item in evidence] == [
        ("finding:f-1", SUPPORTS)
    ]
    assert restarted.history_count(edge.edge_id) == 1


def test_graph_identity_and_repeated_projection_are_idempotent(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    a = GraphNode.from_canonical("ACTOR", "a", "ACTOR", "Actor A", created_at=NOW)
    b = GraphNode.from_canonical("ACTOR", "b", "ACTOR", "Actor B", created_at=NOW)

    assert a.node_id == graph_node_id("actor", "a")
    assert b.node_id == graph_node_id("ACTOR", "b")
    repo.save_node(a)
    repo.save_node(b)
    repo.save_node(a)

    edge = GraphEdge.between(
        a.node_id,
        b.node_id,
        "supports",
        "POLITICAL",
        0.7,
        "Idempotent relationship.",
        observed_at=NOW,
    )
    assert edge.edge_id == graph_edge_id(a.node_id, b.node_id, "SUPPORTS")
    repo.save_edge(edge)
    repo.save_edge(edge)

    evidence = GraphEdgeEvidence(edge.edge_id, "raw_item:r-1", SUPPORTS, NOW)
    repo.add_edge_evidence(evidence)
    repo.add_edge_evidence(evidence)

    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM graph_edge_evidence").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM graph_edge_history").fetchone()[0] == 1


def test_edge_observation_window_merges_deterministically(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    a = GraphNode.from_canonical("ACTOR", "a", "ACTOR", "Actor A", created_at=NOW)
    b = GraphNode.from_canonical("ACTOR", "b", "ACTOR", "Actor B", created_at=NOW)
    repo.save_node(a)
    repo.save_node(b)

    later = NOW + timedelta(hours=2)
    first = GraphEdge.between(
        a.node_id,
        b.node_id,
        "influences",
        "INFLUENCE",
        0.6,
        "First observation.",
        observed_at=later,
    )
    earlier = GraphEdge.between(
        a.node_id,
        b.node_id,
        "influences",
        "INFLUENCE",
        0.65,
        "Earlier evidence arrived later.",
        observed_at=NOW,
        updated_at=later + timedelta(minutes=1),
    )
    repo.save_edge(first)
    repo.save_edge(earlier)

    loaded = repo.get_edge(first.edge_id)
    assert loaded is not None
    assert loaded.first_observed_at == NOW
    assert loaded.last_observed_at == later
    assert loaded.confidence == 0.65
    assert loaded.explanation == "Earlier evidence arrived later."
    assert repo.history_count(first.edge_id) == 1


def test_validated_m4_graph_projects_without_changing_legacy_interface(tmp_path):
    legacy = KnowledgeGraph()
    legacy.add_node(KnowledgeNode("ukraine", "country", {"region": "Europe"}))
    legacy.add_node(KnowledgeNode("eu", "organization", {"region": "Europe"}))
    legacy.add_edge(KnowledgeEdge("ukraine", "eu", "cooperation", 0.8))

    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    first = project_m4_knowledge_graph(legacy, repo, observed_at=NOW)
    second = project_m4_knowledge_graph(legacy, repo, observed_at=NOW)

    assert first == (2, 1)
    assert second == (2, 1)
    assert set(legacy.nodes) == {"ukraine", "eu"}
    assert len(legacy.edges) == 1

    edges = repo.list_edges()
    assert len(edges) == 1
    assert edges[0].relation_type == "COOPERATION"
    assert edges[0].confidence == 0.8
    assert [(item.evidence_role, item.evidence_ref) for item in repo.list_edge_evidence(edges[0].edge_id)] == [
        (CONTEXT, "compat:m4:ukraine:eu:cooperation")
    ]


def test_graph_contract_rejects_non_deterministic_identity_and_invalid_confidence():
    try:
        GraphNode(
            node_id="wrong",
            node_kind="ACTOR",
            canonical_ref_type="ACTOR",
            canonical_ref_id="a",
            label="Actor A",
            created_at=NOW,
            updated_at=NOW,
        )
    except ValueError as exc:
        assert "deterministic" in str(exc)
    else:
        raise AssertionError("non-deterministic node identity must fail")

    a_id = graph_node_id("ACTOR", "a")
    b_id = graph_node_id("ACTOR", "b")
    try:
        GraphEdge.between(
            a_id,
            b_id,
            "supports",
            "POLITICAL",
            1.1,
            "Invalid confidence.",
            observed_at=NOW,
        )
    except ValueError as exc:
        assert "confidence" in str(exc)
    else:
        raise AssertionError("invalid graph confidence must fail")
