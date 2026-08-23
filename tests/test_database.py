from kgeopolitical_monitor.database import initialize_database


def test_database_initialization(tmp_path):
    db = tmp_path / "test.db"
    initialize_database(str(db))
    assert db.exists()
