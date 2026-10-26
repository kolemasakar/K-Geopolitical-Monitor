# KGM P5 — Owner-authorized manual offline on-demand requests (2026-10-26)

## What has been implemented

Workflow `.github/workflows/p5-owner-on-demand-offline.yml` is **workflow_dispatch-only**, restricted to repository `kolemasakar/K-Geopolitical-Monitor`, GitHub actor `kolemasakar`, and branch `main`. GitHub's RBAC determines who may dispatch; the job also fails closed on a mismatched owner actor/repository/ref/event context. It is NOT a public user API and is NOT independent user identity verification beyond authenticated GitHub Actions context.

The owner supplies a single bounded text topic (1–256 characters; no controls), safe request ID and fixed choice `OFFLINE_SYNTHETIC`. `on_demand_request_gate.py` validates these, computes a digest without printing the raw topic, and explicitly rejects all live modes. The fixed research child receives the validated topic only in the sandbox environment and emits an aggregate result and SHA-256 digest. The job verifies that the topic digest and request ID match.

Execution takes place in an ephemeral GitHub-hosted Python Docker image with `--network none`, read-only code mount, no retained Git credentials, unprivileged UID, dropped capabilities, bounded resources, limited `/tmp`, 120-second outer timeout. It executes the same fixed synthetic one-shot pipeline: **NOT GDACS/GDELT/Consilium** and no real news content. The host gate rejects context before image pull and job execution.

Unit tests exercise accept/deny cases for wrong actor, branch, repository, event, mode and malformed input and verify the workflow has no `push`/`pull_request` trigger and no live choice.

## Security qualifications / Critic

- GitHub Actions logs/workflow-dispatch metadata may retain user-supplied topic in event metadata. Input must be non-sensitive, never credentials or private research. The raw topic is not printed by scripts, but confidentiality is **not** guaranteed by this API.
- An explicit actor allowlist is a minimal owner policy, not proof of general RBAC, resistant authorization to account takeover, or multiuser production authentication.
- Workflow dispatch does not imply a ChatGPT plugin callable path. No ChatGPT-to-Actions integration is asserted.
- No real external fetch, live egress control, GDPR/content policy assessment, publisher independence or real-world provenance is provided by this synthetic route.
- `--network none` is appropriate for synthetic tests; a future live pilot must use a **separately reviewed network policy and explicit owner approval**, not silently remove this restriction.
- Static YAML validation and tests do not themselves prove manually dispatched workflow executed; that acceptance requires an owner-initiated run on merged `main` and a matching GitHub Actions record.
- This workflow is a test-only manual execution interface, not production deployment or change to existing watch scheduler.

**Gate:** `P5_OWNER_OFFLINE_MANUAL_ROUTE_CODE_READY` subject to CI; `P5_MANUAL_DISPATCH_RUNTIME_PENDING` until owner-run evidence; `P5_LIVE_E2E_NO_GO`.

Policy: ON_DEMAND_ONLY / FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
