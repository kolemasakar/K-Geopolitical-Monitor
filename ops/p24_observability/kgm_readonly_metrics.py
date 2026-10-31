#!/usr/bin/env python3
"""Read-only bounded KGM runtime observability; no journal content or DB rows."""
import json, os, pathlib, subprocess, datetime
SERVICE = "kgm-monitor.service"
def cmd(*args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=8)
        return p.stdout.strip() if p.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None
def measure():
    fields=("ActiveState","NRestarts","MemoryCurrent","MemoryPeak","MemoryMax",
            "CPUQuotaPerSecUSec","CPUUsageNSec","TasksCurrent","TasksMax")
    data=cmd("systemctl","show",SERVICE,*[v for f in fields for v in ("-p",f)])
    kv=dict(s.split("=",1) for s in (data or "").splitlines() if "=" in s)
    stat=os.statvfs("/opt/k-geopolitical-monitor")
    obs={"schema":1,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "service":{k:kv.get(k) for k in fields},
         "disk_free_percent":round(100*stat.f_bavail/stat.f_blocks,2),
         "memory_events":None}
    cg=cmd("systemctl","show",SERVICE,"-p","ControlGroup")
    group=(cg or "").removeprefix("ControlGroup=")
    if group.startswith("/") and ".." not in pathlib.PurePosixPath(group).parts:
        path=pathlib.Path("/sys/fs/cgroup")/group.lstrip("/")/"memory.events"
        try:
            obs["memory_events"]={k:int(v) for line in path.read_text().splitlines()
                                  for k,v in [line.split()]}
        except (OSError,ValueError):
            pass
    obs["state"]="PASS" if kv.get("ActiveState")=="active" and obs["disk_free_percent"]>=10 else "ALERT"
    return obs
if __name__=="__main__":
    print(json.dumps(measure(),ensure_ascii=False,sort_keys=True))
