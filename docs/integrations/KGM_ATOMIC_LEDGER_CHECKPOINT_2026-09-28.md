# KGM atomic producer ledger checkpoint — 2026-09-28

Issue #162 / draft PR #163; coordination Sentinel PR #26 and K-Trader PR #87.

Exact code SHA `817af5b372aa6411dcb553fea308d9a27f92f1f8` tested in a disposable KGM-host clone using the KGM venv. Seven synthetic test modules: **47 passed in 0.46s, exit 0**. No production process, DB, credentials or host configuration modified.

New isolated candidate `exchange_ledger_atomic_v1.py` uses a dedicated cooperative `flock` for readers/writers, writes a complete JSONL snapshot to a temporary file, fsyncs and atomically replaces the ledger, then fsyncs its parent. Tests verify replay/idempotency, two batches, torn input rejection and a simulated replacement failure preserving the prior ledger. The earlier append-only `exchange_ledger_v1.py` remains present only for comparison and is not approved for deployment.

**Important limitations:** atomic file replacement protects the old/new ledger snapshot but cannot prove resilience to real power loss on all filesystems. The lock requires all cooperating readers and writers to use this module. Ledger retention/pruning and an authenticated private cross-host receiver remain unimplemented. The existing strict exchange validator does not itself authorize release of real data. No live exporter or K-Trader transport has been enabled.

Next gates: agree retention and explicit cursor-expiry snapshot behavior; run synthetic private host-to-host transfer with Sentinel-managed restricted identity after separately authorized credentials; measure KGM source/analysis/forecast health via approved owner-only read path; review licensing/redaction and approve versioned release policy before any real sample. Private Plugin PR #161 remains paused.
