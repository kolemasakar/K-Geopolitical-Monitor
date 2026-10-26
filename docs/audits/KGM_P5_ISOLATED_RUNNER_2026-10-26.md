# KGM P5 — Isolated synthetic executor on GitHub Actions (2026-10-26)

**Purpose:** test a one-shot, user-request-shaped research execution in a disposable, constrained environment. No live source fetches or production connections.

## Why

On `kgm-e4-owner-pilot`, unprivileged `unshare --user --map-root-user --net` failed with `Operation not permitted`. This does not establish that other isolated execution modes are unavailable. A GitHub-hosted Docker runner can potentially create a separate network namespace via `docker run --network none`, without modifying production host permission.

## Workflow

`.github/workflows/p5-isolated-synthetic-runner.yml` supports explicit manual dispatch and PR-triggered verification when the isolation runner files change. The job uses ephemeral `ubuntu-latest`, the public Python container image, and:

- `--network none` (no outside networking);
- `--read-only` and read-only source mount, bounded `/tmp`;
- `--cap-drop ALL`, `no-new-privileges`, unprivileged UID;
- `--pids-limit 64`, `--memory 512m`, `--cpus 1`, outer wall timeout;
- no repository auth token passed into the container, no secrets, no production DB;
- fixed `offline_isolation_child` synthetic research run, which checks network interfaces and IPv4 default route before collection.

The runner validates structured aggregate output. Test sources are synthetic `.example` references, never queried via the network. CI success would prove only the disposable Docker runner and in-process synthetic pipeline, NOT production namespace creation or a live real-source request.

## Fail-closed rules

If Docker, public image, isolated network namespace, process budget, synthetic DB, or expected output are unavailable, the job fails; it **must not** silently use host networking. No fallback to production VM; no adjusting kernel capabilities on production.

## Separate gates after runner CI

1. Independently attest the actual GitHub Actions job result for the specific SHA (not merely code review).
2. Design authenticated one-request ingress and source allowlist. The current dispatcher is fixture-only.
3. Arrange a separately approved *live* execution environment with bounded egress to GDACS/GDELT/Consilium, no unsolicited sending, and evidence provenance.
4. Record true external response status, publication time, source disagreements, Critic and reproducibility.
5. Full on-demand production acceptance remains **NO_GO** until the above evidence and explicit release authorization.

Policy: ON_DEMAND_ONLY / FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
