import sqlite3
from pathlib import Path
import hashlib

import pytest

from kgeopolitical_monitor.busy_qualification_p244 import _forward_rows_retained,qualify_busy


def copies(tmp_path):
    before=tmp_path/'before.db';after=tmp_path/'after.db'
    with sqlite3.connect(before) as c:
        c.execute('CREATE TABLE monitoring_watches(watch_id TEXT PRIMARY KEY, enabled INTEGER)')
        c.execute("INSERT INTO monitoring_watches VALUES ('candidate',1)")
        c.execute('CREATE TABLE forward_state(id TEXT PRIMARY KEY,value TEXT)')
        c.execute("INSERT INTO forward_state VALUES ('new','committed')")
    after.write_bytes(before.read_bytes())
    return before,after


def test_writer_may_append_without_losing_committed_forward_rows(tmp_path):
    before,after=copies(tmp_path)
    with sqlite3.connect(after) as c:
        c.execute('UPDATE monitoring_watches SET enabled=0')
        c.execute("INSERT INTO forward_state VALUES ('prior','added')")
    assert _forward_rows_retained(before,after)


@pytest.mark.parametrize('sql',["DELETE FROM forward_state", "UPDATE forward_state SET value='overwritten'", "DELETE FROM monitoring_watches"])
def test_writer_cannot_drop_or_overwrite_committed_data(tmp_path,sql):
    before,after=copies(tmp_path)
    with sqlite3.connect(after) as c: c.execute(sql)
    assert not _forward_rows_retained(before,after)


def test_prior_writer_needs_explicit_clean_release_gate(tmp_path):
    before,_=copies(tmp_path);digest=hashlib.sha256(before.read_bytes()).hexdigest()
    for kwargs in [{'prior_writer':True},{'prior_python':Path('/usr/bin/python3')},{'prior_writer':1}]:
        with pytest.raises(ValueError): qualify_busy(before,expected_sha256=digest,**kwargs)


def test_writer_branch_with_current_code_fixture_preserves_forward_state(tmp_path):
    # Branch coverage fixture, not evidence about the pinned historical release.
    # Real b31b213 is checked independently on ARM64 with the public entry point.
    import os
    import json
    import subprocess
    import sys
    from kgeopolitical_monitor.database import initialize_database
    root=tmp_path/'work';root.mkdir();initialize_database(str(root/'baseline.db'))
    checkout=Path(__file__).resolve().parents[1]
    script='from kgeopolitical_monitor.busy_qualification_p244 import _busy_child; import sys,json; print(json.dumps(_busy_child(sys.argv[1],sys.argv[2],2,True)))'
    r=subprocess.run([sys.executable,'-c',script,str(root),str(checkout)],cwd=tmp_path,
                     env={'PATH':os.defpath,'PYTHONPATH':str(checkout/'src'),'PYTHONDONTWRITEBYTECODE':'1'},
                     text=True,capture_output=True,timeout=30)
    assert r.returncode==0,r.stderr
    report=json.loads(r.stdout)
    assert report['legacy_smoke']['total_executions']==8
    assert report['prior_writer_fixture_compatible']
    assert report['legacy_smoke']['forward_rows_retained']
    assert not report['rollback_gate']['writer_resumption_validated']


@pytest.mark.parametrize('change,accepted',[
    ("UPDATE owner_runtime_health SET last_supervisor_tick_at='2026-10-19T14:00:00+00:00'",True),
    ("UPDATE owner_runtime_health SET last_supervisor_tick_at='2026-10-19T12:00:00+00:00'",False),
    ("UPDATE owner_runtime_health SET last_successful_execution_at=NULL",False),
    ("UPDATE owner_runtime_health SET instrumentation_version='changed'",False),
    ("DELETE FROM owner_runtime_health",False),
])
def test_health_projection_changes_are_explicit_and_monotonic(tmp_path,change,accepted):
    before,after=copies(tmp_path)
    for p in (before,after):
        with sqlite3.connect(p) as c:
            c.execute('CREATE TABLE owner_runtime_health(singleton_id INTEGER PRIMARY KEY,instrumentation_version TEXT,last_supervisor_tick_at TEXT,last_completed_tick_at TEXT,last_successful_execution_at TEXT)')
            c.execute("INSERT INTO owner_runtime_health VALUES(1,'v1','2026-10-19T13:00:00+00:00','2026-10-19T13:00:00+00:00','2026-10-19T13:00:00+00:00')")
    with sqlite3.connect(after) as c: c.execute(change)
    assert _forward_rows_retained(before,after) is accepted
