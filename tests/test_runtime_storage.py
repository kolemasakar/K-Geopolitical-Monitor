from pathlib import Path

import pytest

from kgeopolitical_monitor.runtime_storage import RuntimeStoragePolicy


def test_runtime_storage_defaults_to_project_local_data_directory(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    policy = RuntimeStoragePolicy(project_root)

    resolved = policy.resolve_database()

    assert resolved == (project_root / "data" / "kgeopolitical_monitor.db").resolve()


def test_runtime_storage_accepts_explicit_project_local_database(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    policy = RuntimeStoragePolicy(project_root)

    resolved = policy.resolve_database(Path("data") / "m5-test.db")

    assert resolved == (project_root / "data" / "m5-test.db").resolve()


def test_runtime_storage_rejects_paths_outside_project_data_directory(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    policy = RuntimeStoragePolicy(project_root)

    with pytest.raises(ValueError, match="project-local data directory"):
        policy.resolve_database("../other-project/runtime.db")

    with pytest.raises(ValueError, match="project-local data directory"):
        policy.resolve_database(tmp_path / "external-runtime.db")
