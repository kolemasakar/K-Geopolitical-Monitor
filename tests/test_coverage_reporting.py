from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.coverage_reporting import (
    CoverageAwareReportRepository,
    CoverageReportingService,
    OperationalCoverageQuery,
)
from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementResultDraft,
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.region_language_coverage import RegionLanguageCoverageService
from kgeopolitical_monitor.report_rendering import ReportRenderer
from kgeopolitical_monitor.reporting_environment import (
    COVERAGE_REPORT,
    GLOBAL_GEOPOLITICAL_BRIEF,
    REGIONAL_COUNTRY_BRIEF,
    SQLiteReportRepository,
)


NOW = datetime(2026, 8, 26, 18, 30, tzinfo=timezone.utc)


def _runtime(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Coverage reporting watch",
        "Ukraine",
        30,
        watch_id="watch-reporting",
        created_at=NOW - timedelta(hours=6),
    )
    return project_root, runtime


def _result(requirement, status, measured_at, *, refs=()):
    return CoverageRequirementResultDraft(
        requirement_id=requirement.requirement_id,
        status=status,
        evidence_refs=tuple(refs),
        explanation=f"Persisted P11.5 acceptance state: {status}.",
        measured_at=measured_at,
    )


def _contract_with_history(runtime):
    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL:p11.5-history",
        name="P11.5 history contract",
        watch_id="watch-reporting",
        assessment_window_seconds=7200,
        freshness_requirement_seconds=900,
        requirements=(
            CoverageRequirementSpec("SOURCE_ID", "source-history"),
            CoverageRequirementSpec("ACTOR", "actor:unsupported"),
        ),
        created_at=NOW - timedelta(hours=3),
    )
    requirements = {
        (item.dimension, item.requirement_key): item
        for item in coverage.requirements(contract.coverage_contract_id)
    }
    older_at = NOW - timedelta(hours=1)
    older = coverage.create_snapshot(
        contract.coverage_contract_id,
        (
            _result(
                requirements[("SOURCE_ID", "source-history")],
                "UNKNOWN",
                older_at,
            ),
            _result(
                requirements[("ACTOR", "actor:unsupported")],
                "UNMEASURED",
                older_at,
            ),
        ),
        assessed_at=older_at,
    )
    latest = coverage.create_snapshot(
        contract.coverage_contract_id,
        (
            _result(
                requirements[("SOURCE_ID", "source-history")],
                "GAP",
                NOW,
                refs=("source:source-history",),
            ),
            _result(
                requirements[("ACTOR", "actor:unsupported")],
                "UNMEASURED",
                NOW,
            ),
        ),
        assessed_at=NOW,
    )
    return coverage, contract, older, latest


def test_latest_and_history_preserve_old_gap_and_limitation_state_after_restart(tmp_path):
    project_root, runtime = _runtime(tmp_path)
    _, contract, older, latest = _contract_with_history(runtime)

    query = OperationalCoverageQuery(runtime)
    history = query.history(contract.coverage_contract_id)
    assert [item.snapshot.coverage_snapshot_id for item in history] == [
        older.coverage_snapshot_id,
        latest.coverage_snapshot_id,
    ]
    assert {item.status for item in history[0].results} == {"UNKNOWN", "UNMEASURED"}
    assert {item.status for item in history[1].results} == {"GAP", "UNMEASURED"}
    assert history[0].snapshot.unknown_count == 1
    assert history[0].snapshot.unmeasured_count == 1
    assert query.latest_snapshot(contract.coverage_contract_id).snapshot == latest

    restarted = OperationalMonitoringRuntime(project_root)
    restarted_query = OperationalCoverageQuery(restarted)
    restarted_history = restarted_query.history(contract.coverage_contract_id)
    assert restarted_history == history
    assert restarted_query.latest_snapshot(contract.coverage_contract_id).snapshot == latest


def test_global_report_persists_phase11_snapshot_and_renders_unknown_unmeasured(tmp_path):
    _, runtime = _runtime(tmp_path)
    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL:p11.5-render",
        name="P11.5 render contract",
        watch_id="watch-reporting",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=900,
        requirements=(
            CoverageRequirementSpec("SOURCE_ID", "source-unknown"),
            CoverageRequirementSpec("ACTOR", "actor:unsupported"),
        ),
        created_at=NOW - timedelta(hours=2),
    )
    requirements = {
        (item.dimension, item.requirement_key): item
        for item in coverage.requirements(contract.coverage_contract_id)
    }
    snapshot = coverage.create_snapshot(
        contract.coverage_contract_id,
        (
            _result(requirements[("SOURCE_ID", "source-unknown")], "UNKNOWN", NOW),
            _result(requirements[("ACTOR", "actor:unsupported")], "UNMEASURED", NOW),
        ),
        assessed_at=NOW,
    )

    reporting = CoverageReportingService(runtime)
    bundle = reporting.global_report(
        snapshot.coverage_snapshot_id,
        title="Global coverage visibility",
        summary="Coverage limitations remain explicit.",
        as_of=NOW,
    )

    assert bundle.snapshot.report_type == GLOBAL_GEOPOLITICAL_BRIEF
    assert len(bundle.sections) == 1
    coverage_payload = bundle.sections[0].content["coverage_reports"][0]
    assert coverage_payload["coverage_snapshot_id"] == snapshot.coverage_snapshot_id
    assert coverage_payload["unknown_count"] == 1
    assert coverage_payload["unmeasured_count"] == 1
    assert coverage_payload["unknown_requirements"] == ["SOURCE_ID:source-unknown"]
    assert coverage_payload["unmeasured_requirements"] == ["ACTOR:actor:unsupported"]
    assert {item["status"] for item in coverage_payload["requirement_results"]} == {
        "UNKNOWN",
        "UNMEASURED",
    }
    assert any(
        ref.reference_kind == COVERAGE_REPORT
        and ref.reference_value == snapshot.coverage_snapshot_id
        for ref in bundle.references
    )

    generic_repository = SQLiteReportRepository(runtime.database_path)
    assert generic_repository.get_bundle(bundle.snapshot.report_id) == bundle

    renderer = ReportRenderer(CoverageAwareReportRepository(runtime.database_path))
    markdown = renderer.markdown(bundle.snapshot.report_id)
    structured = renderer.structured(bundle.snapshot.report_id)
    assert "UNKNOWN" in markdown
    assert "UNMEASURED" in markdown
    assert snapshot.coverage_snapshot_id in markdown
    assert structured["sections"][0]["presentation_class"] == "COVERAGE_METADATA"


def test_regional_report_requires_explicit_region_language_requirement(tmp_path):
    _, runtime = _runtime(tmp_path)
    regional = RegionLanguageCoverageService(runtime)
    regional.register_region("UKRAINE", "Ukraine", created_at=NOW - timedelta(hours=2))
    regional.register_language("uk", "Ukrainian", created_at=NOW - timedelta(hours=2))
    regional.register_language("en", "English", created_at=NOW - timedelta(hours=2))

    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="REGION:UKRAINE",
        name="Ukraine regional coverage",
        watch_id="watch-reporting",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=900,
        requirements=(
            CoverageRequirementSpec("REGION_LANGUAGE", "UKRAINE:uk"),
            CoverageRequirementSpec("ACTOR", "actor:unsupported"),
        ),
        created_at=NOW - timedelta(hours=1),
    )
    requirements = {
        (item.dimension, item.requirement_key): item
        for item in coverage.requirements(contract.coverage_contract_id)
    }
    snapshot = coverage.create_snapshot(
        contract.coverage_contract_id,
        (
            _result(requirements[("REGION_LANGUAGE", "UKRAINE:uk")], "UNKNOWN", NOW),
            _result(requirements[("ACTOR", "actor:unsupported")], "UNMEASURED", NOW),
        ),
        assessed_at=NOW,
    )

    reporting = CoverageReportingService(runtime)
    bundle = reporting.regional_report(
        snapshot.coverage_snapshot_id,
        "UKRAINE",
        ("uk",),
        title="Ukraine coverage",
        summary="Regional limitations remain explicit.",
        as_of=NOW,
    )
    assert bundle.snapshot.report_type == REGIONAL_COUNTRY_BRIEF
    assert bundle.snapshot.subject_ref_type == "REGION"
    assert bundle.snapshot.subject_ref_id == "UKRAINE"
    assert bundle.sections[0].content["coverage_reports"][0]["unknown_count"] == 1
    assert bundle.sections[0].content["coverage_reports"][0]["unmeasured_count"] == 1

    with pytest.raises(ValueError, match="does not declare requested regional scope"):
        reporting.regional_report(
            snapshot.coverage_snapshot_id,
            "UKRAINE",
            ("en",),
            title="Invalid English scope",
            summary="Must fail closed.",
            as_of=NOW + timedelta(minutes=1),
        )


def test_phase11_reporting_uses_existing_m13_tables_only(tmp_path):
    _, runtime = _runtime(tmp_path)
    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL:p11.5-store",
        name="Store convergence",
        watch_id="watch-reporting",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=900,
        requirements=(CoverageRequirementSpec("ACTOR", "actor:unsupported"),),
        created_at=NOW - timedelta(hours=1),
    )
    requirement = coverage.requirements(contract.coverage_contract_id)[0]
    snapshot = coverage.create_snapshot(
        contract.coverage_contract_id,
        (_result(requirement, "UNMEASURED", NOW),),
        assessed_at=NOW,
    )
    bundle = CoverageReportingService(runtime).global_report(
        snapshot.coverage_snapshot_id,
        title="Canonical M13 store",
        summary="No parallel report truth store.",
        as_of=NOW,
    )

    with sqlite3.connect(runtime.database_path) as connection:
        report_count = connection.execute(
            "SELECT COUNT(*) FROM report_snapshots WHERE report_id = ?",
            (bundle.snapshot.report_id,),
        ).fetchone()[0]
        coverage_ref_count = connection.execute(
            """
            SELECT COUNT(*) FROM report_references
            WHERE report_id = ? AND reference_kind = 'COVERAGE_REPORT'
              AND reference_value = ?
            """,
            (bundle.snapshot.report_id, snapshot.coverage_snapshot_id),
        ).fetchone()[0]
        parallel_tables = connection.execute(
            """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type = 'table' AND name LIKE 'phase11_report%'
            """
        ).fetchone()[0]
    assert report_count == 1
    assert coverage_ref_count == 1
    assert parallel_tables == 0
