# P24.2-A — cleanup executor security design (no authorization to delete)

## Release policy
Current production cleanup remains **HOLD**. The current `kgm-p24-cleanup` must not execute. The review-only executor has no deletion methods. This design is for a separately reviewed future implementation, not a runbook authorizing deletion.

## Immutable target set
Only four regular files, then exactly two now-empty leaf directories, as identified by the accepted owner evidence. Root ancestor directories must never be removed. Approved bytes/hash/size for each file are pinned to the owner acceptance, not user-supplied untrusted runtime paths.

## Path-confusion and race control
1. Open the fixed base directory with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC` from a trusted root context. Descend each directory component by `open(..., dir_fd=parentfd)` with `O_NOFOLLOW|O_DIRECTORY`. Verify root uid, mode/type and expected `st_dev` for each pinned FD; reject mount-point surprises.
2. Enumerate entries from pinned parent descriptors; require exact allowlisted names and no hidden extras. Store `fstat` identities `(st_dev, st_ino, st_mode, st_uid, st_gid, st_nlink, st_size)` and compare against `stat(name, dir_fd=fd, follow_symlinks=False)`.
3. Read each file only through `os.open(name, O_RDONLY|O_NOFOLLOW, dir_fd=fd)`; compute SHA-256 via that FD. Reject symlink, hardlink count != 1, wrong uid, wrong size, changed metadata during read. Compare manifest/report/DB with pinned acceptance evidence.
4. Preflight must finish for **all** targets before any unlink. At execution time revalidate identity of every target against pinned descriptors immediately before its unlink; never follow symlinks. No recursive `rm` or globs.
5. Filesystem replacement races are still possible if other actors can write the parent directories. Explicitly require all parent directory owners and permissions to prohibit writes by any other relevant actor; reject otherwise. Linux Python `os.unlink(dir_fd=...)` does not atomically assert inode identity; strict exclusion of concurrent writers or stronger kernel primitives must be justified before approval.
6. Use `os.unlink(name, dir_fd=parentfd)` on files in the exact authorized order; then `os.rmdir(name, dir_fd=grandparentfd)` on the two exact leaf directories, propagating every error. Multi-object cleanup is **not atomic**; if interrupted, report `PARTIAL` and enumerate remaining/missing objects. Never falsely report PASS.
7. Verify all six intended targets absent by safe dirfd-based checks; prove production `kgm-monitor.service` remains active; retain a root-controlled audit result with before/after identities, no raw DB rows.

## Authorization envelope
- Owner approval must explicitly identify the six fixed targets, four accepted SHA-256 values, the implementation commit and tested binary digest, expiration window and intended maintenance period.
- No `workflow_dispatch` may automatically authorize deletion simply by running a workflow; it may only gather preflight evidence pending a separate user decision.
- Require a fresh backup and isolated restore before future cutover, independently of the older historical snapshot.

## Acceptance tests to add
- Distinct directory symlink at each component, leaf symlink, hardlink, extra sibling, wrong owner, wrong mode, concurrent replacement simulation, mount/different device, mismatched SHA, mismatched inode after hash, error on unlink, error on rmdir, interruption after first file, missing post-state, service unexpectedly inactive, expired or mismatched approval.
- Confirm zero filesystem modifications on every failed preflight; confirm zero actions against /opt/k-geopolitical-monitor and its production SQLite.

Current result: design prepared; **execution prohibited**. FREE_ONLY / NO_SEND / production NO-GO retained.
