# KGM O1 P5 — Free GitHub Actions container isolation qualification

Date: 2026-10-26. Owner mode: ON_DEMAND_ONLY.

## Motivation and prior evidence

On KGM production host, `unshare --user --map-root-user --net` was denied with `Operation not permitted` during UID map setup (audit PR #265). No changes to production permissions or namespaces were authorized. Instead, prepare a separate short-lived **GitHub Actions hosted runner** and use Docker `--network none`. Hosted runners are CI infrastructure, not a persistent KGM service, and the synthetic workflow has **no connected production server credentials**.

## Fixed runner

Workflow: `.github/workflows/o1-p5-offline-container-attestation.yml`.

Build phase may retrieve a public Python base image and Python dependencies. This is **not** source collection and build-time network access must not be confused with runtime isolation. Docker image is based on `python:3.11-slim-bookworm` (digest not pinned; image/release reproducibility remains open).

Execution phase uses `docker run --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 512m --memory-swap 512m --cpus 1 --ulimit nofile=64:64 --tmpfs /tmp:... --user 65534:65534`. The host runs only a preselected Python entrypoint, not arbitrary user input. A 60s wall deadline and 4KiB output schema check are enforced externally by GitHub workflow.

The child checks that `/sys/class/net` lists exactly `lo` and `/proc/net/route` has no default IPv4 route; it **fails closed** otherwise. The result is limited synthetic aggregates, with two fixture-only adapters, a temporary SQLite created within container /tmp and no external HTTP. No source metadata or secrets are published.

This is a **real kernel container network namespace test** if the CI run actually succeeds. Interface/route inspection and Docker `--network none` are stronger operational evidence than unit mocks, but are NOT a general proof of kernel security, supply-chain image identity, DNS policy under a different runtime, network access in a later live release, or approval to deploy.

## Gates

| Gate | Status before actual workflow result |
|---|---|
| Authoritative P5 production unshare | SHORTFALL |
| Docker isolated synthetic runtime on CI | **PASS** — run #40256670532, corrected commit 81f599fee0c7ef581e6e3f5e8013f788ac71e1b8 |
| Docker runtime has no external interface/default IPv4 route | **PASS** — container reported only `lo`, no default IPv4 route |
| One synthetic request, two fixture sources, SQLite analysis | **PASS** — collection `COMPLETED`, two fixture sources, two evidence items |
| Actual GDACS/GDELT/Consilium responses via approved KGM live route | NOT_EXECUTED |
| Authorized on-demand user entrypoint | NOT_ATTESTED |
| Source independence & article-level currentness | NOT_ATTESTED |
| Production release acceptance | PRODUCTION_NO_GO |

Next stages: review actual workflow run output; only on success accept an **offline Docker isolation milestone**. Then design fixed allowlisted live adapter runner and explicit request authorization separately, with artifact evidence, bounded egress, source provenance, Critic and owner release gate. Never enable two dormant production watches.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.

## Actual CI evidence, 2026-10-26

- Candidate SHA `81f599fee0c7ef581e6e3f5e8013f788ac71e1b8`, standalone workflow **KGM O1 P5 Offline Container Isolation Attestation**, run **#40256670532**, conclusion **SUCCESS**.
- Build `Dockerfile.p5-offline-isolation` succeeded. An initial prior build (run #40256582963) correctly failed when migrations were omitted from a non-editable package; amended image copies the canonical `migrations/` directory and installs the code editable so `database.py` finds them. No production database was involved.
- The Docker execution step succeeded with `--network none`, read-only root, non-root UID/GID 65534, cap-drop ALL, no-new-privileges, memory/CPU/PID/FD limits and tmpfs.
- Report validation succeeded: `O1_P5_DOCKER_NO_NETWORK_SYNTHETIC_PASS`, `network_interfaces=["lo"]`, `collection_status="COMPLETED"`, `synthetic=true`, two sources and two evidence records. This is a real ephemeral container test, **not** a live source retrieval.
- The ordinary full project regression check runs separately; its result must be verified before merging this PR. Container image provenance digest still not pinned and production/live identity remains a separate gate.
