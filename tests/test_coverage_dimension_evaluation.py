from datetime import datetime, timedelta, timezone
import json
import sqlite3

from kgeopolitical_monitor.coverage_dimension_evaluation import CoverageDimensionEvaluator
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.region_language_coverage import RegionLanguageCoverageService


NOW = datetime(2026, 8, 26, 16, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Watch A",
        "Ukraine",
        30,
        watch_id="watch-a",
        created_at=NOW - timedelta(hours=6),
    )
    runtime.create_watch(
        "Watch B",
        "Ukraine",
        30,
        watch_id="watch-b",
        created_at=NOW - timedelta(hours=6),
    )
    return runtime


def _contract(runtime, requirements, *, watch_id="watch-a", window=7200, freshness=900):
    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key=f"scope:{watch_id or 'project'}:{len(tuple(requirements))}",
        name="Dimension convergence contract",
        watch_id=watch_id,
        assessment_window_seconds=window,
        freshness_requirement_seconds=freshness,
        requirements=tuple(requirements),
        created_at=NOW - timedelta(hours=4),
    )
    return coverage, contract


def _result_by_dimension(coverage, contract, results):
    dimensions = {
        item.requirement_id: item.dimension
        for item in coverage.requirements(contract.coverage_contract_id)
    }
    return {dimensions[item.requirement_id]: item for item in results}


def _save_pilot_coverage(runtime, *, created_at, source_classes, gaps, run_id):
    runtime.start_run("watch-a", run_id=run_id, started_at=created_at)
    runtime.complete_run(run_id, completed_at=created_at)
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute(
            """
            INSERT INTO pilot_coverage_reports(
                run_id, watch_id, examined_count, matched_count,
                source_classes, coverage_confidence, gaps, created_at
            ) VALUES (?, 'watch-a', 1, 1, ?, ?, ?, ?)
            """,
            (
                run_id,
                json.dumps(tuple(source_classes)),
                1.0 if not gaps else 0.0,
                json.dumps(tuple(gaps)),
                created_at.isoformat(),
            ),
        )


def test_source_class_uses_m6_pilot_coverage_without_source_count_inflation(tmp_path):
    runtime = _runtime(tmp_path)
    _save_pilot_coverage(
        runtime,
        created_at=NOW,
        source_classes=("Official sources", "Structured data"),
        gaps=(),
        run_id="run-pilot-observed",
    )
    coverage, contract = _contract(
        runtime,
        (CoverageRequirementSpec("SOURCE_CLASS", "Official sources"),),
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    results = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)

    assert len(results) == 1
    assert results[0].status == "SATISFIED"
    assert results[0].evidence_refs == ("pilot_coverage:run-pilot-observed",)
    assert "Source quantity does not change" in results[0].explanation


def test_fresh_m6_source_class_absence_is_gap_and_stale_measurement_is_stale(tmp_path):
    runtime = _runtime(tmp_path)
    _save_pilot_coverage(
        runtime,
        created_at=NOW,
        source_classes=("Structured data",),
        gaps=("Official sources",),
        run_id="run-pilot-gap",
    )
    coverage, contract = _contract(
        runtime,
        (CoverageRequirementSpec("SOURCE_CLASS", "Official sources"),),
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    fresh = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)[0]
    assert fresh.status == "GAP"

    stale_assessed_at = NOW + timedelta(minutes=30)
    stale = evaluator.evaluate_contract(
        contract.coverage_contract_id,
        assessed_at=stale_assessed_at,
    )[0]
    assert stale.status == "STALE"


def _configure_region_language(runtime, watch_id="watch-a"):
    service = RegionLanguageCoverageService(runtime)
    service.register_region("EUROPE", "Europe", created_at=NOW - timedelta(hours=5))
    service.register_language("uk", "Ukrainian", created_at=NOW - timedelta(hours=5))
    service.configure_watch_scope(
        watch_id,
        [("EUROPE", "uk")],
        configured_at=NOW - timedelta(hours=4),
    )
    return service


def _collect_raw(runtime, watch_id, *, at, item_id):
    class Adapter:
        source_id = f"source-{watch_id}"
        source_name = f"Source {watch_id}"
        source_class = "Official sources"

        def fetch(self, watch, collected_at):
            return [
                LiveSourceItem(
                    item_id=item_id,
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_class=self.source_class,
                    title="Ukraine update",
                    summary="Watch-scoped observation.",
                    original_url=f"https://example.org/{item_id}",
                    collected_at=collected_at,
                    reliability="official",
                )
            ]

    LiveSourceCollector(runtime, [Adapter()]).collect(watch_id, at)


def test_region_language_fresh_attribution_satisfies_but_stale_attribution_does_not(tmp_path):
    runtime = _runtime(tmp_path)
    region_language = _configure_region_language(runtime)
    observation_time = NOW - timedelta(minutes=5)
    _collect_raw(runtime, "watch-a", at=observation_time, item_id="raw-region-fresh")
    region_language.tag_observation(
        "watch-a",
        "raw-region-fresh",
        "EUROPE",
        "uk",
        attribution_type="TRANSLATION",
        confidence=0.8,
        original_language=False,
        tagged_at=observation_time,
    )
    coverage, contract = _contract(
        runtime,
        (CoverageRequirementSpec("REGION_LANGUAGE", "EUROPE:uk"),),
        freshness=900,
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    fresh = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)[0]
    assert fresh.status == "SATISFIED"
    assert fresh.evidence_refs == ("raw_item:raw-region-fresh",)
    assert "does not create evidence-source independence" in fresh.explanation

    stale = evaluator.evaluate_contract(
        contract.coverage_contract_id,
        assessed_at=NOW + timedelta(minutes=20),
    )[0]
    assert stale.status == "STALE"


def test_fresh_m10_missing_scope_report_is_gap(tmp_path):
    runtime = _runtime(tmp_path)
    region_language = _configure_region_language(runtime)
    report = region_language.generate_coverage_report("watch-a", created_at=NOW)
    coverage, contract = _contract(
        runtime,
        (CoverageRequirementSpec("REGION_LANGUAGE", "EUROPE:uk"),),
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    result = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)[0]

    assert "EUROPE:uk" in report.missing_scopes
    assert result.status == "GAP"
    assert result.evidence_refs == (f"region_language_coverage:{report.report_id}",)


def test_region_language_state_cannot_leak_between_watches(tmp_path):
    runtime = _runtime(tmp_path)
    service = _configure_region_language(runtime, watch_id="watch-b")
    _collect_raw(runtime, "watch-b", at=NOW, item_id="raw-watch-b")
    service.tag_observation(
        "watch-b",
        "raw-watch-b",
        "EUROPE",
        "uk",
        tagged_at=NOW,
    )

    service.configure_watch_scope(
        "watch-a",
        [("EUROPE", "uk")],
        configured_at=NOW - timedelta(hours=4),
    )
    coverage, contract = _contract(
        runtime,
        (CoverageRequirementSpec("REGION_LANGUAGE", "EUROPE:uk"),),
        watch_id="watch-a",
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    result = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)[0]
    assert result.status == "UNKNOWN"


def test_unsupported_declared_dimension_and_unconfigured_region_scope_are_unmeasured(tmp_path):
    runtime = _runtime(tmp_path)
    coverage, contract = _contract(
        runtime,
        (
            CoverageRequirementSpec("ACTOR", "actor:example"),
            CoverageRequirementSpec("REGION_LANGUAGE", "EUROPE:uk"),
        ),
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)
    results = _result_by_dimension(
        coverage,
        contract,
        evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW),
    )

    assert results["ACTOR"].status == "UNMEASURED"
    assert results["REGION_LANGUAGE"].status == "UNMEASURED"


def test_freshness_requirement_measures_recency_not_source_success(tmp_path):
    runtime = _runtime(tmp_path)

    class FailingAdapter:
        source_id = "source-fresh-failure"
        source_name = "Fresh Failure"
        source_class = "Structured data"

        def fetch(self, watch, collected_at):
            raise RuntimeError("temporarily unavailable")

    LiveSourceCollector(runtime, [FailingAdapter()]).collect("watch-a", NOW)
    coverage, contract = _contract(
        runtime,
        (
            CoverageRequirementSpec(
                "FRESHNESS",
                "freshness:source-fresh-failure",
                parameters={
                    "target_dimension": "SOURCE_ID",
                    "target_key": "source-fresh-failure",
                },
            ),
        ),
        freshness=900,
    )
    evaluator = CoverageDimensionEvaluator(runtime, coverage)

    fresh = evaluator.evaluate_contract(contract.coverage_contract_id, assessed_at=NOW)[0]
    assert fresh.status == "SATISFIED"
    assert "recency only, not source success" in fresh.explanation

    stale = evaluator.evaluate_contract(
        contract.coverage_contract_id,
        assessed_at=NOW + timedelta(minutes=20),
    )[0]
    assert stale.status == "STALE"
