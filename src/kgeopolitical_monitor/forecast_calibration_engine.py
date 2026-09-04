"""Phase 15.3 provenance-bound forecast calibration engine.

This layer creates immutable, scoreable observations from exact forecast/scenario
versions and exact Phase 15 outcome assessments. It deliberately does not update
legacy M12 evaluation/calibration history and never writes factual-verification
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import sqlite3

from .database import initialize_database
from .forecast_calibration_contract import OUTCOME_RESOLVED
from .forecast_metrics import calculate_brier_score
from .operational_monitoring import _normalize_time, utc_now


P15_3_GATE = "P15_3_CALIBRATION_ENGINE_VALIDATED"
SCORING_METHOD = "BINARY_ONE_VS_REST_BRIER_RELIABILITY"
SCORING_METHOD_VERSION = "1"
DEFAULT_RELIABILITY_BUCKET_COUNT = 10

PERSISTED_EVIDENCE_KINDS = {
    "RAW_ITEM",
    "SEMANTIC_CLAIM",
    "SEMANTIC_EVIDENCE",
}


class CalibrationEngineError(ValueError):
    """Raised when a requested calibration observation is not safely scoreable."""


def _nonempty(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise CalibrationEngineError(f"{field_name} must not be empty")
    return normalized


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def reliability_bucket(probability: float, bucket_count: int = DEFAULT_RELIABILITY_BUCKET_COUNT) -> int:
    """Return a zero-based equal-width reliability bucket.

    Probability 1.0 is explicitly assigned to the final bucket rather than a
    non-existent bucket at index ``bucket_count``.
    """

    probability_value = float(probability)
    count = int(bucket_count)
    if not 0.0 <= probability_value <= 1.0:
        raise CalibrationEngineError("probability must be between 0 and 1")
    if count < 2:
        raise CalibrationEngineError("reliability bucket_count must be at least 2")
    return min(int(probability_value * count), count - 1)


@dataclass(frozen=True)
class CalibrationObservation:
    observation_id: str
    assessment_id: str
    forecast_id: str
    forecast_version_id: str
    scenario_version_id: str
    legacy_outcome_id: str
    horizon: str
    scenario_type: str
    scenario_label: str
    legacy_outcome_state: str
    observed_value: float
    raw_probability: float
    calibrated_probability: float
    brier_score_raw: float
    brier_score_calibrated: float
    raw_reliability_bucket: int
    calibrated_reliability_bucket: int
    reliability_bucket_count: int
    scoring_method: str
    scoring_method_version: str
    evaluated_at: datetime
    created_at: datetime


class ProvenanceBoundCalibrationEngine:
    """Create immutable P15.3 Brier/reliability observations.

    The engine scores only ``RESOLVED`` Phase 15 assessments that are linked to
    a binary legacy outcome (``OBSERVED`` or ``NOT_OBSERVED``) and retain at
    least one addressable persisted ``OUTCOME_EVIDENCE`` reference. Raw and
    calibrated probabilities are always evaluated independently. Scenario
    confidence is intentionally not selected or used.
    """

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        initialize_database(str(self.database_path))

    @staticmethod
    def _evidence_exists(
        connection: sqlite3.Connection,
        evidence_kind: str,
        evidence_ref: str,
    ) -> bool:
        if evidence_kind == "RAW_ITEM":
            row = connection.execute(
                "SELECT 1 FROM raw_items WHERE id = ?", (evidence_ref,)
            ).fetchone()
        elif evidence_kind == "SEMANTIC_CLAIM":
            row = connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id = ?",
                (evidence_ref,),
            ).fetchone()
        elif evidence_kind == "SEMANTIC_EVIDENCE":
            row = connection.execute(
                "SELECT 1 FROM semantic_evidence_relation_versions WHERE evidence_relation_version_id = ?",
                (evidence_ref,),
            ).fetchone()
        else:
            return False
        return row is not None

    def _assert_scoreable_provenance(
        self,
        connection: sqlite3.Connection,
        assessment_id: str,
    ) -> None:
        evidence_rows = connection.execute(
            """SELECT evidence_kind, evidence_ref, provenance_role
               FROM forecast_outcome_assessment_evidence
               WHERE assessment_id = ? ORDER BY evidence_order""",
            (assessment_id,),
        ).fetchall()
        scoreable = [
            (str(kind), str(ref))
            for kind, ref, role in evidence_rows
            if str(role) == "OUTCOME_EVIDENCE" and str(kind) in PERSISTED_EVIDENCE_KINDS
        ]
        if not scoreable:
            raise CalibrationEngineError(
                "RESOLVED assessment lacks persisted OUTCOME_EVIDENCE provenance"
            )
        missing = [
            f"{kind}:{ref}"
            for kind, ref in scoreable
            if not self._evidence_exists(connection, kind, ref)
        ]
        if missing:
            raise CalibrationEngineError(
                "persisted outcome evidence is no longer addressable: " + ", ".join(missing)
            )

    @staticmethod
    def _row_to_observation(row: tuple[object, ...]) -> CalibrationObservation:
        return CalibrationObservation(
            observation_id=str(row[0]),
            assessment_id=str(row[1]),
            forecast_id=str(row[2]),
            forecast_version_id=str(row[3]),
            scenario_version_id=str(row[4]),
            legacy_outcome_id=str(row[5]),
            horizon=str(row[6]),
            scenario_type=str(row[7]),
            scenario_label=str(row[8]),
            legacy_outcome_state=str(row[9]),
            observed_value=float(row[10]),
            raw_probability=float(row[11]),
            calibrated_probability=float(row[12]),
            brier_score_raw=float(row[13]),
            brier_score_calibrated=float(row[14]),
            raw_reliability_bucket=int(row[15]),
            calibrated_reliability_bucket=int(row[16]),
            reliability_bucket_count=int(row[17]),
            scoring_method=str(row[18]),
            scoring_method_version=str(row[19]),
            evaluated_at=datetime.fromisoformat(str(row[20])),
            created_at=datetime.fromisoformat(str(row[21])),
        )

    @staticmethod
    def _select_observation(
        connection: sqlite3.Connection,
        observation_id: str,
    ) -> CalibrationObservation | None:
        row = connection.execute(
            """SELECT observation_id, assessment_id, forecast_id, forecast_version_id,
                      scenario_version_id, legacy_outcome_id, horizon, scenario_type,
                      scenario_label, legacy_outcome_state, observed_value,
                      raw_probability, calibrated_probability, brier_score_raw,
                      brier_score_calibrated, raw_reliability_bucket,
                      calibrated_reliability_bucket, reliability_bucket_count,
                      scoring_method, scoring_method_version, evaluated_at, created_at
               FROM forecast_calibration_observations
               WHERE observation_id = ?""",
            (observation_id,),
        ).fetchone()
        if row is None:
            return None
        return ProvenanceBoundCalibrationEngine._row_to_observation(row)

    @staticmethod
    def _immutable_payload(observation: CalibrationObservation) -> tuple[object, ...]:
        """Fields whose mismatch means the underlying scoreable fact changed."""

        return (
            observation.assessment_id,
            observation.forecast_id,
            observation.forecast_version_id,
            observation.scenario_version_id,
            observation.legacy_outcome_id,
            observation.horizon,
            observation.scenario_type,
            observation.scenario_label,
            observation.legacy_outcome_state,
            observation.observed_value,
            observation.raw_probability,
            observation.calibrated_probability,
            observation.brier_score_raw,
            observation.brier_score_calibrated,
            observation.raw_reliability_bucket,
            observation.calibrated_reliability_bucket,
            observation.reliability_bucket_count,
            observation.scoring_method,
            observation.scoring_method_version,
        )

    def score_assessment(
        self,
        assessment_id: str,
        forecast_version_id: str,
        *,
        reliability_bucket_count: int = DEFAULT_RELIABILITY_BUCKET_COUNT,
        evaluated_at: datetime | None = None,
    ) -> tuple[CalibrationObservation, ...]:
        assessment_id_value = _nonempty(assessment_id, "assessment_id")
        forecast_version_id_value = _nonempty(forecast_version_id, "forecast_version_id")
        bucket_count = int(reliability_bucket_count)
        if bucket_count < 2:
            raise CalibrationEngineError("reliability bucket_count must be at least 2")
        evaluation_time = _normalize_time(evaluated_at or utc_now())

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")

            assessment_row = connection.execute(
                """SELECT forecast_id, resolution_state, legacy_outcome_id
                   FROM forecast_outcome_assessments WHERE assessment_id = ?""",
                (assessment_id_value,),
            ).fetchone()
            if assessment_row is None:
                raise CalibrationEngineError("forecast outcome assessment does not exist")
            forecast_id = str(assessment_row[0])
            resolution_state = str(assessment_row[1])
            legacy_outcome_id = assessment_row[2]
            if resolution_state != OUTCOME_RESOLVED:
                raise CalibrationEngineError(
                    f"outcome assessment is not scoreable: resolution_state={resolution_state}"
                )
            if legacy_outcome_id is None:
                raise CalibrationEngineError(
                    "RESOLVED assessment requires a binary legacy outcome link for scoring"
                )
            legacy_outcome_id_value = str(legacy_outcome_id)
            self._assert_scoreable_provenance(connection, assessment_id_value)

            outcome_row = connection.execute(
                """SELECT forecast_id, outcome_state, observed_scenario_type
                   FROM forecast_outcomes WHERE outcome_id = ?""",
                (legacy_outcome_id_value,),
            ).fetchone()
            if outcome_row is None:
                raise CalibrationEngineError("linked legacy forecast outcome does not exist")
            if str(outcome_row[0]) != forecast_id:
                raise CalibrationEngineError("linked legacy outcome belongs to a different forecast")
            legacy_state = str(outcome_row[1]).upper()
            observed_scenario_type = (
                None if outcome_row[2] is None else str(outcome_row[2]).lower()
            )
            if legacy_state not in {"OBSERVED", "NOT_OBSERVED"}:
                raise CalibrationEngineError(
                    f"linked legacy outcome is not binary-scoreable: {legacy_state}"
                )

            version_row = connection.execute(
                """SELECT fv.forecast_id, f.horizon
                   FROM forecast_versions fv
                   JOIN forecasts f ON f.forecast_id = fv.forecast_id
                   WHERE fv.forecast_version_id = ?""",
                (forecast_version_id_value,),
            ).fetchone()
            if version_row is None:
                raise CalibrationEngineError("forecast version does not exist")
            if str(version_row[0]) != forecast_id:
                raise CalibrationEngineError("forecast version belongs to a different forecast")
            horizon = str(version_row[1])

            # scenario_confidence is intentionally absent from this query.
            scenario_rows = connection.execute(
                """SELECT scenario_version_id, scenario_type, label,
                          raw_probability, calibrated_probability
                   FROM forecast_scenario_versions
                   WHERE forecast_version_id = ?
                   ORDER BY scenario_type, label, scenario_version_id""",
                (forecast_version_id_value,),
            ).fetchall()
            if not scenario_rows:
                raise CalibrationEngineError("forecast version has no scenarios to score")

            if legacy_state == "OBSERVED":
                if observed_scenario_type is None:
                    raise CalibrationEngineError(
                        "OBSERVED legacy outcome is missing observed_scenario_type"
                    )
                matches = [
                    row for row in scenario_rows if str(row[1]).lower() == observed_scenario_type
                ]
                if len(matches) != 1:
                    raise CalibrationEngineError(
                        "OBSERVED outcome must map to exactly one scenario in the scored forecast version"
                    )
            elif observed_scenario_type is not None:
                raise CalibrationEngineError(
                    "NOT_OBSERVED legacy outcome must not set observed_scenario_type"
                )

            observations: list[CalibrationObservation] = []
            for scenario_row in scenario_rows:
                scenario_version_id = str(scenario_row[0])
                scenario_type = str(scenario_row[1]).lower()
                scenario_label = str(scenario_row[2])
                raw_probability = float(scenario_row[3])
                calibrated_probability = float(scenario_row[4])
                observed_value = (
                    1.0
                    if legacy_state == "OBSERVED" and scenario_type == observed_scenario_type
                    else 0.0
                )
                raw_brier = calculate_brier_score(raw_probability, observed_value)
                calibrated_brier = calculate_brier_score(calibrated_probability, observed_value)
                raw_bucket = reliability_bucket(raw_probability, bucket_count)
                calibrated_bucket = reliability_bucket(calibrated_probability, bucket_count)
                observation_id = _stable_id(
                    "fcalobs",
                    assessment_id_value,
                    scenario_version_id,
                    SCORING_METHOD,
                    SCORING_METHOD_VERSION,
                    str(bucket_count),
                )
                candidate = CalibrationObservation(
                    observation_id=observation_id,
                    assessment_id=assessment_id_value,
                    forecast_id=forecast_id,
                    forecast_version_id=forecast_version_id_value,
                    scenario_version_id=scenario_version_id,
                    legacy_outcome_id=legacy_outcome_id_value,
                    horizon=horizon,
                    scenario_type=scenario_type,
                    scenario_label=scenario_label,
                    legacy_outcome_state=legacy_state,
                    observed_value=observed_value,
                    raw_probability=raw_probability,
                    calibrated_probability=calibrated_probability,
                    brier_score_raw=raw_brier,
                    brier_score_calibrated=calibrated_brier,
                    raw_reliability_bucket=raw_bucket,
                    calibrated_reliability_bucket=calibrated_bucket,
                    reliability_bucket_count=bucket_count,
                    scoring_method=SCORING_METHOD,
                    scoring_method_version=SCORING_METHOD_VERSION,
                    evaluated_at=evaluation_time,
                    created_at=evaluation_time,
                )

                existing = self._select_observation(connection, observation_id)
                if existing is not None:
                    if self._immutable_payload(existing) != self._immutable_payload(candidate):
                        raise CalibrationEngineError(
                            "existing calibration observation conflicts with current immutable inputs"
                        )
                    observations.append(existing)
                    continue

                connection.execute(
                    """INSERT INTO forecast_calibration_observations(
                           observation_id, assessment_id, forecast_id, forecast_version_id,
                           scenario_version_id, legacy_outcome_id, horizon, scenario_type,
                           scenario_label, legacy_outcome_state, observed_value,
                           raw_probability, calibrated_probability, brier_score_raw,
                           brier_score_calibrated, raw_reliability_bucket,
                           calibrated_reliability_bucket, reliability_bucket_count,
                           scoring_method, scoring_method_version, evaluated_at, created_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        candidate.observation_id,
                        candidate.assessment_id,
                        candidate.forecast_id,
                        candidate.forecast_version_id,
                        candidate.scenario_version_id,
                        candidate.legacy_outcome_id,
                        candidate.horizon,
                        candidate.scenario_type,
                        candidate.scenario_label,
                        candidate.legacy_outcome_state,
                        candidate.observed_value,
                        candidate.raw_probability,
                        candidate.calibrated_probability,
                        candidate.brier_score_raw,
                        candidate.brier_score_calibrated,
                        candidate.raw_reliability_bucket,
                        candidate.calibrated_reliability_bucket,
                        candidate.reliability_bucket_count,
                        candidate.scoring_method,
                        candidate.scoring_method_version,
                        candidate.evaluated_at.isoformat(),
                        candidate.created_at.isoformat(),
                    ),
                )
                observations.append(candidate)

        return tuple(observations)

    def list_for_assessment(self, assessment_id: str) -> tuple[CalibrationObservation, ...]:
        assessment_id_value = _nonempty(assessment_id, "assessment_id")
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """SELECT observation_id, assessment_id, forecast_id, forecast_version_id,
                          scenario_version_id, legacy_outcome_id, horizon, scenario_type,
                          scenario_label, legacy_outcome_state, observed_value,
                          raw_probability, calibrated_probability, brier_score_raw,
                          brier_score_calibrated, raw_reliability_bucket,
                          calibrated_reliability_bucket, reliability_bucket_count,
                          scoring_method, scoring_method_version, evaluated_at, created_at
                   FROM forecast_calibration_observations
                   WHERE assessment_id = ?
                   ORDER BY scenario_type, scenario_label, scenario_version_id""",
                (assessment_id_value,),
            ).fetchall()
        return tuple(self._row_to_observation(row) for row in rows)
