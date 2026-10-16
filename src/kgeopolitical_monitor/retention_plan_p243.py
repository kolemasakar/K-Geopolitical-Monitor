"""Bounded metadata-only retention planning. No deletion or activation API."""
import math
import os
import stat
from pathlib import Path


def plan(root, *, now, min_age_seconds, keep_last, max_files=1000):
    if (type(now) not in (int, float) or not math.isfinite(now)
            or type(min_age_seconds) not in (int, float)
            or not math.isfinite(min_age_seconds) or min_age_seconds < 0
            or type(keep_last) is not int or keep_last < 1
            or type(max_files) is not int or not 1 <= max_files <= 10000):
        raise ValueError("invalid retention bounds")
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("directory required")
    files = []
    seen = 0
    with os.scandir(root) as entries:
        for item in entries:
            seen += 1
            if seen > max_files:
                raise ValueError("scan limit exceeded; no partial deletion plan")
            if not item.name.startswith("artifact-") or not item.name.endswith(".json"):
                continue
            info = item.stat(follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("aliased or nonregular artifact")
            files.append((item.name, info.st_mtime, info.st_size))
    files.sort(key=lambda x: (-x[1], x[0]))
    eligible = [f for f in files[keep_last:] if now - f[1] >= min_age_seconds]
    return {"dry_run": True, "scanned_entries": seen,
            "artifact_bytes": sum(f[2] for f in files),
            "eligible_bytes": sum(f[2] for f in eligible),
            "eligible": [f[0] for f in eligible],
            "deleted": 0, "send": False}
