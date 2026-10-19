"""Process-level single-writer lease and SQLite contention in an owned copy."""
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import sqlite3
import subprocess
import sys

from .candidate_qualification_p244 import _check

HOLDER='''
import sys
from kgeopolitical_monitor.runtime_lease import RuntimeInstanceLease
with RuntimeInstanceLease(sys.argv[1]):
 print('HELD',flush=True)
 sys.stdin.readline()
'''
CONTENDER='''
import sys,json
from kgeopolitical_monitor.runtime_lease import RuntimeInstanceLease,RuntimeLeaseError
try:
 with RuntimeInstanceLease(sys.argv[1]):
  if sys.argv[3]=='deny': raise RuntimeError('second writer admitted')
  import sqlite3
  with sqlite3.connect(sys.argv[2]) as c: c.execute("INSERT INTO qualification_writer_probe VALUES('resumed','committed')")
 print(json.dumps({'status':'RESUMED_COMMIT'}))
except RuntimeLeaseError:
 if sys.argv[3]!='deny': raise
 print(json.dumps({'status':'DENIED'}))
'''
TRANSACTION='''
import sys,sqlite3,json
from kgeopolitical_monitor.database import connect_runtime_database
c=connect_runtime_database(sys.argv[1]);c.execute('PRAGMA busy_timeout=100')
if sys.argv[2]=='first':
 c.execute('BEGIN IMMEDIATE');c.execute("INSERT INTO qualification_writer_probe VALUES('first','committed')")
 print('LOCKED',flush=True);sys.stdin.readline();c.commit();print('COMMITTED',flush=True)
else:
 try: c.execute('BEGIN IMMEDIATE')
 except sqlite3.OperationalError as e:
  if e.sqlite_errorcode!=sqlite3.SQLITE_BUSY: raise
  c.rollback();print('BUSY',flush=True);sys.stdin.readline()
 else: raise RuntimeError('contention not observed')
 c.execute('BEGIN IMMEDIATE');c.execute("INSERT INTO qualification_writer_probe VALUES('second','committed')");c.commit();print('COMMITTED',flush=True)
c.close()
'''


def _line(process, expected):
    if not select.select([process.stdout],[],[],5)[0]: raise RuntimeError('child handshake timeout')
    if process.stdout.readline().strip()!=expected: raise RuntimeError('child handshake mismatch')


def _finish(process):
    out,err=process.communicate(timeout=5)
    if process.returncode: raise RuntimeError('qualification child failed')
    return out


def contention(root, source_db, prior_checkout, prior_python=''):
    """Caller supplies only its internally owned workspace and checkpoint."""
    root=Path(root)/'contention';root.mkdir()
    db=root/'runtime.db';shutil.copyfile(source_db,db)
    with sqlite3.connect(db) as c:
        c.execute('CREATE TABLE qualification_writer_probe(id TEXT PRIMARY KEY,value TEXT)')
    lease=root/'runtime.lock'
    candidate_env={'PATH':os.defpath,'PYTHONPATH':str(Path(__file__).resolve().parents[1]),'PYTHONDONTWRITEBYTECODE':'1'}
    prior_env={**candidate_env,'PYTHONPATH':str(Path(prior_checkout)/'src')}
    prior_python=str(prior_python or sys.executable)
    children=[]
    def start(python,script,args,env):
        p=subprocess.Popen([python,'-c',script,*map(str,args)],cwd=root,env=env,
                           stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        children.append(p);return p
    try:
        holder=start(sys.executable,HOLDER,[lease],candidate_env);_line(holder,'HELD')
        before=hashlib.sha256(db.read_bytes()).hexdigest()
        blocked=start(prior_python,CONTENDER,[lease,db,'deny'],prior_env)
        if json.loads(_finish(blocked))!={'status':'DENIED'}: raise RuntimeError('lease failed')
        if hashlib.sha256(db.read_bytes()).hexdigest()!=before: raise RuntimeError('denied writer mutated DB')
        # Kill only our disposable holder, wait/reap, then verify the OS released
        # the lease despite the persistent lock-file metadata.
        holder.kill();holder.communicate(timeout=5)
        resumed=start(prior_python,CONTENDER,[lease,db,'resume'],prior_env)
        if json.loads(_finish(resumed))!={'status':'RESUMED_COMMIT'}: raise RuntimeError('lease did not recover')
        first=start(sys.executable,TRANSACTION,[db,'first'],candidate_env);_line(first,'LOCKED')
        second=start(prior_python,TRANSACTION,[db,'second'],prior_env);_line(second,'BUSY')
        with sqlite3.connect(db) as c:
            if c.execute("SELECT count(*) FROM qualification_writer_probe WHERE id IN ('first','second')").fetchone()[0]!=0:
                raise RuntimeError('uncommitted data became visible')
        first.stdin.write('commit\n');first.stdin.flush();_line(first,'COMMITTED');_finish(first)
        second.stdin.write('retry\n');second.stdin.flush();_line(second,'COMMITTED');_finish(second)
        with sqlite3.connect(db) as c:
            _check(c)
            rows=c.execute('SELECT id,value FROM qualification_writer_probe ORDER BY id').fetchall()
            if rows!=[('first','committed'),('resumed','committed'),('second','committed')]:
                raise RuntimeError('committed rows lost or duplicated')
        return {'lease_second_writer':'DENIED_BEFORE_DB_WRITE','lease_after_holder_kill':'RESUMED_COMMIT',
                'sqlite_overlap':'SQLITE_BUSY_ROLLED_BACK_THEN_RETRY_COMMITTED',
                'committed_probe_rows':3,'integrity':'PASS','production_modified':False,'send':False}
    finally:
        for p in children:
            if p.poll() is None: p.kill()
            p.communicate(timeout=5)
