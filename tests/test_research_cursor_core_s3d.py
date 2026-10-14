"""Synthetic crash/replay and validation tests for isolated cursor primitive."""
import json
import pytest
from kgeopolitical_monitor.research_cursor_core_v1 import recover_with_cursor

def root(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "outbox").mkdir()
    return tmp_path

def call(root, fn, **kwargs):
    return recover_with_cursor(root, recover_fn=fn, allowed_consumers=["test"],
                               observed_at_utc="2026-10-14T00:00:00Z", **kwargs)

def test_cursor_advances_only_after_success(tmp_path):
    seen=[]
    def fn(root, *, after_key, **kw):
        seen.append(after_key)
        return {"next_cursor": ("consumer-a","req-a")}
    folder=root(tmp_path)
    call(folder,fn)
    call(folder,fn)
    assert seen==[None, ("consumer-a","req-a")]

def test_failed_recovery_does_not_advance(tmp_path):
    folder=root(tmp_path)
    def failed(root, **kw):
        raise RuntimeError("synthetic recovery crash")
    with pytest.raises(RuntimeError):
        call(folder,failed)
    assert not (folder / ".research-recovery-cursor.json").exists()

def test_invalid_next_cursor_is_not_persisted(tmp_path):
    folder=root(tmp_path)
    with pytest.raises(ValueError):
        call(folder,lambda *a,**kw: {"next_cursor": ("bad/name","req")})
    assert not (folder / ".research-recovery-cursor.json").exists()

def test_symlink_cursor_rejected(tmp_path):
    folder=root(tmp_path)
    target=folder / "target.txt"
    target.write_text('{"version":1,"after_key":null}')
    (folder / ".research-recovery-cursor.json").symlink_to(target)
    with pytest.raises(ValueError,match="alias"):
        call(folder,lambda *a,**kw: {"next_cursor":None})

def test_malformed_stored_record_rejected(tmp_path):
    folder=root(tmp_path)
    (folder / ".research-recovery-cursor.json").write_text(json.dumps({"version":2,"after_key":None}))
    with pytest.raises(ValueError,match="record"):
        call(folder,lambda *a,**kw: {"next_cursor":None})

def test_unbounded_batch_denied(tmp_path):
    folder=root(tmp_path)
    with pytest.raises(ValueError,match="bound"):
        call(folder,lambda *a,**kw: {"next_cursor":None},max_items=1000)
