#!/usr/bin/env python3
"""Fail-closed PRE-FLIGHT ONLY for P24.2-A cleanup. No deletion implemented."""
import argparse, hashlib, json, os, stat, sys
from pathlib import Path

FILES = (
    "kgm-p24-validation/restore-check/kgeopolitical_monitor.db",
    "kgm-p24-export/backup/runtime.db",
    "kgm-p24-export/backup/manifest.json",
    "kgm-p24-export/runtime-report.json",
)
DIRS = ("kgm-p24-validation/restore-check", "kgm-p24-export/backup")
PARENTS = ("kgm-p24-validation", "kgm-p24-export")
CONTENTS = {
    DIRS[0]: {"kgeopolitical_monitor.db"},
    DIRS[1]: {"runtime.db", "manifest.json"},
}

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def inspect(root, evidence, owner_uid=0):
    root = Path(root)
    for rel in ("", *PARENTS, *DIRS):
        s = (root / rel).lstat()
        if not stat.S_ISDIR(s.st_mode) or s.st_uid != owner_uid or s.st_nlink < 2:
            raise ValueError("Unsafe parent directory: " + rel)
    for rel, names in CONTENTS.items():
        if {p.name for p in (root / rel).iterdir()} != names:
            raise ValueError("Unexpected directory entries: " + rel)
    info = {}
    for rel in FILES:
        path = root / rel
        s = path.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_uid != owner_uid or s.st_nlink != 1:
            raise ValueError("Unsafe artifact: " + rel)
        info[rel] = {"sha256": sha256(path), "size": s.st_size}
    for rel in FILES[:2]:
        if info[rel] != {"sha256": evidence["backup_sha256"], "size": evidence["backup_size"]}:
            raise ValueError("Backup mismatch: " + rel)
    for rel, key in ((FILES[2], "manifest_sha256"), (FILES[3], "report_sha256")):
        if info[rel]["sha256"] != evidence[key]:
            raise ValueError("Hash mismatch: " + rel)
    manifest = json.loads((root / FILES[2]).read_text())
    serialized = json.dumps(manifest)
    if evidence["backup_sha256"] not in serialized or str(evidence["backup_size"]) not in serialized:
        raise ValueError("Manifest backup identity mismatch")
    return info

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/var/lib")
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--owner-uid", type=int, default=0, help="isolated test fixtures only")
    args = parser.parse_args()
    try:
        if args.root == "/var/lib" and args.owner_uid != 0:
            raise ValueError("Production requires root owner")
        evidence = json.loads(Path(args.evidence).read_text())
        info = inspect(args.root, evidence, args.owner_uid)
        print(json.dumps({"status":"PREFLIGHT_PASS", "cleanup":"HOLD",
                          "deletion_performed":False, "files":info}, indent=2))
        return 0
    except Exception as ex:
        print(json.dumps({"status":"PREFLIGHT_FAIL", "cleanup":"HOLD",
                          "deletion_performed":False, "error":str(ex)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
