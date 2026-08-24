from kgeopolitical_monitor.provenance import ProvenanceRecord
from kgeopolitical_monitor.contradictions import Contradiction


def test_provenance_creation():
    p = ProvenanceRecord('source-1')
    assert p.source_id == 'source-1'


def test_contradiction_creation():
    c = Contradiction('claim-a', 'claim-b')
    assert c.status == 'DETECTED'
