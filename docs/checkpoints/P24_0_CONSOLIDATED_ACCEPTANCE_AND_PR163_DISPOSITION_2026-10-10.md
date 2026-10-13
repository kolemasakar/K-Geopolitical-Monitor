# P24.0 Consolidated Acceptance and PR #163 Disposition — 2026-10-10

## Scope

Owner-approved Phase 24 planning, independent research quality, isolated owner-pilot ARM64 validation only. No production or cross-project activation.

## Verifiable baseline

- PR #163: draft/open, 366 commits, 178 changed files, head `f135014e2962907c76ea14bf3b10ddc7c288046c`, base `main`, CI #2900 SUCCESS.
- Isolated owner-pilot path `/tmp/kgm-pr163-validation-AWDJxqb2/repo` checked out at the exact PR head; ARM64 machine `kgm-e4-owner-pilot`.
- Research selected suite: 260 PASS / 5.46 s; focused suite: 37 PASS / 0.95 s.
- Initial full-suite collection: 12 errors due test-environment dependency and import configuration, not asserted product failures.
- Isolated test venv `/tmp/kgm-p24-validation-venv` created with project `.[test]` requirements, including psycopg 3.3.6 and httpx2 2.13.1. Product venv under `/opt/k-geopolitical-monitor` unmodified.
- Corrected full-suite command: `PYTHONPATH=.:src /tmp/kgm-p24-validation-venv/bin/python -m pytest -q`.
- Full-suite outcome is still pending independent final result and must not be reported PASS without an exit code and count.

## Readiness gate

`KGM_INDEPENDENT_RESEARCH_READY = PASS_WITH_P1_LIMITATIONS` remains unchanged. Existing tested features include durable processing, archive-backed no-provider historical replay, explicit generic correlation, independent-origin checks and explicit source-contribution/completeness semantics. Production readiness and unattended operation are separate gates.

## PR #163 disposition

**Decision: KEEP DRAFT, PLAN A SPLIT.** A 366-commit / 178-file mixed long-running change set spans independent-research engineering and prior multi-consumer/export preparation. Do not merge it en bloc into `main` during P24.0. Perform file/commit-level scope decomposition, separating:
1. Reproducible independent-research worker, schemas, tests, acceptance documents into reviewable research PR(s).
2. Contract proposal/validator and consumer-facing integration preparations into isolated integration PR(s), retaining Sentinel/K-Trader approvals as separate gates.
3. Administrative handoffs/checkpoints into appropriate documentation updates.

Only merge a scoped slice after exact-head CI, compatibility, reviewer sign-off and downstream boundaries are checked. Do not presume a split itself is already performed.

## Transition

P24.0 is **IN_PROGRESS** until full-suite acceptance, scope decomposition, cross-source consistency closure and formal owner gate. P24.1 preparatory research may begin in a separate planning track without marking P24.0 complete.

P24.1 draft acceptance target: inventory explicit official free source coverage by geopolitical domain; count validated mapping profiles by event and claim identity; prove two genuinely independent origins for each selected acceptance cohort; include false match/non-match and disagreement cases; preserve UNVERIFIED until explicit factual decision. Specify exact numeric coverage thresholds only after actual inventory, not by invention.

## Safety

No production/live or persistent unattended scheduling, no K-Sentinel or K-Trader integration, no public publication, no paid providers, shared runtime or HP-OMEN.
