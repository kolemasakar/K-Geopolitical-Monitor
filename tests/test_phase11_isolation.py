from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

import pytest

from kgeopolitical_monitor.coverage_assessment import OperationalCoverageAssessmentService
from kgeopolitical_monitor.coverage_reporting import (
    CoverageAwareReportRepository,
    CoverageReportingService,
)
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_coverage import (
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.region_language_coverage import RegionLanguageCoverageService
from kgeopolitical_monitor.report_rendering import ReportRenderer
from kgeopolitical_monitor.reporting_environment import ReportBundle


NOW = datetime(2026, 8, 26, 19, 0, tzinfo=timezone.utc)


class GoodAdapter:
    source_id = "official-p11-isolation"
    source_name = "Official P11 Isolation"
    source_class = "Official sources"

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id="raw-p11-isolation",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Ukraine security agreement",
                summary="Single-origin Phase 11 isolation fixture.",
                original_url="https://official.example/p11-isolation",
                collected_at=collected_at,
                reliability="official",
            )
        ]


class FailingAdapter:
    source_id = "regional-p11-failure"
    source_name = "Regional P11 Failure"
    source_class = "Regional media"

    def fetch(self, watch, collected_at):
        raise RuntimeError("regional source unavailable")


def _runtime(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    runtime.create_watch(
        "Phase 11 isolation",
        "Ukraine security agreement",
        30,
        watch_id="watch-p11-isolation",
        created_at=NOW - timedelta(hours=4),
    )
    return project_root, runtime


def _seed_upstream_truth(runtime, collection_id):
    stamp = NOW.isoformat()
    deadline = (NOW + timedelta(days=7)).isoformat()
    with sqlite3.connect(runtime.database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO live_analysis_runs(
                analysis_run_id, collection_id, watch_id, status,
                claim_count, finding_count, created_at
            ) VALUES ('analysis-p11', ?, 'watch-p11-isolation', 'COMPLETED', 1, 0, ?)
            """,
            (collection_id, stamp),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title,
                verification_status, confidence, importance,
                independent_origin_count, source_class_count, origins_json
            ) VALUES (
                'claim-p11', 'analysis-p11', 'ukraine-security-agreement',
                'Ukraine security agreement', 'DETECTED', 0.72, 0.81, 1, 1,
                '["official.example"]'
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO graph_nodes(
                node_id, node_kind, canonical_ref_type, canonical_ref_id,
                label, attributes_json, created_at, updated_at
            ) VALUES (?, 'ACTOR', 'ACTOR', ?, ?, '{}', ?, ?)
            """,
            (
                ("graph-node-a", "actor-a", "Actor A", stamp, stamp),
                ("graph-node-b", "actor-b", "Actor B", stamp, stamp),
            ),
        )
        connection.execute(
            """
            INSERT INTO graph_edges(
                edge_id, source_node_id, target_node_id, relation_type,
                relation_class, confidence, status, valid_from, valid_to,
                first_observed_at, last_observed_at, explanation,
                created_at, updated_at
            ) VALUES (
                'graph-edge-p11', 'graph-node-a', 'graph-node-b', 'influences',
                'INFLUENCE', 0.88, 'ACTIVE', ?, NULL, ?, ?,
                'Persisted M11 isolation fixture.', ?, ?
            )
            """,
            (stamp, stamp, stamp, stamp, stamp),
        )
        connection.execute(
            """
            INSERT INTO forecasts(
                forecast_id, target_key, question, horizon, evaluation_deadline,
                status, created_at, updated_at
            ) VALUES (
                'forecast-p11', 'p11-isolation-target',
                'Will the isolation scenario persist?', 'short_term', ?,
                'ACTIVE', ?, ?
            )
            """,
            (deadline, stamp, stamp),
        )
        connection.execute(
            """
            INSERT INTO forecast_versions(
                forecast_version_id, forecast_id, version_number,
                input_snapshot_json, provenance_refs_json, assumptions_json,
                change_reason, created_at
            ) VALUES (
                'forecast-version-p11', 'forecast-p11', 1,
                '{}', '[]', '[]', 'Isolation fixture.', ?
            )
            """,
            (stamp,),
        )
        connection.executemany(
            """
            INSERT INTO forecast_scenario_versions(
                scenario_version_id, forecast_version_id, scenario_type, label,
                raw_probability, calibrated_probability, scenario_confidence,
                drivers_json, constraints_json, triggers_json, inhibitors_json,
                uncertainty_factors_json, invalidation_signals_json
            ) VALUES (?, 'forecast-version-p11', ?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', '[]', '[]')
            """,
            (
                ("scenario-p11-baseline", "baseline", "Baseline", 0.6, 0.55, 0.7),
                ("scenario-p11-negative", "negative", "Negative", 0.4, 0.45, 0.6),
            ),
        )


def _upstream_rows(database_path):
    with sqlite3.connect(database_path) as connection:
        claim = connection.execute(
            """
            SELECT verification_status, confidence, independent_origin_count,
                   source_class_count, origins_json
            FROM live_analysis_claims WHERE claim_id = 'claim-p11'
            """
        ).fetchone()
        graph = connection.execute(
            """
            SELECT source_node_id, target_node_id, relation_type, relation_class,
                   confidence, status, valid_from, valid_to, first_observed_at,
                   last_observed_at, explanation, created_at, updated_at
            FROM graph_edges WHERE edge_id = 'graph-edge-p11'
            """
        ).fetchone()
        forecast = connection.execute(
            """
            SELECT scenario_version_id, scenario_type, raw_probability,
                   calibrated_probability, scenario_confidence
            FROM forecast_scenario_versions
            WHERE forecast_version_id = 'forecast-version-p11'
            ORDER BY scenario_version_id
            """
        ).fetchall()
    return claim, graph, forecast


def test_phase11_global_coverage_preserves_m8_m11_m12_and_report_truth(tmp_path):
    _, runtime = _runtime(tmp_path)
    collection = LiveSourceCollector(runtime, [GoodAdapter(), FailingAdapter()]).collect(
        "watch-p11-isolation", NOW
    )
    _seed_upstream_truth(runtime, collection.collection_id)
    upstream_before = _upstream_rows(runtime.database_path)
    assert upstream_before[0][2] == 1

    regional = RegionLanguageCoverageService(runtime)
    regional.register_region("UA", "Ukraine", region_group="Europe", created_at=NOW)
    regional.register_language("uk", "Ukrainian", created_at=NOW)
    regional.register_language("en", "English", created_at=NOW)
    regional.configure_watch_scope(
        "watch-p11-isolation", [("UA", "uk"), ("UA", "en")], configured_at=NOW
    )
    regional.tag_observation(
        "watch-p11-isolation", "raw-p11-isolation", "UA", "uk",
        attribution_type="DECLARED", confidence=1.0,
        original_language=True, tagged_at=NOW,
    )
    regional.tag_observation(
        "watch-p11-isolation", "raw-p11-isolation", "UA", "en",
        attribution_type="TRANSLATION", confidence=1.0,
        original_language=False, tagged_at=NOW,
    )
    assert _upstream_rows(runtime.database_path)[0] == upstream_before[0]

    coverage = OperationalCoverageService(runtime)
    contract = coverage.create_contract(
        scope_key="GLOBAL",
        name="Explicit global isolation scope",
        watch_id="watch-p11-isolation",
        assessment_window_seconds=3600,
        freshness_requirement_seconds=900,
        requirements=(
            CoverageRequirementSpec("SOURCE_ID", "official-p11-isolation"),
            CoverageRequirementSpec("SOURCE_CLASS", "Regional media"),
            CoverageRequirementSpec("SOURCE_ID", "source-never-measured"),
            CoverageRequirementSpec("REGION_LANGUAGE", "UA:uk"),
            CoverageRequirementSpec("REGION_LANGUAGE", "UA:en"),
            CoverageRequirementSpec("ACTOR", "actor:unsupported"),
        ),
        created_at=NOW,
    )
    assessment = OperationalCoverageAssessmentService(runtime).assess(
        contract.coverage_contract_id, assessed_at=NOW
    )
    statuses = {item.status for item in assessment.requirement_results}
    assert {"SATISFIED", "GAP", "UNKNOWN", "UNMEASURED"}.issubset(statuses)
    assert assessment.snapshot.coverage_ratio < 1.0
    assert assessment.snapshot.coverage_confidence < 1.0

    report = CoverageReportingService(runtime).global_report(
        assessment.snapshot.coverage_snapshot_id,
        title="Global coverage isolation",
        summary="GLOBAL is an explicit scope key, not a completeness claim.",
        as_of=NOW,
    )
    repository = CoverageAwareReportRepository(runtime.database_path)
    markdown = ReportRenderer(repository).markdown(report.snapshot.report_id)
    assert report.snapshot.scope_key == "GLOBAL"
    assert "GAP" in markdown
    assert "UNKNOWN" in markdown
    assert "UNMEASURED" in markdown
    assert "coverage_ratio" in markdown
    assert "coverage_confidence" in markdown

    upstream_after = _upstream_rows(runtime.database_path)
    assert upstream_after == upstream_before
    assert upstream_after[0][2] == 1

    persisted_before = repository.get_bundle(report.snapshot.report_id)
    later = OperationalCoverageAssessmentService(runtime).assess(
        contract.coverage_contract_id,
        assessed_at=NOW + timedelta(minutes=5),
    )
    assert later.snapshot.coverage_snapshot_id != assessment.snapshot.coverage_snapshot_id
    assert repository.get_bundle(report.snapshot.report_id) == persisted_before

    tampered_section = replace(persisted_before.sections[0], content={"tampered": True})
    tampered = ReportBundle(
        persisted_before.snapshot,
        (tampered_section,),
        persisted_before.references,
    )
    with pytest.raises(ValueError, match="report snapshot is immutable"):
        repository.save_bundle(tampered)


def test_phase11_runtime_remains_project_local_and_rejects_shared_path(tmp_path):
    project_root = tmp_path / "project"
    runtime = OperationalMonitoringRuntime(project_root)
    assert runtime.database_path.parent == (project_root / "data").resolve()

    with pytest.raises(ValueError, match="project-local data directory"):
        OperationalMonitoringRuntime(
            project_root,
            database_path=tmp_path / "shared-runtime.db",
        )


def test_phase11_does_not_change_canonical_production_status():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Production/live operational status: NOT_OPERATIONAL" in readme
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in readme
