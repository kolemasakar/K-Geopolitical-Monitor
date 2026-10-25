# O1 access / operational evidence — owner-requested 1+2+3+4 (2026-10-25)

**Decision: O1_PARTIAL / ACCESS_BLOCKED / PRODUCTION_NO_GO.**

## GitHub
- PR #253 merged after GitHub CI #3721 SUCCESS.
- Merge SHA `38a899a981ce10751a88441aba24d16e3edcea0d`.
- O1 narrow read-only helper was specified as a proposal; it has **not** been installed.

## Fresh server observations
- `kgm-e4-owner-pilot`, connected Remote Desktop Commander, user `kgmops`.
- `systemctl show`: `MainPID=125277`, `ActiveState=active`, `Result=success`, `NRestarts=0`, `ActiveEnterTimestamp=2026-10-24 06:39:45 UTC`.
- Disk checkout remains `b31b2136b5fe982d0b63b0135479b1549041906c`.
- `ls /opt/k-geopolitical-monitor/data` denied to `kgmops`: no live database or forward-state inspection.
- Both `sudo -n true` and `sudo -n journalctl ...` blocked by Remote Desktop Commander command policy. No privileged access was obtained.
- Loaded-code SHA remains UNKNOWN. No last-successful-cycle timestamp, error counts, source freshness, SQLite integrity, consumer delivery, or authoritative runtime provenance can be reported.

## Gate matrix
| Step | Evidence | Verdict |
|---|---|---|
| 1. Scoped read-only access | design accepted in PR #253; sudo/operator route not permitted | DESIGN PASS / INSTALL BLOCKED |
| 2. Journal and cycle/persistent-state checks | permissions deny both data and privileged journal | BLOCKED |
| 3. Actual loaded-code provenance | disk Git SHA only, no process/module attestation | UNKNOWN |
| 4. O1 acceptance | no invented PASS, this checkpoint records shortfall | PARTIAL / NO_GO |

## Next engineering work (owner-admin-only bounded preparation)
- Approve and install narrowly scoped root-owned read-only diagnostic helper (fixed output, redacted summaries only, no arbitrary commands/paths, no network send) through a verified administrative channel, with privilege and side-effect audit.
- Query summarized journal and lifecycle/cycle counters; perform *only* safe DB read-only/snapshot-consistent integrity validation, with no WAL write, no restart or live migration.
- Correlate actual process module provenance with deployment checkout and service start; if impossible mark UNKNOWN.
- Independently document observations, CI and reviewer signoff before O1 operational PASS consideration.

No modification of server permissions, runtime state, production data, service, or source activation occurred during this audit. **FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO** remain in force.
