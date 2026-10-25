import datetime as dt
import importlib.util
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"ops/o1_diag/kgm-o1-watch-due.py"
s=importlib.util.spec_from_file_location("o1_watch_due",P)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def test_schedule_due_and_disabled_and_running():
    now=dt.datetime(2026,10,25,20,tzinfo=dt.timezone.utc)
    watches=[("a",1,60),("b",0,60),("c",1,30),("d",1,15)]
    runs={"a":("COMPLETED","2026-09-01T08:32:14+00:00"),
          "c":("RUNNING","2026-10-25T19:00:00+00:00")}
    out=m.assess(watches,runs,now)
    assert out["enabled"]==3 and out["disabled"]==1
    assert out["due"]==2 and out["no_prior_run_due"]==1
    assert out["running_blocked"]==1
    assert out["most_overdue_minutes"]>1000

def test_fresh_watch_not_due():
    now=dt.datetime(2026,10,25,20,tzinfo=dt.timezone.utc)
    out=m.assess([("a",1,60)],{"a":("COMPLETED","2026-10-25T19:30:00+00:00")},now)
    assert out["not_due"]==1 and out["due"]==0
