# KGM P5.3 owner-initiated manual offline research acceptance — 2026-10-26

**Gate:** `P5_3_OWNER_MANUAL_OFFLINE_REQUEST_PASS / P5_4_LIVE_SOURCE_OPEN / P5_5_REAL_REPORT_OPEN / PRODUCTION_NO_GO`

## Attested GitHub evidence

Owner independently dispatched GitHub Actions workflow `.github/workflows/p5-owner-on-demand-offline.yml` on `main`, run [40262556479](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40262556479), event `workflow_dispatch`, GitHub actor `kolemasakar`, source SHA `160cf3d1b78d8d663ad9b19057cef4ac154d8326`. Creation/start `2026-10-26T03:08:13Z`. GitHub run conclusion: **SUCCESS**; job ID `121377848960`, job `owner-offline-request`, **SUCCESS**.

All phases SUCCESS: checkout without persisting credentials; authorize actor/repo/main/event and bounded request; pull public image; execute synthetic request in no-network container; validate response against request ID and SHA-256 digest. Exact log markers:

- `P5_OWNER_OFFLINE_AUTHORIZED: request digest validated; no raw topic printed`
- `P5_OWNER_OFFLINE_REQUEST_PASS: authorized owner, isolated, synthetic, one-shot`

Aggregates from actual run:
```json
{
  "format": "KGM_O1_NETNS_SYNTHETIC_V1",
  "collection_status": "COMPLETED",
  "evidence_count": 2,
  "finding_count": 1,
  "network_interfaces": ["lo"],
  "network_route_check": "NO_EXTERNAL_INTERFACE_OR_DEFAULT_IPV4_ROUTE",
  "only_synthetic_data": true,
  "request_id": "owner-test",
  "source_count": 2,
  "status": "COMPLETED",
  "topic_sha256": "0225b8b0ed2f16c0726c06fa3a127f13b6819c84585706830f65320b5bbcde24"
}
```

The digest is a control value, not raw topic content. Manual run is separate from CI and establishes actual owner-request execution on GitHub-hosted runner.

## Critic

**PASS within bounded scope:** GitHub Actions owner identity context, one explicit manual trigger, payload checksum matching, synthetic collection + analysis, read-only isolated Docker with `--network none`, no observed external network interface/default IPv4 route, no job-level source execution beyond fixed synthetic sources.

**Known limitations:** GitHub Actions account RBAC and digest matching are not a general-purpose ChatGPT API authorization channel; no claim of real source reachability, independent geopolitical evidence, live freshness or user-facing report. The worker uses a temporary local fixture watch inside disposable SQLite only. This does **not** turn on either persistent production watch.

**OPEN:** P5.4 real bounded GDACS/GDELT/Consilium collection and independent content validation; P5.5 real end-to-end report plus Critic; externally constrained egress and separate owner authorization for live use; production loaded code remains unattested and no production deployment was made.

**Operational policy remains:** ON_DEMAND_ONLY / FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
