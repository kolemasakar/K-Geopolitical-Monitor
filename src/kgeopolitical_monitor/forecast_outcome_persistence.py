"""Phase 15.1 append-only forecast outcome-assessment persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import sqlite3
from typing import Iterable

from .database import initialize_database
from .forecast_calibration_contract import OutcomeResolutionState
from .operational_monitoring import _normalize_time, utc_now


P15_1_GATE = "P15_1_FORECAST_OUTCOME_PERSISTENCE_MODEL_VALIDATED"
ASSESSMENT_METHOD = "PROVENANCE_BOUND_OUTCOME_ASSESSMENT"
ASSESSMENT_METHOD_VERSION = "1"
EVIDENCE_KINDS = {"RAW_ITEM", "SEMANTIC_CLAIM", "SEMANTIC_EVIDENCE", "EXTERNAL_REFERENCE"}
PROVENANCE_ROLES = {"OUTCOME_EVIDENCE", "RESOLUTION_CONTEXT"}


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class OutcomeEvidenceReference:
    evidence_kind: str
    evidence_ref: str
    provenance_role: str = "OUTCOME_EVIDENCE"

    def __post_init__(self) -> None:
        kind = _nonempty(self.evidence_kind, "evidence_kind").upper()
        role = _nonempty(self.provenance_role, "provenance_role").upper()
        if kind not in EVIDENCE_KINDS:
            raise ValueError(f"unsupported evidence_kind: {kind}")
        if role not in PROVENANCE_ROLES:
            raise ValueError(f"unsupported provenance_role: {role}")
        object.__setattr__(self, "evidence_kind", kind)
        object.__setattr__(self, "evidence_ref", _nonempty(self.evidence_ref, "evidence_ref"))
        object.__setattr__(self, "provenance_role", role)


@dataclass(frozen=True)
class ForecastOutcomeAssessment:
    assessment_id: str
    forecast_id: str
    assessment_sequence: int
    resolution_state: OutcomeResolutionState | str
    evidence: tuple[OutcomeEvidenceReference, ...]
    explanation: str
    assessed_at: datetime
    assessment_method: str = ASSESSMENT_METHOD
    assessment_method_version: str = ASSESSMENT_METHOD_VERSION
    legacy_outcome_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        forecast_id = _nonempty(self.forecast_id, "forecast_id")
        if int(self.assessment_sequence) <= 0:
            raise ValueError("assessment_sequence must be positive")
        state_raw = (
            self.resolution_state.value
            if isinstance(self.resolution_state, OutcomeResolutionState)
            else _nonempty(self.resolution_state, "resolution_state").upper()
        )
        try:
            state = OutcomeResolutionState(state_raw)
        except ValueError as exc:
            raise ValueError(f"unsupported resolution_state: {state_raw}") from exc
        evidence = tuple(self.evidence)
        if state is OutcomeResolutionState.RESOLVED and not evidence:
            raise ValueError("RESOLVED assessment requires outcome evidence")
        expected_id = _stable_id("foa", forecast_id, str(int(self.assessment_sequence)))
        if self.assessment_id != expected_id:
            raise ValueError("assessment_id must match deterministic forecast assessment identity")
        object.__setattr__(self, "forecast_id", forecast_id)
        object.__setattr__(self, "assessment_sequence", int(self.assessment_sequence))
        object.__setattr__(self, "resolution_state", state)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "explanation", _nonempty(self.explanation, "explanation"))
        object.__setattr__(self, "assessment_method", _nonempty(self.assessment_method, "assessment_method"))
        object.__setattr__(self, "assessment_method_version", _nonempty(self.assessment_method_version, "assessment_method_version"))
        object.__setattr__(self, "legacy_outcome_id", None if self.legacy_outcome_id is None else _nonempty(self.legacy_outcome_id, "legacy_outcome_id"))
        object.__setattr__(self, "assessed_at", _normalize_time(self.assessed_at))
        object.__setattr__(self, "created_at", _normalize_time(self.created_at))

    @classmethod
    def create(
        cls,
        forecast_id: str,
        assessment_sequence: int,
        resolution_state: OutcomeResolutionState | str,
        *,
        evidence: Iterable[OutcomeEvidenceReference] = (),
        explanation: str,
        assessed_at: datetime,
        assessment_method: str = ASSESSMENT_METHOD,
        assessment_method_version: str = ASSESSMENT_METHOD_VERSION,
        legacy_outcome_id: str | None = None,
        created_at: datetime | None = None,
    ) -> "ForecastOutcomeAssessment":
        forecast_id_value = _nonempty(forecast_id, "forecast_id")
        sequence = int(assessment_sequence)
        return cls(
            assessment_id=_stable_id("foa", forecast_id_value, str(sequence)),
            forecast_id=forecast_id_value,
            assessment_sequence=sequence,
            resolution_state=resolution_state,
            evidence=tuple(evidence),
            explanation=explanation,
            assessed_at=assessed_at,
            assessment_method=assessment_method,
            assessment_method_version=assessment_method_version,
            legacy_outcome_id=legacy_outcome_id,
            created_at=created_at or utc_now(),
        )


class SQLiteForecastOutcomeAssessmentRepository:
    """Append-only Phase 15 outcome-assessment repository.

    The legacy M12 forecast_outcomes table remains readable compatibility state;
    it is never rewritten or reinterpreted by this repository.
    """

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    def save(self, assessment: ForecastOutcomeAssessment) -> ForecastOutcomeAssessment:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            if connection.execute(
                "SELECT 1 FROM forecasts WHERE forecast_id = ?", (assessment.forecast_id,)
            ).fetchone() is None:
                raise ValueError("forecast does not exist")
            if assessment.legacy_outcome_id is not None:
                row = connection.execute(
                    "SELECT forecast_id FROM forecast_outcomes WHERE outcome_id = ?",
                    (assessment.legacy_outcome_id,),
                ).fetchone()
                if row is None:
                    raise ValueError("legacy forecast outcome does not exist")
                if str(row[0]) != assessment.forecast_id:
                    raise ValueError("legacy forecast outcome belongs to a different forecast")

            existing = connection.execute(
                """SELECT forecast_id, assessment_sequence, resolution_state,
                          legacy_outcome_id, assessment_method, assessment_method_version,
                          assessed_at, explanation, created_at
                   FROM forecast_outcome_assessments WHERE assessment_id = ?""",
                (assessment.assessment_id,),
            ).fetchone()
            payload = (
                assessment.forecast_id,
                assessment.assessment_sequence,
                assessment.resolution_state.value,
                assessment.legacy_outcome_id,
                assessment.assessment_method,
                assessment.assessment_method_version,
                assessment.assessed_at.isoformat(),
                assessment.explanation,
                assessment.created_at.isoformat(),
            )
            if existing is not None:
                if tuple(existing) != payload:
                    raise ValueError("forecast outcome assessment is immutable")
                return assessment

            connection.execute(
                """INSERT INTO forecast_outcome_assessments(
                       assessment_id, forecast_id, assessment_sequence, resolution_state,
                       legacy_outcome_id, assessment_method, assessment_method_version,
                       assessed_at, explanation, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (assessment.assessment_id, *payload),
            )
            for index, evidence in enumerate(assessment.evidence, start=1):
                connection.execute(
                    """INSERT INTO forecast_outcome_assessment_evidence(
                           assessment_id, evidence_order, evidence_kind, evidence_ref, provenance_role
                       ) VALUES (?, ?, ?, ?, ?)""",
                    (
                        assessment.assessment_id,
                        index,
                        evidence.evidence_kind,
                        evidence.evidence_ref,
                        evidence.provenance_role,
                    ),
                )
        return assessment

    def list_for_forecast(self, forecast_id: str) -> tuple[ForecastOutcomeAssessment, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """SELECT assessment_id, forecast_id, assessment_sequence, resolution_state,
                          legacy_outcome_id, assessment_method, assessment_method_version,
                          assessed_at, explanation, created_at
                   FROM forecast_outcome_assessments
                   WHERE forecast_id = ? ORDER BY assessment_sequence""",
                (_nonempty(forecast_id, "forecast_id"),),
            ).fetchall()
            results: list[ForecastOutcomeAssessment] = []
            for row in rows:
                evidence_rows = connection.execute(
                    """SELECT evidence_kind, evidence_ref, provenance_role
                       FROM forecast_outcome_assessment_evidence
                       WHERE assessment_id = ? ORDER BY evidence_order""",
                    (row[0],),
                ).fetchall()
                results.append(
                    ForecastOutcomeAssessment(
                        assessment_id=str(row[0]),
                        forecast_id=str(row[1]),
                        assessment_sequence=int(row[2]),
                        resolution_state=str(row[3]),
                        legacy_outcome_id=None if row[4] is None else str(row[4]),
                        assessment_method=str(row[5]),
                        assessment_method_version=str(row[6]),
                        assessed_at=datetime.fromisoformat(str(row[7])),
                        explanation=str(row[8]),
                        created_at=datetime.fromisoformat(str(row[9])),
                        evidence=tuple(
                            OutcomeEvidenceReference(str(item[0]), str(item[1]), str(item[2]))
                            for item in evidence_rows
                        ),
                    )
                )
        return tuple(results)
