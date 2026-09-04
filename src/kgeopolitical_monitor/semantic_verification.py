"""Phase 13 P13.5 policy-controlled semantic verification and confidence.

This additive layer evaluates P13.1 semantic claims against current P13.3
semantic evidence/independence and current P13.4 contradiction state. It keeps
legacy count-based verification/confidence APIs readable for compatibility but
does not use them as canonical truth rules. Confidence is multidimensional and
contains no promotional scalar. P13.6 remains responsible for live cutover.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Mapping

from .database import runtime_database_connection
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


SEMANTIC_VERIFICATION_MODEL_VERSION = "P13.5-1.0"
VERIFICATION_STATES = (
    "DETECTED",
    "PARTLY_VERIFIED",
    "VERIFIED",
    "DISPUTED",
    "UNVERIFIABLE",
)
CONFIDENCE_LEVELS = ("UNKNOWN", "LOW", "MEDIUM", "HIGH")
COVERAGE_LIMITATIONS = ("UNKNOWN", "LIMITED", "ADEQUATE")
POLICY_REVIEW_STATUSES = ("APPROVED", "RETIRED")
DECISION_CODES = (
    "INITIAL",
    "HOLD",
    "PROMOTE",
    "DEMOTE",
    "DISPUTE",
    "MARK_UNVERIFIABLE",
)
CONFIDENCE_DIMENSIONS = (
    "evidence_sufficiency",
    "provenance_independence",
    "authority_proximity",
    "contradiction_resolution",
    "temporal_freshness",
    "extraction_certainty",
    "translation_certainty",
    "claim_specific_certainty",
)
_LEVEL_RANK = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
_STATE_RANK = {"DETECTED": 0, "PARTLY_VERIFIED": 1, "VERIFIED": 2}

DEFAULT_POLICY_RULES: dict[str, object] = {
    "count_only_promotion_forbidden": True,
    "official_status_only_promotion_forbidden": True,
    "source_reputation_only_promotion_forbidden": True,
    "coverage_confidence_promotion_forbidden": True,
    "verified_requires_explicit_independent_support_pair": True,
    "verified_blocks_current_contradicting_evidence": True,
    "verified_blocks_unresolved_contradiction": True,
    "verified_minimum_confidence": {
        "evidence_sufficiency": "HIGH",
        "provenance_independence": "HIGH",
        "authority_proximity": "MEDIUM",
        "contradiction_resolution": "HIGH",
        "temporal_freshness": "MEDIUM",
        "extraction_certainty": "MEDIUM",
        "translation_certainty": "MEDIUM",
        "claim_specific_certainty": "MEDIUM",
    },
    "partly_verified_minimum_confidence": {
        "evidence_sufficiency": "MEDIUM",
        "extraction_certainty": "MEDIUM",
        "claim_specific_certainty": "MEDIUM",
    },
}


def _required(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _optional(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _enum(value: object, field_name: str, allowed: tuple[str, ...]) -> str:
    normalized = _required(value, field_name).upper()
    if normalized not in allowed:
        raise ValueError(f"unsupported {field_name}: {normalized}")
    return normalized


def _stable_version_id(prefix: str, identity: str, version: int) -> str:
    digest = sha256(f"{identity}:{version}".encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _confidence_identity(claim_version_id: str) -> str:
    digest = sha256(claim_version_id.encode("utf-8")).hexdigest()[:24]
    return f"semantic-factual-confidence-{digest}"


def _decision_identity(claim_version_id: str) -> str:
    digest = sha256(claim_version_id.encode("utf-8")).hexdigest()[:24]
    return f"semantic-verification-decision-{digest}"


def _json_object(value: Mapping[str, object], field_name: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object mapping")
    try:
        encoded = json.dumps(dict(value), sort_keys=True, ensure_ascii=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON-serializable") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return decoded


def _normalize_minimums(
    supplied: object,
    baseline: Mapping[str, str],
    field_name: str,
) -> dict[str, str]:
    if not isinstance(supplied, Mapping):
        raise ValueError(f"{field_name} must be an object mapping")
    normalized = dict(baseline)
    for key, value in supplied.items():
        name = str(key)
        if name not in CONFIDENCE_DIMENSIONS:
            raise ValueError(f"unsupported confidence dimension in {field_name}: {name}")
        level = _enum(value, name, CONFIDENCE_LEVELS)
        floor = baseline.get(name, "UNKNOWN")
        if _LEVEL_RANK[level] < _LEVEL_RANK[floor]:
            raise ValueError(f"{field_name} cannot weaken canonical minimum for {name}")
        normalized[name] = level
    return normalized


def _normalize_rules(rules: Mapping[str, object] | None) -> dict[str, object]:
    base = json.loads(json.dumps(DEFAULT_POLICY_RULES))
    if rules is None:
        return base
    supplied = _json_object(rules, "rules")
    allowed = set(DEFAULT_POLICY_RULES)
    unknown = set(supplied) - allowed
    if unknown:
        raise ValueError(f"unsupported policy rule: {sorted(unknown)[0]}")
    invariant_true = {
        "count_only_promotion_forbidden",
        "official_status_only_promotion_forbidden",
        "source_reputation_only_promotion_forbidden",
        "coverage_confidence_promotion_forbidden",
        "verified_requires_explicit_independent_support_pair",
        "verified_blocks_current_contradicting_evidence",
        "verified_blocks_unresolved_contradiction",
    }
    for key in invariant_true:
        if key in supplied and supplied[key] is not True:
            raise ValueError(f"policy cannot weaken permanent invariant: {key}")
        base[key] = True
    if "verified_minimum_confidence" in supplied:
        base["verified_minimum_confidence"] = _normalize_minimums(
            supplied["verified_minimum_confidence"],
            DEFAULT_POLICY_RULES["verified_minimum_confidence"],
            "verified_minimum_confidence",
        )
    if "partly_verified_minimum_confidence" in supplied:
        base["partly_verified_minimum_confidence"] = _normalize_minimums(
            supplied["partly_verified_minimum_confidence"],
            DEFAULT_POLICY_RULES["partly_verified_minimum_confidence"],
            "partly_verified_minimum_confidence",
        )
    return base


@dataclass(frozen=True)
class SemanticVerificationPolicyVersion:
    policy_version_id: str
    policy_id: str
    policy_version: int
    policy_name: str
    rules: dict[str, object]
    review_status: str
    supersedes_policy_version_id: str | None
    created_at: datetime

    @property
    def permits_count_only_promotion(self) -> bool:
        return False


@dataclass(frozen=True)
class SemanticFactualConfidenceVersion:
    factual_confidence_version_id: str
    factual_confidence_id: str
    confidence_version: int
    semantic_claim_version_id: str
    evidence_sufficiency: str
    provenance_independence: str
    authority_proximity: str
    contradiction_resolution: str
    temporal_freshness: str
    extraction_certainty: str
    translation_certainty: str
    claim_specific_certainty: str
    coverage_limitation: str
    assessment_method: str
    assessment_version: str
    note: str | None
    supersedes_confidence_version_id: str | None
    created_at: datetime

    @property
    def presentation_scalar(self) -> None:
        return None

    @property
    def coverage_confidence(self) -> None:
        return None

    @property
    def changes_verification_state(self) -> bool:
        return False


@dataclass(frozen=True)
class SemanticVerificationDecisionVersion:
    verification_decision_version_id: str
    verification_decision_id: str
    decision_version: int
    semantic_claim_version_id: str
    policy_version_id: str
    factual_confidence_version_id: str
    verification_state: str
    decision_code: str
    evidence_snapshot: tuple[dict[str, object], ...]
    independence_snapshot: tuple[dict[str, object], ...]
    contradiction_snapshot: tuple[dict[str, object], ...]
    rationale: str
    supersedes_decision_version_id: str | None
    created_at: datetime

    @property
    def is_policy_controlled(self) -> bool:
        return True

    @property
    def coverage_confidence(self) -> None:
        return None


class SemanticVerificationService:
    """Append-only P13.5 policies, confidence profiles and decisions."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def record_policy_version(
        self,
        policy_id: str,
        *,
        policy_name: str,
        rules: Mapping[str, object] | None = None,
        review_status: str = "APPROVED",
        created_at: datetime,
    ) -> SemanticVerificationPolicyVersion:
        identity = _required(policy_id, "policy_id")
        name = _required(policy_name, "policy_name")
        normalized_rules = _normalize_rules(rules)
        status = _enum(review_status, "review_status", POLICY_REVIEW_STATUSES)
        timestamp = _normalize_time(created_at)
        with runtime_database_connection(self.database_path) as connection:
            previous = connection.execute(
                "SELECT policy_version_id,policy_version FROM semantic_verification_policy_versions WHERE policy_id=? ORDER BY policy_version DESC LIMIT 1",
                (identity,),
            ).fetchone()
            version = 1 if previous is None else int(previous[1]) + 1
            supersedes = None if previous is None else previous[0]
            version_id = _stable_version_id("semantic-verification-policy-version", identity, version)
            connection.execute(
                """INSERT INTO semantic_verification_policy_versions(
                    policy_version_id,policy_id,policy_version,policy_name,rules_json,
                    review_status,supersedes_policy_version_id,created_at
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    version_id,
                    identity,
                    version,
                    name,
                    json.dumps(normalized_rules, sort_keys=True, ensure_ascii=False),
                    status,
                    supersedes,
                    timestamp.isoformat(),
                ),
            )
        return SemanticVerificationPolicyVersion(
            version_id, identity, version, name, normalized_rules, status, supersedes, timestamp
        )

    def policy_current(self, policy_id: str) -> SemanticVerificationPolicyVersion | None:
        identity = _required(policy_id, "policy_id")
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """SELECT policy_version_id,policy_id,policy_version,policy_name,rules_json,
                          review_status,supersedes_policy_version_id,created_at
                   FROM semantic_verification_policy_versions
                   WHERE policy_id=? ORDER BY policy_version DESC LIMIT 1""",
                (identity,),
            ).fetchone()
        return None if row is None else self._policy_from_row(row)

    def policy_history(self, policy_id: str) -> tuple[SemanticVerificationPolicyVersion, ...]:
        identity = _required(policy_id, "policy_id")
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT policy_version_id,policy_id,policy_version,policy_name,rules_json,
                          review_status,supersedes_policy_version_id,created_at
                   FROM semantic_verification_policy_versions
                   WHERE policy_id=? ORDER BY policy_version""",
                (identity,),
            ).fetchall()
        return tuple(self._policy_from_row(row) for row in rows)

    def record_confidence_version(
        self,
        semantic_claim_version_id: str,
        *,
        evidence_sufficiency: str,
        provenance_independence: str,
        authority_proximity: str,
        contradiction_resolution: str,
        temporal_freshness: str,
        extraction_certainty: str,
        translation_certainty: str,
        claim_specific_certainty: str,
        coverage_limitation: str,
        assessment_method: str,
        assessment_version: str,
        note: str | None = None,
        created_at: datetime,
    ) -> SemanticFactualConfidenceVersion:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        levels = {
            name: _enum(value, name, CONFIDENCE_LEVELS)
            for name, value in {
                "evidence_sufficiency": evidence_sufficiency,
                "provenance_independence": provenance_independence,
                "authority_proximity": authority_proximity,
                "contradiction_resolution": contradiction_resolution,
                "temporal_freshness": temporal_freshness,
                "extraction_certainty": extraction_certainty,
                "translation_certainty": translation_certainty,
                "claim_specific_certainty": claim_specific_certainty,
            }.items()
        }
        coverage = _enum(coverage_limitation, "coverage_limitation", COVERAGE_LIMITATIONS)
        method = _required(assessment_method, "assessment_method")
        method_version = _required(assessment_version, "assessment_version")
        normalized_note = _optional(note)
        timestamp = _normalize_time(created_at)
        confidence_id = _confidence_identity(claim_id)
        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id=?",
                (claim_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")
            previous = connection.execute(
                "SELECT factual_confidence_version_id,confidence_version FROM semantic_factual_confidence_versions WHERE factual_confidence_id=? ORDER BY confidence_version DESC LIMIT 1",
                (confidence_id,),
            ).fetchone()
            version = 1 if previous is None else int(previous[1]) + 1
            supersedes = None if previous is None else previous[0]
            version_id = _stable_version_id("semantic-factual-confidence-version", confidence_id, version)
            connection.execute(
                """INSERT INTO semantic_factual_confidence_versions(
                    factual_confidence_version_id,factual_confidence_id,confidence_version,
                    semantic_claim_version_id,evidence_sufficiency,provenance_independence,
                    authority_proximity,contradiction_resolution,temporal_freshness,
                    extraction_certainty,translation_certainty,claim_specific_certainty,
                    coverage_limitation,assessment_method,assessment_version,note,
                    supersedes_confidence_version_id,created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    version_id, confidence_id, version, claim_id,
                    levels["evidence_sufficiency"], levels["provenance_independence"],
                    levels["authority_proximity"], levels["contradiction_resolution"],
                    levels["temporal_freshness"], levels["extraction_certainty"],
                    levels["translation_certainty"], levels["claim_specific_certainty"],
                    coverage, method, method_version, normalized_note, supersedes,
                    timestamp.isoformat(),
                ),
            )
        return SemanticFactualConfidenceVersion(
            version_id, confidence_id, version, claim_id,
            levels["evidence_sufficiency"], levels["provenance_independence"],
            levels["authority_proximity"], levels["contradiction_resolution"],
            levels["temporal_freshness"], levels["extraction_certainty"],
            levels["translation_certainty"], levels["claim_specific_certainty"],
            coverage, method, method_version, normalized_note, supersedes, timestamp,
        )

    def confidence_current(self, semantic_claim_version_id: str) -> SemanticFactualConfidenceVersion | None:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        confidence_id = _confidence_identity(claim_id)
        with runtime_database_connection(self.database_path) as connection:
            row = connection.execute(
                """SELECT factual_confidence_version_id,factual_confidence_id,confidence_version,
                          semantic_claim_version_id,evidence_sufficiency,provenance_independence,
                          authority_proximity,contradiction_resolution,temporal_freshness,
                          extraction_certainty,translation_certainty,claim_specific_certainty,
                          coverage_limitation,assessment_method,assessment_version,note,
                          supersedes_confidence_version_id,created_at
                   FROM semantic_factual_confidence_versions
                   WHERE factual_confidence_id=? ORDER BY confidence_version DESC LIMIT 1""",
                (confidence_id,),
            ).fetchone()
        return None if row is None else self._confidence_from_row(row)

    def confidence_history(self, semantic_claim_version_id: str) -> tuple[SemanticFactualConfidenceVersion, ...]:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        confidence_id = _confidence_identity(claim_id)
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT factual_confidence_version_id,factual_confidence_id,confidence_version,
                          semantic_claim_version_id,evidence_sufficiency,provenance_independence,
                          authority_proximity,contradiction_resolution,temporal_freshness,
                          extraction_certainty,translation_certainty,claim_specific_certainty,
                          coverage_limitation,assessment_method,assessment_version,note,
                          supersedes_confidence_version_id,created_at
                   FROM semantic_factual_confidence_versions
                   WHERE factual_confidence_id=? ORDER BY confidence_version""",
                (confidence_id,),
            ).fetchall()
        return tuple(self._confidence_from_row(row) for row in rows)

    def record_decision(
        self,
        semantic_claim_version_id: str,
        *,
        policy_id: str,
        verification_state: str,
        decision_code: str,
        rationale: str,
        created_at: datetime,
    ) -> SemanticVerificationDecisionVersion:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        policy_identity = _required(policy_id, "policy_id")
        state = _enum(verification_state, "verification_state", VERIFICATION_STATES)
        code = _enum(decision_code, "decision_code", DECISION_CODES)
        normalized_rationale = _required(rationale, "rationale")
        timestamp = _normalize_time(created_at)
        decision_id = _decision_identity(claim_id)

        with runtime_database_connection(self.database_path) as connection:
            if connection.execute(
                "SELECT 1 FROM semantic_claim_versions WHERE semantic_claim_version_id=?",
                (claim_id,),
            ).fetchone() is None:
                raise ValueError("semantic claim version does not exist")
            policy_row = connection.execute(
                """SELECT policy_version_id,policy_id,policy_version,policy_name,rules_json,
                          review_status,supersedes_policy_version_id,created_at
                   FROM semantic_verification_policy_versions
                   WHERE policy_id=? ORDER BY policy_version DESC LIMIT 1""",
                (policy_identity,),
            ).fetchone()
            if policy_row is None:
                raise ValueError("verification policy does not exist")
            policy = self._policy_from_row(policy_row)
            if policy.review_status != "APPROVED":
                raise ValueError("current verification policy is not approved")
            confidence_row = connection.execute(
                """SELECT factual_confidence_version_id,factual_confidence_id,confidence_version,
                          semantic_claim_version_id,evidence_sufficiency,provenance_independence,
                          authority_proximity,contradiction_resolution,temporal_freshness,
                          extraction_certainty,translation_certainty,claim_specific_certainty,
                          coverage_limitation,assessment_method,assessment_version,note,
                          supersedes_confidence_version_id,created_at
                   FROM semantic_factual_confidence_versions
                   WHERE factual_confidence_id=? ORDER BY confidence_version DESC LIMIT 1""",
                (_confidence_identity(claim_id),),
            ).fetchone()
            if confidence_row is None:
                raise ValueError("current factual confidence profile does not exist")
            confidence = self._confidence_from_row(confidence_row)

            evidence = self._current_evidence_snapshot(connection, claim_id)
            independence = self._current_independence_snapshot(connection, claim_id)
            contradictions = self._current_contradiction_snapshot(connection, claim_id)
            self._validate_requested_state(
                state,
                policy.rules,
                confidence,
                evidence,
                independence,
                contradictions,
            )

            previous = connection.execute(
                """SELECT verification_decision_version_id,decision_version,verification_state
                   FROM semantic_verification_decision_versions
                   WHERE verification_decision_id=? ORDER BY decision_version DESC LIMIT 1""",
                (decision_id,),
            ).fetchone()
            expected_code = self._expected_decision_code(None if previous is None else previous[2], state)
            if code != expected_code:
                raise ValueError(f"decision_code must be {expected_code} for this transition")
            version = 1 if previous is None else int(previous[1]) + 1
            supersedes = None if previous is None else previous[0]
            version_id = _stable_version_id("semantic-verification-decision-version", decision_id, version)
            evidence_json = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
            independence_json = json.dumps(independence, sort_keys=True, ensure_ascii=False)
            contradiction_json = json.dumps(contradictions, sort_keys=True, ensure_ascii=False)
            connection.execute(
                """INSERT INTO semantic_verification_decision_versions(
                    verification_decision_version_id,verification_decision_id,decision_version,
                    semantic_claim_version_id,policy_version_id,factual_confidence_version_id,
                    verification_state,decision_code,evidence_snapshot_json,
                    independence_snapshot_json,contradiction_snapshot_json,rationale,
                    supersedes_decision_version_id,created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    version_id, decision_id, version, claim_id, policy.policy_version_id,
                    confidence.factual_confidence_version_id, state, code, evidence_json,
                    independence_json, contradiction_json, normalized_rationale, supersedes,
                    timestamp.isoformat(),
                ),
            )

        return SemanticVerificationDecisionVersion(
            version_id, decision_id, version, claim_id, policy.policy_version_id,
            confidence.factual_confidence_version_id, state, code,
            tuple(evidence), tuple(independence), tuple(contradictions),
            normalized_rationale, supersedes, timestamp,
        )

    def decision_current(self, semantic_claim_version_id: str) -> SemanticVerificationDecisionVersion | None:
        history = self.decision_history(semantic_claim_version_id)
        return history[-1] if history else None

    def decision_history(self, semantic_claim_version_id: str) -> tuple[SemanticVerificationDecisionVersion, ...]:
        claim_id = _required(semantic_claim_version_id, "semantic_claim_version_id")
        decision_id = _decision_identity(claim_id)
        with runtime_database_connection(self.database_path) as connection:
            rows = connection.execute(
                """SELECT verification_decision_version_id,verification_decision_id,decision_version,
                          semantic_claim_version_id,policy_version_id,factual_confidence_version_id,
                          verification_state,decision_code,evidence_snapshot_json,
                          independence_snapshot_json,contradiction_snapshot_json,rationale,
                          supersedes_decision_version_id,created_at
                   FROM semantic_verification_decision_versions
                   WHERE verification_decision_id=? ORDER BY decision_version""",
                (decision_id,),
            ).fetchall()
        return tuple(self._decision_from_row(row) for row in rows)

    @staticmethod
    def _validate_requested_state(
        state: str,
        rules: Mapping[str, object],
        confidence: SemanticFactualConfidenceVersion,
        evidence: list[dict[str, object]],
        independence: list[dict[str, object]],
        contradictions: list[dict[str, object]],
    ) -> None:
        support_ids = {
            str(item["evidence_relation_version_id"])
            for item in evidence
            if item["relation_type"] == "SUPPORTS"
        }
        has_contradicting_evidence = any(item["relation_type"] == "CONTRADICTS" for item in evidence)
        has_active_contradiction = any(item["lifecycle_state"] != "RESOLVED" for item in contradictions)
        explicit_independent_support_pair = any(
            item["independence_state"] == "INDEPENDENT"
            and str(item["subject_evidence_relation_version_id"]) in support_ids
            and str(item["comparison_evidence_relation_version_id"]) in support_ids
            for item in independence
        )

        if state == "VERIFIED":
            if rules["verified_requires_explicit_independent_support_pair"] and not explicit_independent_support_pair:
                raise ValueError("VERIFIED requires an explicit current independent supporting evidence pair")
            if rules["verified_blocks_current_contradicting_evidence"] and has_contradicting_evidence:
                raise ValueError("VERIFIED is blocked by current contradicting evidence")
            if rules["verified_blocks_unresolved_contradiction"] and has_active_contradiction:
                raise ValueError("VERIFIED is blocked by an unresolved current contradiction")
            SemanticVerificationService._require_confidence_minimums(
                confidence, rules["verified_minimum_confidence"], "VERIFIED"
            )
        elif state == "PARTLY_VERIFIED":
            if not support_ids:
                raise ValueError("PARTLY_VERIFIED requires current supporting semantic evidence")
            if has_contradicting_evidence or has_active_contradiction:
                raise ValueError("PARTLY_VERIFIED is blocked by current disputed semantic state")
            SemanticVerificationService._require_confidence_minimums(
                confidence, rules["partly_verified_minimum_confidence"], "PARTLY_VERIFIED"
            )
        elif state == "DISPUTED":
            if not has_contradicting_evidence and not has_active_contradiction:
                raise ValueError("DISPUTED requires current contradicting evidence or an active contradiction")
        elif state == "UNVERIFIABLE":
            if confidence.coverage_limitation != "LIMITED":
                raise ValueError("UNVERIFIABLE requires an explicit LIMITED coverage limitation")
            if _LEVEL_RANK[confidence.claim_specific_certainty] > _LEVEL_RANK["LOW"]:
                raise ValueError("UNVERIFIABLE requires LOW or UNKNOWN claim-specific certainty")
        # DETECTED deliberately has no promotion preconditions.

    @staticmethod
    def _require_confidence_minimums(
        confidence: SemanticFactualConfidenceVersion,
        minimums: object,
        target_state: str,
    ) -> None:
        if not isinstance(minimums, Mapping):
            raise ValueError("verification policy confidence minimums are invalid")
        for dimension, minimum in minimums.items():
            actual = getattr(confidence, str(dimension))
            required = _enum(minimum, str(dimension), CONFIDENCE_LEVELS)
            if _LEVEL_RANK[actual] < _LEVEL_RANK[required]:
                raise ValueError(
                    f"{target_state} requires {dimension} >= {required}; current is {actual}"
                )

    @staticmethod
    def _expected_decision_code(previous_state: str | None, state: str) -> str:
        if previous_state is None:
            return "INITIAL"
        if state == "DISPUTED":
            return "DISPUTE"
        if state == "UNVERIFIABLE":
            return "MARK_UNVERIFIABLE"
        if previous_state == state:
            return "HOLD"
        previous_rank = _STATE_RANK.get(previous_state, 0)
        current_rank = _STATE_RANK.get(state, 0)
        if current_rank > previous_rank:
            return "PROMOTE"
        if current_rank < previous_rank:
            return "DEMOTE"
        return "HOLD"

    @staticmethod
    def _current_evidence_snapshot(connection, claim_id: str) -> list[dict[str, object]]:
        rows = connection.execute(
            """SELECT r.evidence_relation_version_id,r.evidence_relation_id,r.relation_type,
                      r.evidence_provenance_entity_version_id,r.raw_item_id
               FROM semantic_evidence_relation_versions r
               JOIN (
                   SELECT evidence_relation_id,MAX(relation_version) AS latest_version
                   FROM semantic_evidence_relation_versions GROUP BY evidence_relation_id
               ) latest ON latest.evidence_relation_id=r.evidence_relation_id
                       AND latest.latest_version=r.relation_version
               WHERE r.semantic_claim_version_id=? ORDER BY r.evidence_relation_id""",
            (claim_id,),
        ).fetchall()
        return [
            {
                "evidence_relation_version_id": row[0],
                "evidence_relation_id": row[1],
                "relation_type": row[2],
                "evidence_provenance_entity_version_id": row[3],
                "raw_item_id": row[4],
            }
            for row in rows
        ]

    @staticmethod
    def _current_independence_snapshot(connection, claim_id: str) -> list[dict[str, object]]:
        rows = connection.execute(
            """SELECT a.independence_assessment_version_id,a.independence_assessment_id,
                      a.subject_evidence_relation_version_id,a.comparison_evidence_relation_version_id,
                      a.independence_state,a.rationale_code
               FROM semantic_independence_assessment_versions a
               JOIN (
                   SELECT independence_assessment_id,MAX(assessment_version_number) AS latest_version
                   FROM semantic_independence_assessment_versions GROUP BY independence_assessment_id
               ) latest ON latest.independence_assessment_id=a.independence_assessment_id
                       AND latest.latest_version=a.assessment_version_number
               WHERE a.semantic_claim_version_id=? ORDER BY a.independence_assessment_id""",
            (claim_id,),
        ).fetchall()
        return [
            {
                "independence_assessment_version_id": row[0],
                "independence_assessment_id": row[1],
                "subject_evidence_relation_version_id": row[2],
                "comparison_evidence_relation_version_id": row[3],
                "independence_state": row[4],
                "rationale_code": row[5],
            }
            for row in rows
        ]

    @staticmethod
    def _current_contradiction_snapshot(connection, claim_id: str) -> list[dict[str, object]]:
        rows = connection.execute(
            """SELECT c.contradiction_version_id,c.contradiction_id,c.contradiction_dimension,
                      c.lifecycle_state,c.reconciliation_code,
                      c.left_semantic_claim_version_id,c.right_semantic_claim_version_id
               FROM semantic_contradiction_versions c
               JOIN (
                   SELECT contradiction_id,MAX(contradiction_version) AS latest_version
                   FROM semantic_contradiction_versions GROUP BY contradiction_id
               ) latest ON latest.contradiction_id=c.contradiction_id
                       AND latest.latest_version=c.contradiction_version
               WHERE c.left_semantic_claim_version_id=? OR c.right_semantic_claim_version_id=?
               ORDER BY c.contradiction_id""",
            (claim_id, claim_id),
        ).fetchall()
        return [
            {
                "contradiction_version_id": row[0],
                "contradiction_id": row[1],
                "contradiction_dimension": row[2],
                "lifecycle_state": row[3],
                "reconciliation_code": row[4],
                "left_semantic_claim_version_id": row[5],
                "right_semantic_claim_version_id": row[6],
            }
            for row in rows
        ]

    @staticmethod
    def _policy_from_row(row) -> SemanticVerificationPolicyVersion:
        return SemanticVerificationPolicyVersion(
            row[0], row[1], int(row[2]), row[3], json.loads(row[4]), row[5], row[6],
            datetime.fromisoformat(row[7]),
        )

    @staticmethod
    def _confidence_from_row(row) -> SemanticFactualConfidenceVersion:
        return SemanticFactualConfidenceVersion(
            row[0], row[1], int(row[2]), row[3], row[4], row[5], row[6], row[7],
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
            row[16], datetime.fromisoformat(row[17]),
        )

    @staticmethod
    def _decision_from_row(row) -> SemanticVerificationDecisionVersion:
        return SemanticVerificationDecisionVersion(
            row[0], row[1], int(row[2]), row[3], row[4], row[5], row[6], row[7],
            tuple(json.loads(row[8])), tuple(json.loads(row[9])), tuple(json.loads(row[10])),
            row[11], row[12], datetime.fromisoformat(row[13]),
        )
