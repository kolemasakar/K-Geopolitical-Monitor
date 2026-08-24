from kgeopolitical_monitor.repositories_sqlite import (
    SQLiteSourceRepository,
    SQLiteRawItemRepository,
    SQLiteEventRepository,
)


def test_repository_classes_exist():
    assert SQLiteSourceRepository is not None
    assert SQLiteRawItemRepository is not None
    assert SQLiteEventRepository is not None
