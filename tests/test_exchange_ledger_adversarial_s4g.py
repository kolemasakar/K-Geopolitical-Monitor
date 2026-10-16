"""Offline adversarial checks for atomic exchange ledger. No network or production."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from test_exchange_contract_v1 import base


def _fixture(tmp_path, count=2):
    root = tmp_path / "exchange"
    root.mkdir()
    for i in range(count):
        batch = base()
        batch["batch_id"] = f"batch{i}"
        publish_generation(batch, root)
    return root


def test_concurrent_append_no_duplicate_or_sequence_gap(tmp_path):
    root = _fixture(tmp_path)
    ids = ["batch0", "batch1"] * 8
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda item: atomic.append(root, item), ids))
    rows = atomic.replay(root, after_sequence=0)
    assert len(rows) == 2
    assert [x["sequence"] for x in rows] == [1, 2]
    assert {x["batch_id"] for x in rows} == {"batch0", "batch1"}


def test_torn_ledger_remains_rejected_across_process_restart(tmp_path):
    root = _fixture(tmp_path, 1)
    atomic.append(root, "batch0")
    path = root / "ledger-v2.jsonl"
    path.write_bytes(path.read_bytes()[:-1])
    script = """
from pathlib import Path
import sys
from kgeopolitical_monitor.exchange_ledger_atomic_v1 import replay
try:
    replay(Path(sys.argv[1]), 0)
except ValueError:
    sys.exit(22)
sys.exit(23)
"""
    child = subprocess.run([sys.executable, "-c", script, str(root)],
                           capture_output=True, env=os.environ.copy())
    assert child.returncode == 22


def test_symlinked_ledger_is_not_followed(tmp_path):
    root = _fixture(tmp_path, 1)
    target = tmp_path / "outside.jsonl"
    target.write_text('{"sequence":1,"batch_id":"foreign","sha256":"x"}\n')
    (root / "ledger-v2.jsonl").symlink_to(target)
    with pytest.raises((ValueError, OSError)):
        atomic.replay(root, 0)
    assert target.read_text().startswith('{"sequence":1')


def test_lock_symlink_rejected(tmp_path):
    root = _fixture(tmp_path, 1)
    target = tmp_path / "outside.lock"
    target.write_text("protected")
    (root / ".ledger-v2.lock").symlink_to(target)
    with pytest.raises((OSError, ValueError)):
        atomic.append(root, "batch0")
    assert target.read_text() == "protected"
