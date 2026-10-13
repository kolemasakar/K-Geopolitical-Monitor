# P24.1 — Source Mapping, Independence and Coverage Evidence — Checkpoint 1

Status: P24_1_IN_PROGRESS; TARGETED_REGRESSION_PASS
Recorded: 2026-10-13
Scope: independent KGM research, isolated ARM64 owner-pilot, no production changes.

## Source baseline
- Eleven dedicated source adapters inventoried on independent research PR #163 at f135014e2962907c76ea14bf3b10ddc7c288046c.
- Ten HTTP200 transport observations (six earlier probes, four from Oct 13) and one GDELT TLS-handshake timeout on Oct 13. These are transport checks, not a consistent single-time snapshot, nor source parser/semantic acceptance.
- See docs/integrations/P24_1_SOURCE_TRANSPORT_COVERAGE_AUDIT_2026-10-13.md for details and mapping by domain.

## Exact research HEAD targeted test execution
- Host: kgm-e4-owner-pilot, architecture ARM64; isolated checkout /tmp/kgm-pr163-validation-AWDJxqb2/repo.
- Exact checked-out code SHA: f135014e2962907c76ea14bf3b10ddc7c288046c.
- Isolated Python venv: /tmp/kgm-p24-validation-venv.
- Selected test modules:
  - test_research_source_adapter_v1.py
  - test_research_source_consilium_v1.py
  - test_research_source_ecb_v1.py
  - test_research_source_gdelt_v1.py
  - test_research_source_moldova_mfa_v1.py
  - test_research_source_nato_v1.py
  - test_research_source_profiled_official_pages_v1.py
  - test_research_source_resilience_v1.py
  - test_research_generic_mapping_profile_v1.py
  - test_research_generic_mapping_real_v1.py
  - test_research_corroboration_v1.py
  - test_research_result_v3_completeness_v2.py
- Result: **65 passed in 0.85 s**, exit code 0.

## Epistemic acceptance boundary
Passing adapter/corroboration tests proves conformance to selected tested fixtures, not health of every actual live public source. The ability to parse a public statement must not be confused with independent confirmation of the statement's contents.

For further P24.1 acceptance:
1. Execute isolated source-specific bounded fixture coverage of timestamps, malformed/empty/429/TLS timeout and cooldown distinctions.
2. Cover at least one same-origin chain and one independently originated disagreement case in which UNVERIFIED remains preserved.
3. Document domain/geography coverage gaps explicitly and prioritize safe, free and official sources on evidence value (not publisher count).
4. Verify complete contract compatibility with the independent research implementation before merging scoped slices from PR #163.
5. Run new code deltas through CI and ARM64 exact-head tests before accepting the corresponding P24.1 gate.

## Restrictions
- P24.1 is not completed by this checkpoint.
- PR #163 remains Draft/unmerged.
- Canonical Phase 23 gate remains preserved until its independent closure.
- No new owner-pilot source activation, persistent unattended operation, production deployment, public Plugin sharing, paid providers or cross-project integration.
