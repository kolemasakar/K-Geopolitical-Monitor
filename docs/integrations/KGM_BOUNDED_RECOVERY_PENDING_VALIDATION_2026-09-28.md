# KGM bounded offline recovery: implementation checkpoint — 2026-09-28

Owner-approved scope: one authorized human owner; malicious local human user is out of scope. Existing corruption and accidental-safety controls remain.

Branch `integration/kgm-multiconsumer-export-20260928`. New recovery module and five synthetic tests; latest code SHA `862881964b406edde37a2132efe8e8dbab40aefe`.

`research_recovery_pass_v1.py` runs one **explicitly invoked**, bounded (1–100 items) pass over durable pending requests. PROCESSING requests are first offered to the existing strict immutable typed-artifact reconciliation; RECEIVED/ACCEPTED requests are not incorrectly passed to typed completion. A missing artifact can then result in caller-supplied deadline expiry, otherwise the request stays pending. A corrupt/conflicting artifact is recorded as an error and is not expired. The returned report separates reconciled/expired/pending/errors and reports remaining pending count. This is not a daemon, authenticated transport or production scheduler.

Five synthetic tests cover published-result-before-expiry priority, explicit expiry, no-deadline pending, empty bounded pass and invalid bound. **Test status: UNVERIFIED** at this SHA. Remote Desktop Commander calls to the authorized KGM host timed out on the first test launch and follow-up retry; no test pass is claimed for the new module. Last confirmed baseline: `f1e7067b021106a8bac762bd97d6ebf72e7f9878`, **115 passed**.

Next: run all 20 explicit exchange/research modules at exact SHA, inspect failures, add a mixed-workload bounded recovery test, and address the coexistence of legacy fixture and durable typed APIs. No production modification, K-Trader access, live source calls or Plugin PR #161 change.
