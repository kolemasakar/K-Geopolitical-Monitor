# P24.1 — Live Parser and Negative-Origin Evidence
Status: TARGETED_EXACT_HEAD_PASS / FULL_ARM64_AND_CI_PENDING
HEAD (before this doc): 132e162c2289d15f76154a7eac346e8c2a2ddd74

## Bounded live read-only parser check
Official source: https://www.bundesregierung.de/breg-en/news/chancellor-merz-uk-pm-burnham-2456444
Owner-pilot VM retrieval: HTTP 200, approximately 96.9 KB HTML.
BEFORE FIX: existing Bundes adapter raised ValueError: publication timestamp missing. Real page has no time datetime tag; synthetic fixture incorrectly assumed one.
AFTER FIX: article-header list item containing Thursday, 8 October 2026 is recognized with strict fallback. Extracted date anchor 2026-10-08T00:00:00Z; summary text includes Kensington Treaty; 7456 characters extracted. Module import confirmed to refer to the new branch worktree.
PRECISION WARNING: 00Z is an anchor for publisher-supplied day; NOT an exact publication clock time. Do not claim intra-day freshness has been proven.

## Negative and source-bound mapping cases
- Moldova MFA Romanian/diacritic-aware phrase mapping, exact binding to source identity, offset-aware timestamp.
- Missing exact phrase and transliteration mismatch fail closed.
- UK article missing/naive/invalid timestamp rejected.
- TLS/timeout and OSError become explicit UNAVAILABLE, not SUCCESS or false empty.
- Same-origin two-publisher republication cannot become independent evidence.
- Different-origin two-publication match remains only an independent-origin candidate, NOT fact verification.
- Different-origin contradictory claims are not merged.
- Different event dates do not merge; duplicate publisher rejected.
- German public-date article-header fallback and ambiguity/weekday negative cases.
- Local fixture HTML error caused five initial test failures and was corrected.
- A venv editable-install import drift initially pointed tests to the older research checkout; these results were not accepted. Corrected using an explicit PYTHONPATH to the new-branch src and tests; focused suite 29 PASS in 0.50s.

## Status and restrictions
Full exact-head ARM64 regression and GitHub CI remain acceptance gates. This is draft research code on PR #166 stacked on PR #163, not canonical main. No production, paid provider, public Plugin, unattended monitoring, source activation or cross-project change.