# KGM Live Generic Mapping Adapterization and Archive Index Maintenance — 2026-10-10

## Decision

**LIVE_GENERIC_MAPPING_ADAPTERIZATION_AND_ARCHIVE_INDEX_MAINTENANCE = PASS**

Exact validated implementation SHA:
`0974796303333efbbb91381470bf15321cdde519`

Selected research/exchange regression:
**289/289 PASS in 5.21 s**

This checkpoint applies only to the bounded private owner-pilot independent-research path. It does not authorize production/live daemon operation, unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## 1. Live generic mapping adapterization

Added strict source-text mapping profiles.

A mapping profile:
- is bound to one exact source id;
- requires an explicit bounded phrase set;
- carries an explicit event descriptor;
- carries an explicit claim descriptor;
- attaches identity only if every required phrase is present;
- performs no fuzzy matching, synonym inference or NLP extraction.

Added public/free/read-only Moldova MFA source adapter:
- source id: `moldova-mfa`;
- origin group: `moldova-mfa`;
- allowlisted official hosts only;
- exact publication timestamp parsed from official Drupal metadata;
- bounded single-page retrieval;
- historical live backdating denied;
- optional strict generic mapping profile.

The NATO adapter now supports the same strict mapping-profile mechanism and permits an explicitly untagged bounded search when required.

## 2. Real owner-VM two-adapter mapping proof

Real event:
- 8 October 2026;
- NATO Deputy Secretary General Radmila Shekerinska;
- Moldova Deputy Prime Minister / Foreign Minister Mihai Popșoi;
- Chisinau;
- bilateral NATO–Moldova meeting.

Live official source paths:
1. NATO official public search/news endpoint.
2. Moldova Ministry of Foreign Affairs official public page.

Both sources were directly retrievable from the isolated owner VM.

Policy-bound live result:
- source runs:
  - Moldova MFA: 1 / OBSERVED
  - NATO: 1 / OBSERVED
- mapped observations: **2**
- shared event identity:
  `geo-diplomatic-20261008-ffea948e6757519f6b2f0ed34ebb62a4`
- shared claim signature:
  `claim-status-c25aaea1abcf75af8864c6bc15f5896a`
- explicit origin groups:
  - `moldova-mfa`
  - `nato`
- records: **1**
- merged two-source records: **1**
- record verification: `UNVERIFIED`

Typed result:
- `research_status = COMPLETE`
- `coverage = COMPLETE`
- `source_health = HEALTHY`
- result id:
  `result-07af79e47ef1294b0912c225`
- stage SHA:
  `7ed9ebeab557f034500474edb56d51f3478de89f3d9ec5466bbeefe0bf7d8b38`
- recovery pending: empty.

This is the first fully live owner-VM generic diplomatic mapping cycle across two independent official source adapters.

The merged record remains UNVERIFIED. Shared mapping does not auto-promote factual verification.

## 3. Archive index maintenance

Added automatic index maintenance after each durable CURRENT archive append.

Normal maintenance behavior:
- initial/missing index → bounded REBUILD;
- exactly one new archive entry → APPEND;
- already synchronized index → CURRENT;
- unexpected stale/corrupt/drift state → bounded authoritative REBUILD;
- maximum managed entries remains bounded.

The immutable evidence archive remains authoritative.

The historical selector continues to:
- prefer verified index fast path;
- verify archive/index manifest equality;
- load and validate the selected authoritative archive artifact;
- fall back to bounded authoritative scan when index is missing/stale/corrupt;
- fail closed above the fallback scan bound until index repair/rebuild.

## 4. Live archive-index acceptance

The live two-adapter CURRENT cycle automatically produced:
- archive index entries: **1**
- subsequent maintenance state: `CURRENT`

A historical snapshot lookup for the same source policy returned:
- selection path: `INDEX`
- selected historical snapshot SHA:
  `9638de249500d75bbbbc4358ff294835e0c0b25b420a5b57a9c359c42af0f1a6`

Deterministic tests also prove:
- automatic worker index creation;
- missing index repair;
- one-entry incremental APPEND;
- corrupt index bounded rebuild;
- stale index fail-closed for indexed-only selection;
- stale/missing index authoritative fallback for fast selector.

## 5. Validation

Targeted mapping/source/index/worker suite:
**35/35 PASS**

Selected research/exchange regression:
**289/289 PASS in 5.21 s**

## Readiness interpretation

The previous live-adapter mapping limitation is closed.

Current owner-pilot state:
`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS`

Remaining quality limitations are no longer blockers for bounded owner-pilot readiness, but include:
- broader generic mapping coverage across more political/military/economic event families;
- more than two independent origin groups where strategically useful;
- automated index retention execution remains intentionally disabled; retention is still plan-only;
- no unattended scheduler or production daemon.

## Next technical track

`MULTI_DOMAIN_GENERIC_MAPPING_SCALE_AND_RETENTION_POLICY`
