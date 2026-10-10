from pathlib import Path
from kgeopolitical_monitor.research_archive_retention_policy_v1 import plan_retention, execute_retention
from kgeopolitical_monitor.research_evidence_archive_index_v1 import load_archive_index
from test_research_evidence_archive_index_v1 import seed

POLICY={"schema_version":"kgm.research.archive-retention-policy.v1","consumer_id":"ktrader",
        "keep_latest":1,"min_age_days":1,"max_delete_count":1,"max_delete_fraction":0.5}

def test_retention_plan_is_non_destructive(tmp_path):
    seed(tmp_path,"req-01");seed(tmp_path,"req-02")
    before=sorted(x.name for x in (tmp_path/"evidence_archive"/"ktrader").glob("*.json"))
    plan=plan_retention(tmp_path,POLICY,observed_at_utc="2026-10-10T12:00:00Z")
    after=sorted(x.name for x in (tmp_path/"evidence_archive"/"ktrader").glob("*.json"))
    assert plan["delete_count"]==1
    assert before==after

def test_retention_execute_requires_explicit_flag(tmp_path):
    seed(tmp_path,"req-01");seed(tmp_path,"req-02")
    result=execute_retention(tmp_path,POLICY,observed_at_utc="2026-10-10T12:00:00Z")
    assert result["executed"] is False
    assert result["deleted"]==[]
    assert len(list((tmp_path/"evidence_archive"/"ktrader").glob("*.json")))==2

def test_retention_execute_deletes_only_bounded_candidate_and_repairs_index(tmp_path):
    seed(tmp_path,"req-01");seed(tmp_path,"req-02")
    result=execute_retention(tmp_path,POLICY,observed_at_utc="2026-10-10T12:00:00Z",allow_delete=True)
    assert result["executed"] is True
    assert len(result["deleted"])==1
    files=list((tmp_path/"evidence_archive"/"ktrader").glob("*.json"))
    assert len(files)==1
    idx=load_archive_index(tmp_path,"ktrader")
    assert len(idx["index"]["entries"])==1

def test_retention_policy_delete_fraction_never_exceeds_half(tmp_path):
    import pytest
    bad=dict(POLICY);bad["max_delete_fraction"]=0.75
    with pytest.raises(ValueError,match="fraction"):
        plan_retention(tmp_path,bad,observed_at_utc="2026-10-10T12:00:00Z")
