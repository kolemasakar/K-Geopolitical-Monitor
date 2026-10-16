"""Real POSIX limits in disposable child probes; never touches active service."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

def probe(kind):
    if kind not in {"memory","file","descriptors","cpu","timeout"}:
        raise ValueError("unknown probe")
    script = """
import os,resource,sys
resource.setrlimit(resource.RLIMIT_AS,(96*1024*1024,96*1024*1024))
resource.setrlimit(resource.RLIMIT_FSIZE,(1024,1024))
resource.setrlimit(resource.RLIMIT_NOFILE,(32,32))
resource.setrlimit(resource.RLIMIT_CPU,(1,1))
kind=sys.argv[1]
try:
 if kind=='memory': x=bytearray(256*1024*1024)
 elif kind=='file':
  with open('bounded-file','wb') as f: f.write(b'x'*4096)
 elif kind=='descriptors': handles=[open('bounded-file','ab') for _ in range(64)]
 else:
  while True: pass
except (MemoryError,OSError):
 sys.exit(42)
sys.exit(0)
"""
    with tempfile.TemporaryDirectory(prefix="kgm-resource-probe-") as temp:
        try:
            result=subprocess.run([sys.executable,"-I","-c",script,kind],
                cwd=temp,capture_output=True,timeout=0.1 if kind=="timeout" else 5,
                env={"PATH":os.defpath})
            status="LIMIT_ENFORCED" if result.returncode==42 or (kind in {"cpu","file"} and result.returncode<0) else "FAILED"
            return {"kind":kind,"status":status,"returncode":result.returncode,
                    "max_observed_file_bytes":max((p.stat().st_size for p in Path(temp).iterdir()),default=0)}
        except subprocess.TimeoutExpired:
            return {"kind":kind,"status":"TIMEOUT","child_reaped":True}
