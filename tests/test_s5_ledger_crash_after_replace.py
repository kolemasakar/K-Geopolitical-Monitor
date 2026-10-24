"""S5.1: isolated child hard exit between ledger replacement and directory fsync."""
import json
import os
import subprocess
import sys

from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
from test_exchange_contract_v1 import base


def test_hard_exit_after_replace_replay_and_retry_are_idempotent(tmp_path):
    root = tmp_path / "private-exchange"
    root.mkdir()
    batch = base()
    publish_generation(batch, root)
    script = """
import os, sys
from pathlib import Path
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
previous = atomic.os.replace
def replace_then_exit(src, dst):
    previous(src,dst)
    os._exit(73)
atomic.os.replace = replace_then_exit
atomic.append(Path(sys.argv[1]),"batch1")
"""
    child = subprocess.run([sys.executable, "-c", script, str(root)],
                           capture_output=True,env=os.environ.copy(),timeout=10)
    assert child.returncode == 73
    records = atomic.replay(root, after_sequence=0)
    assert len(records) == 1
    assert records[0]["batch_id"] == "batch1"
    assert atomic.append(root, "batch1") == records[0]
    assert atomic.replay(root, after_sequence=0) == records


def test_failure_after_replace_is_uncertain_commit_not_rollback(tmp_path, monkeypatch):
    root = tmp_path / "private-exchange"
    root.mkdir()
    publish_generation(base(), root)
    def synthetic_fsync_failure(_):
        raise OSError("synthetic parent directory fsync fail")
    monkeypatch.setattr(atomic, "_sync_directory", synthetic_fsync_failure)
    import pytest
    with pytest.raises(OSError):
        atomic.append(root, "batch1")
    assert len(atomic.replay(root, after_sequence=0)) == 1
    assert atomic.append(root, "batch1")["sequence"] == 1
