# P24.0 — Baseline Acceptance and P24.1 Entry

Decision: **P24.0 BASELINE ACCEPTED WITH DOCUMENTED BOUNDARIES**.
Date: 2026-10-13
Scope: documentation/planning PR #164, exact-head research reference PR #163, and isolated owner-pilot validation.

## Evidence
- PR #164, HEAD `1296808742c058c239921b5f62a70b24c62871d9`: GitHub Actions CI run #2980 SUCCESS, **1409 passed in 121.07 s**.
- PR #163, independent research implementation HEAD `f135014e2962907c76ea14bf3b10ddc7c288046c`: CI run #2900 SUCCESS; isolated aarch64 complete research branch suite **1722 passed in 444.89 s**, earlier targeted research suite 260 passed.
- Earlier #164 historical-test mismatch from incorrectly promoting `roadmap.current_position` to Phase 24 was corrected by **preserving Phase 23 canonical current position** while recording Phase 24 as owner-approved parallel work.
- M24.0–M24.3 private Plugin migration separately owner-approved; not production readiness.
- Original Phase 23 P23.4 gate not closed by Phase 24 planning; preserved as `PHASE_23_P23_3_CORROBORATION_EVIDENCE_RELATION_POPULATION_VALIDATED`.

## Acceptance boundary
- **P24.0 documentation/baseline gate: PASS_WITH_BOUNDARIES**. This does not imply the 366 commits / 178 files of draft PR #163 are merged to main.
- PR #163 remains independent, draft and awaiting file/commit-level split.
- PR #164 is eligible for controlled docs merge after final exact-head CI on the closure commit; no bypass of CI. If merge fails, do not report it merged.
- Research readiness remains `PASS_WITH_P1_LIMITATIONS`; full production readiness not established.
- No production/live, unattended activation, paid providers, public publication, cross-project integrations or deployment modifications.

## P24.1 entry
Proceed with measured source/region/domain coverage, free official-source mapping profiles, response freshness, origin-group independence, cooldown/transport failure classification and exact-head reproducible test fixtures. Source presence or HTTP200 alone never counts as parsed usable evidence.
