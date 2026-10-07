import pytest
from kgeopolitical_monitor.research_origin_assessment_v1 import assess_origin_groups

def test_same_origin_denies_independence_credit():
    r=assess_origin_groups([{"origin_group":"usgs-neic"},{"origin_group":"usgs-neic"}])
    assert r=={"assessment":"SAME_ORIGIN","independent_origin_credit":False,"origin_groups":["usgs-neic"]}

def test_unknown_origin_fails_closed():
    r=assess_origin_groups([{"origin_group":"usgs-neic"},{"origin_group":None}])
    assert r["assessment"]=="UNKNOWN"
    assert r["independent_origin_credit"] is False

def test_distinct_explicit_origins_can_earn_origin_credit():
    r=assess_origin_groups([{"origin_group":"origin-a"},{"origin_group":"origin-b"}])
    assert r["assessment"]=="DISTINCT_ORIGIN"
    assert r["independent_origin_credit"] is True
