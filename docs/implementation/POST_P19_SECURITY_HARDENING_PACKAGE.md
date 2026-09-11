# Post-P19 Security Hardening Package

Date: 2026-09-11
Status: `STAGED_ON_NON_MAIN_BRANCH / DO_NOT_MERGE_DURING_ACTIVE_P19_SOAK`
Base: `5714a76aaf12c77993ed5a02165c02a48d953758`

This package prepares remediation for the repository security/static audit without changing the active P19 soak chain on canonical `main`.

## Staged immutable action pins

The following tag resolutions were independently read from the upstream GitHub repositories on 2026-09-11 and are staged as immutable references in the high-sensitivity CI/P19 workflows in this branch:

```text
actions/checkout@v5
  -> fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09

actions/setup-python@v6
  -> ece7cb06caefa5fff74198d8649806c4678c61a1

actions/upload-artifact@v4
  -> ea165f8d65b6e75b540449e92b4886f43607fa02

tailscale/github-action@v4
  -> 306e68a486fd2350f2bfc3b19fcd143891a4a2d8
```

Human-readable major-version comments are retained beside each SHA.

Current staged scope:

- `.github/workflows/ci.yml`;
- `.github/workflows/p19-owner-local-soak-gate-audit.yml`;
- `.github/workflows/p19-owner-local-real-soak.yml`;
- `.github/workflows/tailscale-kgm-control.yml`.

The P19 contract check is tightened to require the pinned `upload-artifact` SHA rather than the mutable `@v4` tag.

Before this package may be merged, perform a repository-wide sweep of every remaining `uses:` reference and either pin it to an audited immutable SHA or document an explicit exception. The current branch is intentionally a staging package, not a claim that MEDIUM-2 is fully closed repository-wide.

## SSH host-key verification remediation

Current bounded inventory still contains:

```text
StrictHostKeyChecking=no
UserKnownHostsFile=/dev/null
ANSIBLE_HOST_KEY_CHECKING=False
```

This branch does **not** invent or trust an SSH host key. The host-key remediation must be fail-closed and requires an authenticated owner-local host-key capture/verification step at a controlled boundary.

Required implementation sequence after P19 soak-sensitive work:

1. Obtain the server SSH host public key/fingerprint through an authenticated owner-controlled channel.
2. Record the expected algorithm and fingerprint as a security-controlled value.
3. Build an ephemeral `known_hosts` file on the runner from the authenticated value.
4. Replace `StrictHostKeyChecking=no` with `StrictHostKeyChecking=yes`.
5. Remove `UserKnownHostsFile=/dev/null` and set the explicit ephemeral known-hosts path.
6. Remove `ANSIBLE_HOST_KEY_CHECKING=False`.
7. Prove negative behavior with a deliberately wrong host key: connection must fail closed.
8. Re-run exact host/IP, DB-denial, root-denial and health-only assertions.

No TOFU-only `ssh-keyscan` output may be accepted as the sole trust anchor.

## Main-branch protection/ruleset target

Repository settings should enforce, after the controlled boundary:

```text
TARGET_BRANCH = main
DIRECT_UNVALIDATED_PUSH = BLOCKED
FORCE_PUSH = BLOCKED
BRANCH_DELETION = BLOCKED
REQUIRED_PR = YES
REQUIRED_STATUS_CHECKS = CI + architecture checks required by current project policy
STALE_APPROVAL_POLICY = EXPLICITLY_DEFINED
OWNER_EMERGENCY_BYPASS = EXPLICIT / AUDITABLE / NOT_IMPLICIT
```

This is an admin/settings action and is not changed by this branch.

## Dependency/security automation target

Prepare after the action-pin sweep:

- dependency update automation compatible with exact-version pinning;
- Python/static security scan that does not mutate runtime;
- GitHub Actions workflow/static scan;
- optional CODEOWNERS once collaboration policy requires it;
- no auto-deploy or automatic runtime mutation from security automation.

## Controlled merge gates

This branch must remain unmerged while P19 Attempt 2 is active unless an urgent vulnerability requires a separately authorized exception.

Before merge require:

```text
P19_SOAK_SENSITIVE_WINDOW = CLOSED_OR_EXPLICITLY_AUTHORIZED
REPO_WIDE_ACTION_PIN_SWEEP = PASS
CI = PASS
P19_CONTRACT_CHECK = PASS
HOST_KEY_TRUST_DESIGN = APPROVED
NO_RUNTIME_DEPLOYMENT_FROM_MERGE = CONFIRMED
NO_BASELINE_CHANGE_FROM_MERGE = CONFIRMED
```

Host-key verification may be delivered as a second controlled PR if the authenticated key material is not yet available. The immutable action pins do not require waiting for that key, but neither item should be misreported as fully remediated until its own gate passes.

## Current result

```text
SECURITY_HARDENING_PACKAGE = STAGED
MUTABLE_ACTION_PIN_REMEDIATION = PARTIAL_HIGH_SENSITIVITY_SCOPE
SSH_HOST_KEY_REMEDIATION = DESIGNED_NOT_APPLIED
MAIN_PROTECTION = DESIGNED_NOT_APPLIED
P19_RUNTIME_MUTATION = NO
P19_BASELINE_MUTATION = NO
P19_MAIN_WORKFLOW_MUTATION = NO
```
