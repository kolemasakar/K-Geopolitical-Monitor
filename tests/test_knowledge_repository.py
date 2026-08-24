from src.kgeopolitical_monitor.knowledge_repository import KnowledgeRepository, KnowledgeSnapshot


def test_repository_snapshot():
    repo = KnowledgeRepository()
    repo.save(KnowledgeSnapshot(version=1))
    assert repo.latest().version == 1
