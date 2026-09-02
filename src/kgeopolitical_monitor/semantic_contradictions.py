"""Phase 13 P13.4 typed contradiction model and resolution lifecycle.

This additive semantic layer records typed contradictions between immutable
P13.1 semantic claim versions and optional links to current P13.3 evidence
relation versions. Contradiction lifecycle state is analytical/auditable only:
it does not decide factual truth, promote verification state, or calculate
factual/coverage confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SEMANTIC_CONTRADICTION_MODEL_VERSION = "P13.4-1.0"
CONTRADICTION_DIMENSIONS = (
    "OCCURRENCE_EXISTENCE",
    "ATTRIBUTION_RESPONSIBILITY",
    "ACTOR_IDENTITY",
    "QUANTITY_VALUE",
    "TIME",
    "LOCATION",
    "STATUS_OUTCOME",
    "SCOPE_EXTENT",
    "CAUSAL_INTERPRETATION",
    "OTHER",
)
CONTRADICTION_LIFECYCLE_STATES = ("DETECTED", "UNRESOLVED", "EVOLVING", "RESOLVED")
RECONCILIATION_CODES = (
    "NONE",
    "NEW_EVIDENCE",
    "OCCURRENCE_RECONCILED",
    "SCOPE_RECONCILED",
    "TIME_RECONCILED",
    "LOCATION_RECONCILED",
    "ATTRIBUTION_RECONCILED",
    "QUANTITY_RECONCILED",
    "ACTOR_IDENTITY_RECONCILED",
    "STATUS_UPDATED",
    "CAUSAL_INTERPRETATION_RECONCILED",
    "SUPERSEDED_INFORMATION",
    "MANUAL_REVIEW",
    "OTHER",
)
CONTRADICTION_EVIDENCE_SIDES = ("LEFT", "RIGHT")
CONTRADICTION_EVIDENCE_LINK_ROLES = (
    "CLAIM_EVIDENCE",
    "CONTRADICTION_TRIGGER",
    "QUALIFIER",
    "RESOLUTION_CONTEXT",
)


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


def _stable_version_id(contradiction_id: str, version: int) -> str:
    digest = sha256(f"{contradiction_id}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"semantic-contradiction-version-{digest}"


def _stable_evidence_link_id(
    contradiction_version_id: str,
    evidence_relation_version_id: str,
    claim_side: str,
    link_role: str,
) -> str:
    digest = sha256(
        f"{contradiction_version_id}:{evidence_relation_version_id}:{claim_side}:{link_role}".encode("utf-8")
    ).hexdigest()[:24]
    return f"semantic-contradiction-evidence-link-{digest}"


@dataclass(frozen=True)
class SemanticContradictionVersion:
    contradiction_version_id: str
    contradiction_id: str
    contradiction_version: int
    left_semantic_claim_version_id: str
    right_semantic_claim_version_id: str
    contradiction_dimension: str
    lifecycle_state: str
    reconciliation_code: str
    assessment_method: str
    assessment_version: str
    note: str | None
    supersedes_contradiction_version_id: str | None
    created_at: datetime

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def determines_factual_truth(self) -> bool:
        return False

    @property
    def factual_confidence(self) -> None:
        return None


@dataclass(frozen=True)
class SemanticContradictionEvidenceLink:
    contradiction_evidence_link_id: str
    contradiction_version_id: str
    evidence_relation_version_id: str
    claim_side: str
    link_role: str
    note: str | None
    created_at: datetime

    @property
    def changes_verification_state(self) -> bool:
        return False


class SemanticContradictionService:
    """Append-only P13.4 contradiction persistence and evidence linkage."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def record_version(
        self,
        contradiction_id: str,
        *,
        left_semantic_claim_version_id: str,
        right_semantic_claim_version_id: str,
        contradiction_dimension: str,
        lifecycle_state: str,
        reconciliation_code: str = "NONE",
        assessment_method: str,
        assessment_version: str,
        note: str | None = None,
        created_at: datetime,
    ) -> SemanticContradictionVersion:
        identity = _required(contradiction_id, "contradiction_id")
        left_id = _required(left_semantic_claim_version_id, "left_semantic_claim_version_id")
        right_id = _required(right_semantic_claim_version_id, "right_semantic_claim_version_id")
        if left_id == right_id:
            raise ValueError("contradiction requires two different semantic claim versions")
        dimension = _enum(contradiction_dimension, "contradiction_dimension", CONTRADICTION_DIMENSIONS)
        state = _enum(lifecycle_state, "lifecycle_state", CONTRADICTION_LIFECYCLE_STATES)
        reconciliation = _enum(reconciliation_code, "reconciliation_code", RECONCILIATION_CODES)
        method = _required(assessment_method, "assessment_method")
        method_version = _required(assessment_version, "assessment_version")
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)
        self._validate_lifecycle(state, reconciliation, normalized_note)

        with runtime_database_connection(self.database_path) as connection:
            claims = connection.execute(
                "SELECT semantic_claim_version_id FROM semantic_claim_versions WHERE semantic_claim_version_id IN (?, ?)",
                (left_id, right_id),
            ).fetchall()
            if len(claims) != 2:
                raise ValueError("both semantic claim versions must exist")

            previous = connection.execute(
                """SELECT contradiction_version_id, contradiction_version,
                          left_semantic_claim_version_id, right_semantic_claim_version_id,
                          contradiction_dimension
                   FROM semantic_contradiction_versions
                   WHERE contradiction_id=?
                   ORDER BY contradiction_version DESC LIMIT 1""",
                (identity,),
            ).fetchone()
            if previous is None:
                version = 1
                supersedes = None
            else:
                if (previous[2], previous[3], previous[4]) != (left_id, right_id, dimension):
                    raise ValueError(
                        "contradiction identity cannot change claim versions or contradiction dimension"
                    )
                version = int(previous[1]) + 1
                supersedes = previous[0]

            version_id = _stable_version_id(identity, version)
            connection.execute(
                """INSERT INTO semantic_contradiction_versions(
                    contradiction_version_id, contradiction_id, contradiction_version,
                    left_semantic_claim_version_id, right_semantic_claim_version_id,
                    contradiction_dimension, lifecycle_state, reconciliation_code,
                    assessment_method, assessment_version, note,
                    supersedes_contradiction_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    version_id,
                    identity,
                    version,
                    left_id,
                    right_id,
                    dimension,
                    state,
                    reconciliation,
                    method,
                    method_version,
                    normalized_note,
                    supersedes,
                    timestamp.isoformat(),
                ),
            )

        return SemanticContradictionVersion(
            contradiction_version_id=version_id,
            contradiction_id=identity,
            contradiction_version=version,
            left_semantic_claim_version_id=left_id,
            right_semantic_claim_version_id=right_id,
            contradiction_dimension=dimension,
            lifecycle_state=state,
            reconciliation_code=reconciliation,
            assessment_method=method,
            assessment_version=method_version,
            note=normalized_note,
            supersedes_contradiction_version_id=supersedes,
            created_at=timestamp,
        )

    def current(self, contradiction_id: str) -> SemanticContradictionVersion | None:
        history = self.history(contradiction_id)
        return history[-1] if history else None

    def history(self, contradiction_id: str) -> tuple[SemanticContradictionVersion, ...]:
        identity = _required(contradiction_id, "contradiction_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT contradiction_version_id, contradiction_id, contradiction_version,
                          left_semantic_claim_version_id, right_semantic_claim_version_id,
                          contradiction_dimension, lifecycle_state, reconciliation_code,
                          assessment_method, assessment_version, note,
                          supersedes_contradiction_version_id, created_at
                   FROM semantic_contradiction_versions
                   WHERE contradiction_id=? ORDER BY contradiction_version""",
                (identity,),
            ).fetchall()
        return tuple(self._contradiction_from_row(row) for row in rows)

    def contradictions_for_claim(
        self, semantic_claim_version_id: str
    ) -> tuple[SemanticContradictionVersion, ...]:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id=?",
                (claim_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")
            rows = connection.execute(
                """SELECT c.contradiction_version_id, c.contradiction_id, c.contradiction_version,
                          c.left_semantic_claim_version_id, c.right_semantic_claim_version_id,
                          c.contradiction_dimension, c.lifecycle_state, c.reconciliation_code,
                          c.assessment_method, c.assessment_version, c.note,
                          c.supersedes_contradiction_version_id, c.created_at
                   FROM semantic_contradiction_versions c
                   JOIN (
                       SELECT contradiction_id, MAX(contradiction_version) AS max_version
                       FROM semantic_contradiction_versions
                       GROUP BY contradiction_id
                   ) latest
                     ON latest.contradiction_id=c.contradiction_id
                    AND latest.max_version=c.contradiction_version
                   WHERE c.left_semantic_claim_version_id=? OR c.right_semantic_claim_version_id=?
                   ORDER BY c.contradiction_id""",
                (claim_id, claim_id),
            ).fetchall()
        return tuple(self._contradiction_from_row(row) for row in rows)

    def record_evidence_link(
        self,
        *,
        contradiction_version_id: str,
        evidence_relation_version_id: str,
        claim_side: str,
        link_role: str,
        note: str | None = None,
        created_at: datetime,
    ) -> SemanticContradictionEvidenceLink:
        contradiction_version = _required(contradiction_version_id, "contradiction_version_id")
        evidence_version = _required(evidence_relation_version_id, "evidence_relation_version_id")
        side = _enum(claim_side, "claim_side", CONTRADICTION_EVIDENCE_SIDES)
        role = _enum(link_role, "link_role", CONTRADICTION_EVIDENCE_LINK_ROLES)
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)

        with runtime_database_connection(self.database_path) as connection:
            contradiction = connection.execute(
                """SELECT left_semantic_claim_version_id, right_semantic_claim_version_id
                   FROM semantic_contradiction_versions WHERE contradiction_version_id=?""",
                (contradiction_version,),
            ).fetchone()
            if contradiction is None:
                raise ValueError("contradiction version does not exist")

            evidence = connection.execute(
                """SELECT evidence_relation_id, relation_version, semantic_claim_version_id
                   FROM semantic_evidence_relation_versions WHERE evidence_relation_version_id=?""",
                (evidence_version,),
            ).fetchone()
            if evidence is None:
                raise ValueError("evidence relation version does not exist")
            current_version = connection.execute(
                "SELECT MAX(relation_version) FROM semantic_evidence_relation_versions WHERE evidence_relation_id=?",
                (evidence[0],),
            ).fetchone()[0]
            if int(evidence[1]) != int(current_version):
                raise ValueError("contradiction evidence links require the current evidence relation version")

            expected_claim_id = contradiction[0] if side == "LEFT" else contradiction[1]
            if evidence[2] != expected_claim_id:
                raise ValueError("evidence relation claim does not match contradiction claim side")

            link_id = _stable_evidence_link_id(contradiction_version, evidence_version, side, role)
            existing = connection.execute(
                """SELECT note, created_at FROM semantic_contradiction_evidence_links
                   WHERE contradiction_evidence_link_id=?""",
                (link_id,),
            ).fetchone()
            if existing is None:
                connection.execute(
                    """INSERT INTO semantic_contradiction_evidence_links(
                        contradiction_evidence_link_id, contradiction_version_id,
                        evidence_relation_version_id, claim_side, link_role, note, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        link_id,
                        contradiction_version,
                        evidence_version,
                        side,
                        role,
                        normalized_note,
                        timestamp.isoformat(),
                    ),
                )
            else:
                if existing[0] != normalized_note:
                    raise ValueError("existing contradiction evidence link is immutable and differs")
                timestamp = datetime.fromisoformat(existing[1])

        return SemanticContradictionEvidenceLink(
            contradiction_evidence_link_id=link_id,
            contradiction_version_id=contradiction_version,
            evidence_relation_version_id=evidence_version,
            claim_side=side,
            link_role=role,
            note=normalized_note,
            created_at=timestamp,
        )

    def evidence_links(
        self, contradiction_version_id: str
    ) -> tuple[SemanticContradictionEvidenceLink, ...]:
        version_id = _required(contradiction_version_id, "contradiction_version_id")
        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_contradiction_versions WHERE contradiction_version_id=?",
                (version_id,),
            ).fetchone() is None:
                raise ValueError("contradiction version does not exist")
            rows = connection.execute(
                """SELECT contradiction_evidence_link_id, contradiction_version_id,
                          evidence_relation_version_id, claim_side, link_role, note, created_at
                   FROM semantic_contradiction_evidence_links
                   WHERE contradiction_version_id=?
                   ORDER BY claim_side, link_role, evidence_relation_version_id""",
                (version_id,),
            ).fetchall()
        return tuple(
            SemanticContradictionEvidenceLink(
                contradiction_evidence_link_id=row[0],
                contradiction_version_id=row[1],
                evidence_relation_version_id=row[2],
                claim_side=row[3],
                link_role=row[4],
                note=row[5],
                created_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        )

    @staticmethod
    def _validate_lifecycle(state: str, reconciliation: str, note: str | None) -> None:
        if state == "RESOLVED":
            if reconciliation == "NONE":
                raise ValueError("RESOLVED contradiction requires a reconciliation code")
            if note is None:
                raise ValueError("RESOLVED contradiction requires an explanatory note")
        elif reconciliation != "NONE":
            raise ValueError("non-RESOLVED contradiction must use reconciliation_code NONE")

    @staticmethod
    def _contradiction_from_row(row) -> SemanticContradictionVersion:
        return SemanticContradictionVersion(
            contradiction_version_id=row[0],
            contradiction_id=row[1],
            contradiction_version=int(row[2]),
            left_semantic_claim_version_id=row[3],
            right_semantic_claim_version_id=row[4],
            contradiction_dimension=row[5],
            lifecycle_state=row[6],
            reconciliation_code=row[7],
            assessment_method=row[8],
            assessment_version=row[9],
            note=row[10],
            supersedes_contradiction_version_id=row[11],
            created_at=datetime.fromisoformat(row[12]),
        )
