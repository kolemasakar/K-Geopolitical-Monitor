"""Phase 15.2 provenance-bound forecast outcome resolution.

The resolver is deliberately fail-closed. It verifies that outcome evidence is
persisted and addressable, maps legacy forecast-result vocabulary to the Phase
15 resolution lifecycle, and never writes or promotes canonical factual
verification state.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Iterable

from .database import initialize_database
from .forecast_calibration_contract import (
    OUTCOME_AMBIGUOUS,
    OUTCOME_PARTIAL,
    OUTCOME_RESOLVED,
    OUTCOME_UNRESOLVED,
)
from .forecast_outcome_persistence import (
    ForecastOutcomeAssessment,
    OutcomeEvidenceReference,
    SQLiteForecastOutcomeAssessmentRepository,
)


P15_2_GATE = "P15_2_PROVENANCE_BOUND_OUTCOME_RESOLUTION_VALIDATED"

PERSISTED_EVIDENCE_KINDS = {
    "RAW_ITEM",
    "SEMANTIC_CLAIM",
    "SEMANTIC_EVIDENCE",
}

LEGACY_RESULT_TO_RESOLUTION = {
    "OBSERVED": OUTCOME_RESOLVED,
    "NOT_OBSERVED": OUTCOME_RESOLVED,
    "PARTIAL": OUTCOME_PARTIAL,
    "AMBIGUOUS": OUTCOME_AMBIGUOUS,
}


class OutcomeResolutionError(ValueError):
    """Raised when a resolution request cannot satisfy the P15.2 contract."""


def _lookup_exists(connection: sqlite3.Connection, evidence: OutcomeEvidenceReference) -> bool:
    if evidence.evidence_kind == "RAW_ITEM":
        row = connection.execute(
            "SELECT 1 FROM raw_items WHERE id = ?", (evidence.evidence_ref,)
        ).fetchone()
    elif evidence.evidence_kind == "SEMANTIC_CLAIM":
        row = connection.execute(
            "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id = ?",
            (evidence.evidence_ref,),
        ).fetchone()
    elif evidence.evidence_kind == "SEMANTIC_EVIDENCE":
        row = connection.execute(
            "SELECT 1 FROM semantic_evidence_relation_versions WHERE evidence_relation_version_id = ?",
            (evidence.evidence_ref,),
        ).fetchone()
    else:
        return True
    return row is not None


class ProvenanceBoundOutcomeResolver:
    """Canonical P15.2 resolver for persisted forecast outcome assessments."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))
        self.repository = SQLiteForecastOutcomeAssessmentRepository(self.database_path)

    def resolve(
        self,
        forecast_id: str,
        *,
        assessed_at: datetime,
        explanation: str,
        evidence: Iterable[OutcomeEvidenceReference] = (),
        legacy_outcome_id: str | None = None,
    ) -> ForecastOutcomeAssessment:
        evidence_refs = tuple(evidence)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            if connection.execute(
                "SELECT 1 FROM forecasts WHERE forecast_id = ?", (forecast_id,)
            ).fetchone() is None:
                raise OutcomeResolutionError("forecast does not exist")

            for item in evidence_refs:
                if not _lookup_exists(connection, item):
                    raise OutcomeResolutionError(
                        f"outcome evidence does not exist: {item.evidence_kind}:{item.evidence_ref}"
                    )

            if legacy_outcome_id is None:
                resolution_state = OUTCOME_UNRESOLVED
            else:
                row = connection.execute(
                    "SELECT forecast_id, outcome_state FROM forecast_outcomes WHERE outcome_id = ?",
                    (legacy_outcome_id,),
                ).fetchone()
                if row is None:
                    raise OutcomeResolutionError("legacy forecast outcome does not exist")
                if str(row[0]) != str(forecast_id):
                    raise OutcomeResolutionError("legacy forecast outcome belongs to a different forecast")
                legacy_state = str(row[1]).upper()
                try:
                    resolution_state = LEGACY_RESULT_TO_RESOLUTION[legacy_state]
                except KeyError as exc:
                    raise OutcomeResolutionError(
                        f"unsupported legacy outcome state: {legacy_state}"
                    ) from exc

            if resolution_state == OUTCOME_RESOLVED:
                persisted = [
                    item for item in evidence_refs if item.evidence_kind in PERSISTED_EVIDENCE_KINDS
                ]
                if not persisted:
                    raise OutcomeResolutionError(
                        "RESOLVED outcome requires at least one persisted outcome-evidence reference"
                    )
                if not any(item.provenance_role == "OUTCOME_EVIDENCE" for item in persisted):
                    raise OutcomeResolutionError(
                        "RESOLVED outcome requires persisted evidence with OUTCOME_EVIDENCE provenance role"
                    )

            sequence = int(
                connection.execute(
                    "SELECT COALESCE(MAX(assessment_sequence), 0) + 1 FROM forecast_outcome_assessments WHERE forecast_id = ?",
                    (forecast_id,),
                ).fetchone()[0]
            )

        assessment = ForecastOutcomeAssessment.create(
            forecast_id,
            sequence,
            resolution_state,
            evidence=evidence_refs,
            explanation=explanation,
            assessed_at=assessed_at,
            legacy_outcome_id=legacy_outcome_id,
        )
        return self.repository.save(assessment)
