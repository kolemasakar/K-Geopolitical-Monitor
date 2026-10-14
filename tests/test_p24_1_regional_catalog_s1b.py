from kgeopolitical_monitor.research_regional_source_candidates_p24_1 import validated_candidate

def test_source_disabled():
    for name in ('african-union-press', 'asean-news', 'gcc-secretariat-news', 'oas-press'):
        x = validated_candidate(name)
        assert x['adapter_enabled'] is False
        assert x['factual_verification_credit'] is False
        assert x['source_independence_credit'] is False
