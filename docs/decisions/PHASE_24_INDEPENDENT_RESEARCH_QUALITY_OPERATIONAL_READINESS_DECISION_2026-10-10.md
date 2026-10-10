# Phase 24 — Independent Research Quality & Operational Readiness

Date: 2026-10-10
Decision: APPROVED BY OWNER
Status: P24.0 IN PROGRESS
Project: K-Geopolitical Monitor

## Objective

Move bounded independent owner-pilot research readiness toward a technically validated foundation for possible later operation, without declaring or activating production.

## Approved sequence

1. **P24.0 — Baseline and consolidated exact-HEAD acceptance.** Confirm PR #163 identity, branch, source/test baseline, exact-head CI and isolated ARM64 checks; assess source-of-truth alignment, readiness and PR disposition.
2. **P24.1 — Source, mapping-profile and research-quality coverage.** Expand official free sources, explicit controlled event/claim mappings, negative cases, independence/origin handling, and multi-domain corroboration; no heuristic fact verification.
3. **P24.2 — Unattended reliability and crash recovery engineering.** Design and validate owner-isolated scheduling, durable recovery, bounded retries and fail-closed safety in test mode before any persistent unattended activation.
4. **P24.3 — Retention, resource controls and observability.** Validate guarded retention execution, audit visibility, limits, health and controlled rollback; destructive tests remain isolated.
5. **P24.4 — Final readiness audit and distinct owner production decision.** Publish acceptance with explicit known limitations, production requirements and an independent owner approval gate; no implicit deployment.

## Baseline evidence (isolated owner-pilot)

- PR #163 active recovery branch: `integration/kgm-multiconsumer-export-20260928`.
- Exact validated HEAD on 2026-10-10: `f135014e2962907c76ea14bf3b10ddc7c288046c`.
- GitHub CI #2900: SUCCESS at that HEAD.
- On `kgm-e4-owner-pilot` ARM64, selected research regression: **260 passed in 5.46 s**; focused tests: **37 passed in 0.95 s**.
- Existing owner-pilot readiness gate: `PASS_WITH_P1_LIMITATIONS`; no unconditional readiness promotion authorized.
- Isolated checkout path: `/tmp/kgm-pr163-validation-AWDJxqb2/repo`; production path `/opt/k-geopolitical-monitor` not modified.

## Strategic and branch boundaries

- Legacy Phase 23 / P23.4 acceptance status is preserved; Phase 24 owner approval does not retroactively close Phase 23 gates.
- PR #163 remains a separate draft integration/research carrier, NOT auto-merged; decide split versus merge after explicit scope assessment.
- Implementation on PR #163 is not represented as already merged into `main`.
- Research-quality work, production-readiness work and cross-project integration are separate gates.
- No production/live daemon activation, new persistent unattended scheduler, K-Sentinel/K-Trader integration, shared runtime, paid providers, public Plugin publication or HP-OMEN use.
- Mainline Phase 24 planning is tracked separately from PR #163 until its scope and integration gates are resolved.

## P24.0 exit criteria

- Current source-of-truth/ROADMAP/implementation-test alignment reported.
- All selected exact-HEAD checks pass or limitations documented; full-suite verification is a distinct required check before release.
- PR #163 merge/split/draft decision recorded without bypassing controls.
- Research readiness unchanged unless new owner-approved acceptance justifies advancement.
- P24.1 acceptance plan and measurable coverage targets proposed; no production claims.
