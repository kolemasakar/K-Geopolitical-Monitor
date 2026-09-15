import json
import sqlite3
from datetime import datetime, timezone

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import LiveSourceCollector, LiveSourceItem
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.recovery_coverage import (
    BOUNDED_HISTORY,
    SourceRecoveryCapability,
)

PREVIOUS = datetime(2026, 9, 15, 0, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 15, 9, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    runtime = OperationalMonitoringRuntime(tmp_path / "project")
    runtime.create_watch(
        "Ukraine security", "Ukraine", 60,
        watch_id="watch-recovery", created_at=PREVIOUS,
    )
    run = runtime.start_run("watch-recovery", started_at=PREVIOUS)
    runtime.complete_run(run.run_id, completed_at=PREVIOUS)
    return runtime


class RecoverableGdelt:
    source_id = "gdelt-doc-2"
    source_name = "GDELT DOC 2.0"
    source_class = "Structured data"

    def recovery_capability(self):
        return SourceRecoveryCapability(BOUNDED_HISTORY, 24 * 3600)

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id="recovery-item",
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title="Ukraine security recovery update",
                summary="Recovered discovery metadata.",
                original_url="https://publisher.example/recovery",
                collected_at=collected_at,
                metadata={"seendate": "20260915T085500Z"},
                reliability="discovery-only",
            )
        ]


class UnknownHistoryConsilium:
    source_id = "consilium-press-releases"
    source_name = "Council of the EU / European Council Press Releases"
    source_class = "Official sources"

    def fetch(self, watch, collected_at):
        return []


def _coverage_rows(runtime, snapshot_id):
    with sqlite3.connect(runtime.database_path) as connection:
        return connection.execute(
            """
            SELECT requirement.dimension, requirement.requirement_key,
                   result.status, result.explanation
            FROM operational_coverage_requirement_results AS result
            JOIN operational_coverage_requirements AS requirement
              ON requirement.requirement_id = result.requirement_id
            WHERE result.coverage_snapshot_id = ?
            ORDER BY requirement.dimension, requirement.requirement_key
            """,
            (snapshot_id,),
        ).fetchall()


def test_recovery_collection_persists_covered_uncovered_and_freshness(tmp_path):
    runtime = _runtime(tmp_path)
    collector = LiveSourceCollector(
        runtime, [RecoverableGdelt(), UnknownHistoryConsilium()]
    )

    report = collector.collect("watch-recovery", NOW)

    assert report.recovery_window_start.isoformat() == "2026-09-15T01:00:00+00:00"
    assert report.recovery_window_end == NOW
    assert report.recovery_coverage_snapshot_id

    rows = _coverage_rows(runtime, report.recovery_coverage_snapshot_id)
    statuses = {(dimension, source): status for dimension, source, status, _ in rows}
    assert statuses[("SOURCE_ID", "gdelt-doc-2")] == "SATISFIED"
    assert statuses[("FRESHNESS", "gdelt-doc-2")] == "SATISFIED"
    assert statuses[("SOURCE_ID", "consilium-press-releases")] == "UNKNOWN"
    assert statuses[("FRESHNESS", "consilium-press-releases")] == "UNKNOWN"

    recovery = json.loads(next(row[3] for row in rows if row[:2] == ("SOURCE_ID", "gdelt-doc-2")))
    assert recovery["temporal_state"] == "RECOVERED"
    assert recovery["uncovered_intervals"] == []
    unknown = json.loads(next(
        row[3] for row in rows
        if row[:2] == ("SOURCE_ID", "consilium-press-releases")
    ))
    assert unknown["temporal_state"] == "MISSING_OR_UNPROVEN"
    assert unknown["uncovered_intervals"] == [[
        "2026-09-15T01:00:00+00:00", "2026-09-15T09:00:00+00:00"
    ]]

    result = LiveEndToEndProcessor(runtime).process_collection(
        report.collection_id, processed_at=NOW
    )
    assert result.coverage_snapshot_ids == (report.recovery_coverage_snapshot_id,)
    assert any(
        f"coverage_snapshot:{report.recovery_coverage_snapshot_id}" in finding.evidence_refs
        for finding in result.findings
    )


def test_recovery_replay_keeps_raw_item_deduplicated(tmp_path):
    runtime = _runtime(tmp_path)
    collector = LiveSourceCollector(runtime, [RecoverableGdelt()])
    first = collector.collect("watch-recovery", NOW)
    second = collector.collect("watch-recovery", NOW)
    assert first.recovery_coverage_snapshot_id != second.recovery_coverage_snapshot_id
    with sqlite3.connect(runtime.database_path) as connection:
        raw_count = connection.execute(
            "SELECT COUNT(*) FROM raw_items WHERE id = 'recovery-item'"
        ).fetchone()[0]
        provenance_count = connection.execute(
            "SELECT COUNT(*) FROM live_source_provenance WHERE raw_item_id = 'recovery-item'"
        ).fetchone()[0]
    assert raw_count == 1
    assert provenance_count == 2


class ShortHistorySource:
    source_id = "short-history"
    source_name = "Short History"
    source_class = "Official sources"

    def recovery_capability(self):
        return SourceRecoveryCapability(BOUNDED_HISTORY, 2 * 3600)

    def fetch(self, watch, collected_at):
        return [
            LiveSourceItem(
                item_id="short-item", source_id=self.source_id,
                source_name=self.source_name, source_class=self.source_class,
                title="Ukraine short history", summary="Short history item.",
                original_url="https://short.example/item",
                collected_at=collected_at, metadata={}, reliability="official",
            )
        ]


def test_partial_history_window_persists_explicit_uncovered_interval(tmp_path):
    runtime = _runtime(tmp_path)
    report = LiveSourceCollector(runtime, [ShortHistorySource()]).collect(
        "watch-recovery", NOW
    )
    rows = _coverage_rows(runtime, report.recovery_coverage_snapshot_id)
    source_row = next(row for row in rows if row[:2] == ("SOURCE_ID", "short-history"))
    assert source_row[2] == "GAP"
    payload = json.loads(source_row[3])
    assert payload["temporal_state"] == "PARTIAL_RECOVERY"
    assert payload["covered_intervals"] == [[
        "2026-09-15T07:00:00+00:00", "2026-09-15T09:00:00+00:00"
    ]]
    assert payload["uncovered_intervals"] == [[
        "2026-09-15T01:00:00+00:00", "2026-09-15T07:00:00+00:00"
    ]]
