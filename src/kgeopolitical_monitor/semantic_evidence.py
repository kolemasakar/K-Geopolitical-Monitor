"""Phase 13 P13.3 typed evidence relations and independence assessments.

This layer records how evidence bears on a P13.1 semantic claim and separately
records pairwise independence assessments using P13.2 provenance. It does not
resolve contradictions, promote verification state, calculate factual
confidence, or cut over live analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SEMANTIC_EVIDENCE_MODEL_VERSION = "P13.3-1.0"
EVIDENCE_RELATION_TYPES = (
    "SUPPORTS",
    "CONTRADICTS",
    "QUALIFIES",
    "CONTEXT_ONLY",
    "ATTRIBUTION_ONLY",
    "DUPLICATE_OR_SAME_ORIGIN",
)
INDEPENDENCE_STATES = ("INDEPENDENT", "NOT_INDEPENDENT", "UNKNOWN", "MIXED")
INDEPENDENCE_RATIONALE_CODES = (
    "EXPLICIT_DISTINCT_UNDERLYING_ORIGINS",
    "SAME_UNDERLYING_ORIGIN",
    "DERIVATION_PATH",
    "DUPLICATE_OR_SAME_ORIGIN",
    "UNRESOLVED_ORIGIN",
    "MIXED_ORIGIN",
    "INSUFFICIENT_PROVENANCE",
    "MANUAL_REVIEW",
    "OTHER",
)
_DERIVATION_RELATION_TYPES = {
    "ACQUIRED_FROM",
    "CITES",
    "QUOTES",
    "SYNDICATED_FROM",
    "REPOSTED_FROM",
    "TRANSLATED_FROM",
    "DERIVED_FROM",
    "DATA_EXTRACTED_FROM",
}


def _required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _optional(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _enum(value: object, field_name: str, allowed: tuple[str, ...]) -> str:
    normalized = _required(value, field_name).upper()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
    return normalized


def _stable_version_id(prefix: str, identity: str, version: int) -> str:
    digest = sha256(f"{identity}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class SemanticEvidenceRelationVersion:
    evidence_relation_version_id: str
    evidence_relation_id: str
    relation_version: int
    semantic_claim_version_id: str
    evidence_provenance_entity_version_id: str
    raw_item_id: str | None
    relation_type: str
    assessment_method: str
    assessment_version: str
    note: str | None
    supersedes_relation_version_id: str | None
    created_at: datetime

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def resolves_contradiction(self) -> bool:
        return False


@dataclass(frozen=True)
class IndependenceAssessmentVersion:
    independence_assessment_version_id: str
    independence_assessment_id: str
    assessment_version_number: int
    semantic_claim_version_id: str
    subject_evidence_relation_version_id: str
    comparison_evidence_relation_version_id: str
    independence_state: str
    rationale_code: str
    assessment_method: str
    assessment_version: str
    note: str | None
    supersedes_assessment_version_id: str | None
    created_at: datetime

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def factual_confidence(self) -> None:
        return None


class SemanticEvidenceService:
    """Append-only P13.3 evidence relation and independence persistence."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def record_relation_version(
        self,
        evidence_relation_id: str,
        *,
        semantic_claim_version_id: str,
        evidence_provenance_entity_version_id: str,
        relation_type: str,
        assessment_method: str,
        assessment_version: str,
        raw_item_id: str | None = None,
        note: str | None = None,
        created_at: datetime,
    ) -> SemanticEvidenceRelationVersion:
        relation_id = _required(evidence_relation_id, "evidence_relation_id")
        claim_version_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        entity_version_id = _required(evidence_provenance_entity_version_id, "evidence_provenance_entity_version_id")
        normalized_relation = _enum(relation_type, "relation_type", EVIDENCE_RELATION_TYPES)
        method = _required(assessment_method, "assessment_method")
        method_version = _required(assessment_version, "assessment_version")
        normalized_raw = _optional(raw_item_id)
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)

        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id = ?",
                (claim_version_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")
            entity = connection.execute(
                "SELECT raw_item_id FROM semantic_provenance_entity_versions WHERE provenance_entity_version_id = ?",
                (entity_version_id,),
            ).fetchone()
            if entity is None:
                raise ValueError("provenance entity version does not exist")
            if normalized_raw is not None:
                if connection.execute("SELECT 1 FROM raw_items WHERE id = ?", (normalized_raw,)).fetchone() is None:
                    raise ValueError("raw_item_id does not exist")
                if entity[0] is not None and entity[0] != normalized_raw:
                    raise ValueError("raw_item_id does not match provenance entity raw item")
            previous = connection.execute(
                "SELECT evidence_relation_version_id, relation_version FROM semantic_evidence_relation_versions WHERE evidence_relation_id = ? ORDER BY relation_version DESC LIMIT 1",
                (relation_id,),
            ).fetchone()
            version = 1 if previous is None else int(previous[1]) + 1
            supersedes = None if previous is None else previous[0]
            version_id = _stable_version_id("evidence-relation-version", relation_id, version)
            connection.execute(
                """INSERT INTO semantic_evidence_relation_versions(
                    evidence_relation_version_id,evidence_relation_id,relation_version,
                    semantic_claim_version_id,evidence_provenance_entity_version_id,raw_item_id,
                    relation_type,assessment_method,assessment_version,note,
                    supersedes_relation_version_id,created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (version_id, relation_id, version, claim_version_id, entity_version_id,
                 normalized_raw, normalized_relation, method, method_version,
                 normalized_note, supersedes, timestamp.isoformat()),
            )
        return SemanticEvidenceRelationVersion(
            version_id, relation_id, version, claim_version_id, entity_version_id,
            normalized_raw, normalized_relation, method, method_version,
            normalized_note, supersedes, timestamp,
        )

    def relation_current(self, evidence_relation_id: str) -> SemanticEvidenceRelationVersion | None:
        history = self.relation_history(evidence_relation_id)
        return history[-1] if history else None

    def relation_history(self, evidence_relation_id: str) -> tuple[SemanticEvidenceRelationVersion, ...]:
        relation_id = _required(evidence_relation_id, "evidence_relation_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT evidence_relation_version_id,evidence_relation_id,relation_version,
                    semantic_claim_version_id,evidence_provenance_entity_version_id,raw_item_id,
                    relation_type,assessment_method,assessment_version,note,
                    supersedes_relation_version_id,created_at
                    FROM semantic_evidence_relation_versions
                    WHERE evidence_relation_id=? ORDER BY relation_version""",
                (relation_id,),
            ).fetchall()
        return tuple(self._relation_from_row(row) for row in rows)

    def relations_for_claim(self, semantic_claim_version_id: str) -> tuple[SemanticEvidenceRelationVersion, ...]:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT r.evidence_relation_version_id,r.evidence_relation_id,r.relation_version,
                    r.semantic_claim_version_id,r.evidence_provenance_entity_version_id,r.raw_item_id,
                    r.relation_type,r.assessment_method,r.assessment_version,r.note,
                    r.supersedes_relation_version_id,r.created_at
                    FROM semantic_evidence_relation_versions r
                    JOIN (SELECT evidence_relation_id,MAX(relation_version) max_version
                          FROM semantic_evidence_relation_versions
                          WHERE semantic_claim_version_id=? GROUP BY evidence_relation_id) c
                      ON c.evidence_relation_id=r.evidence_relation_id AND c.max_version=r.relation_version
                    ORDER BY r.evidence_relation_id""",
                (claim_id,),
            ).fetchall()
        return tuple(self._relation_from_row(row) for row in rows)

    def record_independence_version(
        self,
        independence_assessment_id: str,
        *,
        semantic_claim_version_id: str,
        subject_evidence_relation_version_id: str,
        comparison_evidence_relation_version_id: str,
        independence_state: str,
        rationale_code: str,
        assessment_method: str,
        assessment_version: str,
        note: str | None = None,
        created_at: datetime,
    ) -> IndependenceAssessmentVersion:
        assessment_id = _required(independence_assessment_id, "independence_assessment_id")
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        subject_id = _required(subject_evidence_relation_version_id, "subject_evidence_relation_version_id")
        comparison_id = _required(comparison_evidence_relation_version_id, "comparison_evidence_relation_version_id")
        if subject_id == comparison_id:
            raise ValueError("independence assessment requires two different evidence relations")
        state = _enum(independence_state, "independence_state", INDEPENDENCE_STATES)
        rationale = _enum(rationale_code, "rationale_code", INDEPENDENCE_RATIONALE_CODES)
        self._validate_state_rationale(state, rationale)
        method = _required(assessment_method, "assessment_method")
        method_version = _required(assessment_version, "assessment_version")
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)

        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                "SELECT evidence_relation_version_id,semantic_claim_version_id FROM semantic_evidence_relation_versions WHERE evidence_relation_version_id IN (?,?)",
                (subject_id, comparison_id),
            ).fetchall()
            if len(rows) != 2:
                raise ValueError("both evidence relation versions must exist")
            if any(row[1] != claim_id for row in rows):
                raise ValueError("evidence relation versions must belong to the semantic claim version")
            previous = connection.execute(
                "SELECT independence_assessment_version_id,assessment_version_number FROM semantic_independence_assessment_versions WHERE independence_assessment_id=? ORDER BY assessment_version_number DESC LIMIT 1",
                (assessment_id,),
            ).fetchone()
            version = 1 if previous is None else int(previous[1]) + 1
            supersedes = None if previous is None else previous[0]
            version_id = _stable_version_id("independence-assessment-version", assessment_id, version)
            connection.execute(
                """INSERT INTO semantic_independence_assessment_versions(
                    independence_assessment_version_id,independence_assessment_id,assessment_version_number,
                    semantic_claim_version_id,subject_evidence_relation_version_id,comparison_evidence_relation_version_id,
                    independence_state,rationale_code,assessment_method,assessment_version,note,
                    supersedes_assessment_version_id,created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (version_id, assessment_id, version, claim_id, subject_id, comparison_id,
                 state, rationale, method, method_version, normalized_note, supersedes,
                 timestamp.isoformat()),
            )
        return IndependenceAssessmentVersion(
            version_id, assessment_id, version, claim_id, subject_id, comparison_id,
            state, rationale, method, method_version, normalized_note, supersedes, timestamp,
        )

    def assessment_current(self, independence_assessment_id: str) -> IndependenceAssessmentVersion | None:
        history = self.assessment_history(independence_assessment_id)
        return history[-1] if history else None

    def assessment_history(self, independence_assessment_id: str) -> tuple[IndependenceAssessmentVersion, ...]:
        assessment_id = _required(independence_assessment_id, "independence_assessment_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT independence_assessment_version_id,independence_assessment_id,
                    assessment_version_number,semantic_claim_version_id,
                    subject_evidence_relation_version_id,comparison_evidence_relation_version_id,
                    independence_state,rationale_code,assessment_method,assessment_version,note,
                    supersedes_assessment_version_id,created_at
                    FROM semantic_independence_assessment_versions
                    WHERE independence_assessment_id=? ORDER BY assessment_version_number""",
                (assessment_id,),
            ).fetchall()
        return tuple(self._assessment_from_row(row) for row in rows)

    def infer_pair_fail_closed(
        self,
        *,
        subject_evidence_relation_version_id: str,
        comparison_evidence_relation_version_id: str,
    ) -> tuple[str, str]:
        """Infer only provable non-independence or uncertainty; never INDEPENDENT."""
        subject_id = _required(subject_evidence_relation_version_id, "subject_evidence_relation_version_id")
        comparison_id = _required(comparison_evidence_relation_version_id, "comparison_evidence_relation_version_id")
        if subject_id == comparison_id:
            return "NOT_INDEPENDENT", "DUPLICATE_OR_SAME_ORIGIN"
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT evidence_relation_version_id,semantic_claim_version_id,
                    evidence_provenance_entity_version_id,relation_type
                    FROM semantic_evidence_relation_versions
                    WHERE evidence_relation_version_id IN (?,?)""",
                (subject_id, comparison_id),
            ).fetchall()
            if len(rows) != 2:
                raise ValueError("both evidence relation versions must exist")
            by_id = {row[0]: row for row in rows}
            subject, comparison = by_id[subject_id], by_id[comparison_id]
            if subject[1] != comparison[1]:
                raise ValueError("evidence relation versions must belong to the same semantic claim")
            if subject[3] == "DUPLICATE_OR_SAME_ORIGIN" or comparison[3] == "DUPLICATE_OR_SAME_ORIGIN":
                return "NOT_INDEPENDENT", "DUPLICATE_OR_SAME_ORIGIN"
            left_id, right_id = subject[2], comparison[2]
            entities = connection.execute(
                "SELECT provenance_entity_version_id,provenance_entity_id,entity_kind FROM semantic_provenance_entity_versions WHERE provenance_entity_version_id IN (?,?)",
                (left_id, right_id),
            ).fetchall()
            if len(entities) != 2:
                raise ValueError("evidence provenance entities must exist")
            by_entity = {row[0]: row for row in entities}
            left, right = by_entity[left_id], by_entity[right_id]
            if left[1] == right[1]:
                return "NOT_INDEPENDENT", "SAME_UNDERLYING_ORIGIN"
            if "MIXED" in {left[2], right[2]}:
                return "MIXED", "MIXED_ORIGIN"
            if "UNKNOWN" in {left[2], right[2]}:
                return "UNKNOWN", "UNRESOLVED_ORIGIN"
            if self._has_current_derivation_path(connection, left_id, right_id):
                return "NOT_INDEPENDENT", "DERIVATION_PATH"
        return "UNKNOWN", "INSUFFICIENT_PROVENANCE"

    @staticmethod
    def _validate_state_rationale(state: str, rationale: str) -> None:
        allowed = {
            "INDEPENDENT": {"EXPLICIT_DISTINCT_UNDERLYING_ORIGINS", "MANUAL_REVIEW"},
            "NOT_INDEPENDENT": {"SAME_UNDERLYING_ORIGIN", "DERIVATION_PATH", "DUPLICATE_OR_SAME_ORIGIN", "MANUAL_REVIEW"},
            "UNKNOWN": {"UNRESOLVED_ORIGIN", "INSUFFICIENT_PROVENANCE", "MANUAL_REVIEW", "OTHER"},
            "MIXED": {"MIXED_ORIGIN", "MANUAL_REVIEW"},
        }
        if rationale not in allowed[state]:
            raise ValueError(f"rationale_code {rationale} is incompatible with {state}")

    @staticmethod
    def _has_current_derivation_path(connection, start: str, target: str) -> bool:
        rows = connection.execute(
            """SELECT r.subject_entity_version_id,r.object_entity_version_id,r.relation_type
               FROM semantic_provenance_relation_versions r
               JOIN (
                   SELECT provenance_relation_id,MAX(relation_version) AS max_version
                   FROM semantic_provenance_relation_versions
                   GROUP BY provenance_relation_id
               ) current
                 ON current.provenance_relation_id=r.provenance_relation_id
                AND current.max_version=r.relation_version"""
        ).fetchall()
        adjacency: dict[str, set[str]] = {}
        for subject, object_id, relation_type in rows:
            if relation_type not in _DERIVATION_RELATION_TYPES:
                continue
            adjacency.setdefault(subject, set()).add(object_id)
            adjacency.setdefault(object_id, set()).add(subject)
        seen = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency.get(current, ()):
                if neighbor == target:
                    return True
                if neighbor not in seen:
                    seen.add(neighbor)
                    frontier.append(neighbor)
        return False

    @staticmethod
    def _relation_from_row(row) -> SemanticEvidenceRelationVersion:
        return SemanticEvidenceRelationVersion(
            evidence_relation_version_id=row[0], evidence_relation_id=row[1], relation_version=int(row[2]),
            semantic_claim_version_id=row[3], evidence_provenance_entity_version_id=row[4], raw_item_id=row[5],
            relation_type=row[6], assessment_method=row[7], assessment_version=row[8], note=row[9],
            supersedes_relation_version_id=row[10], created_at=datetime.fromisoformat(row[11]),
        )

    @staticmethod
    def _assessment_from_row(row) -> IndependenceAssessmentVersion:
        return IndependenceAssessmentVersion(
            independence_assessment_version_id=row[0], independence_assessment_id=row[1],
            assessment_version_number=int(row[2]), semantic_claim_version_id=row[3],
            subject_evidence_relation_version_id=row[4], comparison_evidence_relation_version_id=row[5],
            independence_state=row[6], rationale_code=row[7], assessment_method=row[8], assessment_version=row[9],
            note=row[10], supersedes_assessment_version_id=row[11], created_at=datetime.fromisoformat(row[12]),
        )
