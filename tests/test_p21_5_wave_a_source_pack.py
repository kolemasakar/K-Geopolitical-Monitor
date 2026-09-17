from datetime import datetime, timezone
from pathlib import Path

import pytest

from kgeopolitical_monitor.live_sources import HttpResponse
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.p21_5_wave_a_source_pack import (
    P21_5_WAVE_A_VERSION, WAVE_A_SOURCES, build_wave_a_adapters,
    install_wave_a_governance, wave_a_by_id,
)
from kgeopolitical_monitor.source_portfolio import SourcePortfolioService

NOW=datetime(2026,9,17,1,20,tzinfo=timezone.utc)
FIX=Path(__file__).parent/'fixtures'/'p21_5_wave_a'

class FixtureTransport:
    def get(self,url,*,headers=None):
        name='kmu.rss.xml' if 'kmu.gov.ua' in url else 'suspilne.rss.xml'
        return HttpResponse(body=(FIX/name).read_bytes(), content_type='application/rss+xml')

def runtime(tmp_path):
    return OperationalMonitoringRuntime(tmp_path/'project')

def test_wave_a_specs_are_exact_public_free_anonymous_targets():
    assert P21_5_WAVE_A_VERSION=='P21.5-WAVE-A-1.0'
    by=wave_a_by_id()
    assert set(by)=={'ukraine-government-kmu-uk','suspilne-uk'}
    assert by['ukraine-government-kmu-uk'].source_type=='OFFICIAL_GOVERNMENT'
    assert by['suspilne-uk'].source_type=='NATIONAL_MEDIA'
    assert all(s.feed_url.startswith('https://') for s in WAVE_A_SOURCES)
    assert all(s.language_scope==('uk',) and s.region_scope==('UKRAINE',) for s in WAVE_A_SOURCES)

def test_fixture_parsing_and_adapter_identity():
    adapters=build_wave_a_adapters(FixtureTransport(),max_entries=10)
    watch=type('Watch',(),{'query':'unused'})()
    for adapter in adapters:
        items=adapter.fetch(watch,NOW)
        assert len(items)==1
        assert items[0].source_id==adapter.source_id
        assert items[0].metadata['adapter_id']==adapter.adapter_id
        assert items[0].metadata['published_at_raw']

def test_governance_is_active_free_public_and_idempotent(tmp_path):
    r=runtime(tmp_path)
    first=install_wave_a_governance(r,reviewed_at=NOW)
    second=install_wave_a_governance(r,reviewed_at=NOW)
    assert len(first)==2
    assert [x.portfolio_entry_id for x in first]==[x.portfolio_entry_id for x in second]
    assert all(x.availability_state=='ACTIVE' for x in first)
    assert all(x.access_mode=='PUBLIC_ANONYMOUS' and x.cost_mode=='FREE' for x in first)
    assert all(x.authentication_mode=='NONE' and x.data_classification=='PUBLIC' for x in first)
    assert all(x.review_status=='APPROVED' and x.paid_provider_approved is False for x in first)
    assert all(x.establishes_independence is False and x.changes_verification_state is False for x in first)

def test_deterministic_disable_rollback_removes_collection_paths_without_deleting_governance(tmp_path):
    r=runtime(tmp_path); install_wave_a_governance(r,reviewed_at=NOW)
    assert len(build_wave_a_adapters(FixtureTransport(),enabled_source_ids=[]))==0
    svc=SourcePortfolioService(r)
    assert all(svc.current(s.source_id) is not None for s in WAVE_A_SOURCES)
    with pytest.raises(ValueError,match='unknown P21.5 Wave-A source'):
        build_wave_a_adapters(FixtureTransport(),enabled_source_ids=['unknown'])
