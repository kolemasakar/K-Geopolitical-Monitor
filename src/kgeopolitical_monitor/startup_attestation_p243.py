"""Secret-free startup observations; cannot attest a pre-existing process."""
import hashlib
import marshal
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def startup_record(project_root, adapters):
    root = Path(project_root)
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            capture_output=True, text=True, timeout=5)
    sha = result.stdout.strip() if result.returncode == 0 else None
    if sha is not None and (len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha)):
        sha = None
    return {"version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(), "checkout_sha_at_startup": sha,
            "sources": [{"source_id": a.source_id,
                         "class": type(a).__name__,
                         "loaded_fetch_code_sha256": hashlib.sha256(
                             marshal.dumps(type(a).fetch.__code__)).hexdigest()}
                        for a in adapters],
            "scope": "STARTUP_OBSERVATION_NOT_FULL_RELEASE_ATTESTATION",
            "secrets_included": False}
