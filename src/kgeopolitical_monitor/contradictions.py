# Contradiction handling

class Contradiction:
    def __init__(self, claim_a, claim_b, status='DETECTED'):
        self.claim_a = claim_a
        self.claim_b = claim_b
        self.status = status
