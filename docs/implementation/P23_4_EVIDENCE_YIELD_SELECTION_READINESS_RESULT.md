# P23.4 — Evidence-Yield Coverage Expansion — Selection Readiness

Date: 2026-09-21
Status: `PRESELECTION_COMPLETE / OWNER_DECISION_REQUIRED_FOR_EXPANSION`

This is a **preparatory package**, not P23.4 gate closure.

## Deterministic readiness result

The governed 13-candidate Wave-B inventory resolves into:

- 2 already repository-active paths: OFAC and White House;
- 1 path ready for an owner-gated activation revalidation: `uk-sanctions-list-en`;
- 1 path still transport-blocked: `russian-government-news-ru`;
- 3 exact-taxonomy fixture-build-qualified paths that still require rights-review preparation: `cctv-news-zh`, `anadolu-en`, `trt-haber-tr`;
- 4 paths requiring rights review;
- 2 paths requiring both taxonomy/governance and rights review.

## Owner-gate candidate

`uk-sanctions-list-en` is the only candidate that P23.1 moved to `READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION`.

Its expected structural contribution is limited to:

- required coverage in `global.en.sanctions_regulatory`;
- an additional explicit institutional provenance/origin group distinct from OFAC.

This is **not** factual independence credit and does not establish corroboration.

## Preparation cohort

The lowest unresolved governance shape among the remaining unactivated candidates is:

- `cctv-news-zh` — `east_asia.zh.national_media`;
- `anadolu-en` — `global.en.wire_service`;
- `trt-haber-tr` — `black_sea.tr.national_media`.

They remain blocked on automated-collection rights review before fixture/onboarding work is treated as activation-ready.

## Gate state

`P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED` is **not validated** by this package.

Current canonical position remains P23.3 validated. Source activation, repository activation, runtime mutation, or acquisition-limit relaxation remains zero.

P13.5/P13.6 remain factual-verification authority.
