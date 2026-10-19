"""Bounded synthetic busy workload on a private real-snapshot copy.

Prepares code-only rollback with forward data retained; never restores old data
or switches a production release. Legacy smoke is initialization/read only.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

from .candidate_qualification_p244 import MAX_SNAPSHOT, _check, _inventory

PRIOR_SHA = 'b31b2136b5fe982d0b63b0135479b1549041906c'


def rollback_gate(*, baseline_hash, current_hash, writers_quiesced,
                  fresh_checkpoint, prior_read_compatible):
    for value in (baseline_hash, current_hash):
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('SHA256 required')
    if any(type(v) is not bool for v in (writers_quiesced, fresh_checkpoint, prior_read_compatible)):
        raise ValueError('explicit gate evidence required')
    ready = writers_quiesced and fresh_checkpoint and prior_read_compatible
    return {'decision': 'CODE_ONLY_KEEP_FORWARD_DB' if ready else 'STOP_KEEP_FORWARD_DB',
            'post_baseline_changes': baseline_hash != current_hash,
            'baseline_restore_allowed': False, 'production_execution_authorized': False,
            'writer_resumption_validated': False}


class FixtureTransport:
    """Never delegates to network; serves marked synthetic bodies to real parsers."""
    def __init__(self, phase):
        self.phase = phase
        self.calls = 0
        self.failures = 0

    def get(self, url, *, headers=None):
        from .live_sources import HttpResponse
        host = urlsplit(url).hostname
        if host not in {'www.consilium.europa.eu', 'api.gdeltproject.org'}:
            raise ValueError('unexpected fixture destination')
        self.calls += 1
        if self.phase == 2 or (self.phase == 1 and host == 'api.gdeltproject.org'):
            self.failures += 1
            raise RuntimeError('SYNTHETIC_OFFLINE_FAILURE')
        title = f'Offline qualification synthetic event {self.phase}'
        if host == 'www.consilium.europa.eu':
            body = (f'<rss version="2.0"><channel><item><title>{title}</title>'
                    f'<description>Synthetic offline fixture only.</description>'
                    f'<link>https://www.consilium.europa.eu/en/press/offline-fixture-{self.phase}/</link>'
                    '<pubDate>Mon, 19 Oct 2026 12:00:00 GMT</pubDate></item></channel></rss>').encode()
            return HttpResponse(body, 'application/rss+xml')
        return HttpResponse(json.dumps({'articles':[{
            'url':f'https://example.org/offline-fixture-{self.phase}', 'title':title,
            'domain':'example.org', 'seendate':'20261019T120000Z',
            'language':'English', 'sourcecountry':'United States'}]}).encode(), 'application/json')


LEGACY_SCRIPT = '''
import json,sys
from pathlib import Path
def deny(event,args):
 if event.startswith('socket.'): raise RuntimeError('OFFLINE_SOCKET_DENIED')
sys.addaudithook(deny)
from kgeopolitical_monitor.unattended_runner import build_unattended_service
class Denied:
 def get(self,*args,**kwargs): raise RuntimeError('OFFLINE_NETWORK_DENIED')
service=build_unattended_service(Path(sys.argv[1]),transport=Denied())
watches=service.runtime.repository.list_watches()
print(json.dumps({'status':'INITIALIZE_AND_READ_PASS','watch_count':len(watches)}))
'''


def _busy_child(root, prior_checkout, watches):
    # Limits are child-only; the old-release read child inherits these limits.
    for key, value in [(resource.RLIMIT_AS, 256*1024*1024),
                       (resource.RLIMIT_FSIZE,16*1024*1024),
                       (resource.RLIMIT_NOFILE,64),(resource.RLIMIT_CPU,30)]:
        resource.setrlimit(key,(value,value))
    socket_attempts = [0]
    def deny(event,args):
        if event.startswith('socket.'):
            socket_attempts[0] += 1
            raise RuntimeError('OFFLINE_SOCKET_DENIED')
    sys.addaudithook(deny)
    from .unattended_runner import build_unattended_service
    from .resource_observation_p243 import observe
    root = Path(root)
    db = root/'data'/'kgeopolitical_monitor.db'
    db.parent.mkdir()
    shutil.copyfile(root/'baseline.db', db)
    service = build_unattended_service(root, transport=FixtureTransport(0))
    # Only this disposable copy is changed. Existing watches are disabled to
    # separate the synthetic workload from owner watch settings and schedules.
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE monitoring_watches SET enabled=0')
    now = datetime(2026,10,19,13,tzinfo=timezone.utc)
    for i in range(watches):
        service.runtime.create_watch('Offline synthetic load','Offline qualification',1,
                                     watch_id=f'offline-busy-{i}',created_at=now)
    service.runtime.create_watch('Offline interrupted fixture','Offline qualification',1,
                                 watch_id='offline-recovery',created_at=now)
    service.runtime.start_run('offline-recovery',started_at=now-timedelta(minutes=2))
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE monitoring_watches SET enabled=0 WHERE watch_id='offline-recovery'")
    phases=[]
    for phase in range(4):
        transport=FixtureTransport(phase)
        # Rebuild actual supervisor each round to exercise persisted cadence and
        # startup recovery, rather than resetting its in-memory startup flag.
        service=build_unattended_service(root,transport=transport)
        current=now+timedelta(minutes=phase)
        due=service.runtime.due_watches(current)
        obs=observe(queue_depth=len(due),queue_bytes=sum(len(json.dumps(vars(w),default=str).encode()) for w in due),
                    disk_free_bytes=shutil.disk_usage(root).free,
                    rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    retries=0,sources=['UNKNOWN'])
        if obs['status']=='BLOCKED': raise ValueError('resource admission blocked')
        tick=service.run_once(current)
        if len(tick.executions)!=watches: raise ValueError('busy execution count mismatch')
        if service.run_once(current).executions: raise ValueError('cadence duplicated a run')
        if tick.recovered_runs != (1 if phase==0 else 0): raise ValueError('startup recovery mismatch')
        failed=sum(e.status=='FAILED' for e in tick.executions)
        if failed != (watches if phase==2 else 0): raise ValueError('unexpected workload outcome')
        if phase != 2 and not all(e.result_count>0 for e in tick.executions):
            raise ValueError('synthetic fixture did not exercise processing')
        if transport.calls!=2*watches: raise ValueError('parser workload mismatch')
        phases.append({'phase':phase,'executions':len(tick.executions),'failed':failed,
                       'results':sum(e.result_count for e in tick.executions),
                       'fixture_http_calls':transport.calls,'fixture_failures':transport.failures,
                       'recovered_runs':tick.recovered_runs,
                       'max_runtime_retry_count':max(e.retry_count for e in tick.executions),
                       'observation_before':obs})
        with sqlite3.connect(db) as conn: _check(conn)
    # All candidate writers have returned. Capture CURRENT committed data using
    # SQLite backup, not the pre-candidate baseline, before the read-only rollback
    # rehearsal. Old-release initialization/read runs against another copy.
    checkpoint=root/'forward-checkpoint.db'
    with sqlite3.connect(db) as src, sqlite3.connect(checkpoint) as dst:
        src.backup(dst)
    with sqlite3.connect(checkpoint) as conn:
        _check(conn); forward_inventory=_inventory(conn)
    with sqlite3.connect(root/'baseline.db') as conn: baseline_inventory=_inventory(conn)
    if forward_inventory==baseline_inventory: raise ValueError('busy workload created no committed changes')
    legacy_root=root/'legacy';(legacy_root/'data').mkdir(parents=True)
    legacy_db=legacy_root/'data'/'kgeopolitical_monitor.db'
    shutil.copyfile(checkpoint,legacy_db)
    legacy={'status':'NOT_RUN_NO_PINNED_PRIOR_CHECKOUT'}
    compatible=False
    if prior_checkout:
        env={'PATH':os.defpath,'PYTHONPATH':str(Path(prior_checkout)/'src'),
             'PYTHONDONTWRITEBYTECODE':'1'}
        result=subprocess.run([sys.executable,'-c',LEGACY_SCRIPT,str(legacy_root)],
                              cwd=legacy_root,env=env,capture_output=True,text=True,timeout=10)
        if result.returncode==0:
            legacy=json.loads(result.stdout)
            with sqlite3.connect(legacy_db) as conn:
                _check(conn); compatible=_inventory(conn)==forward_inventory
        else:
            legacy={'status':'FAILED','returncode':result.returncode}
    if prior_checkout and not compatible: raise ValueError('prior release changed or cannot read forward state')
    # Rehearsal leaves candidate and checkpoint inventories intact. No baseline
    # restore is ever attempted once writes exist, even on a failed legacy gate.
    with sqlite3.connect(db) as conn:
        if _inventory(conn)!=forward_inventory: raise ValueError('candidate changed during rollback preparation')
    current_hash=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    gate=rollback_gate(baseline_hash=hashlib.sha256((root/'baseline.db').read_bytes()).hexdigest(),
                       current_hash=current_hash,writers_quiesced=True,
                       fresh_checkpoint=True,prior_read_compatible=compatible)
    return {'status':'PASS_WITH_LIMITATIONS','workload':'SYNTHETIC_ON_REAL_SNAPSHOT_COPY',
            'phases':phases,'total_executions':sum(p['executions'] for p in phases),
            'socket_attempts_denied':socket_attempts[0], 'forward_rows_preserved':True,
            'changed_tables':sum(forward_inventory.get(t)!=baseline_inventory.get(t) for t in forward_inventory),
            'legacy_smoke':legacy,'prior_read_compatible':compatible,'rollback_gate':gate,
            'production_modified':False,'send':False}


def qualify_busy(snapshot,*,expected_sha256,prior_checkout=None,watches=10):
    if type(watches) is not int or not 1<=watches<=20: raise ValueError('workload bounded to 1..20 watches')
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ValueError('SHA256 required')
    if prior_checkout:
        prior_checkout=Path(prior_checkout).resolve()
        sha=subprocess.check_output(['git','-C',str(prior_checkout),'rev-parse','HEAD'],text=True).strip()
        # Include untracked files: a shadow module could otherwise bypass pinning.
        dirty=subprocess.check_output(['git','-C',str(prior_checkout),'status','--porcelain','--untracked-files=all'],text=True)
        if sha!=PRIOR_SHA or dirty: raise ValueError('clean pinned prior release required')
    fd=os.open(snapshot,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as source:
        info=os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>MAX_SNAPSHOT:
            raise ValueError('bounded single-link regular snapshot required')
        data=source.read(MAX_SNAPSHOT+1)
    if len(data)>MAX_SNAPSHOT or hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise ValueError('snapshot hash or size mismatch')
    with tempfile.TemporaryDirectory(prefix='kgm-busy-qualification-') as temp:
        (Path(temp)/'baseline.db').write_bytes(data)
        script='import json,sys; from kgeopolitical_monitor.busy_qualification_p244 import _busy_child; print(json.dumps(_busy_child(sys.argv[1],sys.argv[2],int(sys.argv[3])),sort_keys=True))'
        env={'PATH':os.defpath,'PYTHONPATH':str(Path(__file__).resolve().parents[1]),'PYTHONDONTWRITEBYTECODE':'1'}
        try:
            r=subprocess.run([sys.executable,'-c',script,temp,str(prior_checkout or ''),str(watches)],
                             cwd=temp,env=env,capture_output=True,text=True,timeout=90)
        except subprocess.TimeoutExpired:
            return {'status':'FAIL','cause':'TIMEOUT','child_reaped':True,'send':False}
        if r.returncode: return {'status':'FAIL','cause':'CHILD_FAILED','returncode':r.returncode,'send':False}
        report=json.loads(r.stdout)
        report.update(snapshot_sha256=expected_sha256,prior_release_sha=PRIOR_SHA if prior_checkout else None)
    report['temporary_workspace_removed']=True
    return report


def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot',type=Path);p.add_argument('--expected-sha256',required=True)
    p.add_argument('--prior-checkout',type=Path);p.add_argument('--watches',type=int,default=10)
    a=p.parse_args(argv)
    r=qualify_busy(a.snapshot,expected_sha256=a.expected_sha256,prior_checkout=a.prior_checkout,watches=a.watches)
    print(json.dumps(r,sort_keys=True));return 0 if r['status']=='PASS_WITH_LIMITATIONS' else 1


if __name__=='__main__': raise SystemExit(main())
