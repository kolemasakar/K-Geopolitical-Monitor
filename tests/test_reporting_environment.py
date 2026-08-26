from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.reporting_environment import (
    ANALYTICAL_CONTEXT,
    ANALYST_ASSUMPTION,
    EVENT,
    EVENT_DOSSIER,
    FORECAST,
    FORECAST_REPORT,
    GLOBAL_GEOPOLITICAL_BRIEF,
    OBSERVED_FACT,
    RAW_ITEM,
    REGION,
    REGIONAL_COUNTRY_BRIEF,
    STORYLINE_REPORT,
    STRATEGIC_OUTLOOK,
    ReportBundle,
    ReportReference,
    ReportSection,
    ReportSnapshot,
    SQLiteReportRepository,
)


NOW = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)


def _seed(db):
    SQLiteReportRepository(db)
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO region_catalog(region_code, name, region_group, created_at) VALUES ('UA', 'Ukraine', 'EUROPE', ?)",
            (NOW.isoformat(),),
        )
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES ('source-1', 'Official source', 'Official sources', 'HIGH')"
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES ('raw-1', 'source-1', 'Item', 'Body', ?)",
            (NOW.isoformat(),),
        )
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES ('event-1', 'Event one', 'ACTIVE', 'HIGH')"
        )
        connection.execute(
            """
            INSERT INTO forecasts(
                forecast_id, target_key, question, horizon, evaluation_deadline,
                status, created_at, updated_at
            ) VALUES ('forecast-1', 'target-1', 'Question?', 'short_term', ?, 'ACTIVE', ?, ?)
            """,
            (NOW.isoformat(), NOW.isoformat(), NOW.isoformat()),
        )


def _regional_bundle():
    snapshot = ReportSnapshot.create(
        REGIONAL_COUNTRY_BRIEF,
        "region:UA",
        "Ukraine brief",
        "Short regional summary.",
        NOW,
        subject_ref_type=REGION,
        subject_ref_id="UA",
        created_at=NOW,
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "CRITICAL_EVENTS",
        "Critical events",
        OBSERVED_FACT,
        {"event_ids": ["event-1"]},
        "Critical events are selected from explicit persisted event references.",
        created_at=NOW,
    )
    references = (
        ReportReference.create(
            snapshot.report_id,
            EVENT,
            "event-1",
            "PRIMARY",
            section_id=section.section_id,
            created_at=NOW,
        ),
        ReportReference.create(
            snapshot.report_id,
            RAW_ITEM,
            "raw-1",
            "EVIDENCE",
            section_id=section.section_id,
            created_at=NOW,
        ),
        ReportReference.create(
            snapshot.report_id,
            REGION,
            "UA",
            "SCOPE",
            created_at=NOW,
        ),
    )
    return ReportBundle(snapshot, (section,), references)


def test_report_snapshot_identity_persistence_restart_and_idempotence(tmp_path):
    db = tmp_path / "project.db"
    _seed(db)
    bundle = _regional_bundle()
    repo = SQLiteReportRepository(db)

    first = repo.save_bundle(bundle)
    repeated = repo.save_bundle(bundle)
    restarted = SQLiteReportRepository(db).get_bundle(bundle.snapshot.report_id)

    assert first == repeated == restarted
    assert first.snapshot.report_type == REGIONAL_COUNTRY_BRIEF
    assert first.snapshot.subject_ref_type == REGION
    assert first.sections[0].presentation_class == OBSERVED_FACT
    assert tuple(item.reference_kind for item in first.references) == (REGION, EVENT, RAW_ITEM)


def test_report_snapshot_is_immutable_after_first_persistence(tmp_path):
    db = tmp_path / "project.db"
    _seed(db)
    repo = SQLiteReportRepository(db)
    bundle = _regional_bundle()
    repo.save_bundle(bundle)

    conflicting_snapshot = ReportSnapshot.create(
        REGIONAL_COUNTRY_BRIEF,
        "region:UA",
        "Ukraine brief",
        "Changed summary must create an immutable conflict.",
        NOW,
        subject_ref_type=REGION,
        subject_ref_id="UA",
        created_at=NOW,
    )
    conflicting = ReportBundle(conflicting_snapshot, bundle.sections, bundle.references)

    with pytest.raises(ValueError, match="immutable"):
        repo.save_bundle(conflicting)


def test_unknown_canonical_subject_and_reference_fail_closed(tmp_path):
    db = tmp_path / "project.db"
    _seed(db)
    repo = SQLiteReportRepository(db)

    unknown_subject = ReportSnapshot.create(
        EVENT_DOSSIER,
        "event:missing",
        "Missing event",
        "This must not persist.",
        NOW,
        subject_ref_type=EVENT,
        subject_ref_id="event-missing",
        created_at=NOW,
    )
    with pytest.raises(ValueError, match="unknown canonical report subject"):
        repo.save_bundle(ReportBundle(unknown_subject))

    snapshot = ReportSnapshot.create(
        GLOBAL_GEOPOLITICAL_BRIEF,
        "global",
        "Global brief",
        "Global summary.",
        NOW,
        created_at=NOW,
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "CONTEXT",
        "Context",
        ANALYTICAL_CONTEXT,
        {"note": "explicit refs only"},
        "Context section.",
        created_at=NOW,
    )
    missing_ref = ReportReference.create(
        snapshot.report_id,
        EVENT,
        "event-missing",
        "CONTEXT",
        section_id=section.section_id,
        created_at=NOW,
    )
    with pytest.raises(ValueError, match="unknown canonical report reference"):
        repo.save_bundle(ReportBundle(snapshot, (section,), (missing_ref,)))

    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM report_snapshots").fetchone()[0] == 0


def test_analyst_assumption_reference_is_explicit_but_does_not_require_canonical_row(tmp_path):
    db = tmp_path / "project.db"
    _seed(db)
    repo = SQLiteReportRepository(db)
    snapshot = ReportSnapshot.create(
        STRATEGIC_OUTLOOK,
        "global:30d",
        "Strategic outlook",
        "Scenario-oriented outlook.",
        NOW,
        created_at=NOW,
    )
    section = ReportSection.create(
        snapshot.report_id,
        0,
        "ASSUMPTIONS",
        "Assumptions",
        ANALYST_ASSUMPTION,
        {"assumptions": ["Negotiations continue"]},
        "Assumptions are explicitly analytical and are not source evidence.",
        created_at=NOW,
    )
    assumption = ReportReference.create(
        snapshot.report_id,
        ANALYST_ASSUMPTION,
        "Negotiations continue",
        "ASSUMPTION",
        section_id=section.section_id,
        created_at=NOW,
    )

    saved = repo.save_bundle(ReportBundle(snapshot, (section,), (assumption,)))
    assert saved.references[0].reference_kind == ANALYST_ASSUMPTION


def test_scope_only_reports_do_not_create_hidden_storyline_subject_truth():
    for report_type, scope in (
        (GLOBAL_GEOPOLITICAL_BRIEF, "global"),
        (STORYLINE_REPORT, "storyline-scope:security-negotiations"),
        (STRATEGIC_OUTLOOK, "global:90d"),
    ):
        snapshot = ReportSnapshot.create(
            report_type,
            scope,
            "Title",
            "Summary",
            NOW,
            created_at=NOW,
        )
        assert snapshot.subject_ref_type is None
        assert snapshot.subject_ref_id is None

    with pytest.raises(ValueError, match="scope-only subject semantics"):
        ReportSnapshot.create(
            STORYLINE_REPORT,
            "storyline-scope:x",
            "Storyline",
            "Summary",
            NOW,
            subject_ref_type=EVENT,
            subject_ref_id="event-1",
            created_at=NOW,
        )


def test_report_type_subject_contracts_are_explicit():
    with pytest.raises(ValueError, match="requires a canonical subject"):
        ReportSnapshot.create(
            EVENT_DOSSIER,
            "event:event-1",
            "Event dossier",
            "Summary",
            NOW,
            created_at=NOW,
        )

    with pytest.raises(ValueError, match="invalid subject reference type"):
        ReportSnapshot.create(
            REGIONAL_COUNTRY_BRIEF,
            "region:UA",
            "Regional brief",
            "Summary",
            NOW,
            subject_ref_type=EVENT,
            subject_ref_id="event-1",
            created_at=NOW,
        )

    forecast_report = ReportSnapshot.create(
        FORECAST_REPORT,
        "forecast:forecast-1",
        "Forecast report",
        "Summary",
        NOW,
        subject_ref_type=FORECAST,
        subject_ref_id="forecast-1",
        created_at=NOW,
    )
    assert forecast_report.subject_ref_type == FORECAST
