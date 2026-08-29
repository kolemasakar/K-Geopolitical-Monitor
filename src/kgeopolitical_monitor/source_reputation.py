"""Post-Phase-11 E2 durable source reputation and status history.

Source reputation is contextual metadata about a publisher/source. It is not a truth
operator and does not modify M8 evidence independence or verification state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3
from typing import Iterable

from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time, utc_now


SOURCE_STATUSES = {
    "ACTIVE",
    "WATCH",
    "COMPROMISED",
    "RESTRICTED",
    "SUSPENDED",
    "RESTORED",
    "RETIRED",
}
ADVERSE_STATUSES = {"COMPROMISED", "RESTRICTED", "SUSPENDED"}
RELIABILITY_RATINGS = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}


@dataclass(frozen=True)
class SourceReputationRecord:
    assessment_id: str
    source_id: str
    assessment_version: int
    status: str
    reliability_rating: str
    reason: str
    evidence_refs: tuple[str, ...]
    policy_name: str
    policy_version: str
    assessed_at: datetime
    reviewed_at: datetime
    review_due_at: datetime | None
    supersedes_assessment_id: str | None
    restoration_of_assessment_id: str | None
    created_at: datetime

    @property
    def automatically_false(self) -> bool:
        return False

    @property
    def changes_claim_truth(self) -> bool:
        return False

    @property
    def changes_independent_origin_count(self) -> bool:
        return False

    @property
    def can_describe_claim_or_narrative(self) -> bool:
        return True


def _stable_assessment_id(source_id: str, version: int) -> str:
    digest = sha256(f"{source_id}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"source-reputation-{digest}"


def _normalize_required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_status(value: object) -> str:
    status = _normalize_required(value, "status").upper()
    if status not in SOURCE_STATUSES:
        raise ValueError(f"unsupported source status: {status}")
    return status


def _normalize_rating(value: object) -> str:
    rating = _normalize_required(value, "reliability_rating").upper()
    if rating not in RELIABILITY_RATINGS:
        raise ValueError(f"unsupported reliability rating: {rating}")
    return rating


def _normalize_evidence_refs(values: Iterable[str]) -> tuple[str, ...]:
    normalized = []
    seen = set()
    for value in values:
        ref = str(value).strip()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        normalized.append(ref)
    return tuple(sorted(normalized))


class SourceReputationService:
    """Append-only source reputation/status history with deterministic current state."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def _source_exists(self, source_id: str) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT 1 FROM sources WHERE id = ?",
                (source_id,),
            ).fetchone()
        return row is not None

    def _latest_row(self, source_id: str):
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute(
                """
                SELECT assessment_id, source_id, assessment_version, status,
                       reliability_rating, reason, evidence_refs_json,
                       policy_name, policy_version, assessed_at, reviewed_at,
                       review_due_at, supersedes_assessment_id,
                       restoration_of_assessment_id, created_at
                FROM source_reputation_history
                WHERE source_id = ?
                ORDER BY assessment_version DESC
                LIMIT 1
                """,
                (source_id,),
            ).fetchone()

    def _assessment_row(self, assessment_id: str):
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute(
                """
                SELECT assessment_id, source_id, assessment_version, status,
                       reliability_rating, reason, evidence_refs_json,
                       policy_name, policy_version, assessed_at, reviewed_at,
                       review_due_at, supersedes_assessment_id,
                       restoration_of_assessment_id, created_at
                FROM source_reputation_history
                WHERE assessment_id = ?
                """,
                (assessment_id,),
            ).fetchone()

    def record_assessment(
        self,
        source_id: str,
        *,
        status: str,
        reliability_rating: str,
        reason: str,
        evidence_refs: Iterable[str] = (),
        policy_name: str,
        policy_version: str,
        assessed_at: datetime | None = None,
        reviewed_at: datetime | None = None,
        review_due_at: datetime | None = None,
        restoration_of_assessment_id: str | None = None,
    ) -> SourceReputationRecord:
        normalized_source = _normalize_required(source_id, "source_id")
        if not self._source_exists(normalized_source):
            raise ValueError("source does not exist")

        normalized_status = _normalize_status(status)
        normalized_rating = _normalize_rating(reliability_rating)
        normalized_reason = _normalize_required(reason, "reason")
        normalized_policy = _normalize_required(policy_name, "policy_name")
        normalized_policy_version = _normalize_required(policy_version, "policy_version")
        normalized_refs = _normalize_evidence_refs(evidence_refs)

        assessed = _normalize_time(assessed_at or utc_now())
        reviewed = _normalize_time(reviewed_at or assessed)
        review_due = _normalize_time(review_due_at) if review_due_at is not None else None
        if reviewed < assessed:
            raise ValueError("reviewed_at cannot precede assessed_at")
        if review_due is not None and review_due < reviewed:
            raise ValueError("review_due_at cannot precede reviewed_at")

        latest_row = self._latest_row(normalized_source)
        previous = None if latest_row is None else self._record_from_row(latest_row)
        version = 1 if previous is None else previous.assessment_version + 1
        supersedes = None if previous is None else previous.assessment_id

        restoration_id = (
            _normalize_required(restoration_of_assessment_id, "restoration_of_assessment_id")
            if restoration_of_assessment_id is not None
            else None
        )
        if normalized_status == "RESTORED":
            if restoration_id is None:
                raise ValueError("RESTORED status requires restoration_of_assessment_id")
            restoration_row = self._assessment_row(restoration_id)
            if restoration_row is None:
                raise ValueError("restoration assessment does not exist")
            restoration_record = self._record_from_row(restoration_row)
            if restoration_record.source_id != normalized_source:
                raise ValueError("restoration assessment belongs to another source")
            if restoration_record.status not in ADVERSE_STATUSES:
                raise ValueError("RESTORED must reference an adverse assessment")
        elif restoration_id is not None:
            raise ValueError("restoration_of_assessment_id is only valid for RESTORED")

        assessment_id = _stable_assessment_id(normalized_source, version)
        created = assessed
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO source_reputation_history(
                    assessment_id, source_id, assessment_version, status,
                    reliability_rating, reason, evidence_refs_json,
                    policy_name, policy_version, assessed_at, reviewed_at,
                    review_due_at, supersedes_assessment_id,
                    restoration_of_assessment_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_id,
                    normalized_source,
                    version,
                    normalized_status,
                    normalized_rating,
                    normalized_reason,
                    json.dumps(normalized_refs),
                    normalized_policy,
                    normalized_policy_version,
                    assessed.isoformat(),
                    reviewed.isoformat(),
                    review_due.isoformat() if review_due is not None else None,
                    supersedes,
                    restoration_id,
                    created.isoformat(),
                ),
            )

        return SourceReputationRecord(
            assessment_id=assessment_id,
            source_id=normalized_source,
            assessment_version=version,
            status=normalized_status,
            reliability_rating=normalized_rating,
            reason=normalized_reason,
            evidence_refs=normalized_refs,
            policy_name=normalized_policy,
            policy_version=normalized_policy_version,
            assessed_at=assessed,
            reviewed_at=reviewed,
            review_due_at=review_due,
            supersedes_assessment_id=supersedes,
            restoration_of_assessment_id=restoration_id,
            created_at=created,
        )

    def current(self, source_id: str) -> SourceReputationRecord | None:
        normalized_source = _normalize_required(source_id, "source_id")
        row = self._latest_row(normalized_source)
        return None if row is None else self._record_from_row(row)

    def history(self, source_id: str) -> tuple[SourceReputationRecord, ...]:
        normalized_source = _normalize_required(source_id, "source_id")
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT assessment_id, source_id, assessment_version, status,
                       reliability_rating, reason, evidence_refs_json,
                       policy_name, policy_version, assessed_at, reviewed_at,
                       review_due_at, supersedes_assessment_id,
                       restoration_of_assessment_id, created_at
                FROM source_reputation_history
                WHERE source_id = ?
                ORDER BY assessment_version
                """,
                (normalized_source,),
            ).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    def current_all(self) -> tuple[SourceReputationRecord, ...]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT h.assessment_id, h.source_id, h.assessment_version, h.status,
                       h.reliability_rating, h.reason, h.evidence_refs_json,
                       h.policy_name, h.policy_version, h.assessed_at, h.reviewed_at,
                       h.review_due_at, h.supersedes_assessment_id,
                       h.restoration_of_assessment_id, h.created_at
                FROM source_reputation_history h
                JOIN (
                    SELECT source_id, MAX(assessment_version) AS max_version
                    FROM source_reputation_history
                    GROUP BY source_id
                ) latest
                  ON latest.source_id = h.source_id
                 AND latest.max_version = h.assessment_version
                ORDER BY h.source_id
                """
            ).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    @staticmethod
    def _record_from_row(row: tuple) -> SourceReputationRecord:
        return SourceReputationRecord(
            assessment_id=row[0],
            source_id=row[1],
            assessment_version=int(row[2]),
            status=row[3],
            reliability_rating=row[4],
            reason=row[5],
            evidence_refs=tuple(json.loads(row[6])),
            policy_name=row[7],
            policy_version=row[8],
            assessed_at=datetime.fromisoformat(row[9]),
            reviewed_at=datetime.fromisoformat(row[10]),
            review_due_at=datetime.fromisoformat(row[11]) if row[11] else None,
            supersedes_assessment_id=row[12],
            restoration_of_assessment_id=row[13],
            created_at=datetime.fromisoformat(row[14]),
        )
