# KGM O1 P4 — Source evidence, GDACS and isolated execution addendum

Date: 2026-10-25. Owner mode: **ON_DEMAND_ONLY**.

## Scientific/source accuracy

Official GDACS material documents free API access and the RSS feed `https://www.gdacs.org/xml/rss.xml`. Reference: https://www.gdacs.org/Documents/2025/GDACS_API_quickstart_v1.pdf and https://www.gdacs.org/documents/2025/GDACS_MHEWS_guide.pdf. No live GDACS endpoint request or current reliability verification has been performed in this PR.

- New `GdacsRssAdapter` consumes bounded RSS XML through an injected transport, returns provenance-tagged `LiveSourceItem`, extracts parseable `pubDate` and does not activate itself.
- GDACS is an alert aggregation source, not independently validated ground truth.
- New `assess_evidence` uses explicit publication timestamps; missing timestamps produce UNKNOWN, stale dates STALE, future-dated items INVALID. Fetch time is not used as publication time.
- Host-count and source-ID count are NOT proof of independent institutions, syndication chains, or corroboration. Ownership independence stays `NOT_ATTESTED_OWNERSHIP_OR_SYNDICATION`.
- GDELT DOC 2.0 returns discovery publisher links; it is not equivalent to independent original-source evidence. Consilium RSS is official institutional output. GDACS RSS covers natural-disaster alerts, not general-purpose geopolitical claims.

## Isolation defense in depth

`offline_isolation.py` constructs a fixed Linux subprocess inside an `unshare --user --map-root-user --net` namespace. The hard policy is to fail closed if `unshare` is missing, not permitted by host kernel, or child exits non-zero. Child payload `offline_isolation_child.py` is *fixed synthetic-only* and returns aggregate JSON. Resource limits: 20-second wall timeout, CPU soft 10s/hard 12s, virtual memory 512 MiB, 1 MiB file size, 64 file descriptors; 4 KiB stdout cap. Credentials are not forwarded through the explicit environment. No production paths are read.

The tests assert command construction and error handling with mocks. **An actual working network namespace is not established unless separately executed under a permitted isolated CI runner and supported by recorded evidence.** No request for service restart, setuid changes, new capabilities, production network or host permission.

## Acceptance matrix

| Gate | Meaning | Status |
|---|---|---|
| Exact HTTPS GDELT, Consilium, GDACS endpoint matching | Bounded network policy tests | PENDING CI |
| GDACS RSS parsing | Synthetic XML only | PENDING CI |
| Publication-time freshness | No inferred publisher independence | PENDING CI |
| Fail-closed netns runner | Unit-tested construction only | PENDING CI |
| Real netns startup | Actual namespace creation | NOT EXECUTED |
| Real GDACS/GDELT/Consilium request | Network source retrieval | NOT EXECUTED |
| User-authenticated request entrypoint | Production integration | NOT IMPLEMENTED |
| Full live source-independent corroboration | Multi-source provenance | OPEN |

**No production deployment or live collection is authorized by this PR.** FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
