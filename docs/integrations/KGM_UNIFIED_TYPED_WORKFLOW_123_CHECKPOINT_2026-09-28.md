# KGM unified typed workflow — isolated 123-test checkpoint

Date: 2026-09-28. Exact tested code SHA `3fb70ea56f07b0b8242acee5a1282893f5bc7268`. Authorized isolated host `kgm-e4-owner-pilot`, checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo`. Full selected 21-module exchange/research test run **123 passed in 1.46s**; new workflow's three tests independently passed **3 in 0.11s**.

Added `research_typed_workflow_v1.py`, a canonical **offline synthetic fixture-facing** facade around existing durable admission, transitions, immutable typed completion and bounded recovery. It introduces no provider, scheduler, HTTP listener or cross-host connection. Legacy minimal fixture modules remain for compatibility but are not called by this facade. Tests cover complete lifecycle, idempotent admission and pending quota.

Owner-only threat model remains in force; no hostile local human-user certification. Existing accidental integrity checks remain. This is **not** a production-ready integration: trusted caller identity is still not authenticated; lower-level legacy paths remain callable; real corpus coverage and source provenance are unverified; actual K-Trader exchange awaits separate owner authorization. No production, live providers, Plugin PR #161 or K-Trader modifications.

Next engineering gates: isolate or explicitly deprecate unsafe legacy entry points; define trusted local worker invocation with durable deadline registry rather than caller-supplied ephemeral deadlines; add mixed-workload crash/expiry tests and independent actual-corpus verification when authorized.
