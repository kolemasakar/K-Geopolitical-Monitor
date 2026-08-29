"""Durable additive reproducibility instrumentation for machine-run research.

This module records only state actually observed by instrumented execution. It
references existing canonical provenance instead of copying source URLs,
retrieval timestamps, claim/evidence links or report references into a parallel
store.
"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import inspect
import json
import sqlite3
from typing import Iterable
from uuid import uuid4

from .live_sources import LiveSourceCollector, SourceCollectionReport
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


INSTRUMENTATION_VERSION = "E6-1.0"
ARTIFACT_HASH_BASIS = "KGM_PERSISTED_LIVE_ITEM_V1"
ALLOWED_COLLECTION_STATUSES = {"COMPLETED", "PARTIAL", "FAILED"}
ALLOWED_PROVENANCE_RELATIONS = {
    "PRIMARY_ORIGIN",
    "SYNDICATION",
    "REPOST",
    "TRANSLATION",
    "CITATION",
    "DUPLICATE",
    "DISCOVERY_INDEX",
}


def _adapter_identity(adapter: object) -> str:
    cls = adapter.__class__
    return f"{cls.__module__}.{cls.__qualname__}"


def _adapter_version(adapter: object) -> str:
    declared = str(getattr(adapter, "adapter_version", "") or "").strip()
    if declared:
        return declared
    try:
        source = inspect.getsource(adapter.__class__)
    except (OSError, TypeError):
        return "NOT_AVAILABLE"
    return f"code-sha256:{sha256(source.encode('utf-8')).hexdigest()}"


def _persisted_item_hash(
    *,
    raw_item_id: str,
    source_id: str | None,
    title: str | None,
    content: str | None,
    collected_at: str | None,
    original_url: str,
    metadata_json: str,
) -> str:
    """Hash the persisted parsed artifact, not an unpersisted remote response."""

    payload = json.dumps(
        {
            "raw_item_id": raw_item_id,
            "source_id": source_id,
            "title": title,
            "content": content,
            "collected_at": collected_at,
            "original_url": original_url,
            "metadata_json": metadata_json,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


class ReproducibilityStore:
    """Project-local append-only audit projection over existing canonical state."""

    def __init__(self, database_path) -> None:
        self.database_path = database_path

    def start_live_collection(
        self,
        *,
        watch_id: str,
        exact_query: str,
        research_cutoff: datetime,
        started_at: datetime,
    ) -> str:
        cutoff = _normalize_time(research_cutoff)
        started = _normalize_time(started_at)
        if not exact_query.strip():
            raise ValueError("exact_query must not be empty")
        research_run_id = f"research-{uuid4().hex}"
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO research_audit_runs(
                    research_run_id, run_kind, watch_id, collection_id,
                    exact_query_snapshot, research_cutoff,
                    instrumentation_version, status, collection_status,
                    started_at, completed_at, error
                ) VALUES (
                    ?, 'LIVE_COLLECTION', ?, NULL, ?, ?, ?,
                    'RUNNING', NULL, ?, NULL, NULL
                )
                """,
                (
                    research_run_id,
                    watch_id,
                    exact_query,
                    cutoff.isoformat(),
                    INSTRUMENTATION_VERSION,
                    started.isoformat(),
                ),
            )
        return research_run_id

    def fail_run(
        self,
        research_run_id: str,
        *,
        error: str,
        completed_at: datetime,
        collection_id: str | None = None,
        collection_status: str | None = None,
    ) -> None:
        normalized_error = error.strip()
        if not normalized_error:
            raise ValueError("failed research audit requires an error")
        normalized_collection_status = (
            collection_status.strip().upper() if collection_status is not None else None
        )
        if (
            normalized_collection_status is not None
            and normalized_collection_status not in ALLOWED_COLLECTION_STATUSES
        ):
            raise ValueError("unsupported source collection status for reproducibility")
        if normalized_collection_status is not None and collection_id is None:
            raise ValueError("collection_status requires collection_id")

        completed = _normalize_time(completed_at)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute(
                """
                UPDATE research_audit_runs
                SET collection_id = COALESCE(?, collection_id),
                    collection_status = COALESCE(?, collection_status),
                    status = 'FAILED', completed_at = ?, error = ?
                WHERE research_run_id = ? AND status = 'RUNNING'
                """,
                (
                    collection_id,
                    normalized_collection_status,
                    completed.isoformat(),
                    normalized_error,
                    research_run_id,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError("research audit run is missing or already terminal")

    def finalize_live_collection(
        self,
        research_run_id: str,
        report: SourceCollectionReport,
        adapters: Iterable[object],
    ) -> None:
        """Attach canonical collection evidence and machine-captured query metadata."""

        if report.status not in ALLOWED_COLLECTION_STATUSES:
            raise ValueError("unsupported source collection status for reproducibility")
        adapter_by_source: dict[str, object] = {}
        for adapter in adapters:
            source_id = str(getattr(adapter, "source_id", "") or "").strip()
            if not source_id:
                raise ValueError("instrumented adapter source_id must not be empty")
            if source_id in adapter_by_source:
                raise ValueError("instrumented adapter source_id values must be unique")
            adapter_by_source[source_id] = adapter

        completed = _normalize_time(report.completed_at)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            run = connection.execute(
                """
                SELECT exact_query_snapshot, status
                FROM research_audit_runs
                WHERE research_run_id = ?
                """,
                (research_run_id,),
            ).fetchone()
            if run is None or run[1] != "RUNNING":
                raise ValueError("research audit run is missing or already terminal")
            exact_query = str(run[0])

            attempts = connection.execute(
                """
                SELECT source_id, attempted_at
                FROM source_collection_attempts
                WHERE collection_id = ?
                ORDER BY source_id
                """,
                (report.collection_id,),
            ).fetchall()
            attempt_sources = {str(row[0]) for row in attempts}
            if attempt_sources != set(adapter_by_source):
                raise RuntimeError(
                    "source collection attempts do not match instrumented adapter identity"
                )

            for source_id, attempted_at in attempts:
                adapter = adapter_by_source[str(source_id)]
                connection.execute(
                    """
                    INSERT INTO research_query_executions(
                        research_run_id, collection_id, source_id,
                        adapter_identity, adapter_version, exact_query,
                        request_locator, request_locator_capture_state, captured_at
                    ) VALUES (?, ?, ?, ?, ?, ?, NULL, 'NOT_INSTRUMENTED', ?)
                    """,
                    (
                        research_run_id,
                        report.collection_id,
                        source_id,
                        _adapter_identity(adapter),
                        _adapter_version(adapter),
                        exact_query,
                        attempted_at,
                    ),
                )

            artifacts = connection.execute(
                """
                SELECT r.id, r.source_id, r.title, r.content, r.collected_at,
                       p.original_url, p.metadata_json
                FROM live_source_provenance p
                JOIN raw_items r ON r.id = p.raw_item_id
                WHERE p.collection_id = ?
                ORDER BY r.id
                """,
                (report.collection_id,),
            ).fetchall()
            for row in artifacts:
                content_hash = _persisted_item_hash(
                    raw_item_id=str(row[0]),
                    source_id=row[1],
                    title=row[2],
                    content=row[3],
                    collected_at=row[4],
                    original_url=str(row[5]),
                    metadata_json=str(row[6]),
                )
                connection.execute(
                    """
                    INSERT INTO research_artifact_hashes(
                        research_run_id, raw_item_id, hash_algorithm,
                        content_hash, hash_basis, captured_at
                    ) VALUES (?, ?, 'SHA256', ?, ?, ?)
                    """,
                    (
                        research_run_id,
                        row[0],
                        content_hash,
                        ARTIFACT_HASH_BASIS,
                        completed.isoformat(),
                    ),
                )

            cursor = connection.execute(
                """
                UPDATE research_audit_runs
                SET collection_id = ?, status = 'COMPLETED',
                    collection_status = ?, completed_at = ?, error = NULL
                WHERE research_run_id = ? AND status = 'RUNNING'
                """,
                (
                    report.collection_id,
                    report.status,
                    completed.isoformat(),
                    research_run_id,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("research audit run finalization did not persist")

    def annotate_provenance(
        self,
        research_run_id: str,
        raw_item_id: str,
        *,
        origin_id: str,
        relation_class: str,
        classification_basis: str,
        classified_at: datetime,
    ) -> None:
        """Persist an explicit classification only when an analyst/system actually made it."""

        normalized_relation = relation_class.strip().upper()
        if normalized_relation not in ALLOWED_PROVENANCE_RELATIONS:
            raise ValueError("unsupported provenance relation_class")
        if not origin_id.strip():
            raise ValueError("origin_id must not be empty")
        if not classification_basis.strip():
            raise ValueError("classification_basis must not be empty")
        timestamp = _normalize_time(classified_at)

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            belongs = connection.execute(
                """
                SELECT 1
                FROM research_audit_runs a
                JOIN live_source_provenance p
                  ON p.collection_id = a.collection_id
                WHERE a.research_run_id = ? AND p.raw_item_id = ?
                """,
                (research_run_id, raw_item_id),
            ).fetchone()
            if belongs is None:
                raise ValueError("raw item does not belong to research audit collection")
            connection.execute(
                """
                INSERT INTO research_provenance_annotations(
                    research_run_id, raw_item_id, origin_id, relation_class,
                    classification_basis, classified_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    research_run_id,
                    raw_item_id,
                    origin_id,
                    normalized_relation,
                    classification_basis,
                    timestamp.isoformat(),
                ),
            )

    def bundle_for_collection(self, collection_id: str) -> dict[str, object] | None:
        """Return a reproducibility bundle without inventing absent classifications."""

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            run = connection.execute(
                """
                SELECT research_run_id, run_kind, watch_id, collection_id,
                       exact_query_snapshot, research_cutoff,
                       instrumentation_version, status, collection_status,
                       started_at, completed_at, error
                FROM research_audit_runs
                WHERE collection_id = ?
                """,
                (collection_id,),
            ).fetchone()
            if run is None:
                return None
            research_run_id = str(run["research_run_id"])

            query_rows = connection.execute(
                """
                SELECT q.source_id, q.adapter_identity, q.adapter_version,
                       q.exact_query, q.request_locator,
                       q.request_locator_capture_state, q.captured_at,
                       a.status AS attempt_status, a.item_count,
                       a.error AS attempt_error, a.attempted_at
                FROM research_query_executions q
                JOIN source_collection_attempts a
                  ON a.collection_id = q.collection_id
                 AND a.source_id = q.source_id
                WHERE q.research_run_id = ?
                ORDER BY q.source_id
                """,
                (research_run_id,),
            ).fetchall()

            artifact_rows = connection.execute(
                """
                SELECT h.raw_item_id, h.hash_algorithm, h.content_hash,
                       h.hash_basis, h.captured_at, r.source_id,
                       r.collected_at, p.original_url,
                       n.origin_id, n.relation_class,
                       n.classification_basis, n.classified_at
                FROM research_artifact_hashes h
                JOIN raw_items r ON r.id = h.raw_item_id
                JOIN live_source_provenance p
                  ON p.raw_item_id = h.raw_item_id
                 AND p.collection_id = ?
                LEFT JOIN research_provenance_annotations n
                  ON n.research_run_id = h.research_run_id
                 AND n.raw_item_id = h.raw_item_id
                WHERE h.research_run_id = ?
                ORDER BY h.raw_item_id
                """,
                (collection_id, research_run_id),
            ).fetchall()

        return {
            "research_run": dict(run),
            "query_executions": [dict(row) for row in query_rows],
            "artifacts": [dict(row) for row in artifact_rows],
            "classification_note": (
                "origin/relation fields remain null unless explicitly classified; "
                "absence is not reconstructed or inferred from URL count"
            ),
        }


class ReproducibilityInstrumentedCollector:
    """Fail-closed wrapper adding E6 audit capture to the existing M7 collector."""

    def __init__(self, collector: LiveSourceCollector) -> None:
        self.collector = collector
        self.runtime: OperationalMonitoringRuntime = collector.runtime
        self.adapters = list(collector.adapters)
        self.reproducibility = ReproducibilityStore(self.runtime.database_path)

    def collect(self, watch_id: str, now: datetime) -> SourceCollectionReport:
        current = _normalize_time(now)
        watch = self.runtime.repository.get_watch(watch_id)
        if watch is None:
            raise ValueError("watch does not exist")
        if not watch.enabled:
            raise ValueError("disabled watch cannot collect live sources")

        research_run_id = self.reproducibility.start_live_collection(
            watch_id=watch.watch_id,
            exact_query=watch.query,
            research_cutoff=current,
            started_at=current,
        )
        try:
            report = self.collector.collect(watch_id, current)
        except Exception as exc:
            error = str(exc).strip() or exc.__class__.__name__
            self.reproducibility.fail_run(
                research_run_id,
                error=f"instrumented collection failed before terminal report: {error}",
                completed_at=current,
            )
            raise

        try:
            self.reproducibility.finalize_live_collection(
                research_run_id,
                report,
                self.adapters,
            )
        except Exception as exc:
            error = str(exc).strip() or exc.__class__.__name__
            try:
                self.reproducibility.fail_run(
                    research_run_id,
                    collection_id=report.collection_id,
                    collection_status=report.status,
                    error=f"reproducibility finalization failed: {error}",
                    completed_at=report.completed_at,
                )
            except Exception:
                pass
            raise RuntimeError(f"reproducibility finalization failed: {error}") from exc

        return report
