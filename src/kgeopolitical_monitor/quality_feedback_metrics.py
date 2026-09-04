"""P16.6 deterministic advisory quality metrics.

Read-only aggregation over persisted delivery and operator-feedback evidence. Results
are descriptive observations and explicit review proposals only; this module never
changes verification, source, alert, forecast, delivery policy, or provider state.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Final


P16_6_GATE: Final[str] = "P16_6_ADVISORY_QUALITY_FEEDBACK_LOOP_VALIDATED"
QUALITY_METRICS_VERSION: Final[str] = "KGM_ADVISORY_QUALITY_METRICS_V1"


@dataclass(frozen=True)
class AdvisoryQualitySnapshot:
    cohort_definition: str
    sample_size: int
    delivery_intent_count: int
    terminal_delivery_count: int
    delivered_count: int
    failed_count: int
    suppressed_count: int
    attempted_intent_count: int
    retry_intent_count: int
    transport_attempt_count: int
    receipt_count: int
    feedback_count: int
    useful_count: int
    not_useful_count: int
    timely_count: int
    late_count: int
    duplicate_noisy_count: int
    correction_request_count: int
    delivery_success_rate: float | None
    delivery_failure_rate: float | None
    retry_rate: float | None
    usefulness_rate: float | None
    timeliness_rate: float | None
    noise_feedback_rate: float | None
    latest_state_distribution: tuple[tuple[str, int], ...]
    event_type_distribution: tuple[tuple[str, int], ...]
    advisory_proposals: tuple[str, ...]
    limitations: tuple[str, ...]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator <= 0 else numerator / denominator


class SQLiteAdvisoryQualityMetrics:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def _table_exists(self, name: str) -> bool:
        return self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
            (name,),
        ).fetchone() is not None

    def snapshot(
        self,
        *,
        created_from: str | None = None,
        created_before: str | None = None,
    ) -> AdvisoryQualitySnapshot:
        clauses: list[str] = []
        params: list[str] = []
        cohort_parts = ["delivery_intents"]
        if created_from is not None:
            value = str(created_from)
            clauses.append("d.created_at >= ?")
            params.append(value)
            cohort_parts.append(f"created_at>={value}")
        if created_before is not None:
            value = str(created_before)
            clauses.append("d.created_at < ?")
            params.append(value)
            cohort_parts.append(f"created_at<{value}")
        where_sql = "" if not clauses else "WHERE " + " AND ".join(clauses)
        cohort_definition = ";".join(cohort_parts)

        cohort_rows = self.connection.execute(
            f"""
            SELECT d.delivery_intent_id, d.event_type
            FROM delivery_intents d
            {where_sql}
            ORDER BY d.delivery_intent_id ASC
            """,
            tuple(params),
        ).fetchall()
        intent_ids = tuple(str(row[0]) for row in cohort_rows)
        event_counts: dict[str, int] = {}
        for _, event_type in cohort_rows:
            key = str(event_type)
            event_counts[key] = event_counts.get(key, 0) + 1

        state_counts: dict[str, int] = {}
        transport_attempt_count = 0
        receipt_count = 0
        attempted_intent_count = 0
        retry_intent_count = 0
        feedback_counts: dict[str, int] = {}
        feedback_exists = self._table_exists("operator_quality_feedback")

        for intent_id in intent_ids:
            latest = self.connection.execute(
                """
                SELECT state FROM delivery_intent_audit_events
                WHERE delivery_intent_id = ?
                ORDER BY event_sequence DESC LIMIT 1
                """,
                (intent_id,),
            ).fetchone()
            state = "UNKNOWN" if latest is None else str(latest[0])
            state_counts[state] = state_counts.get(state, 0) + 1

            attempt_row = self.connection.execute(
                """
                SELECT COUNT(*), COALESCE(MAX(attempt_sequence), 0)
                FROM delivery_transport_attempts
                WHERE delivery_intent_id = ?
                """,
                (intent_id,),
            ).fetchone()
            attempts = int(attempt_row[0])
            max_sequence = int(attempt_row[1])
            transport_attempt_count += attempts
            if attempts > 0:
                attempted_intent_count += 1
            if max_sequence > 1:
                retry_intent_count += 1

            receipt_count += int(
                self.connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM delivery_receipts r
                    JOIN delivery_transport_attempts a
                      ON a.transport_attempt_id = r.transport_attempt_id
                    WHERE a.delivery_intent_id = ?
                    """,
                    (intent_id,),
                ).fetchone()[0]
            )

            if feedback_exists:
                for feedback_type, count in self.connection.execute(
                    """
                    SELECT feedback_type, COUNT(*)
                    FROM operator_quality_feedback
                    WHERE delivery_intent_id = ?
                    GROUP BY feedback_type
                    """,
                    (intent_id,),
                ).fetchall():
                    key = str(feedback_type)
                    feedback_counts[key] = feedback_counts.get(key, 0) + int(count)

        delivered = state_counts.get("DELIVERED", 0)
        failed = state_counts.get("FAILED", 0)
        suppressed = state_counts.get("SUPPRESSED", 0)
        terminal = delivered + failed + suppressed
        useful = feedback_counts.get("USEFUL", 0)
        not_useful = feedback_counts.get("NOT_USEFUL", 0)
        timely = feedback_counts.get("TIMELY", 0)
        late = feedback_counts.get("LATE", 0)
        duplicate_noisy = feedback_counts.get("DUPLICATE_NOISY", 0)
        correction_requests = feedback_counts.get("FACTUAL_CORRECTION_REQUESTED", 0)
        feedback_count = sum(feedback_counts.values())

        proposals: list[str] = []
        if failed:
            proposals.append("PROPOSAL_REVIEW_DELIVERY_FAILURE_EVIDENCE")
        if duplicate_noisy:
            proposals.append("PROPOSAL_REVIEW_DUPLICATE_SUPPRESSION_POLICY")
        if correction_requests:
            proposals.append("PROPOSAL_ROUTE_CORRECTION_REQUESTS_TO_PROVENANCE_REVIEW")

        return AdvisoryQualitySnapshot(
            cohort_definition=cohort_definition,
            sample_size=len(intent_ids),
            delivery_intent_count=len(intent_ids),
            terminal_delivery_count=terminal,
            delivered_count=delivered,
            failed_count=failed,
            suppressed_count=suppressed,
            attempted_intent_count=attempted_intent_count,
            retry_intent_count=retry_intent_count,
            transport_attempt_count=transport_attempt_count,
            receipt_count=receipt_count,
            feedback_count=feedback_count,
            useful_count=useful,
            not_useful_count=not_useful,
            timely_count=timely,
            late_count=late,
            duplicate_noisy_count=duplicate_noisy,
            correction_request_count=correction_requests,
            delivery_success_rate=_rate(delivered, terminal),
            delivery_failure_rate=_rate(failed, terminal),
            retry_rate=_rate(retry_intent_count, attempted_intent_count),
            usefulness_rate=_rate(useful, useful + not_useful),
            timeliness_rate=_rate(timely, timely + late),
            noise_feedback_rate=_rate(duplicate_noisy, feedback_count),
            latest_state_distribution=tuple(sorted(state_counts.items())),
            event_type_distribution=tuple(sorted(event_counts.items())),
            advisory_proposals=tuple(proposals),
            limitations=(
                "DESCRIPTIVE_ADVISORY_ONLY",
                "NO_AUTOMATIC_POLICY_MUTATION",
                "NO_FACTUAL_VERIFICATION_PROMOTION",
                "NO_PROVIDER_ACTIVATION",
            ),
        )
