# Project Checkpoint — 2026-10-10 — Real Generic Mapping and Archive Index Fast Path

## Gate

`REAL_GENERIC_EVENT_MAPPING_AND_INDEX_FAST_PATH = PASS_WITH_LIVE_ADAPTER_MAPPING_LIMITATION`

Validated implementation SHA:
`8fef756bcaeff9514718e579f0dfa1fc23328f70`

## Real mapping acceptance

Official source pair:
- NATO official news;
- official website of the President of Ukraine.

Common event:
- 24 September 2026;
- Mark Rutte / Volodymyr Zelenskyy;
- New York;
- bilateral diplomatic meeting.

Deterministic result:
- event match: true;
- claim match: true;
- independent-origin candidate: true;
- origin groups: `nato`, `president-ukraine`;
- event identity: `geo-diplomatic-20260924-2afad3e80899d4325c7776b7c596737d`;
- claim signature: `claim-status-c25aaea1abcf75af8864c6bc15f5896a`;
- automatic verification: false.

Direct owner-VM retrieval:
- NATO: available;
- President of Ukraine official page: HTTP 403.
Public-web retrieval of the official President page succeeded, so semantic mapping is validated at source-fact level, not yet as a fully live two-adapter owner-VM cycle.

## Archive fast path

- verified index preferred;
- immutable archive authoritative;
- missing/stale/corrupt index -> bounded authoritative scan fallback;
- default fallback bound: 10,000;
- fail closed above fallback bound pending index rebuild.

On-disk benchmark:
- 1k: scan 2.0836 s, indexed 0.0211 s, 98.89x;
- 10k: scan 21.3310 s, indexed 0.1952 s, 109.25x;
- selected SHA identical.

## Regression

`278 passed in 5.10s`

## Readiness

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

Next:
`LIVE_GENERIC_MAPPING_ADAPTERIZATION_AND_ARCHIVE_INDEX_MAINTENANCE`

No production daemon, unattended scheduler, Sentinel, K-Trader, paid provider, shared runtime, public Plugin or HP-OMEN activation is authorized.
