"""Phase 23 P23.3 corroboration and evidence-relation observation.

Read-only exact-cohort observer. It reports current typed evidence relations and
current independence assessments without creating evidence, independence,
verification, contradiction, or factual-confidence state.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from .operational_monitoring import OperationalMonitoringRuntime
from .semantic_evidence import EVIDENCE_RELATION_TYPES, INDEPENDENCE_STATES


P23_3_CORROBORATION_OBSERVATION_VERSION = "P23.3-1.0"


@dataclass(frozen=True)
class CorroborationObservation:
    analysis_run_id: str
    claim_count: int
    relation_distribution: dict[str, int]
    independence_distribution: dict[str, int]
    claims_with_support: int
    claims_with_contradiction: int
    claims_with_explicit_independent_support_pair: int

    @property
    def corroborated_claim_count(self) -> int:
        return self.claims_with_explicit_independent_support_pair

    @property
    def changes_verification_state(self) -> bool:
        return False

    @property
    def grants_factual_independence_credit(self) -> bool:
        return False


class CorroborationEvidenceObserver:
    """Observe current P13.3 evidence state for an exact live-analysis cohort.

    A claim is counted as corroborated only when a current INDEPENDENT
    assessment references two current SUPPORTS evidence relation versions.
    Domain/source/host/language counts and ATTRIBUTION_ONLY relations never
    satisfy this condition.
    """

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.database_path = runtime.database_path

    def observe_analysis_run(self, analysis_run_id: str) -> CorroborationObservation:
        run_id = str(analysis_run_id).strip()
        if not run_id:
            raise ValueError("analysis_run_id must not be empty")

        relation_distribution = {name: 0 for name in EVIDENCE_RELATION_TYPES}
        independence_distribution = {name: 0 for name in INDEPENDENCE_STATES}
        claims_with_support = 0
        claims_with_contradiction = 0
        corroborated = 0

        with sqlite3.connect(self.database_path) as connection:
            claim_rows = connection.execute(
                """
                SELECT DISTINCT c.semantic_claim_version_id
                FROM semantic_claim_versions c
                JOIN semantic_claim_links l
                  ON l.semantic_claim_version_id=c.semantic_claim_version_id
                 AND l.target_type='LIVE_ANALYSIS_CLAIM'
                JOIN live_analysis_claims lc
                  ON lc.claim_id=l.target_id
                WHERE lc.analysis_run_id=?
                  AND c.extraction_method='PUBLICATION_ATTRIBUTION_BRIDGE'
                ORDER BY c.semantic_claim_version_id
                """,
                (run_id,),
            ).fetchall()

            for (claim_id,) in claim_rows:
                evidence = connection.execute(
                    """
                    SELECT r.evidence_relation_version_id,r.relation_type
                    FROM semantic_evidence_relation_versions r
                    JOIN (
                        SELECT evidence_relation_id,MAX(relation_version) AS latest_version
                        FROM semantic_evidence_relation_versions
                        GROUP BY evidence_relation_id
                    ) latest
                      ON latest.evidence_relation_id=r.evidence_relation_id
                     AND latest.latest_version=r.relation_version
                    WHERE r.semantic_claim_version_id=?
                    ORDER BY r.evidence_relation_id
                    """,
                    (claim_id,),
                ).fetchall()
                relation_by_version = {}
                for version_id, relation_type in evidence:
                    relation_by_version[str(version_id)] = str(relation_type)
                    relation_distribution.setdefault(str(relation_type), 0)
                    relation_distribution[str(relation_type)] += 1

                support_ids = {
                    version_id
                    for version_id, relation_type in relation_by_version.items()
                    if relation_type == "SUPPORTS"
                }
                if support_ids:
                    claims_with_support += 1
                if any(value == "CONTRADICTS" for value in relation_by_version.values()):
                    claims_with_contradiction += 1

                assessments = connection.execute(
                    """
                    SELECT a.subject_evidence_relation_version_id,
                           a.comparison_evidence_relation_version_id,
                           a.independence_state
                    FROM semantic_independence_assessment_versions a
                    JOIN (
                        SELECT independence_assessment_id,
                               MAX(assessment_version_number) AS latest_version
                        FROM semantic_independence_assessment_versions
                        GROUP BY independence_assessment_id
                    ) latest
                      ON latest.independence_assessment_id=a.independence_assessment_id
                     AND latest.latest_version=a.assessment_version_number
                    WHERE a.semantic_claim_version_id=?
                    ORDER BY a.independence_assessment_id
                    """,
                    (claim_id,),
                ).fetchall()

                explicit_pair = False
                for subject_id, comparison_id, independence_state in assessments:
                    state = str(independence_state)
                    independence_distribution.setdefault(state, 0)
                    independence_distribution[state] += 1
                    if (
                        state == "INDEPENDENT"
                        and str(subject_id) in support_ids
                        and str(comparison_id) in support_ids
                    ):
                        explicit_pair = True
                if explicit_pair:
                    corroborated += 1

        return CorroborationObservation(
            analysis_run_id=run_id,
            claim_count=len(claim_rows),
            relation_distribution=relation_distribution,
            independence_distribution=independence_distribution,
            claims_with_support=claims_with_support,
            claims_with_contradiction=claims_with_contradiction,
            claims_with_explicit_independent_support_pair=corroborated,
        )
