# P24.1 — African Union Single-Article Adapter Pilot

Status: CI_PASS_WITH_LIVE_RUNTIME_PENDING / NO_SOURCE_ACTIVATION
Reference: PR #172 stacked on PR #171, which itself is stacked on draft research PR #163.
Recorded 2026-10-13; no production/main changes.

## Grounded page observation
Public African Union original document: https://au.int/en/pressreleases/20261011/auc-chairperson-statement-tragic-loss-migrant-lives-coast-djibouti
Public page shows its original AU Commission Chairperson statement with date Oct 11, 2026, and body text. This validates the document exists, but not exact raw HTML parsing on the owner-pilot VM.

## Candidate and adapter contracts
- African Union registered as a discover-only candidate, no enabled shared source.
- New adapter is **opt-in by direct explicit URL** and allows only HTTPS au.int/www.au.int /en/pressreleases/YYYYMMDD/slug.
- Only official publisher attribution is credited; no verified battlefield/independent factual corroboration.
- Day of publication comes from URL and must also appear in page text. A 00:00Z day anchor is NOT known exact publication time.
- Transport TimeoutError/OSError yields explicit UNAVAILABLE; malformed headings, dates, origin, or oversized responses fail closed.
- Historical-as-of queries cannot infer that information was available earlier than the pilot's first verified observation.
- The HTML/date parsing uses a narrow headline+date check; webpage design variability and dynamic structure still require an actual owner-pilot direct-fetch acceptance test.

## Automated tests
- Regional candidate code PR #171 CI #3058: 1765 passed in 115.84s.
- AU parser code PR #172 CI #3062: 1778 passed in 125.13s.
- Additional local independent ARM64 check for the exact PR #172 head is PENDING due to remote access timeout, NOT claimed completed.

## Required before acceptance/merge
1. Restore read-only VM access and save bounded AU live-response parser result including source date and exact import path.
2. Run exact-head owner-pilot ARM64 full suite with PYTHONPATH to checked-out source.
3. Review potential false dating from generic page/nav text; restrict to AU article date metadata if necessary.
4. Keep PR #172 and #171 draft/unmerged until those evidence gates are satisfied.
5. After actual acceptance: record source capability and independent-origin coverage, still no production/paid/public/other-project activation.
