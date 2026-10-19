# P24.2-A owner SSH and real-artifact read-only preflight — 2026-10-19

GitHub Actions run: https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/39240557681
Job result: SUCCESS.

- Existing repository secrets E4_HOST, E4_SSH_PRIVATE_KEY, E4_SSH_KNOWN_HOSTS reused; SSH ubuntu user, sudo uid=0: PASS.
- kgm-monitor.service active: PASS.
- Preflight script SHA-256 pinned 5ac4e4f89e834073b68e0ad879b99c491533579ca0c2420569ffd090baa2252a; seven isolated tests PASS.
- Root read-only real-artifact preflight status: PREFLIGHT_PASS.
- Restored DB and backup DB: both 704512 bytes, SHA256 4c5c27a1716c706753b8ccda2abeae59982b3e6d5cad8b1eddce154c1bffa8f7.
- Manifest: SHA256 a3d4a3a79d7717f8ef6c965a7976027f5241a600ccd6e82738352087acde5bcd; 5520 bytes.
- Report: SHA256 7d906d7677a11385c687e827ff4abe569d34ef0dfb0de7c32c84ddd11c43f557; 1249 bytes.
- Directory contents and file types/ownership/links matched preflight expectations.
- Workflow logs explicitly show deletion_performed=false, cleanup=HOLD.
- Temporary evidence staging was created for inspection and scheduled for cleanup; production evidence/artifacts were not altered.

**This is preflight acceptance only. No reviewed deletion executor, independent mutation-time safety/TOCTOU proof, or cleanup authorization yet. CLEANUP HOLD, FREE_ONLY, NO_SEND, production NO-GO maintained.**
