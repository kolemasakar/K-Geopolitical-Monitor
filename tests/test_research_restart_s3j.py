"""Real separate-process cursor continuation with two isolated consumers; offline only."""
import json
import os
import subprocess
import sys
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from test_research_typed_result_v1 import typed

POLICY={"ktrader":"review-v1","consumer-b":"review-v1"}
NOW="2026-09-28T12:06:00Z"

def invoke(root):
    script=(
        "import json,sys;"
        "from pathlib import Path;"
        "from kgeopolitical_monitor.research_durable_cursor_v1 import recover_durable;"
        "x=recover_durable(Path(sys.argv[1]),allowed_consumers={'ktrader':'review-v1','consumer-b':'review-v1'},"
        "observed_at_utc='2026-09-28T12:06:00Z',max_items=1);"
        "print(json.dumps(x))"
    )
    completed=subprocess.run([sys.executable,"-c",script,str(root)],
        check=True,capture_output=True,text=True,env=os.environ.copy())
    return json.loads(completed.stdout)

def test_cursor_persists_across_independent_python_processes(tmp_path):
    req,_=typed()
    for consumer in ("ktrader","consumer-b"):
        copy=dict(req,consumer_id=consumer,request_id="req-01")
        accept_request(tmp_path,copy,allowed_consumers=POLICY,
                       accepted_at_utc="2026-09-28T12:01:00Z")
    first=invoke(tmp_path)
    second=invoke(tmp_path)
    third=invoke(tmp_path)
    assert first["pending"]==[["consumer-b","req-01"]]
    assert second["pending"]==[["ktrader","req-01"]]
    assert third["pending"]==[["consumer-b","req-01"]]
    assert (tmp_path/".research-recovery-cursor.json").is_file()
