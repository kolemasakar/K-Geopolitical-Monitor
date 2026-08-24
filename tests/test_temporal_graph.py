from datetime import datetime
from kgeopolitical_monitor.temporal_graph import TemporalGraphAnalyzer, TemporalRelation


def test_temporal_change():
    graph = TemporalGraphAnalyzer()
    graph.add_relation(TemporalRelation('A','B','influence',datetime.now(),0.5))
    graph.add_relation(TemporalRelation('A','B','influence',datetime.now(),0.8))
    assert graph.influence_change('A') == 0.3
