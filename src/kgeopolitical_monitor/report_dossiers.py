"""M13.4 event dossier and report-scoped storyline composition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Iterable

from .report_assembly import ReportAssembler, ReportAssemblyRequest
from .reporting_environment import (
    ANALYTICAL_CONTEXT,
    CLAIM,
    EVENT,
    EVENT_DOSSIER,
    FINDING,
    GRAPH_EDGE,
    GRAPH_NODE,
    OBSERVED_FACT,
    RAW_ITEM,
    SOURCE,
    STORYLINE_REPORT,
    VERIFICATION_STATE,
    ReportBundle,
    ReportReference,
    ReportSection,
    ReportSnapshot,
    SQLiteReportRepository,
)


@dataclass(frozen=True)
class DossierStorylineSelection:
    event_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    raw_item_ids: tuple[str, ...] = ()
    finding_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    graph_edge_ids: tuple[str, ...] = ()
    contradiction_pairs: tuple[tuple[str, str], ...] = ()
    assumptions: tuple[str, ...] = ()

    def has_any(self) -> bool:
        return bool(
            self.event_ids
            or self.claim_ids
            or self.raw_item_ids
            or self.finding_ids
            or self.graph_node_ids
            or self.graph_edge_ids
            or self.contradiction_pairs
            or self.assumptions
        )


class DossierStorylineService:
    """Compose dossier/storyline snapshots without a hidden storyline truth model."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.assembler = ReportAssembler(self.database_path)
        self.repository = SQLiteReportRepository(self.database_path)

    @staticmethod
    def _unique(values: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))

    def _events(self, event_ids: tuple[str, ...]) -> tuple[dict[str, object], ...]:
        ids = self._unique(event_ids)
        if not ids:
            return ()
        placeholders = ",".join("?" for _ in ids)
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                f"SELECT id, title, status, importance FROM events WHERE id IN ({placeholders}) ORDER BY id",
                ids,
            ).fetchall()
        found = {row[0] for row in rows}
        missing = sorted(set(ids) - found)
        if missing:
            raise ValueError(f"unknown event reference(s): {', '.join(missing)}")
        return tuple(
            {
                "event_id": row[0],
                "title": row[1],
                "status": row[2],
                "importance": row[3],
            }
            for row in rows
        )

    def _claims(self, claim_ids: tuple[str, ...]) -> tuple[dict[str, object], ...]:
        ids = self._unique(claim_ids)
        payloads = []
        missing = []
        with sqlite3.connect(self.database_path) as connection:
            for claim_id in ids:
                row = connection.execute(
                    "SELECT id, text, confidence FROM claims WHERE id = ?",
                    (claim_id,),
                ).fetchone()
                if row is not None:
                    payloads.append(
                        {
                            "claim_id": row[0],
                            "text": row[1],
                            "verification_status": None,
                            "confidence": row[2],
                        }
                    )
                    continue
                row = connection.execute(
                    """
                    SELECT claim_id, title, verification_status, confidence, importance
                    FROM live_analysis_claims WHERE claim_id = ?
                    """,
                    (claim_id,),
                ).fetchone()
                if row is None:
                    missing.append(claim_id)
                    continue
                payloads.append(
                    {
                        "claim_id": row[0],
                        "text": row[1],
                        "verification_status": row[2],
                        "confidence": float(row[3]),
                        "importance": float(row[4]),
                    }
                )
        if missing:
            raise ValueError(f"unknown claim reference(s): {', '.join(sorted(missing))}")
        return tuple(sorted(payloads, key=lambda item: str(item["claim_id"])))

    def _raw_items(self, raw_item_ids: tuple[str, ...]) -> tuple[dict[str, object], ...]:
        ids = self._unique(raw_item_ids)
        if not ids:
            return ()
        placeholders = ",".join("?" for _ in ids)
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT r.id, r.source_id, r.title, r.collected_at, s.name, s.source_class
                FROM raw_items AS r
                LEFT JOIN sources AS s ON s.id = r.source_id
                WHERE r.id IN ({placeholders})
                ORDER BY r.collected_at, r.id
                """,
                ids,
            ).fetchall()
        found = {row[0] for row in rows}
        missing = sorted(set(ids) - found)
        if missing:
            raise ValueError(f"unknown raw item reference(s): {', '.join(missing)}")
        return tuple(
            {
                "raw_item_id": row[0],
                "source_id": row[1],
                "title": row[2],
                "collected_at": row[3],
                "source_name": row[4],
                "source_class": row[5],
            }
            for row in rows
        )

    def _contradictions(
        self,
        pairs: tuple[tuple[str, str], ...],
    ) -> tuple[tuple[str, str], ...]:
        normalized = tuple(
            sorted(
                {
                    tuple(sorted((str(left).strip(), str(right).strip())))
                    for left, right in pairs
                    if str(left).strip() and str(right).strip()
                }
            )
        )
        if any(left == right for left, right in normalized):
            raise ValueError("contradiction pair requires two different claims")
        if normalized:
            self._claims(tuple(value for pair in normalized for value in pair))
        return normalized

    def _assembler_bundle(
        self,
        snapshot: ReportSnapshot,
        selection: DossierStorylineSelection,
    ) -> ReportBundle | None:
        if not (
            selection.finding_ids
            or selection.graph_node_ids
            or selection.graph_edge_ids
            or selection.assumptions
        ):
            return None
        return self.assembler.assemble(
            ReportAssemblyRequest(
                snapshot=snapshot,
                finding_ids=selection.finding_ids,
                graph_node_ids=selection.graph_node_ids,
                graph_edge_ids=selection.graph_edge_ids,
                assumptions=selection.assumptions,
            ),
            persist=False,
        )

    def _compose(
        self,
        snapshot: ReportSnapshot,
        *,
        event_ids: tuple[str, ...],
        selection: DossierStorylineSelection,
        persist: bool,
    ) -> ReportBundle:
        events = self._events(event_ids)
        claims = self._claims(selection.claim_ids)
        raw_items = self._raw_items(selection.raw_item_ids)
        contradictions = self._contradictions(selection.contradiction_pairs)
        base = self._assembler_bundle(snapshot, selection)

        sections: list[ReportSection] = []
        references: list[ReportReference] = []

        def add_section(section_type, heading, presentation_class, content, explanation, specs):
            section = ReportSection.create(
                snapshot.report_id,
                len(sections),
                section_type,
                heading,
                presentation_class,
                content,
                explanation,
                created_at=snapshot.created_at,
            )
            sections.append(section)
            for kind, value, role in specs:
                references.append(
                    ReportReference.create(
                        snapshot.report_id,
                        kind,
                        value,
                        role,
                        section_id=section.section_id,
                        created_at=snapshot.created_at,
                    )
                )

        if events:
            add_section(
                "EVENTS",
                "Events",
                OBSERVED_FACT,
                {"events": list(events)},
                "Event rows are explicit persisted references; reporting does not change event status or importance.",
                tuple((EVENT, str(item["event_id"]), "EVENT_SCOPE") for item in events),
            )
        if claims:
            add_section(
                "CLAIMS",
                "Claims and verification state",
                VERIFICATION_STATE,
                {"claims": list(claims)},
                "Claim verification/confidence is displayed from persisted state and is not recalculated by reporting.",
                tuple((CLAIM, str(item["claim_id"]), "CLAIM_CONTEXT") for item in claims),
            )
        if raw_items:
            source_specs = []
            for item in raw_items:
                source_specs.append((RAW_ITEM, str(item["raw_item_id"]), "SOURCE_EVIDENCE"))
                if item["source_id"]:
                    source_specs.append((SOURCE, str(item["source_id"]), "SOURCE_PROVENANCE"))
            add_section(
                "SOURCE_EVIDENCE",
                "Source evidence",
                OBSERVED_FACT,
                {"raw_items": list(raw_items)},
                "Only explicitly selected persisted observations are included; source listing does not increase independent-origin counts.",
                tuple(source_specs),
            )
            timeline = [
                {
                    "raw_item_id": item["raw_item_id"],
                    "collected_at": item["collected_at"],
                    "title": item["title"],
                }
                for item in raw_items
            ]
            add_section(
                "TIMELINE",
                "Observation timeline",
                ANALYTICAL_CONTEXT,
                {"observations": timeline},
                "Timeline timestamps are persisted collection times for explicit observations, not inferred event-occurrence times.",
                tuple((RAW_ITEM, str(item["raw_item_id"]), "TIMELINE_OBSERVATION") for item in raw_items),
            )
        if contradictions:
            add_section(
                "CONTRADICTIONS",
                "Contradictions",
                ANALYTICAL_CONTEXT,
                {"claim_pairs": [list(pair) for pair in contradictions]},
                "Contradiction pairs are explicit report-scoped analytical context and do not mutate claim verification state.",
                tuple(
                    (CLAIM, claim_id, "CONTRADICTION_SIDE")
                    for pair in contradictions
                    for claim_id in pair
                ),
            )

        if base is not None:
            section_map: dict[str, str] = {}
            for old in base.sections:
                new = ReportSection.create(
                    snapshot.report_id,
                    len(sections),
                    old.section_type,
                    old.heading,
                    old.presentation_class,
                    old.content,
                    old.explanation,
                    created_at=snapshot.created_at,
                )
                sections.append(new)
                section_map[old.section_id] = new.section_id
            for old in base.references:
                references.append(
                    ReportReference.create(
                        snapshot.report_id,
                        old.reference_kind,
                        old.reference_value,
                        old.reference_role,
                        section_id=(
                            section_map.get(old.section_id)
                            if old.section_id is not None
                            else None
                        ),
                        created_at=snapshot.created_at,
                    )
                )

        if not sections:
            raise ValueError("dossier/storyline report requires explicit persisted references")
        bundle = ReportBundle(snapshot, tuple(sections), tuple(references))
        return self.repository.save_bundle(bundle) if persist else bundle

    def event_dossier(
        self,
        event_id: str,
        selection: DossierStorylineSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        normalized_event = str(event_id).strip()
        event = self._events((normalized_event,))[0]
        snapshot = ReportSnapshot.create(
            EVENT_DOSSIER,
            f"event:{normalized_event}",
            title,
            summary,
            as_of,
            subject_ref_type=EVENT,
            subject_ref_id=normalized_event,
            created_at=as_of,
            generator_version="m13.4",
        )
        return self._compose(
            snapshot,
            event_ids=(str(event["event_id"]),),
            selection=selection,
            persist=persist,
        )

    def storyline_report(
        self,
        scope_key: str,
        selection: DossierStorylineSelection,
        *,
        title: str,
        summary: str,
        as_of: datetime,
        persist: bool = True,
    ) -> ReportBundle:
        if not selection.has_any():
            raise ValueError("storyline report requires explicit persisted references")
        snapshot = ReportSnapshot.create(
            STORYLINE_REPORT,
            scope_key,
            title,
            summary,
            as_of,
            created_at=as_of,
            generator_version="m13.4",
        )
        return self._compose(
            snapshot,
            event_ids=selection.event_ids,
            selection=selection,
            persist=persist,
        )


__all__ = ["DossierStorylineSelection", "DossierStorylineService"]
