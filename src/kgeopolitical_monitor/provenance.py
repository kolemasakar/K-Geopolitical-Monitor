# Provenance model

# Historical compatibility surface retained for legacy callers/tests.
class ProvenanceRecord:
    def __init__(self, source_id, reliability='MEDIUM', independence='UNKNOWN'):
        self.source_id = source_id
        self.reliability = reliability
        self.independence = independence


# P13.2 additive semantic provenance API. The legacy class above is not
# reinterpreted or migrated by importing the new layer.
from .semantic_provenance import (  # noqa: E402
    ATTRIBUTION_STATES,
    ENTITY_KINDS,
    PROVENANCE_ROLES,
    RELATION_TYPES,
    SEMANTIC_PROVENANCE_MODEL_VERSION,
    ClaimProvenanceRoleVersion,
    ProvenanceEntityVersion,
    ProvenanceRelationVersion,
    SemanticProvenanceService,
)
