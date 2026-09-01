import os

import pytest

from kgeopolitical_monitor.runtime_lease import (
    RuntimeInstanceLease,
    RuntimeLeaseError,
    default_runtime_lease_path,
)


def test_default_runtime_lease_path_is_project_local(tmp_path):
    assert default_runtime_lease_path(tmp_path) == (
        tmp_path / "data" / ".kgm-monitor.lock"
    ).resolve()


def test_runtime_lease_rejects_second_holder_and_releases(tmp_path):
    path = default_runtime_lease_path(tmp_path)

    with RuntimeInstanceLease(path):
        assert path.is_file()
        assert path.read_text(encoding="utf-8") == f"pid={os.getpid()}\n"
        with pytest.raises(RuntimeLeaseError, match="already holds the lease"):
            RuntimeInstanceLease(path).acquire()

    with RuntimeInstanceLease(path):
        assert path.read_text(encoding="utf-8") == f"pid={os.getpid()}\n"


def test_runtime_lease_release_is_idempotent(tmp_path):
    lease = RuntimeInstanceLease(default_runtime_lease_path(tmp_path)).acquire()

    lease.release()
    lease.release()

    with RuntimeInstanceLease(default_runtime_lease_path(tmp_path)):
        pass


def test_runtime_lease_object_cannot_acquire_twice(tmp_path):
    lease = RuntimeInstanceLease(default_runtime_lease_path(tmp_path)).acquire()
    try:
        with pytest.raises(RuntimeLeaseError, match="already acquired"):
            lease.acquire()
    finally:
        lease.release()
