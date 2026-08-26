"""Phase 11 source-availability coverage measurement."""

from __future__ import annotations

from datetime import datetime, timedelta
import sqlite3

from .operational_coverage import (
    CoverageRequirementResultDraft,
    OperationalCoverageService,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SOURCE_AVAILABILITY_DIMENSIONS = {"SOURCE_ID", "SOURCE_AVAILABILITY"}


class SourceAvailabilityCoverageEvaluator:
    """Evaluate durable source requirements from persisted per-source collection attempts."""

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        coverage: OperationalCoverageService | None = None,
    ):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.coverage = coverage or OperationalCoverageService(runtime)

    def evaluate_requirement(
        self,
        coverage_contract_id: str,
        requirement_id: str,
        *,
        assessed_at: datetime,
    ) -> CoverageRequirementResultDraft:
        contract = self.coverage.get_contract(coverage_contract_id)
        if contract is None:
            raise ValueError("coverage contract does not exist")
        assessed = _normalize_time(assessed_at)

        requirement = next(
            (
                item
                for item in self.coverage.requirements(contract.coverage_contract_id)
                if item.requirement_id == requirement_id
            ),
            None,
        )
        if requirement is None:
            raise ValueError("coverage requirement does not belong to contract")
        if requirement.dimension not in SOURCE_AVAILABILITY_DIMENSIONS:
            raise ValueError(
                "source availability evaluator requires SOURCE_ID or SOURCE_AVAILABILITY"
            )

        window_start = assessed - timedelta(
            seconds=contract.assessment_window_seconds
        )
        params: list[object] = [
            requirement.requirement_key,
            window_start.isoformat(),
            assessed.isoformat(),
        ]
        watch_clause = ""
        if contract.watch_id is not None:
            watch_clause = " AND collection.watch_id = ?"
            params.append(contract.watch_id)

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                f"""
                SELECT attempt.collection_id, attempt.source_id, attempt.source_name,
                       attempt.source_class, attempt.status, attempt.item_count,
                       attempt.error, attempt.attempted_at, collection.watch_id,
                       collection.status
                FROM source_collection_attempts AS attempt
                JOIN source_collection_runs AS collection
                  ON collection.collection_id = attempt.collection_id
                WHERE attempt.source_id = ?
                  AND attempt.attempted_at >= ?
                  AND attempt.attempted_at <= ?
                  {watch_clause}
                ORDER BY attempt.attempted_at DESC, attempt.collection_id DESC
                LIMIT 1
                """,
                tuple(params),
            ).fetchone()

        source_ref = f"source:{requirement.requirement_key}"
        if row is None:
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="UNKNOWN",
                evidence_refs=(source_ref,),
                explanation=(
                    "No per-source collection attempt exists inside the coverage "
                    "assessment window."
                ),
                measured_at=assessed,
            )

        (
            collection_id,
            source_id,
            source_name,
            source_class,
            attempt_status,
            item_count,
            error,
            attempted_at_raw,
            watch_id,
            collection_status,
        ) = row
        attempted_at = datetime.fromisoformat(attempted_at_raw)
        age_seconds = (assessed - attempted_at).total_seconds()
        evidence_refs = (
            f"collection:{collection_id}",
            source_ref,
            f"source_attempt:{collection_id}:{source_id}",
        )

        if age_seconds > contract.freshness_requirement_seconds:
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="STALE",
                evidence_refs=evidence_refs,
                explanation=(
                    f"Latest in-window source attempt is older than the "
                    f"{contract.freshness_requirement_seconds}s freshness requirement; "
                    f"attempt_status={attempt_status}; collection_status={collection_status}; "
                    f"item_count={int(item_count)}."
                ),
                measured_at=attempted_at,
            )

        if attempt_status == "FAILED":
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="UNAVAILABLE",
                evidence_refs=evidence_refs,
                explanation=(
                    f"Latest fresh source attempt failed; source={source_name}; "
                    f"class={source_class}; watch={watch_id}; "
                    f"collection_status={collection_status}; error={error}."
                ),
                measured_at=attempted_at,
            )

        if attempt_status == "SUCCESS":
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="SATISFIED",
                evidence_refs=evidence_refs,
                explanation=(
                    f"Latest fresh source attempt succeeded; source={source_name}; "
                    f"class={source_class}; watch={watch_id}; "
                    f"collection_status={collection_status}; item_count={int(item_count)}. "
                    "A zero-item successful fetch remains a successful availability check."
                ),
                measured_at=attempted_at,
            )

        raise RuntimeError(f"unsupported persisted source attempt status: {attempt_status}")


__all__ = [
    "SOURCE_AVAILABILITY_DIMENSIONS",
    "SourceAvailabilityCoverageEvaluator",
]
