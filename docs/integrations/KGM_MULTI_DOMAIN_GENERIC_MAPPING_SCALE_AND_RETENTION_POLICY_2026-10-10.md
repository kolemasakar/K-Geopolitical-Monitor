# KGM Multi-Domain Generic Mapping Scale and Retention Policy — 2026-10-10

## Decision

**MULTI_DOMAIN_GENERIC_MAPPING_SCALE_AND_RETENTION_POLICY = PASS**

Exact validated implementation SHA:
`890ee4755d68c995e532b3518a43894d368455c0`

Selected research/exchange regression:
**296/296 PASS in 5.51 s**

This checkpoint applies only to the bounded private owner-pilot independent-research path. It does not authorize production/live daemon operation, unattended scheduling, Sentinel transport, K-Trader integration, paid providers/fallbacks, shared runtime, public Plugin publication or HP-OMEN use.

## 1. Multi-domain live generic mapping

The strict profile-based generic mapping path has now been exercised across three non-earthquake geopolitical families using directly retrievable official sources on the isolated owner VM.

### POLITICAL

Event:
- 8 October 2026;
- United Kingdom / Germany;
- Kensington Treaty ratification in Berlin.

Official source paths:
- GOV.UK;
- German Federal Government.

Live result:
- mapped observations: 2;
- shared event identity:
  `geo-political-20261008-60e96363677f4e8432eb15b8545474cc`;
- shared claim signature:
  `claim-status-315209d4c271b5e0b21af1c92fb70cee`;
- origin groups:
  - `uk-government`
  - `germany-federal-government`;
- one merged two-source record;
- record remains `UNVERIFIED`;
- result: `COMPLETE / COMPLETE / HEALTHY`;
- result id:
  `result-f54e9fdd4f015e12430a499d`;
- stage SHA:
  `d1bca1cf13fe4b51b1edb6b18ce586059d7f17a4ceca022a463318b0c493e390`.

### MILITARY / SECURITY

Event:
- 8 October 2026;
- United Kingdom / Germany;
- counter-hybrid-threat partnership.

Official source paths:
- dedicated GOV.UK announcement;
- German Federal Government joint statement.

Live result:
- mapped observations: 2;
- shared event identity:
  `geo-military-20261008-fa80e36beaf4e1a36c2cc6466e0fdc05`;
- shared claim signature:
  `claim-status-4a0122fabbad5f8e34cd1e57f38b08d0`;
- origin groups:
  - `uk-government`
  - `germany-federal-government`;
- one merged two-source record;
- record remains `UNVERIFIED`;
- result: `COMPLETE / COMPLETE / HEALTHY`;
- result id:
  `result-b37493ff43347c8780f68094`;
- stage SHA:
  `5e7d7e1488d3ca6516ea6380f6320be3655a231b0043b139fce835c6af928b1a`.

### ECONOMIC

Event:
- 2 October 2026;
- G7 leaders;
- global energy security and market stability coordinated measures.

Official source paths:
- GOV.UK;
- French Presidency / Elysee.

Live result:
- mapped observations: 2;
- shared event identity:
  `geo-economic-20261002-40c0e8fd72cc8afb60ad2803de8104a7`;
- shared claim signature:
  `claim-status-ecfc2dd373ce005955fc0ca9c00c0c90`;
- origin groups:
  - `uk-government`
  - `france-presidency`;
- one merged two-source record;
- record remains `UNVERIFIED`;
- result: `COMPLETE / COMPLETE / HEALTHY`;
- result id:
  `result-866eecec8d3658dc6151728d`;
- stage SHA:
  `d1f902e764ee9000f52cfc3b76bcdd568ab63a37a105b7b012ded66075a0c1d3`.

All three families used exact source-specific phrase profiles. No fuzzy matching, semantic model inference, or automatic factual verification was introduced.

## 2. Additional official page adapters

Added bounded, public/free/read-only strict-profile adapters for:
- GOV.UK — source id `govuk-official`, origin `uk-government`;
- German Federal Government — source id `germany-federal-government`;
- French Presidency / Elysee — source id `france-presidency`.

Each adapter:
- allowlists official HTTPS hosts;
- parses publication metadata from the official page;
- bounds response size;
- denies historical live backdating;
- optionally applies a strict source-bound mapping profile.

## 3. Retention policy

Added:
`kgm.research.archive-retention-policy.v1`

Policy fields:
- consumer id;
- keep-latest floor;
- minimum age in days;
- maximum delete count;
- maximum delete fraction.

Safety properties:
- retention is never automatic;
- default execution is dry-run / no deletion;
- actual deletion requires explicit `allow_delete=True`;
- maximum delete fraction is capped at 50%;
- maximum delete count is bounded;
- only indexed archive filenames are candidates;
- symlink/non-file targets are denied;
- archive index is repaired after a successful deletion set.

## 4. Isolated destructive acceptance

A real destructive retention acceptance was performed only inside the temporary isolated owner-pilot root:

`/tmp/kgm-multidomain-scale-owner-pilot`

It did **not** touch production data.

Before retention:
- archive index entries: 3.

Policy:
- keep latest: 2;
- minimum age: 0 days for this controlled acceptance;
- maximum delete count: 1;
- maximum delete fraction: 0.5.

Plan:
- delete candidates: 1.

Execution:
- explicit delete flag: true;
- deleted archive snapshots: 1;
- index entries after execution: 2;
- index repair succeeded;
- recovery pending: empty.

This proves the guarded execution path while preserving the production boundary that retention execution is not automatically enabled.

## 5. Query-window finding

During the first military live run, the GOV.UK announcement was legitimately excluded because its exact publication timestamp converted to `2026-10-07T23:01:02Z`, while the initial query window began at `2026-10-08T00:00:00Z`.

The worker correctly treated an invoked adapter returning no observations as a healthy EMPTY source run under the existing contract. The query window was corrected to include the actual publication timestamp, and the military two-source mapping then passed.

No change was made to the approved healthy-empty source semantics.

## 6. Validation

Targeted profiled-source / retention / worker suite:
**19/19 PASS**

Full selected research/exchange regression:
**296/296 PASS in 5.51 s**

## Readiness interpretation

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS` remains valid.

No P1 blocker prevents bounded owner-pilot research. Remaining work is quality assurance and scale, especially:
- broader mapping-profile catalog coverage;
- explicit retention defaults for long-running owner-pilot archives;
- quality audit of false merge / false split / false COMPLETE / false VERIFIED resistance across the expanded source portfolio.

## Next technical track

`INDEPENDENT_RESEARCH_QUALITY_AUDIT_V1`
