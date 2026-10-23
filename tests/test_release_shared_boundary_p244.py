"""Isolated release/source boundaries must share one persistent runtime root.

No production services, networks or protected data are touched by these tests.
"""
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

from kgeopolitical_monitor.runtime_lease import RuntimeInstanceLease, default_runtime_lease_path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _make_release(tmp_path, name):
    release = tmp_path / "releases" / name / "source"
    release.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "src" / "kgeopolitical_monitor", release / "src" / "kgeopolitical_monitor")
    shutil.copytree(REPO_ROOT / "migrations", release / "migrations")
    return release


def _invoke(source, runtime_root, *, check=True):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "kgeopolitical_monitor.unattended_runner",
         "--project-root", str(runtime_root), "--once"],
        cwd=runtime_root, env=env, capture_output=True, text=True,
        timeout=40, check=check,
    )


def test_two_immutable_source_locations_reuse_one_database_and_lease(tmp_path):
    old_source = _make_release(tmp_path, "old")
    new_source = _make_release(tmp_path, "new")
    runtime_root = tmp_path / "persistent"
    runtime_root.mkdir()

    old_result = _invoke(old_source, runtime_root)
    assert '"execution_count": 0' in old_result.stdout
    database = (runtime_root / "data" / "kgeopolitical_monitor.db").resolve()
    lease = default_runtime_lease_path(runtime_root)
    assert database.is_file()
    assert lease.is_file()
    before = sqlite3.connect(database)
    try:
        before.execute("CREATE TABLE IF NOT EXISTS release_boundary_fixture (id INTEGER PRIMARY KEY, value TEXT)")
        before.execute("INSERT INTO release_boundary_fixture VALUES (1, 'forward-row')")
        before.commit()
    finally:
        before.close()

    new_result = _invoke(new_source, runtime_root)
    assert '"execution_count": 0' in new_result.stdout
    previous_again = _invoke(old_source, runtime_root)
    assert '"execution_count": 0' in previous_again.stdout
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT value FROM release_boundary_fixture WHERE id=1").fetchone() == ("forward-row",)
        assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert sorted(p.name for p in (runtime_root / "data").glob("*.db")) == ["kgeopolitical_monitor.db"]


def test_different_source_releases_cannot_bypass_canonical_lease(tmp_path):
    old_source = _make_release(tmp_path, "old")
    new_source = _make_release(tmp_path, "new")
    runtime_root = tmp_path / "persistent"
    runtime_root.mkdir()
    lease = default_runtime_lease_path(runtime_root)
    with RuntimeInstanceLease(lease):
        old = _invoke(old_source, runtime_root, check=False)
        new = _invoke(new_source, runtime_root, check=False)
        assert old.returncode != 0
        assert new.returncode != 0
        assert "already holds the lease" in old.stderr
        assert "already holds the lease" in new.stderr
        assert not (runtime_root / "data" / "kgeopolitical_monitor.db").exists()
    assert _invoke(new_source, runtime_root).returncode == 0
