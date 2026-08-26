"""Phase 11 cross-dimensional operational coverage evaluation."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
import sqlite3

from .coverage_source_availability import SourceAvailabilityCoverageEvaluator
from .operational_coverage import (
    CoverageContract,
    CoverageRequirement,
    CoverageRequirementResultDraft,
    OperationalCoverageService,
)
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time
from .region_language_coverage import normalize_language_code, normalize_region_code


class CoverageDimensionEvaluator:
    """Converge canonical M6/M7/M10 coverage state without changing truth semantics."""

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        coverage: OperationalCoverageService | None = None,
    ):
        self.runtime = runtime
        self.database_path = runtime.database_path
        self.coverage = coverage or OperationalCoverageService(runtime)
        self.source_availability = SourceAvailabilityCoverageEvaluator(
            runtime, self.coverage
        )

    def evaluate_contract(
        self,
        coverage_contract_id: str,
        *,
        assessed_at: datetime,
    ) -> tuple[CoverageRequirementResultDraft, ...]:
        contract = self.coverage.get_contract(coverage_contract_id)
        if contract is None:
            raise ValueError("coverage contract does not exist")
        assessed = _normalize_time(assessed_at)
        results = [
            self._evaluate_requirement(contract, requirement, assessed)
            for requirement in self.coverage.requirements(contract.coverage_contract_id)
        ]
        return tuple(sorted(results, key=lambda item: item.requirement_id))

    def _evaluate_requirement(
        self,
        contract: CoverageContract,
        requirement: CoverageRequirement,
        assessed: datetime,
    ) -> CoverageRequirementResultDraft:
        if requirement.dimension in {"SOURCE_ID", "SOURCE_AVAILABILITY"}:
            return self.source_availability.evaluate_requirement(
                contract.coverage_contract_id,
                requirement.requirement_id,
                assessed_at=assessed,
            )
        if requirement.dimension == "SOURCE_CLASS":
            return self._evaluate_source_class(contract, requirement, assessed)
        if requirement.dimension == "REGION_LANGUAGE":
            return self._evaluate_region_language(contract, requirement, assessed)
        if requirement.dimension == "FRESHNESS":
            return self._evaluate_freshness(contract, requirement, assessed)
        return CoverageRequirementResultDraft(
            requirement_id=requirement.requirement_id,
            status="UNMEASURED",
            evidence_refs=(),
            explanation=(
                f"Coverage dimension {requirement.dimension} is declared but has no "
                "approved canonical Phase 11 measurement adapter."
            ),
            measured_at=assessed,
        )

    def _window_start(self, contract: CoverageContract, assessed: datetime) -> datetime:
        return assessed - timedelta(seconds=contract.assessment_window_seconds)

    @staticmethod
    def _age_seconds(assessed: datetime, measured_at: datetime) -> float:
        return (assessed - measured_at).total_seconds()

    def _evaluate_source_class(
        self,
        contract: CoverageContract,
        requirement: CoverageRequirement,
        assessed: datetime,
    ) -> CoverageRequirementResultDraft:
        if contract.watch_id is None:
            return self._unmeasured(
                requirement,
                assessed,
                "SOURCE_CLASS measurement requires an explicit watch-scoped contract.",
            )
        source_class = requirement.requirement_key
        window_start = self._window_start(contract, assessed)

        with sqlite3.connect(self.database_path) as connection:
            attempt_rows = connection.execute(
                """
                SELECT attempt.collection_id, attempt.source_id, attempt.status,
                       attempt.item_count, attempt.error, attempt.attempted_at
                FROM source_collection_attempts AS attempt
                JOIN source_collection_runs AS collection
                  ON collection.collection_id = attempt.collection_id
                WHERE collection.watch_id = ?
                  AND attempt.source_class = ?
                  AND attempt.attempted_at >= ?
                  AND attempt.attempted_at <= ?
                ORDER BY attempt.attempted_at DESC,
                         attempt.source_id,
                         attempt.collection_id
                """,
                (
                    contract.watch_id,
                    source_class,
                    window_start.isoformat(),
                    assessed.isoformat(),
                ),
            ).fetchall()
            pilot_rows = connection.execute(
                """
                SELECT run_id, source_classes, gaps, created_at
                FROM pilot_coverage_reports
                WHERE watch_id = ?
                  AND created_at >= ?
                  AND created_at <= ?
                ORDER BY created_at DESC, run_id DESC
                """,
                (
                    contract.watch_id,
                    window_start.isoformat(),
                    assessed.isoformat(),
                ),
            ).fetchall()

        fresh_positive: list[tuple[datetime, tuple[str, ...], str]] = []
        fresh_negative: list[tuple[datetime, tuple[str, ...], str]] = []
        stale_measurements: list[tuple[datetime, tuple[str, ...], str]] = []

        for collection_id, source_id, status, item_count, error, attempted_at_raw in attempt_rows:
            measured_at = datetime.fromisoformat(attempted_at_raw)
            refs = (
                f"collection:{collection_id}",
                f"source:{source_id}",
                f"source_attempt:{collection_id}:{source_id}",
            )
            detail = (
                f"source attempt status={status}; item_count={int(item_count)}"
                + (f"; error={error}" if error else "")
            )
            if self._age_seconds(assessed, measured_at) > contract.freshness_requirement_seconds:
                stale_measurements.append((measured_at, refs, detail))
            elif status == "SUCCESS":
                fresh_positive.append((measured_at, refs, detail))
            else:
                fresh_negative.append((measured_at, refs, detail))

        for run_id, source_classes_json, gaps_json, created_at_raw in pilot_rows:
            measured_at = datetime.fromisoformat(created_at_raw)
            try:
                observed = set(json.loads(source_classes_json))
                gaps = set(json.loads(gaps_json))
            except (TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError("invalid persisted M6 pilot coverage JSON") from exc
            refs = (f"pilot_coverage:{run_id}",)
            if source_class in observed:
                detail = "M6 pilot coverage report observed the required source class."
                target = fresh_positive
            else:
                missing_note = "explicit gap" if source_class in gaps else "not observed"
                detail = f"M6 pilot coverage report marked class as {missing_note}."
                target = fresh_negative
            if self._age_seconds(assessed, measured_at) > contract.freshness_requirement_seconds:
                stale_measurements.append((measured_at, refs, detail))
            else:
                target.append((measured_at, refs, detail))

        if fresh_positive:
            measured_at, refs, detail = max(fresh_positive, key=lambda item: item[0])
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="SATISFIED",
                evidence_refs=refs,
                explanation=(
                    f"Required source class {source_class!r} has fresh canonical "
                    f"coverage evidence; {detail}. Source quantity does not change "
                    "this single requirement unit."
                ),
                measured_at=measured_at,
            )
        if fresh_negative:
            measured_at, refs, detail = max(fresh_negative, key=lambda item: item[0])
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="GAP",
                evidence_refs=refs,
                explanation=(
                    f"Required source class {source_class!r} has a fresh measurement "
                    f"but no fresh successful/observed class evidence; {detail}."
                ),
                measured_at=measured_at,
            )
        if stale_measurements:
            measured_at, refs, detail = max(stale_measurements, key=lambda item: item[0])
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="STALE",
                evidence_refs=refs,
                explanation=(
                    f"Required source class {source_class!r} has only in-window "
                    f"coverage evidence older than the "
                    f"{contract.freshness_requirement_seconds}s freshness requirement; "
                    f"{detail}."
                ),
                measured_at=measured_at,
            )
        return CoverageRequirementResultDraft(
            requirement_id=requirement.requirement_id,
            status="UNKNOWN",
            evidence_refs=(),
            explanation=(
                f"No canonical M6/M7 measurement for source class {source_class!r} "
                "exists inside the assessment window for this watch."
            ),
            measured_at=assessed,
        )

    def _parse_region_language(
        self, requirement: CoverageRequirement
    ) -> tuple[str, str] | None:
        region_raw, separator, language_raw = requirement.requirement_key.partition(":")
        if not separator or not region_raw.strip() or not language_raw.strip():
            return None
        try:
            return (
                normalize_region_code(region_raw),
                normalize_language_code(language_raw),
            )
        except ValueError:
            return None

    def _evaluate_region_language(
        self,
        contract: CoverageContract,
        requirement: CoverageRequirement,
        assessed: datetime,
    ) -> CoverageRequirementResultDraft:
        pair = self._parse_region_language(requirement)
        if pair is None:
            return self._unmeasured(
                requirement,
                assessed,
                "REGION_LANGUAGE requirement_key must use REGION:language syntax.",
            )
        if contract.watch_id is None:
            return self._unmeasured(
                requirement,
                assessed,
                "REGION_LANGUAGE measurement requires an explicit watch-scoped contract.",
            )
        region, language = pair
        encoded_pair = f"{region}:{language}"
        window_start = self._window_start(contract, assessed)

        with sqlite3.connect(self.database_path) as connection:
            scope_row = connection.execute(
                """
                SELECT required
                FROM watch_region_language_scopes
                WHERE watch_id = ? AND region_code = ? AND language_code = ?
                """,
                (contract.watch_id, region, language),
            ).fetchone()
            attribution_rows = connection.execute(
                """
                SELECT raw_item_id, attribution_type, created_at
                FROM observation_region_language
                WHERE watch_id = ? AND region_code = ? AND language_code = ?
                  AND created_at >= ? AND created_at <= ?
                ORDER BY created_at DESC, raw_item_id, attribution_type
                """,
                (
                    contract.watch_id,
                    region,
                    language,
                    window_start.isoformat(),
                    assessed.isoformat(),
                ),
            ).fetchall()
            report_rows = connection.execute(
                """
                SELECT report_id, observed_scopes, missing_scopes, created_at
                FROM region_language_coverage_reports
                WHERE watch_id = ?
                  AND created_at >= ? AND created_at <= ?
                ORDER BY created_at DESC, report_id DESC
                """,
                (
                    contract.watch_id,
                    window_start.isoformat(),
                    assessed.isoformat(),
                ),
            ).fetchall()

        if scope_row is None or not bool(scope_row[0]):
            return self._unmeasured(
                requirement,
                assessed,
                (
                    f"{encoded_pair} is not an explicit required M10 scope for "
                    f"watch {contract.watch_id}."
                ),
            )

        fresh_attributions = []
        stale_attributions = []
        for raw_item_id, attribution_type, created_at_raw in attribution_rows:
            measured_at = datetime.fromisoformat(created_at_raw)
            item = (
                measured_at,
                (f"raw_item:{raw_item_id}",),
                attribution_type,
            )
            if self._age_seconds(assessed, measured_at) <= contract.freshness_requirement_seconds:
                fresh_attributions.append(item)
            else:
                stale_attributions.append(item)

        fresh_missing_reports = []
        stale_reports = []
        for report_id, observed_json, missing_json, created_at_raw in report_rows:
            measured_at = datetime.fromisoformat(created_at_raw)
            try:
                observed = set(json.loads(observed_json))
                missing = set(json.loads(missing_json))
            except (TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError("invalid persisted M10 coverage report JSON") from exc
            refs = (f"region_language_coverage:{report_id}",)
            detail = (
                "missing" if encoded_pair in missing else
                "observed" if encoded_pair in observed else
                "not explicitly classified"
            )
            item = (measured_at, refs, detail)
            if self._age_seconds(assessed, measured_at) <= contract.freshness_requirement_seconds:
                if encoded_pair in missing:
                    fresh_missing_reports.append(item)
            else:
                stale_reports.append(item)

        if fresh_attributions:
            measured_at, refs, attribution_type = max(
                fresh_attributions, key=lambda item: item[0]
            )
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="SATISFIED",
                evidence_refs=refs,
                explanation=(
                    f"Required M10 scope {encoded_pair} has a fresh watch-scoped "
                    f"attribution ({attribution_type}). Attribution is coverage metadata "
                    "and does not create evidence-source independence."
                ),
                measured_at=measured_at,
            )
        if fresh_missing_reports:
            measured_at, refs, _ = max(
                fresh_missing_reports, key=lambda item: item[0]
            )
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="GAP",
                evidence_refs=refs,
                explanation=(
                    f"A fresh M10 watch-scoped coverage report explicitly marks "
                    f"required scope {encoded_pair} as missing."
                ),
                measured_at=measured_at,
            )
        stale_candidates = stale_attributions + stale_reports
        if stale_candidates:
            measured_at, refs, detail = max(stale_candidates, key=lambda item: item[0])
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="STALE",
                evidence_refs=refs,
                explanation=(
                    f"Required M10 scope {encoded_pair} has only in-window state older "
                    f"than the {contract.freshness_requirement_seconds}s freshness "
                    f"requirement; latest state={detail}."
                ),
                measured_at=measured_at,
            )
        return CoverageRequirementResultDraft(
            requirement_id=requirement.requirement_id,
            status="UNKNOWN",
            evidence_refs=(),
            explanation=(
                f"No M10 attribution or coverage assessment for required scope "
                f"{encoded_pair} exists inside the assessment window."
            ),
            measured_at=assessed,
        )

    def _evaluate_freshness(
        self,
        contract: CoverageContract,
        requirement: CoverageRequirement,
        assessed: datetime,
    ) -> CoverageRequirementResultDraft:
        target_dimension = str(requirement.parameters.get("target_dimension", "")).strip().upper()
        target_key = str(requirement.parameters.get("target_key", "")).strip()
        if not target_dimension or not target_key:
            return self._unmeasured(
                requirement,
                assessed,
                "FRESHNESS requires target_dimension and target_key parameters.",
            )
        if contract.watch_id is None:
            return self._unmeasured(
                requirement,
                assessed,
                "FRESHNESS baseline measurement requires an explicit watch-scoped contract.",
            )

        latest = self._latest_target_measurement(
            contract,
            target_dimension=target_dimension,
            target_key=target_key,
            assessed=assessed,
        )
        if latest is None:
            return CoverageRequirementResultDraft(
                requirement_id=requirement.requirement_id,
                status="UNKNOWN",
                evidence_refs=(),
                explanation=(
                    f"No canonical measurement for freshness target "
                    f"{target_dimension}:{target_key} exists inside the assessment window."
                ),
                measured_at=assessed,
            )
        measured_at, refs = latest
        age_seconds = self._age_seconds(assessed, measured_at)
        status = (
            "SATISFIED"
            if age_seconds <= contract.freshness_requirement_seconds
            else "STALE"
        )
        return CoverageRequirementResultDraft(
            requirement_id=requirement.requirement_id,
            status=status,
            evidence_refs=refs,
            explanation=(
                f"Freshness target {target_dimension}:{target_key} was measured "
                f"{int(age_seconds)}s before assessment; requirement="
                f"{contract.freshness_requirement_seconds}s. Freshness evaluates "
                "measurement recency only, not source success or factual truth."
            ),
            measured_at=measured_at,
        )

    def _latest_target_measurement(
        self,
        contract: CoverageContract,
        *,
        target_dimension: str,
        target_key: str,
        assessed: datetime,
    ) -> tuple[datetime, tuple[str, ...]] | None:
        window_start = self._window_start(contract, assessed)
        if target_dimension in {"SOURCE_ID", "SOURCE_AVAILABILITY"}:
            with sqlite3.connect(self.database_path) as connection:
                row = connection.execute(
                    """
                    SELECT attempt.collection_id, attempt.source_id, attempt.attempted_at
                    FROM source_collection_attempts AS attempt
                    JOIN source_collection_runs AS collection
                      ON collection.collection_id = attempt.collection_id
                    WHERE collection.watch_id = ? AND attempt.source_id = ?
                      AND attempt.attempted_at >= ? AND attempt.attempted_at <= ?
                    ORDER BY attempt.attempted_at DESC, attempt.collection_id DESC
                    LIMIT 1
                    """,
                    (
                        contract.watch_id,
                        target_key,
                        window_start.isoformat(),
                        assessed.isoformat(),
                    ),
                ).fetchone()
            if row is None:
                return None
            return (
                datetime.fromisoformat(row[2]),
                (
                    f"collection:{row[0]}",
                    f"source:{row[1]}",
                    f"source_attempt:{row[0]}:{row[1]}",
                ),
            )

        if target_dimension == "SOURCE_CLASS":
            with sqlite3.connect(self.database_path) as connection:
                attempt = connection.execute(
                    """
                    SELECT attempt.collection_id, attempt.source_id, attempt.attempted_at
                    FROM source_collection_attempts AS attempt
                    JOIN source_collection_runs AS collection
                      ON collection.collection_id = attempt.collection_id
                    WHERE collection.watch_id = ? AND attempt.source_class = ?
                      AND attempt.attempted_at >= ? AND attempt.attempted_at <= ?
                    ORDER BY attempt.attempted_at DESC, attempt.source_id,
                             attempt.collection_id
                    LIMIT 1
                    """,
                    (
                        contract.watch_id,
                        target_key,
                        window_start.isoformat(),
                        assessed.isoformat(),
                    ),
                ).fetchone()
                pilot = connection.execute(
                    """
                    SELECT run_id, created_at
                    FROM pilot_coverage_reports
                    WHERE watch_id = ? AND created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC, run_id DESC
                    LIMIT 1
                    """,
                    (
                        contract.watch_id,
                        window_start.isoformat(),
                        assessed.isoformat(),
                    ),
                ).fetchone()
            candidates = []
            if attempt is not None:
                candidates.append(
                    (
                        datetime.fromisoformat(attempt[2]),
                        (
                            f"collection:{attempt[0]}",
                            f"source:{attempt[1]}",
                            f"source_attempt:{attempt[0]}:{attempt[1]}",
                        ),
                    )
                )
            if pilot is not None:
                candidates.append(
                    (datetime.fromisoformat(pilot[1]), (f"pilot_coverage:{pilot[0]}",))
                )
            return max(candidates, key=lambda item: item[0]) if candidates else None

        if target_dimension == "REGION_LANGUAGE":
            region_raw, separator, language_raw = target_key.partition(":")
            if not separator:
                return None
            try:
                region = normalize_region_code(region_raw)
                language = normalize_language_code(language_raw)
            except ValueError:
                return None
            with sqlite3.connect(self.database_path) as connection:
                attribution = connection.execute(
                    """
                    SELECT raw_item_id, created_at
                    FROM observation_region_language
                    WHERE watch_id = ? AND region_code = ? AND language_code = ?
                      AND created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC, raw_item_id
                    LIMIT 1
                    """,
                    (
                        contract.watch_id,
                        region,
                        language,
                        window_start.isoformat(),
                        assessed.isoformat(),
                    ),
                ).fetchone()
                report = connection.execute(
                    """
                    SELECT report_id, created_at
                    FROM region_language_coverage_reports
                    WHERE watch_id = ? AND created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC, report_id DESC
                    LIMIT 1
                    """,
                    (
                        contract.watch_id,
                        window_start.isoformat(),
                        assessed.isoformat(),
                    ),
                ).fetchone()
            candidates = []
            if attribution is not None:
                candidates.append(
                    (
                        datetime.fromisoformat(attribution[1]),
                        (f"raw_item:{attribution[0]}",),
                    )
                )
            if report is not None:
                candidates.append(
                    (
                        datetime.fromisoformat(report[1]),
                        (f"region_language_coverage:{report[0]}",),
                    )
                )
            return max(candidates, key=lambda item: item[0]) if candidates else None
        return None

    @staticmethod
    def _unmeasured(
        requirement: CoverageRequirement,
        assessed: datetime,
        explanation: str,
    ) -> CoverageRequirementResultDraft:
        return CoverageRequirementResultDraft(
            requirement_id=requirement.requirement_id,
            status="UNMEASURED",
            evidence_refs=(),
            explanation=explanation,
            measured_at=assessed,
        )


__all__ = ["CoverageDimensionEvaluator"]
