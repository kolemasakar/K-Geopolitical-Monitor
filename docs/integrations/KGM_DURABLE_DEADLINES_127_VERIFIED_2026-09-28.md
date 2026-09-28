# KGM durable deadlines and mixed recovery — verified checkpoint

Date: 2026-09-28. Exact tested code SHA `4e89cc6df2014e2d79c984547071aa860f021016`. Authorized isolated host `kgm-e4-owner-pilot`, checkout `/tmp/kgm-pr163-validation-AWDJxqb2/repo`. Full selected **22 exchange/research test modules: 127 passed in 1.58s**.

Added `research_deadline_registry_v1.py`: immutable, fsynced per-request synthetic deadline metadata with request-digest correlation, cooperative lock, policy checks, no implicit expiry if deadline absent. Durable request quota/recovery scans explicitly skip deadline metadata. Canonical `research_typed_workflow_v1.py` exposes `register_request_deadline` and `recover_registered`. Four new tests cover persisted deadline expiry, mixed workload (existing typed artifact reconciled while second request expires), immutable deadline conflict and quota isolation.

**Important limits:** This is explicit invocation, not an installed unattended daemon or production scheduler. A request and its deadline are still registered in two separate atomic steps; a crash between them leaves a pending request without a deadline, which safely remains pending but may need operational reconciliation. The deadline registry itself is not an authorization source. Lower-level legacy minimal fixture paths still exist; no real historical corpus coverage or cross-host transport has been validated.

Owner-only scope remains: malicious local human user is out of scope; accidental corruption, crash recovery and logical consumer separation remain. No production, live providers, HP-OMEN, K-Trader or Plugin PR #161 changes.

Next: document and gate legacy paths; test crash between admission and deadline registration, bounded restart recovery with mixed consumers, and explicit operational reconciliation of missing deadlines. Real exchange only after owner authorization.
