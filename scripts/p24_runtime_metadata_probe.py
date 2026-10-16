#!/usr/bin/env python3
"""Fixed, read-only KGM metadata probe; stdout JSON, no credentials or raw logs."""
import json
import os
import subprocess
from datetime import datetime, timezone

def command(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=10)
    return {"exit": p.returncode, "stdout": p.stdout.strip()}
r = {"observed_at": datetime.now(timezone.utc).isoformat(),
     "service": command(["systemctl","show","kgm-monitor.service","-p","MainPID",
          "-p","ActiveState","-p","User","-p","WorkingDirectory","-p","ExecMainStartTimestamp"]),
     "checkout": command(["git","-c","safe.directory=/opt/k-geopolitical-monitor",
          "-C","/opt/k-geopolitical-monitor","rev-parse","HEAD"]),
     "loaded_python_release": "NOT_ATTESTABLE_RETROSPECTIVELY"}
pid = command(["systemctl","show","kgm-monitor.service","--property=MainPID","--value"])["stdout"]
if pid.isdigit() and int(pid) > 0:
    for name in ("cwd", "exe"):
        try:
            r["process_"+name] = os.readlink("/proc/"+pid+"/"+name)
        except OSError:
            r["process_"+name] = "UNAVAILABLE"
print(json.dumps(r, indent=2))
