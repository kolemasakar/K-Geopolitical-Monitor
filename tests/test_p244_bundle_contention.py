import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import zipfile

import pytest

from kgeopolitical_monitor.wheel_lock_p244 import wheel_lock
from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.contention_qualification_p244 import contention


def wheel(root,name='sample',version='1.0'):
    p=root/f'{name}-{version}-py3-none-any.whl'
    with zipfile.ZipFile(p,'w') as w:
        w.writestr(f'{name}-{version}.dist-info/METADATA',f'Name: {name}\nVersion: {version}\n')
    return p


def test_wheel_lock_binds_exact_identity_and_bytes(tmp_path):
    p=wheel(tmp_path);lock,manifest=wheel_lock(tmp_path)
    assert f'sample==1.0 --hash=sha256:{hashlib.sha256(p.read_bytes()).hexdigest()}' in lock
    assert manifest['wheels'][0]['filename']==p.name
    before=manifest['wheels'][0]['sha256'];p.write_bytes(p.read_bytes()+b'changed')
    assert wheel_lock(tmp_path)[1]['wheels'][0]['sha256']!=before


def test_wheel_lock_rejects_alias_duplicate_and_nonwheel(tmp_path):
    p=wheel(tmp_path);alias=tmp_path/'alias.whl';alias.symlink_to(p)
    with pytest.raises(ValueError):wheel_lock(tmp_path)
    alias.unlink();wheel(tmp_path,version='2.0')
    with pytest.raises(ValueError,match='one wheel'):wheel_lock(tmp_path)


def test_process_lease_and_sqlite_contention_keep_all_commits(tmp_path):
    db=tmp_path/'source.db';initialize_database(str(db));before=db.read_bytes()
    r=contention(tmp_path,db,Path(__file__).resolve().parents[1])
    assert r['lease_second_writer']=='DENIED_BEFORE_DB_WRITE'
    assert r['lease_after_holder_kill']=='RESUMED_COMMIT'
    assert r['sqlite_overlap']=='SQLITE_BUSY_ROLLED_BACK_THEN_RETRY_COMMITTED'
    assert r['committed_probe_rows']==3
    assert db.read_bytes()==before


def test_overlapping_items_and_old_writer_branch_on_owned_fixture(tmp_path):
    # Current-code fixture covers the mechanism; actual old source is separately
    # pinned and run on ARM64 with the public entry point.
    root=tmp_path/'work';root.mkdir();initialize_database(str(root/'baseline.db'))
    checkout=Path(__file__).resolve().parents[1]
    script='from kgeopolitical_monitor.busy_qualification_p244 import _busy_child; import sys,json; print(json.dumps(_busy_child(sys.argv[1],sys.argv[2],2,True,"",True,True)))'
    r=subprocess.run([sys.executable,'-c',script,str(root),str(checkout)],cwd=tmp_path,
                     env={'PATH':os.defpath,'PYTHONPATH':str(checkout/'src'),'PYTHONDONTWRITEBYTECODE':'1'},
                     text=True,capture_output=True,timeout=45)
    assert r.returncode==0,r.stderr
    report=json.loads(r.stdout)
    assert report['overlapping_items'] and report['prior_writer_fixture_compatible']
    assert report['contention']['committed_probe_rows']==3
    assert not report['rollback_gate']['production_execution_authorized']
