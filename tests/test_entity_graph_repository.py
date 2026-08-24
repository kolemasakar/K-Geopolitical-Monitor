from kgeopolitical_monitor.entity_graph_repository import EntityGraphRepository, EntityRelation


def test_relation_storage():
    repo = EntityGraphRepository()
    repo.add_relation(EntityRelation('A', 'B', 'ACTOR_OF', 0.8))
    assert len(repo.list_relations()) == 1
