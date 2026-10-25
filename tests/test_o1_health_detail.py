import importlib.util
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/"ops/o1_diag/kgm-o1-health-detail.py"
spec=importlib.util.spec_from_file_location("o1_health_detail",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_time_normalization():
    assert m.canonical_time("2026-10-25T20:07:52Z")=="2026-10-25T20:07:52+00:00"
    assert m.canonical_time(None)=="EMPTY"
    assert m.canonical_time("not-a-timestamp")=="UNPARSEABLE"

def test_static_allowlist():
    assert {"GDACS","GDELT"}.issubset(m.ALLOWED_SOURCE)
    assert "last_supervisor_tick_at" in m.HEALTH_TIME
    assert "last_successful_execution_at" in m.HEALTH_TIME
