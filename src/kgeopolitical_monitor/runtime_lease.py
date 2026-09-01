"""Single-instance lease for the owner-only unattended runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
import errno
import os
from pathlib import Path
from typing import IO

from .runtime_storage import RuntimeStoragePolicy


class RuntimeLeaseError(RuntimeError):
    """Raised when another runtime instance already owns the lease."""


def default_runtime_lease_path(project_root: str | Path) -> Path:
    """Return the canonical project-local lease path."""

    policy = RuntimeStoragePolicy(Path(project_root))
    return (policy.data_root / ".kgm-monitor.lock").resolve()


def _lock_posix(handle: IO[str]) -> None:
    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in {errno.EACCES, errno.EAGAIN}:
            raise RuntimeLeaseError(
                "another unattended runtime instance already holds the lease"
            ) from exc
        raise


def _unlock_posix(handle: IO[str]) -> None:
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _lock_windows(handle: IO[str]) -> None:
    import msvcrt

    handle.seek(0)
    if not handle.read(1):
        handle.seek(0)
        handle.write("0")
        handle.flush()
    handle.seek(0)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError as exc:
        if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
            raise RuntimeLeaseError(
                "another unattended runtime instance already holds the lease"
            ) from exc
        raise


def _unlock_windows(handle: IO[str]) -> None:
    import msvcrt

    handle.seek(0)
    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _lock(handle: IO[str]) -> None:
    if os.name == "nt":
        _lock_windows(handle)
    else:
        _lock_posix(handle)


def _unlock(handle: IO[str]) -> None:
    if os.name == "nt":
        _unlock_windows(handle)
    else:
        _unlock_posix(handle)


@dataclass
class RuntimeInstanceLease:
    """Non-blocking OS-backed lease for one KGM unattended supervisor.

    The lock file is persistent diagnostic metadata. Ownership is determined only
    by the active OS lock, so a stale PID string after an abnormal exit never
    blocks recovery by itself.
    """

    path: Path
    _handle: IO[str] | None = field(default=None, init=False, repr=False)

    def acquire(self) -> "RuntimeInstanceLease":
        if self._handle is not None:
            raise RuntimeLeaseError("runtime lease is already acquired by this object")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+", encoding="utf-8")
        try:
            _lock(handle)
        except BaseException:
            handle.close()
            raise

        try:
            handle.seek(0)
            handle.truncate()
            handle.write(f"pid={os.getpid()}\n")
            handle.flush()
        except BaseException:
            try:
                _unlock(handle)
            finally:
                handle.close()
            raise

        self._handle = handle
        return self

    def release(self) -> None:
        handle = self._handle
        if handle is None:
            return
        self._handle = None
        try:
            _unlock(handle)
        finally:
            handle.close()

    def __enter__(self) -> "RuntimeInstanceLease":
        return self.acquire()

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.release()
