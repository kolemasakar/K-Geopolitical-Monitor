# Private Plugin standalone test evidence — 2026-09-25

## Environment
- KGM-only RDC device: `kgm-e4-owner-pilot`, owner user `kgmops`.
- Source fetched by GitHub connector at exact commit `071af158b3ea316e498bf250a02d7bf82ffb975b`: `src/kgeopolitical_monitor/private_plugin_status.py` and `tests/test_private_plugin_status.py`.
- Source transferred to an isolated directory `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/standalone`; an empty package `__init__.py` was added solely to avoid resolution to an older installed package. Production KGM was not modified.
- Test runner: existing KGM validation virtualenv pytest 9.1.1.

## Command and result
```bash
cd /home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/standalone
PYTHONPATH=src /home/kgmops/validation/kgeopolitical-monitor/p23-4/venv/bin/python -m pytest -q tests/test_private_plugin_status.py
```
```
...... [100%]
6 passed in 0.01s
```

## Remaining gate
This validates the standalone projection only, **not** the full exact-SHA repository integration or owner-authenticated FastAPI endpoint. A private-repository Git fetch of the exact SHA from the isolated checkout returned `git upload-pack: not our ref`; `gh` is not installed on this user account. Do not claim integration PASS, merge PR or deploy private plugin until full isolated checkout, integration tests, and transport security gate complete.
