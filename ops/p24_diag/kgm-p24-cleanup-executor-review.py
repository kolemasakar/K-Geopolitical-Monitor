#!/usr/bin/env python3
"""P24 cleanup executor DRY RUN ONLY. No unlink/rmdir/remove functions are present.

This program is an independent decision-gate verifier, NOT a production deleter.
"""
import argparse
import json
import os
import stat
from pathlib import Path

APPROVAL_LITERAL = "P24_2_A_OWNER_APPROVED_CLEANUP_V1"
PRODUCTION_ROOT = "/var/lib"
TARGETS = (
    "kgm-p24-validation/restore-check/kgeopolitical_monitor.db",
    "kgm-p24-export/backup/runtime.db",
    "kgm-p24-export/backup/manifest.json",
    "kgm-p24-export/runtime-report.json",
    "kgm-p24-validation/restore-check",
    "kgm-p24-export/backup",
)

def decision(root: str, preflight: dict, approval: dict) -> dict:
    # Fail closed: even a valid approval never enables deletion in this revision.
    if str(Path(root).resolve()) == PRODUCTION_ROOT:
        raise ValueError("production_executor_not_implemented")
    if preflight.get("status") != "PREFLIGHT_PASS":
        raise ValueError("preflight_not_pass")
    if preflight.get("deletion_performed") is not False:
        raise ValueError("unexpected_preflight_mutation")
    if set(preflight.get("files", {})) != set(TARGETS[:4]):
        raise ValueError("unexpected_target_manifest")
    if approval.get("decision") != APPROVAL_LITERAL:
        raise ValueError("explicit_owner_approval_missing")
    if approval.get("targets") != list(TARGETS):
        raise ValueError("approval_target_mismatch")
    if approval.get("preflight_digest") != preflight.get("digest"):
        raise ValueError("preflight_digest_mismatch")
    return {"status":"REVIEW_ONLY","cleanup":"HOLD",
            "deletion_performed":False,"target_count":len(TARGETS)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--preflight",required=True)
    p.add_argument("--approval",required=True)
    args=p.parse_args()
    try:
        print(json.dumps(decision(args.root,json.loads(Path(args.preflight).read_text()),
                                  json.loads(Path(args.approval).read_text()))))
    except Exception as ex:
        print(json.dumps({"status":"BLOCKED","cleanup":"HOLD","deletion_performed":False,
                          "error":str(ex)}))
        raise SystemExit(1)

if __name__=="__main__":
    main()
