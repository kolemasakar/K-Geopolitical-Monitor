"""Real POSIX limits in disposable child probes; no active-service mutation."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED={"memory":"MEMORY_LIMIT","file":"EFBIG","descriptors":"EMFILE",
          "cpu":"SIGXCPU"}

def _classify(kind,result):
    try:
        evidence=json.loads(result.stdout)
    except (ValueError,TypeError):
        return "FAILED"
    return ("LIMIT_ENFORCED" if result.returncode==42 and
            evidence=={"cause":EXPECTED[kind]} else "FAILED")

def probe(kind):
    if kind not in {*EXPECTED,"timeout"}:
        raise ValueError("unknown probe")
    script = """
import errno,json,resource,signal,sys
def finish(cause):
 print(json.dumps({'cause':cause}),flush=True)
 sys.exit(42)
def cpu_limit(*args): finish('SIGXCPU')
signal.signal(signal.SIGXCPU,cpu_limit)
resource.setrlimit(resource.RLIMIT_AS,(96*1024*1024,96*1024*1024))
resource.setrlimit(resource.RLIMIT_FSIZE,(1024,1024))
resource.setrlimit(resource.RLIMIT_NOFILE,(32,32))
resource.setrlimit(resource.RLIMIT_CPU,(1,2))
kind=sys.argv[1]
try:
 if kind=='memory': x=bytearray(256*1024*1024)
 elif kind=='file':
  with open('bounded-file','wb') as f: f.write(b'x'*4096)
 elif kind=='descriptors': handles=[open('bounded-file','ab') for _ in range(64)]
 else:
  while True: pass
except MemoryError:
 if kind=='memory': finish('MEMORY_LIMIT')
 sys.exit(43)
except OSError as error:
 expected={'file':errno.EFBIG,'descriptors':errno.EMFILE}.get(kind)
 if expected is not None and error.errno==expected:
  finish(errno.errorcode[error.errno])
 sys.exit(43)
sys.exit(0)
"""
    with tempfile.TemporaryDirectory(prefix="kgm-resource-probe-") as temp:
        try:
            result=subprocess.run([sys.executable,"-I","-c",script,kind],
                cwd=temp,capture_output=True,text=True,
                timeout=0.1 if kind=="timeout" else 5,env={"PATH":os.defpath})
            return {"kind":kind,"status":_classify(kind,result) if kind!="timeout" else "FAILED",
                    "returncode":result.returncode,
                    "max_observed_file_bytes":max((p.stat().st_size for p in Path(temp).iterdir()),default=0)}
        except subprocess.TimeoutExpired:
            return {"kind":kind,"status":"TIMEOUT","child_reaped":True}
