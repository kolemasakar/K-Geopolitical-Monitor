# KGM-only crash reconciliation: implementation pending host verification

Date: 2026-09-28. Owner direction: KGM work independently; no K-Trader interaction.

Branch `integration/kgm-multiconsumer-export-20260928`, implementation/test HEAD `ef5bcf61087595952a79fc850973c60907be7e54` in draft PR #163.

Added `research_completion_v1.py`: trusted local offline synthetic worker publishes a strict typed immutable correlated result first, then records durable COMPLETE/PARTIAL. Recovery-only mode validates the existing artifact, request digest, correlation, current consumer policy and typed result before advancing a still-PROCESSING request. Missing/corrupt/conflicting artifacts fail closed. Cooperative POSIX lock serializes participating writers. This is **not an atomic multi-file transaction**, authenticated API or production worker.

Added `tests/test_research_completion_v1.py` with six synthetic tests: normal completion/replay, crash between artifact publication and terminal transition, missing artifact, conflicting replay, revoked consumer policy and PARTIAL reconciliation.

**Verification status: UNVERIFIED** for this new HEAD: authorized KGM remote process calls timed out, including a later log read. Do not claim 107 passed or that new tests passed. Last confirmed result was **101 passed in 1.00s** at prior code SHA `d085cc9622f9f20ca358a56ee106d95f98e3bdd8`. Rerun the explicit 17 exchange/research test modules on exact new SHA before gate advancement.

Further unresolved issues: legacy minimal fixture path and typed durable path coexist; lifecycle may be independently advanced to COMPLETE without artifact via lower-level function; malicious local actor and root symlink races remain out of scope; no real historical corpus or live source verification; no cross-host exchange, no production activation, no Plugin PR #161 change.
