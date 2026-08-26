import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from kgeopolitical_monitor.advanced_graph import (
    ACTIVE,
    CONTEXT,
    CONTRADICTS,
    INVALIDATED,
    RESOLVED,
    SUPPORTS,
    UPDATED,
    GraphEdge,
    GraphEdgeEvidence,
    GraphNode,
    SQLiteAdvancedGraphRepository,
)
from kgeopolitical_monitor.relationship_lifecycle import RelationshipLifecycleManager


NOW = datetime(2026, 8, 26, 14, 0, tzinfo=timezone.utc)


def _relationship(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    manager = RelationshipLifecycleManager(repo)
    a = GraphNode.from_canonical("ACTOR", "a", "ACTOR", "Actor A", created_at=NOW)
    b = GraphNode.from_canonical("ACTOR", "b", "ACTOR", "Actor B", created_at=NOW)
    repo.save_node(a)
    repo.save_node(b)
    edge = GraphEdge.between(
        a.node_id,
        b.node_id,
        "supports",
        "POLITICAL",
        0.6,
        "Initial observed relationship.",
        observed_at=NOW,
        valid_from=NOW,
    )
    return db, repo, manager, edge


def test_relationship_evidence_accumulates_without_duplicate_edge_or_history(tmp_path):
    db, repo, manager, edge = _relationship(tmp_path)
    manager.save_relationship(
        edge,
        evidence=(GraphEdgeEvidence(edge.edge_id, "finding:f-1", SUPPORTS, NOW),),
    )

    later = NOW + timedelta(hours=1)
    updated = GraphEdge(
        edge_id=edge.edge_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        relation_type=edge.relation_type,
        relation_class=edge.relation_class,
        confidence=0.75,
        status=UPDATED,
        first_observed_at=NOW,
        last_observed_at=later,
        explanation="Updated with additional evidence.",
        valid_from=NOW,
        created_at=NOW,
        updated_at=later,
    )
    evidence = (
        GraphEdgeEvidence(edge.edge_id, "finding:f-2", SUPPORTS, later),
        GraphEdgeEvidence(edge.edge_id, "claim:c-1", CONTRADICTS, later),
        GraphEdgeEvidence(edge.edge_id, "source:s-1", CONTEXT, later),
    )
    manager.save_relationship(updated, evidence=evidence)
    manager.save_relationship(updated, evidence=evidence)

    loaded = repo.get_edge(edge.edge_id)
    assert loaded is not None
    assert loaded.status == UPDATED
    assert loaded.confidence == 0.75
    assert loaded.explanation == "Updated with additional evidence."

    stored_evidence = repo.list_edge_evidence(edge.edge_id)
    assert {(item.evidence_ref, item.evidence_role) for item in stored_evidence} == {
        ("finding:f-1", SUPPORTS),
        ("finding:f-2", SUPPORTS),
        ("claim:c-1", CONTRADICTS),
        ("source:s-1", CONTEXT),
    }
    history = manager.history(edge.edge_id)
    assert [item.event_type for item in history] == ["CREATED", "STATUS_UPDATED"]
    assert history[-1].payload["previous"]["confidence"] == 0.6
    assert history[-1].payload["current"]["confidence"] == 0.75

    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM graph_edge_history").fetchone()[0] == 2


def test_relationship_invalidation_and_resolution_preserve_material_history(tmp_path):
    _, repo, manager, edge = _relationship(tmp_path)
    manager.save_relationship(edge)

    invalidated_at = NOW + timedelta(hours=2)
    invalidated = manager.transition(
        edge.edge_id,
        status=INVALIDATED,
        observed_at=invalidated_at,
        confidence=0.2,
        explanation="Contradictory evidence invalidated the current relationship.",
        valid_to=invalidated_at,
        evidence=(
            GraphEdgeEvidence(edge.edge_id, "claim:contradiction", CONTRADICTS, invalidated_at),
        ),
    )
    assert invalidated.status == INVALIDATED
    assert invalidated.valid_to == invalidated_at

    resolved_at = NOW + timedelta(hours=3)
    resolved = manager.transition(
        edge.edge_id,
        status=RESOLVED,
        observed_at=resolved_at,
        explanation="Relationship lifecycle closed while history remains available.",
    )
    assert resolved.status == RESOLVED
    assert resolved.valid_to == invalidated_at

    history = manager.history(edge.edge_id)
    assert [item.event_type for item in history] == [
        "CREATED",
        "STATUS_INVALIDATED",
        "STATUS_RESOLVED",
    ]
    assert history[1].status == INVALIDATED
    assert history[2].status == RESOLVED


def test_relationship_confidence_cannot_escape_graph_bounds(tmp_path):
    _, _, manager, edge = _relationship(tmp_path)
    manager.save_relationship(edge)

    with pytest.raises(ValueError, match="confidence"):
        manager.transition(
            edge.edge_id,
            status=ACTIVE,
            observed_at=NOW + timedelta(minutes=5),
            confidence=1.2,
        )

    assert len(manager.history(edge.edge_id)) == 1


def test_graph_relationship_changes_do_not_mutate_m8_claim_confidence_or_origin_count(tmp_path):
    db, _, manager, edge = _relationship(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute(
            """
            INSERT INTO live_analysis_runs(
                analysis_run_id, collection_id, watch_id, status,
                claim_count, finding_count, created_at
            ) VALUES ('analysis-1', 'collection-1', 'watch-1', 'COMPLETED', 1, 0, ?)
            """,
            (NOW.isoformat(),),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title, verification_status,
                confidence, importance, independent_origin_count,
                source_class_count, origins_json
            ) VALUES ('claim-1', 'analysis-1', 'key-1', 'Claim', 'PARTLY_VERIFIED',
                      0.42, 0.5, 2, 2, '[]')
            """
        )

    manager.save_relationship(
        edge,
        evidence=(GraphEdgeEvidence(edge.edge_id, "claim:claim-1", SUPPORTS, NOW),),
    )
    manager.transition(
        edge.edge_id,
        status=UPDATED,
        observed_at=NOW + timedelta(hours=1),
        confidence=0.95,
        explanation="Graph confidence changed independently of upstream claim confidence.",
    )

    with sqlite3.connect(db) as connection:
        upstream = connection.execute(
            "SELECT confidence, independent_origin_count FROM live_analysis_claims WHERE claim_id = 'claim-1'"
        ).fetchone()
    assert upstream == (0.42, 2)
