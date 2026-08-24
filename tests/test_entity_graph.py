from kgeopolitical_monitor.entity_graph import Entity, EntityGraph, EntityRelation


def test_entity_graph_baseline():
    graph = EntityGraph()
    graph.add_entity(Entity('1', 'Ukraine', 'country'))
    graph.add_entity(Entity('2', 'EU', 'organization'))
    graph.add_relation(EntityRelation('1', '2', 'cooperation', 0.8))

    assert len(graph.entities) == 2
    assert len(graph.relations) == 1
