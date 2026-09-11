# K-Geopolitical Monitor — Repository Security / Static Audit

Date: 2026-09-11
Status: `READ_ONLY_AUDIT_COMPLETE`
Audit base: `b4c0f6b2e5d5772654842ebb3a22e7c2a87dfb4f`

This audit records static repository/control-plane findings. It does not change workflows, secrets, branch settings, Tailscale trust, runtime state, or the P19 soak chain.

## Summary

```text
CRITICAL_FINDINGS = 0
HIGH_FINDINGS = 0 security-specific
MEDIUM_FINDINGS = 3
LOW_PROCESS_FINDINGS = 2
POSITIVE_CONTROLS = multiple
```

The separate P19 deployed-runtime SHA drift is an operational integrity / assurance closure blocker and is documented in `PHASE_19_OWNER_LOCAL_RUNTIME_DRIFT_AUDIT_2026-09-11.md`; it is not counted here as a conventional repository vulnerability.

## Positive controls observed

### Workflow least privilege

Key workflows use explicit, bounded permissions:

- CI: `contents: read`;
- P19 soak audit: `actions: read`, `contents: read`;
- P19 dispatcher: `actions: write`, `contents: read`, where Actions write is required for workflow dispatch;
- Tailscale control: `contents: read`, `id-token: write` for OIDC.

No `pull_request_target` workflow was found in the repository search performed for this audit.

### Remote-control boundary

The KGM control workflow:

- targets exact host `kgm-e4-owner-pilot`;
- checks exact Tailscale IP `100.102.136.23`;
- uses workload identity rather than a long-lived Tailscale auth key;
- uses dedicated user `kgmops`;
- verifies runtime DB read is denied to `kgmops`;
- verifies arbitrary root escalation is denied;
- automatic P19 operation is health-only; restart is skipped unless explicitly requested.

### Dependency determinism

`constraints/ci.txt` pins the CI dependency set to exact versions. Exact-main CI also executes `pip check` and the latest observed run was clean.

### Basic secret spot checks

Repository searches performed during this audit found no matches for representative high-risk patterns including:

```text
BEGIN PRIVATE KEY
AKIA
password=
```

This is a spot check, not a substitute for dedicated secret scanning.

## Findings

### MEDIUM-1 — default branch has no enforced protection/ruleset

Observed at audit time:

```text
main.protected = false
repository_rulesets = []
```

Impact: project process currently relies on manual guarded-merge discipline rather than repository-enforced prevention of direct/unvalidated changes.

Recommended remediation after the current P19 soak-sensitive work is stabilized:

- protect `main` or create an equivalent repository ruleset;
- require the intended CI/check set before merge;
- block force pushes/deletion as appropriate;
- preserve an owner emergency path deliberately rather than implicitly.

This requires repository settings/admin authority and is not changed by this audit.

### MEDIUM-2 — GitHub Actions are referenced by mutable major-version tags

Observed examples include:

```text
actions/checkout@v5
actions/setup-python@v6
actions/upload-artifact@v4
tailscale/github-action@v4
```

Impact: a major tag can move to a different commit, creating supply-chain drift independent of repository commits.

Recommended remediation:

- pin third-party and GitHub actions to immutable commit SHAs;
- retain human-readable version comments beside pins;
- update pins through an audited dependency-update process.

Do not modify P19 control workflows in the middle of the current real-soak attempt solely for this hardening item; schedule the change at a controlled boundary unless an urgent security advisory requires immediate action.

### MEDIUM-3 — SSH host-key verification is disabled in the bounded Ansible inventory

Observed SSH options include:

```text
StrictHostKeyChecking=no
UserKnownHostsFile=/dev/null
```

The exact Tailscale host/IP verification and tailnet authorization substantially reduce exposure, but the SSH layer itself does not pin a host key.

Recommended remediation:

- establish an authenticated/pinned KGM SSH host identity, or
- document and validate an equivalent Tailscale SSH identity mechanism that removes the need to disable host-key verification.

Any change to this control path should be separately validated and must not silently broaden Tailscale trust.

### LOW-1 — no CODEOWNERS file

No `CODEOWNERS` file was found in the supported locations checked (`/`, `/.github/`, `/docs/`).

For the current owner-only beta this is not a major exposure, but adding ownership rules later can make sensitive workflow/security changes more explicit if collaboration expands.

### LOW-2 — no repository-managed dependency/security automation found

No Dependabot or CodeQL configuration was found by repository search, and `.github` currently exposes only the workflows directory rather than a Dependabot config.

Recommended future hardening:

- add dependency-update automation appropriate to the pinned dependency policy;
- add static/security scanning appropriate to Python and GitHub Actions;
- ensure alerts do not auto-mutate production/runtime state.

## P19 interaction

No security hardening mutation is performed by this audit because P19 Attempt 2 is collecting elapsed real-soak evidence. Recommended changes are queued as post-soak or controlled-boundary work unless a newly discovered vulnerability makes immediate remediation necessary.

```text
P19_BASELINE_CHANGE = NO
P19_CADENCE_CHANGE = NO
TAILSCALE_TRUST_CHANGE = NO
RUNTIME_CHANGE = NO
```

## Priority after the soak boundary

Recommended remediation order:

1. resolve P19 deployed-runtime candidate identity;
2. enforce branch/ruleset protections;
3. pin GitHub Actions to immutable SHAs;
4. restore/pin SSH host identity verification;
5. add dependency/security automation and optional CODEOWNERS policy.

These recommendations do not authorize A5, shared runtime, paid resources, or canonical cutover.
