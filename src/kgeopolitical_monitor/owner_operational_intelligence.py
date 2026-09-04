"""Phase 14 owner operational intelligence readiness layer.

This module is intentionally read-only. It projects existing project-local runtime
state into an owner-facing operational workspace while enforcing the Phase 13
semantic verification boundary. Legacy live-analysis verification/confidence and
host/source counts remain compatibility metadata and never become canonical truth.

The module does not activate unattended operation, mutate watches or alerts, open
public ingress, enable paid providers, or change ``PRODUCTION_LIVE``. Operational
activation remains an explicit owner decision outside this package.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json

from .admin_dashboard_app import AdminDashboardReader
from .operational_monitoring import OperationalMonitoringRuntime
from .semantic_live_compatibility import SemanticLiveCompatibilityService


OWNER_OPERATIONAL_INTELLIGENCE_VERSION = "P14-1.0"
PHASE_14_GATE = "PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY"
OWNER_OPERATIONAL_ACTIVATION = "OWNER_DECISION_REQUIRED"
PRODUCTION_LIVE = "NOT_OPERATIONAL"
RUNTIME_STORAGE = "PROJECT_LOCAL_ONLY"

_CANONICAL_ALERT_RANK = {
    "DETECTED": 0,
    "PARTLY_VERIFIED": 1,
    "VERIFIED": 2,
}
_PRIORITY_RANK = {None: -1, "NORMAL": 0, "HIGH": 1, "CRITICAL": 2}


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("owner operational intelligence timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _limit(value: int, *, maximum: int = 100) -> int:
    number = int(value)
    if number <= 0 or number > maximum:
        raise ValueError(f"limit must be between 1 and {maximum}")
    return number


def _json_refs(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return ()
    if not isinstance(parsed, list):
        return ()
    return tuple(str(item) for item in parsed)


class OwnerOperationalIntelligenceReader(AdminDashboardReader):
    """Read-only owner workspace over persisted KGM state.

    Canonical verification is accepted only from a current P13.5 decision reached
    through the explicit P13.1/P13.6 live-compatibility link. Missing, stale,
    ambiguous, or unlinked state fails closed.
    """

    def __init__(self, runtime: OperationalMonitoringRuntime):
        super().__init__(runtime)
        self._semantic = SemanticLiveCompatibilityService(runtime)

    def _semantic_binding(self, evidence_refs_json: str | None) -> dict[str, object]:
        refs = _json_refs(evidence_refs_json)
        live_claim_ids = tuple(
            ref.split(":", 1)[1]
            for ref in refs
            if ref.startswith("claim:")
            and len(ref.split(":", 1)) == 2
            and ref.split(":", 1)[1]
        )
        unique_claim_ids = tuple(dict.fromkeys(live_claim_ids))

        base: dict[str, object] = {
            "live_claim_ids": list(unique_claim_ids),
            "live_claim_id": unique_claim_ids[0] if len(unique_claim_ids) == 1 else None,
            "semantic_compatibility_state": None,
            "semantic_claim_version_id": None,
            "semantic_verification_state": None,
            "canonical_verification_available": False,
            "canonical_verification_source": None,
            "reproducibility_state": None,
            "research_run_id": None,
            "legacy_live_verification_status": None,
            "legacy_live_confidence": None,
            "legacy_independent_origin_count": None,
            "legacy_fields_canonical": False,
        }

        if not unique_claim_ids:
            base["semantic_compatibility_state"] = "NO_LIVE_CLAIM_REF"
            return base
        if len(unique_claim_ids) != 1:
            base["semantic_compatibility_state"] = "AMBIGUOUS_LIVE_CLAIM_REFS"
            return base

        try:
            projection = self._semantic.project(unique_claim_ids[0])
        except ValueError:
            base["semantic_compatibility_state"] = "MISSING_LIVE_CLAIM"
            return base

        base.update(
            {
                "semantic_compatibility_state": projection.compatibility_state,
                "semantic_claim_version_id": projection.semantic_claim_version_id,
                "semantic_verification_state": projection.semantic_verification_state,
                "canonical_verification_available": projection.semantic_decision is not None,
                "canonical_verification_source": (
                    "P13.5_DECISION" if projection.semantic_decision is not None else None
                ),
                "reproducibility_state": projection.reproducibility_state,
                "research_run_id": projection.research_run_id,
                "legacy_live_verification_status": (
                    projection.legacy.legacy_verification_status
                ),
                "legacy_live_confidence": projection.legacy.legacy_confidence,
                "legacy_independent_origin_count": (
                    projection.legacy.legacy_independent_origin_count
                ),
            }
        )
        return base

    def recent_findings(self, limit: int = 20) -> list[dict[str, object]]:
        count = _limit(limit)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT finding_id, run_id, watch_id, title, summary,
                       importance, confidence, evidence_refs, explanation, created_at
                FROM operational_findings
                ORDER BY created_at DESC, importance DESC, finding_id DESC
                LIMIT ?
                """,
                (count,),
            ).fetchall()

        result: list[dict[str, object]] = []
        for row in rows:
            binding = self._semantic_binding(row[7])
            result.append(
                {
                    "finding_id": row[0],
                    "run_id": row[1],
                    "watch_id": row[2],
                    "title": row[3],
                    "summary": row[4],
                    "importance_score": float(row[5]),
                    "finding_confidence": float(row[6]),
                    "finding_confidence_semantics": "ANALYTICAL_NON_FACTUAL",
                    "evidence_refs": list(_json_refs(row[7])),
                    "explanation": row[8],
                    "created_at": row[9],
                    **binding,
                }
            )
        return result

    def recent_alerts(self, limit: int = 20) -> list[dict[str, object]]:
        count = _limit(limit)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT a.alert_id, a.watch_id, a.finding_id, a.trigger_type,
                       a.priority, a.status, a.first_triggered_at, a.last_updated_at,
                       a.explanation, a.invalidation_reason,
                       f.title, f.summary, f.importance, f.confidence, f.evidence_refs
                FROM strategic_alerts a
                JOIN operational_findings f ON f.finding_id = a.finding_id
                ORDER BY a.last_updated_at DESC, a.alert_id DESC
                LIMIT ?
                """,
                (count,),
            ).fetchall()

        result: list[dict[str, object]] = []
        for row in rows:
            binding = self._semantic_binding(row[14])
            result.append(
                {
                    "alert_id": row[0],
                    "watch_id": row[1],
                    "finding_id": row[2],
                    "trigger_type": row[3],
                    "priority": row[4],
                    "status": row[5],
                    "first_triggered_at": row[6],
                    "last_updated_at": row[7],
                    "alert_explanation": row[8],
                    "invalidation_reason": row[9],
                    "event": row[10],
                    "summary": row[11],
                    "importance_score": float(row[12]),
                    "finding_confidence": float(row[13]),
                    "finding_confidence_semantics": "ANALYTICAL_NON_FACTUAL",
                    "historical_alert_record": True,
                    "historical_alert_record_is_canonical_verification": False,
                    **binding,
                }
            )
        return result

    def watch_queue(self, *, now: datetime | None = None) -> list[dict[str, object]]:
        current = _normalize_time(now or datetime.now(timezone.utc))
        watches = self.watch_states(now=current)
        with self._connect() as connection:
            policy_rows = connection.execute(
                """
                SELECT watch_id, priority, minimum_importance, minimum_confidence,
                       minimum_verification_rank, created_at, updated_at
                FROM monitoring_watch_alert_policies
                ORDER BY watch_id
                """
            ).fetchall()
            alert_rows = connection.execute(
                """
                SELECT watch_id,
                       SUM(CASE WHEN priority='NORMAL' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN priority='HIGH' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN priority='CRITICAL' THEN 1 ELSE 0 END)
                FROM strategic_alerts
                WHERE status IN ('OPEN', 'UPDATED')
                GROUP BY watch_id
                """
            ).fetchall()

        policies = {
            str(row[0]): {
                "priority": row[1],
                "minimum_importance": float(row[2]),
                "minimum_confidence": float(row[3]),
                "minimum_verification_rank": int(row[4]),
                "created_at": row[5],
                "updated_at": row[6],
            }
            for row in policy_rows
        }
        alert_counts = {
            str(row[0]): {
                "NORMAL": int(row[1] or 0),
                "HIGH": int(row[2] or 0),
                "CRITICAL": int(row[3] or 0),
            }
            for row in alert_rows
        }

        queue: list[dict[str, object]] = []
        for watch in watches:
            watch_id = str(watch["watch_id"])
            policy = policies.get(watch_id)
            counts = alert_counts.get(watch_id, {"NORMAL": 0, "HIGH": 0, "CRITICAL": 0})
            if counts["CRITICAL"]:
                active_alert_priority = "CRITICAL"
            elif counts["HIGH"]:
                active_alert_priority = "HIGH"
            elif counts["NORMAL"]:
                active_alert_priority = "NORMAL"
            else:
                active_alert_priority = None
            queue.append(
                {
                    **watch,
                    "alert_policy": policy,
                    "configured_priority": None if policy is None else policy["priority"],
                    "active_alert_counts": counts,
                    "active_alert_priority": active_alert_priority,
                    "owner_execution_enabled": False,
                    "owner_execution_state": OWNER_OPERATIONAL_ACTIVATION,
                }
            )

        queue.sort(
            key=lambda item: (
                -_PRIORITY_RANK.get(item.get("active_alert_priority"), -1),
                -_PRIORITY_RANK.get(item.get("configured_priority"), -1),
                0 if item.get("due") else 1,
                str(item.get("watch_id")),
            )
        )
        return queue

    def dry_run_alert_qualification(self, finding_id: str) -> dict[str, object]:
        identity = str(finding_id).strip()
        if not identity:
            raise ValueError("finding_id must not be empty")

        with self._connect() as connection:
            finding = connection.execute(
                """
                SELECT finding_id, watch_id, importance, confidence, evidence_refs
                FROM operational_findings
                WHERE finding_id = ?
                """,
                (identity,),
            ).fetchone()
            if finding is None:
                raise ValueError("operational finding does not exist")
            policy = connection.execute(
                """
                SELECT priority, minimum_importance, minimum_confidence,
                       minimum_verification_rank
                FROM monitoring_watch_alert_policies
                WHERE watch_id = ?
                """,
                (finding[1],),
            ).fetchone()

        binding = self._semantic_binding(finding[4])
        semantic_state = binding.get("semantic_verification_state")
        semantic_rank = _CANONICAL_ALERT_RANK.get(str(semantic_state), -1)

        if policy is None:
            thresholds: dict[str, object] | None = None
            would_qualify = False
            reason = "NO_PERSISTED_ALERT_POLICY"
        else:
            thresholds = {
                "priority": policy[0],
                "minimum_importance": float(policy[1]),
                "minimum_confidence": float(policy[2]),
                "minimum_verification_rank": int(policy[3]),
            }
            importance_ok = float(finding[2]) >= float(policy[1])
            analytical_confidence_ok = float(finding[3]) >= float(policy[2])
            canonical_verification_ok = semantic_rank >= int(policy[3])
            would_qualify = (
                importance_ok and analytical_confidence_ok and canonical_verification_ok
            )
            if not binding["canonical_verification_available"]:
                reason = "NO_CANONICAL_SEMANTIC_DECISION"
            elif not canonical_verification_ok:
                reason = "CANONICAL_VERIFICATION_BELOW_POLICY"
            elif not importance_ok:
                reason = "IMPORTANCE_BELOW_POLICY"
            elif not analytical_confidence_ok:
                reason = "ANALYTICAL_CONFIDENCE_BELOW_POLICY"
            else:
                reason = "QUALIFIES_IF_OWNER_ACTIVATES_PHASE_14"

        return {
            "evaluation_mode": "DRY_RUN_READ_ONLY",
            "owner_operational_activation": OWNER_OPERATIONAL_ACTIVATION,
            "activation_blocked": True,
            "persisted_alert_created": False,
            "finding_id": finding[0],
            "watch_id": finding[1],
            "importance_score": float(finding[2]),
            "finding_confidence": float(finding[3]),
            "finding_confidence_semantics": "ANALYTICAL_NON_FACTUAL",
            "policy": thresholds,
            "canonical_verification_rank": semantic_rank,
            "would_qualify_after_activation": would_qualify,
            "reason": reason,
            "legacy_verification_used_for_qualification": False,
            **binding,
        }

    def operational_health(self, *, now: datetime | None = None) -> dict[str, object]:
        current = _normalize_time(now or datetime.now(timezone.utc))
        watches = self.watch_queue(now=current)
        sources = self.source_states()
        coverage = self.latest_coverage()
        runs = self.monitoring_runs(limit=100)

        degraded_sources = [
            item
            for item in sources
            if item.get("availability_state") in {"UNAVAILABLE", "STALE"}
        ]
        failed_watches = [item for item in watches if item.get("failed")]
        running_watches = [item for item in watches if item.get("running")]
        due_watches = [item for item in watches if item.get("due")]

        return {
            "observed_at": current.isoformat(),
            "runtime_storage": RUNTIME_STORAGE,
            "production_live": PRODUCTION_LIVE,
            "owner_operational_activation": OWNER_OPERATIONAL_ACTIVATION,
            "persisted_backend_state_only": True,
            "ad_hoc_web_substitution": False,
            "active_watch_count": len(watches),
            "due_watch_count": len(due_watches),
            "running_watch_count": len(running_watches),
            "failed_watch_count": len(failed_watches),
            "degraded_source_count": len(degraded_sources),
            "degraded_sources": degraded_sources,
            "latest_coverage": coverage,
            "last_monitoring_run": runs[0] if runs else None,
        }

    def owner_brief(self, *, now: datetime | None = None, limit: int = 10) -> dict[str, object]:
        current = _normalize_time(now or datetime.now(timezone.utc))
        findings = self.recent_findings(limit=limit)
        alerts = self.recent_alerts(limit=limit)
        health = self.operational_health(now=current)

        verified = [
            item for item in findings if item.get("semantic_verification_state") == "VERIFIED"
        ]
        unresolved = [
            item for item in findings if item.get("semantic_verification_state") != "VERIFIED"
        ]

        limitations: list[str] = []
        if health["degraded_source_count"]:
            limitations.append("DEGRADED_SOURCES_PRESENT")
        coverage = health["latest_coverage"]
        if not coverage:
            limitations.append("NO_PERSISTED_COVERAGE_ASSESSMENT")
        else:
            if any(
                int(item.get("gap_count") or 0)
                + int(item.get("unavailable_count") or 0)
                + int(item.get("stale_count") or 0)
                + int(item.get("unknown_count") or 0)
                + int(item.get("unmeasured_count") or 0)
                > 0
                for item in coverage
            ):
                limitations.append("COVERAGE_LIMITATIONS_PRESENT")
        if any(not item.get("canonical_verification_available") for item in findings):
            limitations.append("UNRESOLVED_SEMANTIC_VERIFICATION_PRESENT")

        return {
            "brief_contract_version": OWNER_OPERATIONAL_INTELLIGENCE_VERSION,
            "generated_at": current.isoformat(),
            "runtime_storage": RUNTIME_STORAGE,
            "production_live": PRODUCTION_LIVE,
            "owner_operational_activation": OWNER_OPERATIONAL_ACTIVATION,
            "verified_items": verified,
            "analysis_or_unresolved_items": unresolved,
            "alerts": alerts,
            "coverage": coverage,
            "limitations": limitations,
            "coverage_is_verification": False,
            "legacy_counts_establish_independence": False,
            "legacy_scalar_confidence_is_canonical": False,
        }

    def workspace_snapshot(
        self,
        *,
        now: datetime | None = None,
        limit: int = 20,
    ) -> dict[str, object]:
        current = _normalize_time(now or datetime.now(timezone.utc))
        count = _limit(limit)
        return {
            "owner_operational_intelligence_version": OWNER_OPERATIONAL_INTELLIGENCE_VERSION,
            "phase_14_gate": PHASE_14_GATE,
            "phase_14_gate_state": "IMPLEMENTED_VALIDATION_PENDING",
            "owner_operational_activation": OWNER_OPERATIONAL_ACTIVATION,
            "owner_execution_enabled": False,
            "runtime_storage": RUNTIME_STORAGE,
            "production_live": PRODUCTION_LIVE,
            "generated_at": current.isoformat(),
            "watches": self.watch_queue(now=current),
            "findings": self.recent_findings(limit=count),
            "alerts": self.recent_alerts(limit=count),
            "health": self.operational_health(now=current),
            "brief": self.owner_brief(now=current, limit=min(count, 10)),
        }
