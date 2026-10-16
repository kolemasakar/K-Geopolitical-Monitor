"""S5.1: bounded child-process SIGKILL at two ledger commit boundaries."""
import os
import signal
import subprocess
import sys

from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from test_exchange_contract_v1 import base


def run_child(root, failpoint):
    program = """
import os, signal, sys
from pathlib import Path
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as a
def kill(*args, **kwargs):
    os.kill(os.getpid(), signal.SIGKILL)
if sys.argv[2] == "before_replace":
    a.os.replace = kill
elif sys.argv[2] == "after_replace":
    a._sync_directory = kill
a.append(Path(sys.argv[1]), "batch1")
"""
    return subprocess.run([sys.executable, "-c", program, str(root), failpoint],
                          capture_output=True, env=os.environ.copy())


def test_killed_before_atomic_replace_preserves_previous_ledger(tmp_path):
    root = tmp_path / "exchange"
    root.mkdir()
    first=base()
    publish_generation(first, root)
    atomic.append(root,"batch1")
    second=base()
    second["batch_id"]="batch2"
    publish_generation(second,root)
    # Isolate fault to second batch, not the already committed initial state.
    program = """
import os, signal, sys
from pathlib import Path
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as a
def kill(*args, **kwargs):
    os.kill(os.getpid(), signal.SIGKILL)
a.os.replace = kill
a.append(Path(sys.argv[1]), "batch2")
"""
    child=subprocess.run([sys.executable,"-c",program,str(root)],capture_output=True,env=os.environ.copy())
    assert child.returncode == -signal.SIGKILL
    assert [r["batch_id"] for r in atomic.replay(root,0)] == ["batch1"]
    assert atomic.append(root,"batch2")["sequence"] == 2


def test_killed_after_replace_has_replayable_complete_record(tmp_path):
    root=tmp_path/"exchange"
    root.mkdir()
    publish_generation(base(),root)
    child=run_child(root,"after_replace")
    assert child.returncode == -signal.SIGKILL
    rows=atomic.replay(root,0)
    assert len(rows)==1 and rows[0]["batch_id"]=="batch1"
    assert atomic.append(root,"batch1")==rows[0]
