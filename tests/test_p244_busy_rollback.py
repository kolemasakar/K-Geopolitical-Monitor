import hashlib
from pathlib import Path
import sqlite3

import pytest

from kgeopolitical_monitor.busy_qualification_p244 import qualify_busy, rollback_gate
from kgeopolitical_monitor.database import initialize_database


def snapshot(tmp_path):
    db=tmp_path/'snapshot.db';initialize_database(str(db))
    return db,hashlib.sha256(db.read_bytes()).hexdigest()


def test_busy_pipeline_persists_success_failure_restart_and_cadence(tmp_path):
    db,digest=snapshot(tmp_path);before=db.read_bytes()
    r=qualify_busy(db,expected_sha256=digest,watches=3)
    assert r['status']=='PASS_WITH_LIMITATIONS'
    assert r['total_executions']==12
    assert [p['failed'] for p in r['phases']]==[0,0,3,0]
    assert sum(p['recovered_runs'] for p in r['phases'])==1
    assert r['phases'][3]['max_runtime_retry_count']>0
    assert r['socket_attempts_denied']==0
    assert r['changed_tables']>0 and r['forward_rows_preserved']
    assert r['rollback_gate']['decision']=='STOP_KEEP_FORWARD_DB'
    assert not r['rollback_gate']['baseline_restore_allowed']
    assert r['temporary_workspace_removed']
    assert db.read_bytes()==before


@pytest.mark.parametrize('flags',[(False,True,True),(True,False,True),(True,True,False)])
def test_missing_rollback_gate_never_restores_baseline(flags):
    r=rollback_gate(baseline_hash='a'*64,current_hash='b'*64,
                    writers_quiesced=flags[0],fresh_checkpoint=flags[1],prior_read_compatible=flags[2])
    assert r['decision']=='STOP_KEEP_FORWARD_DB' and r['post_baseline_changes']
    assert not r['baseline_restore_allowed'] and not r['production_execution_authorized']


def test_code_only_rollback_retains_new_writes_even_if_read_compatible():
    r=rollback_gate(baseline_hash='a'*64,current_hash='b'*64,
                   writers_quiesced=True,fresh_checkpoint=True,prior_read_compatible=True)
    assert r['decision']=='CODE_ONLY_KEEP_FORWARD_DB'
    assert not r['baseline_restore_allowed'] and not r['writer_resumption_validated']


def test_invalid_inputs_rejected_before_qualification(tmp_path):
    db,digest=snapshot(tmp_path)
    for watches in (0,21,True):
        with pytest.raises(ValueError): qualify_busy(db,expected_sha256=digest,watches=watches)
    with pytest.raises(ValueError): qualify_busy(db,expected_sha256='0'*64)
    with pytest.raises(ValueError):
        qualify_busy(db,expected_sha256=digest,prior_checkout=Path(__file__).resolve().parents[1])
    with pytest.raises(ValueError):
        rollback_gate(baseline_hash='a'*64,current_hash='b'*64,writers_quiesced=1,
                      fresh_checkpoint=True,prior_read_compatible=True)
