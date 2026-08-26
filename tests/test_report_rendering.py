from datetime import datetime, timezone
import json
import sqlite3

import pytest

from kgeopolitical_monitor.report_rendering import (
    ProjectLocalReportRenderer,
    ReportRenderer,
)
from kgeopolitical_monitor.reporting_environment import (
    ALERT,
    ANALYTICAL_CONTEXT,
    CLAIM,
    COVERAGE_REPORT,
    EVENT,
    EVENT_DOSSIER,
    FORECAST_REPORT,
    FORECAST_VERSION,
    GLOBAL_GEOPOLITICAL_BRIEF,
    GRAPH_EDGE,
    LANGUAGE,
    OBSERVED_FACT,
    RAW_ITEM,
    REGION,
    REGIONAL_COUNTRY_BRIEF,
    SCENARIO_VERSION,
    STORYLINE_REPORT,
    STRATEGIC_ALERT,
    STRATEGIC_OUTLOOK,
    ReportBundle,
    ReportReference,
    ReportSection,
    ReportSnapshot,
    SQLiteReportRepository,
)


NOW = datetime(2026, 8, 26, 20, 0, tzinfo=timezone.utc)


def _simple_persisted_report(db):
    repo = SQLiteReportRepository(db)
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES ('source-r', 'Renderer source', 'Official sources', 'HIGH')"
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES ('raw-r', 'source-r', 'Renderer item', 'Body', ?)",
            (NOW.isoformat(),),
        )

    snapshot = ReportSnapshot.create(
        GLOBAL_GEOPOLITICAL_BRIEF,
        "global:renderer",
        "Renderer brief",
        "Deterministic rendering summary.",
        NOW,
        created_at=NOW,
        generator_version="m13.6",
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "CONTEXT",
        "Context",
        ANALYTICAL_CONTEXT,
        {"z": [2, 1], "a": {"b": 2, "a": 1}},
        "Context is rendered from the immutable persisted snapshot.",
        created_at=NOW,
    )
    reference = ReportReference.create(
        snapshot.report_id,
        RAW_ITEM,
        "raw-r",
        "EVIDENCE",
        section_id=section.section_id,
        created_at=NOW,
    )
    bundle = repo.save_bundle(ReportBundle(snapshot, (section,), (reference,)))
    return repo, bundle


def test_persisted_snapshot_renders_identically_after_restart(tmp_path):
    db = tmp_path / "project.db"
    repo, bundle = _simple_persisted_report(db)

    first = ReportRenderer(repo)
    structured = first.structured_json(bundle.snapshot.report_id)
    markdown = first.markdown(bundle.snapshot.report_id)
    digest = first.digest(bundle.snapshot.report_id)

    restarted = ReportRenderer(SQLiteReportRepository(db))
    assert restarted.structured_json(bundle.snapshot.report_id) == structured
    assert restarted.markdown(bundle.snapshot.report_id) == markdown
    assert restarted.digest(bundle.snapshot.report_id) == digest
    assert json.loads(structured)["sections"][0]["content"] == {
        "a": {"a": 1, "b": 2},
        "z": [2, 1],
    }


def test_renderer_preserves_presentation_and_reference_traceability(tmp_path):
    db = tmp_path / "project.db"
    repo, bundle = _simple_persisted_report(db)
    renderer = ReportRenderer(repo)

    rendered = renderer.structured(bundle.snapshot.report_id)
    section = rendered["sections"][0]
    reference = rendered["references"][0]

    assert section["presentation_class"] == ANALYTICAL_CONTEXT
    assert reference["reference_kind"] == RAW_ITEM
    assert reference["reference_value"] == "raw-r"
    assert reference["reference_role"] == "EVIDENCE"
    assert reference["section_id"] == section["section_id"]
    assert reference["reference_id"] in renderer.markdown(bundle.snapshot.report_id)


def test_all_approved_report_types_use_the_same_render_contract():
    subjects = {
        STRATEGIC_ALERT: (ALERT, "alert-1"),
        GLOBAL_GEOPOLITICAL_BRIEF: None,
        REGIONAL_COUNTRY_BRIEF: (REGION, "UA"),
        STORYLINE_REPORT: None,
        EVENT_DOSSIER: (EVENT, "event-1"),
        FORECAST_REPORT: (FORECAST_VERSION, "forecast-version-1"),
        STRATEGIC_OUTLOOK: None,
    }

    for index, (report_type, subject) in enumerate(subjects.items()):
        kwargs = {}
        if subject is not None:
            kwargs = {
                "subject_ref_type": subject[0],
                "subject_ref_id": subject[1],
            }
        snapshot = ReportSnapshot.create(
            report_type,
            f"scope:{index}",
            f"Report {index}",
            "Summary",
            NOW,
            created_at=NOW,
            **kwargs,
        )
        section = ReportSection.create(
            snapshot.report_id,
            0,
            "SUMMARY_CONTEXT",
            "Context",
            OBSERVED_FACT,
            {"report_type": report_type},
            "Same common section contract.",
            created_at=NOW,
        )
        bundle = ReportBundle(snapshot, (section,), ())

        structured = ReportRenderer.structured_bundle(bundle)
        markdown = ReportRenderer.markdown_bundle(bundle)
        assert structured["snapshot"]["report_type"] == report_type
        assert structured["sections"][0]["presentation_class"] == OBSERVED_FACT
        assert snapshot.report_id in markdown


def test_project_local_runtime_entry_point_rejects_external_database(tmp_path):
    root = tmp_path / "project"
    renderer = ProjectLocalReportRenderer.open(root)
    expected = (root / "data" / "kgeopolitical_monitor.db").resolve()
    assert renderer.repository.database_path.resolve() == expected

    with pytest.raises(ValueError, match="project-local data directory"):
        ProjectLocalReportRenderer.open(root, tmp_path / "shared.db")


def _seed_cross_layer_truth(db):
    SQLiteReportRepository(db)
    with sqlite3.connect(db) as connection:
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title, verification_status,
                confidence, importance, independent_origin_count, source_class_count, origins_json
            ) VALUES ('claim-r', 'analysis-r', 'key-r', 'Claim R', 'DETECTED', 0.61, 0.7, 1, 1, '[\"origin.example\"]')
            """
        )
        connection.execute(
            "INSERT INTO region_catalog(region_code, name, region_group, created_at) VALUES ('UA', 'Ukraine', 'EUROPE', ?)",
            (NOW.isoformat(),),
        )
        connection.execute(
            "INSERT INTO language_catalog(language_code, name, created_at) VALUES ('uk', 'Ukrainian', ?)",
            (NOW.isoformat(),),
        )
        connection.execute(
            """
            INSERT INTO region_language_coverage_reports(
                report_id, watch_id, required_scopes, observed_scopes, observed_regions,
                observed_languages, missing_scopes, coverage_ratio, created_at
            ) VALUES ('coverage-r', 'watch-r', '[\"UA:uk\"]', '[\"UA:uk\"]', '[\"UA\"]', '[\"uk\"]', '[]', 1.0, ?)
            """,
            (NOW.isoformat(),),
        )
        connection.execute(
            """
            INSERT INTO graph_nodes(
                node_id, node_kind, canonical_ref_type, canonical_ref_id, label,
                attributes_json, created_at, updated_at
            ) VALUES ('node-a', 'ACTOR', 'ACTOR', 'actor:a', 'Actor A', '{}', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO graph_nodes(
                node_id, node_kind, canonical_ref_type, canonical_ref_id, label,
                attributes_json, created_at, updated_at
            ) VALUES ('node-b', 'EVENT', 'EVENT', 'event:b', 'Event B', '{}', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO graph_edges(
                edge_id, source_node_id, target_node_id, relation_type, relation_class,
                confidence, status, valid_from, valid_to, first_observed_at,
                last_observed_at, explanation, created_at, updated_at
            ) VALUES ('edge-r', 'node-a', 'node-b', 'INFLUENCES', 'INFLUENCE', 0.44,
                      'ACTIVE', NULL, NULL, ?, ?, 'Graph inference', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat(), NOW.isoformat(), NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO forecasts(
                forecast_id, target_key, question, horizon, evaluation_deadline,
                status, created_at, updated_at
            ) VALUES ('forecast-r', 'target-r', 'Question R?', 'short_term', ?, 'ACTIVE', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat(), NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO forecast_versions(
                forecast_version_id, forecast_id, version_number, input_snapshot_json,
                provenance_refs_json, assumptions_json, change_reason, created_at
            ) VALUES ('forecast-version-r', 'forecast-r', 1, '{}', '[]', '[]', 'Initial', ?)
            """,
            (NOW.isoformat(),),
        )
        connection.execute(
            """
            INSERT INTO forecast_scenario_versions(
                scenario_version_id, forecast_version_id, scenario_type, label,
                raw_probability, calibrated_probability, scenario_confidence,
                drivers_json, constraints_json, triggers_json, inhibitors_json,
                uncertainty_factors_json, invalidation_signals_json
            ) VALUES ('scenario-r', 'forecast-version-r', 'baseline', 'Baseline',
                      0.6, 0.55, 0.5, '[]', '[]', '[]', '[]', '[]', '[]')
            """
        )


def _cross_layer_state(db):
    with sqlite3.connect(db) as connection:
        return {
            "m8": connection.execute(
                "SELECT verification_status, confidence, independent_origin_count, origins_json FROM live_analysis_claims WHERE claim_id = 'claim-r'"
            ).fetchone(),
            "m10": connection.execute(
                "SELECT required_scopes, observed_scopes, observed_regions, observed_languages, coverage_ratio FROM region_language_coverage_reports WHERE report_id = 'coverage-r'"
            ).fetchone(),
            "m11": connection.execute(
                "SELECT confidence, status, explanation, updated_at FROM graph_edges WHERE edge_id = 'edge-r'"
            ).fetchone(),
            "m12_version": connection.execute(
                "SELECT input_snapshot_json, provenance_refs_json, assumptions_json, change_reason FROM forecast_versions WHERE forecast_version_id = 'forecast-version-r'"
            ).fetchone(),
            "m12_scenario": connection.execute(
                "SELECT raw_probability, calibrated_probability, scenario_confidence, invalidation_signals_json FROM forecast_scenario_versions WHERE scenario_version_id = 'scenario-r'"
            ).fetchone(),
        }


def test_rendering_is_read_only_across_m8_m10_m11_m12_truth(tmp_path):
    db = tmp_path / "project.db"
    _seed_cross_layer_truth(db)
    repo = SQLiteReportRepository(db)

    snapshot = ReportSnapshot.create(
        GLOBAL_GEOPOLITICAL_BRIEF,
        "global:isolation",
        "Isolation report",
        "Rendering must not modify upstream truth.",
        NOW,
        created_at=NOW,
        generator_version="m13.6",
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "TRACEABILITY",
        "Traceability",
        ANALYTICAL_CONTEXT,
        {"note": "Typed references remain presentation metadata."},
        "Cross-layer references are rendered without recalculation.",
        created_at=NOW,
    )
    refs = tuple(
        ReportReference.create(
            snapshot.report_id,
            kind,
            value,
            role,
            section_id=section.section_id,
            created_at=NOW,
        )
        for kind, value, role in (
            (CLAIM, "claim-r", "VERIFICATION_CONTEXT"),
            (REGION, "UA", "COVERAGE_SCOPE"),
            (LANGUAGE, "uk", "COVERAGE_SCOPE"),
            (COVERAGE_REPORT, "coverage-r", "COVERAGE"),
            (GRAPH_EDGE, "edge-r", "GRAPH_CONTEXT"),
            (FORECAST_VERSION, "forecast-version-r", "FORECAST_CONTEXT"),
            (SCENARIO_VERSION, "scenario-r", "FORECAST_SCENARIO"),
        )
    )
    saved = repo.save_bundle(ReportBundle(snapshot, (section,), refs))
    before = _cross_layer_state(db)

    renderer = ReportRenderer(repo)
    first_json = renderer.structured_json(saved.snapshot.report_id)
    first_markdown = renderer.markdown(saved.snapshot.report_id)
    restarted = ReportRenderer(SQLiteReportRepository(db))
    assert restarted.structured_json(saved.snapshot.report_id) == first_json
    assert restarted.markdown(saved.snapshot.report_id) == first_markdown

    after = _cross_layer_state(db)
    assert after == before
    assert after["m8"][2] == 1


def test_unknown_persisted_report_fails_closed(tmp_path):
    renderer = ReportRenderer(SQLiteReportRepository(tmp_path / "project.db"))
    with pytest.raises(ValueError, match="unknown persisted report"):
        renderer.structured_json("report-missing")
