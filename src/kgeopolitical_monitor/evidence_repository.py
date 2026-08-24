# Evidence repository layer

class EvidenceRepository:
    def __init__(self, storage):
        self.storage = storage

    def save(self, evidence):
        return self.storage.save_evidence(evidence)

    def get(self, evidence_id):
        return self.storage.get_evidence(evidence_id)
