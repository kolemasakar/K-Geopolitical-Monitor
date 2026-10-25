"""Fail-closed Linux network-namespace test runner, not a production executor.

Requires kernel user/net namespace permissions. Never falls back to host networking.
Only invokes fixed offline synthetic child, not arbitrary commands or live adapters.
"""
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys


def isolated_command():
    unshare = shutil.which("unshare")
    if sys.platform != "linux" or not unshare:
        raise RuntimeError("offline network namespace unavailable")
    return [unshare, "--user", "--map-root-user", "--net", "--",
            sys.executable, "-m", "kgeopolitical_monitor.offline_isolation_child"]


def _limit_resources():
    resource.setrlimit(resource.RLIMIT_CPU, (10, 12))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))


def run_isolated_synthetic_test():
    """Explicit offline-only invocation, 20s wall timeout, no shells or live DB."""
    cmd = isolated_command()
    p = subprocess.run(cmd, timeout=20, check=False, capture_output=True,
                       text=True, stdin=subprocess.DEVNULL, preexec_fn=_limit_resources,
                       env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"},
                       cwd="/tmp")
    if p.returncode != 0:
        raise RuntimeError("isolated synthetic execution failed closed")
    if len(p.stdout) > 4096:
        raise RuntimeError("isolated output exceeds cap")
    report = json.loads(p.stdout)
    if report.get("format") != "KGM_O1_NETNS_SYNTHETIC_V1" or report.get("only_synthetic_data") is not True:
        raise RuntimeError("isolated report schema rejected")
    return report
