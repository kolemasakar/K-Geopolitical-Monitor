#!/usr/bin/env python3
"""Observe natural timer recurrence, read-only. Never starts/restarts units."""
import argparse, datetime as dt, json, subprocess, sys
def properties(unit, fields):
    p=subprocess.run(["systemctl","show",unit,*[v for f in fields for v in ("-p",f)]],
                     capture_output=True,text=True,timeout=8,check=True)
    return dict(line.split("=",1) for line in p.stdout.splitlines() if "=" in line)
def check(now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    timer=properties("kgm-observability.timer",["ActiveState","LastTriggerUSec","Unit"])
    service=properties("kgm-observability.service",["Result","ExecMainStatus","ExecMainStartTimestamp"])
    stamp=timer.get("LastTriggerUSec","")
    try:
        fired=dt.datetime.strptime(stamp,"%a %Y-%m-%d %H:%M:%S %Z").replace(tzinfo=dt.timezone.utc)
        age=(now-fired).total_seconds()
    except ValueError:
        age=None
    status="PASS" if timer.get("ActiveState")=="active" and age is not None and 0<=age<=1200 and service.get("Result")=="success" and service.get("ExecMainStatus")=="0" else "PENDING"
    return {"state":status,"timer_last_trigger_utc":stamp,"trigger_age_s":round(age) if age is not None else None,
            "timer_active":timer.get("ActiveState")=="active",
            "service_last_success":service.get("Result")=="success" and service.get("ExecMainStatus")=="0",
            "two_natural_fires_attested":False}
if __name__=="__main__":
    result=check()
    print(json.dumps(result,sort_keys=True))
    sys.exit(0 if result["state"]=="PASS" else 2)
