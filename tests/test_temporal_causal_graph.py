from datetime import datetime, timedelta, timezone

from kgeopolitical_monitor.advanced_graph import (
    ACTIVE,
    INVALIDATED,
    UPDATED,
    GraphEdge,
    GraphNode,
    SQLiteAdvancedGraphRepository,
)
from kgeopolitical_monitor.relationship_lifecycle import RelationshipLifecycleManager
from kgeopolitical_monitor.temporal_causal_graph import TemporalCausalGraph


T0 = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)


def _node(repo, ref_id):
    node = GraphNode.from_canonical(
        "ACTOR",
        ref_id,
        "ACTOR",
        ref_id.upper(),
        created_at=T0,
    )
    repo.save_node(node)
    return node


def _edge(repo, source, target, relation_type, relation_class, *, confidence=0.6, valid_from=None, valid_to=None):
    edge = GraphEdge.between(
        source.node_id,
        target.node_id,
        relation_type,
        relation_class,
        confidence,
        f"{relation_type} baseline.",
        observed_at=T0,
        valid_from=valid_from,
        valid_to=valid_to,
    )
    RelationshipLifecycleManager(repo).save_relationship(edge)
    return edge


def test_snapshot_reconstructs_material_relationship_state_over_time(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    manager = RelationshipLifecycleManager(repo)
    temporal = TemporalCausalGraph(repo)
    a = _node(repo, "a")
    b = _node(repo, "b")
    edge = _edge(repo, a, b, "supports", "POLITICAL", confidence=0.5)

    t1 = T0 + timedelta(hours=1)
    t2 = T0 + timedelta(hours=2)
    manager.transition(
        edge.edge_id,
        status=UPDATED,
        observed_at=t1,
        confidence=0.75,
        explanation="Updated confidence.",
    )
    manager.transition(
        edge.edge_id,
        status=INVALIDATED,
        observed_at=t2,
        explanation="Relationship invalidated.",
    )

    before_update = temporal.state_at(edge.edge_id, T0 + timedelta(minutes=30))
    after_update = temporal.state_at(edge.edge_id, t1 + timedelta(minutes=1))
    after_invalidation = temporal.state_at(edge.edge_id, t2 + timedelta(minutes=1))

    assert before_update is not None
    assert before_update.status == ACTIVE
    assert before_update.confidence == 0.5
    assert after_update is not None
    assert after_update.status == UPDATED
    assert after_update.confidence == 0.75
    assert after_invalidation is not None
    assert after_invalidation.status == INVALIDATED


def test_current_snapshot_excludes_invalidated_and_resolved_relationships(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    manager = RelationshipLifecycleManager(repo)
    temporal = TemporalCausalGraph(repo)
    a = _node(repo, "a")
    b = _node(repo, "b")
    c = _node(repo, "c")
    active_edge = _edge(repo, a, b, "supports", "POLITICAL")
    invalidated_edge = _edge(repo, a, c, "opposes", "POLITICAL")

    manager.transition(
        invalidated_edge.edge_id,
        status=INVALIDATED,
        observed_at=T0 + timedelta(hours=1),
        explanation="Invalidated.",
    )

    current = temporal.current_edges(as_of=T0 + timedelta(hours=2))
    assert [item.edge_id for item in current] == [active_edge.edge_id]

    historical = temporal.snapshot_at(
        T0 + timedelta(hours=2),
        include_inactive=True,
    )
    assert {item.edge_id for item in historical} == {
        active_edge.edge_id,
        invalidated_edge.edge_id,
    }


def test_snapshot_respects_validity_intervals(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    temporal = TemporalCausalGraph(repo)
    a = _node(repo, "a")
    b = _node(repo, "b")
    valid_from = T0 + timedelta(hours=1)
    valid_to = T0 + timedelta(hours=3)
    edge = _edge(
        repo,
        a,
        b,
        "agreement",
        "POLITICAL",
        valid_from=valid_from,
        valid_to=valid_to,
    )

    assert temporal.snapshot_at(T0 + timedelta(minutes=30)) == ()
    middle = temporal.snapshot_at(T0 + timedelta(hours=2))
    assert [item.edge_id for item in middle] == [edge.edge_id]
    assert temporal.snapshot_at(T0 + timedelta(hours=4)) == ()

    inactive = temporal.snapshot_at(
        T0 + timedelta(hours=4),
        include_inactive=True,
    )
    assert [item.edge_id for item in inactive] == [edge.edge_id]
    assert inactive[0].is_effective_at(T0 + timedelta(hours=4)) is False


def test_causal_traversal_is_bounded_deterministic_and_cycle_safe(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    temporal = TemporalCausalGraph(repo)
    a = _node(repo, "a")
    b = _node(repo, "b")
    c = _node(repo, "c")
    d = _node(repo, "d")

    ab = _edge(repo, a, b, "causes", "CAUSAL")
    bc = _edge(repo, b, c, "influences", "INFLUENCE")
    _edge(repo, c, a, "feeds_back", "CAUSAL")
    bd = _edge(repo, b, d, "contributes_to", "CAUSAL")
    _edge(repo, c, d, "aligned_with", "POLITICAL")

    paths = temporal.causal_paths(
        a.node_id,
        max_depth=2,
        as_of=T0 + timedelta(minutes=1),
    )

    assert [(path.node_ids, path.edge_ids) for path in paths] == [
        ((a.node_id, b.node_id), (ab.edge_id,)),
        ((a.node_id, b.node_id, c.node_id), (ab.edge_id, bc.edge_id)),
        ((a.node_id, b.node_id, d.node_id), (ab.edge_id, bd.edge_id)),
    ]
    assert all(a.node_id not in path.node_ids[1:] for path in paths)
    assert all(path.depth <= 2 for path in paths)


def test_causal_traversal_excludes_invalidated_edges_and_validates_bounds(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    manager = RelationshipLifecycleManager(repo)
    temporal = TemporalCausalGraph(repo)
    a = _node(repo, "a")
    b = _node(repo, "b")
    edge = _edge(repo, a, b, "causes", "CAUSAL")

    manager.transition(
        edge.edge_id,
        status=INVALIDATED,
        observed_at=T0 + timedelta(hours=1),
        explanation="Causal hypothesis invalidated.",
    )

    assert temporal.causal_paths(
        a.node_id,
        max_depth=3,
        as_of=T0 + timedelta(hours=2),
    ) == ()

    try:
        temporal.causal_paths(a.node_id, max_depth=0, as_of=T0)
    except ValueError as exc:
        assert "max_depth" in str(exc)
    else:
        raise AssertionError("non-positive max_depth must fail")
