# P21.0 — Global Baseline Expansion Evidence

Date: 2026-09-16
Status: `DRAFT_GLOBAL_BASELINE_READY_FOR_REVIEW`
Authority: non-operative policy design evidence

## Decision implemented

Owner selected `EXPAND` for P21.0 before policy approval.

The original v0.1 draft was expanded into `0.2-draft-global-baseline` rather than being approved in its narrower form.

## Expansion result

- Target cells: 33
- Geography scopes: 20
- Language labels: 15
- Default requirement state: `UNSET`
- Authority state: `DRAFT`

The baseline now explicitly represents:

- Ukraine, Russia, EU/Europe, Central Europe and Black Sea;
- Middle East;
- East Asia;
- Southeast Asia;
- South Asia;
- Central Asia;
- Caucasus;
- North Africa;
- Sub-Saharan Africa;
- North America and the United States;
- Latin America and Brazil;
- Oceania;
- global cross-cutting wire, sanctions/regulatory, economic/energy, research and public-OSINT roles.

## Design rules preserved

1. A target cell is policy, not evidence.
2. An unobserved target is not an invented source.
3. `multi` is transitional where used and does not prove language completeness.
4. English-language regional coverage does not automatically replace local-language coverage.
5. `GLOBAL` is not an exhaustive-world-coverage assertion.
6. Independent-origin thresholds remain separate from publisher/domain/language counts.
7. P20 historical evidence remains unchanged.
8. No target cell becomes a canonical gap until the policy is separately approved.

## Safety boundary

This expansion performs no live-source onboarding, ingest change, runtime deployment, service restart, paid-provider activation, shared-runtime activation, `migration 033`, production activation, or external publication.

## Gate state

`P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED` remains `NOT_YET_GRANTED` because the global manifest remains `authority_state = DRAFT`.
