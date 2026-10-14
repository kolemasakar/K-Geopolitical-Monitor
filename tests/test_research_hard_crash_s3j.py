"""Separate-process hard exit before cursor commit must not advance durable position."""
import os
import subprocess
import sys
from kgeopolitical_monitor.research_cursor_core_v1 import recover_with_cursor

def test_subprocess_hard_exit_does_not_commit_cursor(tmp_path):
    child = (
      "import os,sys;"
      "from pathlib import Path;"
      "from kgeopolitical_monitor.research_cursor_core_v1 import recover_with_cursor;"
      "def_placeholder"
    )
    script = """
import os, sys
from pathlib import Path
from kgeopolitical_monitor.research_cursor_core_v1 import recover_with_cursor
def crash(*args, **kwargs):
    os._exit(17)
recover_with_cursor(Path(sys.argv[1]),recover_fn=crash,
                    allowed_consumers={'ktrader':'review-v1'},
                    observed_at_utc='2026-10-14T00:00:00Z',max_items=1)
"""
    result=subprocess.run([sys.executable,"-c",script,str(tmp_path)],
                          capture_output=True,env=os.environ.copy())
    assert result.returncode==17
    cursor=tmp_path/".research-recovery-cursor.json"
    assert not cursor.exists()
    seen=[]
    def after_restart(root, *, after_key, **kwargs):
        seen.append(after_key)
        return {"next_cursor":("ktrader","req-01")}
    recover_with_cursor(tmp_path,recover_fn=after_restart,
                        allowed_consumers={"ktrader":"review-v1"},
                        observed_at_utc="2026-10-14T00:00:00Z",max_items=1)
    assert seen==[None]
    assert cursor.is_file()
