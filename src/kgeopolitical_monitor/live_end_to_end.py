"""M8 live collection to verification-aware operational output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re
import sqlite3
from urllib.parse import urlparse

from .confidence_engine import calculate_confidence
from .operational_monitoring import FAILED, OperationalMonitoringRuntime, _normalize_time
from .operational_output import FindingDraft, OperationalFinding, OperationalOutputStore


DETECTED = "DETECTED"
PARTLY_VERIFIED = "PARTLY_VERIFIED"


@dataclass(frozen=True)
class AnalyzedClaim:
    claim_id: str
    claim_key: str
    title: str
    verification_status: str
    confidence: float
    importance: float
    independent_origins: tuple[str, ...]
    source_class_count: int
    raw_item_ids: tuple[str, ...]


@dataclass(frozen=True)
class LiveAnalysisResult:
    analysis_run_id: str
    collection_id: str
    watch_id: str
    monitoring_run_id: str
    claims: tuple[AnalyzedClaim, ...]
    findings: tuple[OperationalFinding, ...]


def _stable_id(prefix: str, value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def normalize_claim_title(title: str) -> str:
    normalized = re.sub(r"[^\w]+", " ", title.casefold(), flags=re.UNICODE)
    return " ".join(normalized.split())


def _origin_host(original_url: str) -> str:
    host = (urlparse(original_url).hostname or "").casefold().strip(".")
    if not host:
        raise ValueError("live provenance original_url must contain a host")
    return host[4:] if host.startswith("www.") else host


def _reliability_value(value: str) -> str:
    normalized = value.strip().casefold()
    if normalized in {"official", "high", "very_high", "very high"}:
        return "HIGH"
    if normalized in {"medium", "pilot", "external", "discovery-only"}:
        return "MEDIUM"
    if normalized == "low":
        return "LOW"
    return "MEDIUM"


class LiveEndToEndProcessor:
    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.output = OperationalOutputStore(runtime.database_path)

    def _collection(self, collection_id: str) -> tuple[str, str] | None:
        with sqlite3.connect(self.runtime.database_path) as connection:
            return connection.execute(
                """
                SELECT watch_id, status
                FROM source_collection_runs
                WHERE collection_id = ?
                """,
                (collection_id,),
            ).fetchone()

    def _existing_analysis(self, collection_id: str) -> tuple[str, str] | None:
        with sqlite3.connect(self.runtime.database_path) as connection:
            return connection.execute(
                """
                SELECT analysis_run_id, status
                FROM live_analysis_runs
                WHERE collection_id = ?
                """,
                (collection_id,),
            ).fetchone()

    def _evidence_rows(self, collection_id: str) -> list[tuple]:
        with sqlite3.connect(self.runtime.database_path) as connection:
            return connection.execute(
                """
                SELECT r.id, r.title, r.content, r.source_id,
                       s.source_class, s.reliability,
                       p.original_url, p.metadata_json
                FROM live_source_provenance p
                JOIN raw_items r ON r.id = p.raw_item_id
                JOIN sources s ON s.id = r.source_id
                WHERE p.collection_id = ?
                ORDER BY r.id
                """,
                (collection_id,),
            ).fetchall()

    def _load_claims(self, analysis_run_id: str) -> tuple[AnalyzedClaim, ...]:
        with sqlite3.connect(self.runtime.database_path) as connection:
            rows = connection.execute(
                """
                SELECT claim_id, claim_key, title, verification_status,
                       confidence, importance, independent_origin_count,
                       source_class_count, origins_json
                FROM live_analysis_claims
                WHERE analysis_run_id = ?
                ORDER BY claim_key
                """,
                (analysis_run_id,),
            ).fetchall()
            evidence = connection.execute(
                """
                SELECT claim_id, raw_item_id
                FROM live_analysis_evidence
                WHERE claim_id IN (
                    SELECT claim_id FROM live_analysis_claims WHERE analysis_run_id = ?
                )
                ORDER BY claim_id, raw_item_id
                """,
                (analysis_run_id,),
            ).fetchall()

        evidence_by_claim: dict[str, list[str]] = {}
        for claim_id, raw_item_id in evidence:
            evidence_by_claim.setdefault(claim_id, []).append(raw_item_id)

        return tuple(
            AnalyzedClaim(
                claim_id=row[0],
                claim_key=row[1],
                title=row[2],
                verification_status=row[3],
                confidence=float(row[4]),
                importance=float(row[5]),
                independent_origins=tuple(json.loads(row[8])),
                source_class_count=int(row[7]),
                raw_item_ids=tuple(evidence_by_claim.get(row[0], [])),
            )
            for row in rows
        )

    def _monitoring_run_for_analysis(self, analysis_run_id: str) -> str:
        return _stable_id("m8-monitor", analysis_run_id)

    def _load_existing_result(
        self,
        analysis_run_id: str,
        collection_id: str,
        watch_id: str,
    ) -> LiveAnalysisResult:
        monitoring_run_id = self._monitoring_run_for_analysis(analysis_run_id)
        claims = self._load_claims(analysis_run_id)
        findings = tuple(self.output.ranked_findings(run_id=monitoring_run_id, limit=1000))
        return LiveAnalysisResult(
            analysis_run_id=analysis_run_id,
            collection_id=collection_id,
            watch_id=watch_id,
            monitoring_run_id=monitoring_run_id,
            claims=claims,
            findings=findings,
        )

    def process_collection(
        self,
        collection_id: str,
        *,
        processed_at: datetime,
    ) -> LiveAnalysisResult:
        current = _normalize_time(processed_at)
        collection = self._collection(collection_id)
        if collection is None:
            raise ValueError("source collection does not exist")
        watch_id, collection_status = collection
        if collection_status == FAILED:
            raise ValueError("FAILED source collection cannot be analyzed")
        if collection_status not in {"COMPLETED", "PARTIAL"}:
            raise ValueError("source collection is not ready for analysis")

        analysis_run_id = _stable_id("analysis", collection_id)
        existing = self._existing_analysis(collection_id)
        if existing is not None:
            existing_id, status = existing
            if status == "COMPLETED":
                return self._load_existing_result(existing_id, collection_id, watch_id)
            raise ValueError("source collection already has a non-completed analysis run")

        evidence_rows = self._evidence_rows(collection_id)
        if not evidence_rows:
            raise ValueError("source collection contains no persisted live evidence")

        grouped: dict[str, list[tuple]] = {}
        for row in evidence_rows:
            claim_key = normalize_claim_title(row[1])
            if not claim_key:
                continue
            grouped.setdefault(claim_key, []).append(row)
        if not grouped:
            raise ValueError("source collection contains no analyzable claim titles")

        monitoring_run_id = self._monitoring_run_for_analysis(analysis_run_id)
        monitoring_run = self.runtime.start_run(
            watch_id,
            run_id=monitoring_run_id,
            started_at=current,
        )

        with sqlite3.connect(self.runtime.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO live_analysis_runs(
                    analysis_run_id, collection_id, watch_id, status,
                    claim_count, finding_count, created_at
                ) VALUES (?, ?, ?, 'RUNNING', 0, 0, ?)
                """,
                (analysis_run_id, collection_id, watch_id, current.isoformat()),
            )

        analyzed_claims: list[AnalyzedClaim] = []
        try:
            for claim_key in sorted(grouped):
                rows = grouped[claim_key]
                origins = tuple(sorted({_origin_host(row[6]) for row in rows}))
                source_classes = {row[4] for row in rows}

                best_by_origin: dict[str, dict[str, str]] = {}
                for row in rows:
                    origin = _origin_host(row[6])
                    candidate = {
                        "source_id": origin,
                        "reliability": _reliability_value(str(row[5] or "")),
                    }
                    previous = best_by_origin.get(origin)
                    rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "VERY_HIGH": 4}
                    if previous is None or rank[candidate["reliability"]] > rank[previous["reliability"]]:
                        best_by_origin[origin] = candidate

                confidence = calculate_confidence(
                    evidence_items=list(best_by_origin.values()),
                    contradictions=[],
                )
                status = PARTLY_VERIFIED if len(origins) >= 2 else DETECTED
                importance = 0.5
                claim_id = _stable_id("claim", f"{analysis_run_id}:{claim_key}")
                raw_item_ids = tuple(sorted(row[0] for row in rows))
                title = sorted((row[1] for row in rows), key=lambda value: (len(value), value))[0]

                with sqlite3.connect(self.runtime.database_path) as connection:
                    connection.execute("PRAGMA foreign_keys = ON")
                    connection.execute(
                        """
                        INSERT INTO live_analysis_claims(
                            claim_id, analysis_run_id, claim_key, title,
                            verification_status, confidence, importance,
                            independent_origin_count, source_class_count, origins_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            claim_id,
                            analysis_run_id,
                            claim_key,
                            title,
                            status,
                            confidence,
                            importance,
                            len(origins),
                            len(source_classes),
                            json.dumps(origins),
                        ),
                    )
                    connection.executemany(
                        """
                        INSERT INTO live_analysis_evidence(
                            claim_id, raw_item_id, original_url, origin_host
                        ) VALUES (?, ?, ?, ?)
                        """,
                        [
                            (claim_id, row[0], row[6], _origin_host(row[6]))
                            for row in rows
                        ],
                    )

                analyzed_claims.append(
                    AnalyzedClaim(
                        claim_id=claim_id,
                        claim_key=claim_key,
                        title=title,
                        verification_status=status,
                        confidence=confidence,
                        importance=importance,
                        independent_origins=origins,
                        source_class_count=len(source_classes),
                        raw_item_ids=raw_item_ids,
                    )
                )

            drafts = []
            for claim in analyzed_claims:
                evidence_refs = (
                    f"claim:{claim.claim_id}",
                    *tuple(f"raw_item:{raw_id}" for raw_id in claim.raw_item_ids),
                    *tuple(f"origin:{origin}" for origin in claim.independent_origins),
                )
                drafts.append(
                    FindingDraft(
                        title=claim.title,
                        summary=(
                            f"Live controlled-pilot claim grouped from {len(claim.raw_item_ids)} "
                            f"observations across {len(claim.independent_origins)} independent origins."
                        ),
                        importance=claim.importance,
                        confidence=claim.confidence,
                        evidence_refs=evidence_refs,
                        explanation=(
                            f"verification_status={claim.verification_status}; "
                            f"independent_origins={len(claim.independent_origins)}; "
                            "strict normalized-title grouping; importance=0.5 neutral pilot baseline."
                        ),
                    )
                )

            findings = tuple(
                self.output.save_findings(
                    monitoring_run.run_id,
                    watch_id,
                    drafts,
                    created_at=current,
                )
            )
            self.runtime.complete_run(
                monitoring_run.run_id,
                result_count=len(findings),
                completed_at=current,
            )
            with sqlite3.connect(self.runtime.database_path) as connection:
                connection.execute(
                    """
                    UPDATE live_analysis_runs
                    SET status = 'COMPLETED', claim_count = ?, finding_count = ?
                    WHERE analysis_run_id = ?
                    """,
                    (len(analyzed_claims), len(findings), analysis_run_id),
                )

            return LiveAnalysisResult(
                analysis_run_id=analysis_run_id,
                collection_id=collection_id,
                watch_id=watch_id,
                monitoring_run_id=monitoring_run.run_id,
                claims=tuple(analyzed_claims),
                findings=findings,
            )
        except Exception as exc:
            error = str(exc).strip() or exc.__class__.__name__
            try:
                self.runtime.fail_run(monitoring_run.run_id, error, completed_at=current)
            except ValueError:
                pass
            with sqlite3.connect(self.runtime.database_path) as connection:
                connection.execute(
                    """
                    UPDATE live_analysis_runs
                    SET status = 'FAILED'
                    WHERE analysis_run_id = ?
                    """,
                    (analysis_run_id,),
                )
            raise
