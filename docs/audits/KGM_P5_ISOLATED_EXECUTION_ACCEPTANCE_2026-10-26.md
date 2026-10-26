# KGM P5 — independently observed isolated-runner qualification, 2026-10-26

## Final accepted evidence

- Implementation PR: [#268](https://github.com/kolemasakar/K-Geopolitical-Monitor/pull/268), **MERGED**, merge SHA `bb136111088a0721262a3746709f52dd9e9a0098`.
- Exact tested head commit: `60e4644d85ce6649958a43c3b1a21124d2306e1e`.
- GitHub Actions `KGM P5 Isolated Synthetic Runner`: run **40258632192**, SUCCESS.
- GitHub Actions full `CI`: run **40258632140**, SUCCESS; **1766 passed in 166.53s**.
- Earlier test run 40258396400 also proved synthetic network-disabled execution but companion CI failed due to prohibited old `actions/checkout@v4`. Fixed to v5, then both checks SUCCESS before merge.
- Actual network-disabled Docker container output:
```json
{"collection_status":"COMPLETED","evidence_count":2,"finding_count":1,"format":"KGM_O1_NETNS_SYNTHETIC_V1","network_interfaces":["lo"],"network_route_check":"NO_EXTERNAL_INTERFACE_OR_DEFAULT_IPV4_ROUTE","only_synthetic_data":true,"source_count":2,"status":"COMPLETED"}
```
- Container: `--network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 512m --cpus 1`, UID 65534, tmpfs 64 MiB, source mount read-only, and external 120-second command timeout. No production mounts, source credentials or live-source requests.

## Critic qualification

**PASS**: runtime-isolated fixed synthetic one-shot acquisition → evidence persistence → analysis, with resource budgets and no default IPv4 route on the GitHub-hosted ephemeral Docker runner. Source/evidence finding counts and no unsolicited dispatch verified by this fixed scenario.

**NOT PROVEN**: no packet-level egress trace, no IPv6 route/firewall forensic validation, and no broader adversarial container security assessment. The in-process interface check and Docker `--network none` are credible scoped proof, not an absolute statement that every possible channel is blocked.

**SHORTFALL**: direct `unshare --user --map-root-user --net` on `kgm-e4-owner-pilot` returned `Operation not permitted`. That production host remains unchanged. This GitHub success does **not** demonstrate the same namespace mechanism works on the production VM.

**OPEN**: explicit authenticated on-demand ingress, allowlisted live-source egress, actual GDACS/GDELT/Consilium response/freshness/provenance, critic after real execution, deployment parity, and owner production authorization.

## New phase decision

`P5_EPHEMERAL_OFFLINE_ISOLATION_PASS / P5_LIVE_ON_DEMAND_SHORTFALL / PRODUCTION_NO_GO`.

Next engineering priority: plan a separate *approved* GitHub Actions manual on-demand live pilot with strict source-only egress and owner authorization, after independent review; use no persistent watches, no production database or service restart. Do not substitute an unrestricted internet-connected job for the validated network-disabled fixture. Keep FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
