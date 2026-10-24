"""S5.1 isolated real child-process SIGKILL lease recovery; never touches production."""
import os
import signal
import subprocess
import sys

import pytest
from kgeopolitical_monitor.runtime_lease import RuntimeInstanceLease, RuntimeLeaseError


@pytest.mark.skipif(os.name != "posix", reason="POSIX SIGKILL and flock contract")
def test_child_sigkill_releases_runtime_lease(tmp_path):
    lock = tmp_path / "isolated" / ".kgm-monitor.lock"
    script = """
import sys
from pathlib import Path
from kgeopolitical_monitor.runtime_lease import RuntimeInstanceLease
lease=RuntimeInstanceLease(Path(sys.argv[1]))
lease.acquire()
print("ACQUIRED", flush=True)
sys.stdin.buffer.read()
"""
    child = subprocess.Popen([sys.executable, "-c", script, str(lock)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    try:
        assert child.stdout.readline().strip() == "ACQUIRED"
        with pytest.raises(RuntimeLeaseError):
            RuntimeInstanceLease(lock).acquire()
        os.kill(child.pid, signal.SIGKILL)
        child.wait(timeout=10)
        assert child.returncode == -signal.SIGKILL
        with RuntimeInstanceLease(lock):
            assert lock.read_text().startswith("pid=")
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)
        child.stdin.close()
        child.stdout.close()
        child.stderr.close()
