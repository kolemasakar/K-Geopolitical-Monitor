# GitHub Actions Quota Contingency — 2026-09-19

Status: `ACTIVE_UNTIL_ACTIONS_RESET_2026-10-01`

Owner-provided account evidence shows the included GitHub Actions allowance at
`2000 / 2000 minutes` for the current billing cycle. Further hosted Actions
usage may be billable until the allowance resets on 2026-10-01.

## Temporary validation mode

Until the reset:

- do not intentionally trigger new GitHub-hosted Actions runs;
- use commit/merge skip instructions where supported;
- validate candidate heads on `kgm-e4-owner-pilot` from the exact Git SHA;
- run targeted tests first and then the full local regression suite;
- record exact SHA, host architecture, command, pass/fail count and runtime;
- do not weaken functional, provenance, verification, runtime or owner gates.

A hosted Actions result that already exists remains valid evidence. This
contingency does not reinterpret a failed functional test as PASS.

## Merge rule

A change may be merged during the quota window only when:

1. exact-head owner-local full regression is PASS;
2. targeted tests for the changed surface are PASS;
3. the branch is conflict-free against current `main`;
4. no branch-protection requirement blocks the merge;
5. the merge commit is marked to avoid an unnecessary hosted run.

After 2026-10-01, normal hosted CI evidence resumes for new changes.

This is a cost-control contingency only. It does not activate production/live,
persistent owner operation, paid/shared resources, migration 033, Plugin
publication, or any factual-verification shortcut.