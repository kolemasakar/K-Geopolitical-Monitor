# KGM bounded recovery exact-SHA verification — 2026-09-28

Authorized KGM-only isolated checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo` on `kgm-e4-owner-pilot`; checked out exact code SHA `862881964b406edde37a2132efe8e8dbab40aefe`. Ran the 20 explicit exchange/research pytest modules using the existing venv; **120 passed in 1.40s**. The five new bounded recovery tests independently passed 5/5 in 0.11s.

RDC diagnostic observations: device was online; `pwd`, repository directory inspection, exact HEAD read, `git fetch`, `git checkout`, single-module tests and full tests all succeeded when invoked as individual direct calls. Previously attempted long compound calls had reported a safety block or timed out, and `/tmp/kgm-recovery-pass.txt` was absent on inspection. The tool did not provide a rule ID or reason, so the exact cause is **not established**. Short, individually auditable calls are a supported normal diagnostic workflow, not evidence of a security policy defect.

This verifies only synthetic offline bounded recovery and selected test modules; no production activation, real providers, K-Trader interaction, authenticated cross-host transport or malicious-local-user certification. Earlier pending-validation note is superseded for test status by this checkpoint.
