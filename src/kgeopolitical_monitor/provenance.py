# Provenance model

class ProvenanceRecord:
    def __init__(self, source_id, reliability='MEDIUM', independence='UNKNOWN'):
        self.source_id = source_id
        self.reliability = reliability
        self.independence = independence
