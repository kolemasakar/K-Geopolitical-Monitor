from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.forecast_calibration_contract import (
    OUTCOME_AMBIGUOUS,
    OUTCOME_PARTIAL,
    OUTCOME_RESOLVED,
    OUTCOME_UNRESOLVED,
)
from kgeopolitical_monitor.forecast_outcome_persistence import OutcomeEvidenceReference
from kgeopolitical_monitor.forecast_outcome_resolution import (
    OutcomeResolutionError,
    P15_2_GATE,
    ProvenanceBoundOutcomeResolver,
)


NOW = datetime(2026, 9, 4, 18, 0, tzinfo=timezone.utc)


def _seed_forecast(db_path, forecast_id="forecast-p15-2"):
    initialize_database(str(db_path))
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecasts(
                   forecast_id, target_key, question, horizon, evaluation_deadline,
                   status, created_at, updated_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                forecast_id,
                f"target-{forecast_id}",
                "Will the target event occur?",
                "short_term",
                "2026-09-10T00:00:00+00:00",
                "ACTIVE",
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )


def _seed_raw_item(db_path, raw_item_id="raw-p15-2"):
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO raw_items(id, title, content, collected_at) VALUES (?, ?, ?, ?)",
            (raw_item_id, "Outcome evidence", "Persisted evidence body", NOW.isoformat()),
        )


def _seed_legacy_outcome(db_path, state, outcome_id=None, forecast_id="forecast-p15-2"):
    outcome_id = outcome_id or f"legacy-{state.lower()}"
    observed_type = "baseline" if state == "OBSERVED" else None
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """INSERT INTO forecast_outcomes(
                   outcome_id, forecast_id, resolved_at, outcome_state,
                   observed_scenario_type, evidence_refs_json, explanation, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                outcome_id,
                forecast_id,
                NOW.isoformat(),
                state,
                observed_type,
                "[]",
                f"Legacy {state} result",
                NOW.isoformat(),
            ),
        )
    return outcome_id


def test_p15_2_gate_name():
    assert P15_2_GATE == "P15_2_PROVENANCE_BOUND_OUTCOME_RESOLUTION_VALIDATED"


def test_no_legacy_outcome_fails_closed_to_unresolved(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    assessment = resolver.resolve(
        "forecast-p15-2",
        assessed_at=NOW,
        explanation="No final forecast result is available.",
    )
    assert assessment.resolution_state == OUTCOME_UNRESOLVED


def test_missing_persisted_evidence_reference_is_rejected(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    outcome_id = _seed_legacy_outcome(db_path, "OBSERVED")
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    with pytest.raises(OutcomeResolutionError, match="does not exist"):
        resolver.resolve(
            "forecast-p15-2",
            assessed_at=NOW,
            explanation="Missing evidence must fail closed.",
            legacy_outcome_id=outcome_id,
            evidence=(OutcomeEvidenceReference("RAW_ITEM", "missing-raw-item"),),
        )


def test_external_reference_alone_cannot_resolve_outcome(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    outcome_id = _seed_legacy_outcome(db_path, "NOT_OBSERVED")
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    with pytest.raises(OutcomeResolutionError, match="persisted outcome-evidence"):
        resolver.resolve(
            "forecast-p15-2",
            assessed_at=NOW,
            explanation="External-only context is insufficient for canonical resolution.",
            legacy_outcome_id=outcome_id,
            evidence=(OutcomeEvidenceReference("EXTERNAL_REFERENCE", "https://example.invalid/outcome"),),
        )


def test_persisted_raw_outcome_evidence_can_support_resolved_state(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    _seed_raw_item(db_path)
    outcome_id = _seed_legacy_outcome(db_path, "OBSERVED")
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    assessment = resolver.resolve(
        "forecast-p15-2",
        assessed_at=NOW,
        explanation="Persisted outcome evidence is traceable.",
        legacy_outcome_id=outcome_id,
        evidence=(OutcomeEvidenceReference("RAW_ITEM", "raw-p15-2", "OUTCOME_EVIDENCE"),),
    )
    assert assessment.resolution_state == OUTCOME_RESOLVED
    assert assessment.legacy_outcome_id == outcome_id


@pytest.mark.parametrize(
    ("legacy_state", "expected_resolution"),
    [("PARTIAL", OUTCOME_PARTIAL), ("AMBIGUOUS", OUTCOME_AMBIGUOUS)],
)
def test_partial_and_ambiguous_legacy_results_remain_unscoreable_resolution_states(
    tmp_path, legacy_state, expected_resolution
):
    db_path = tmp_path / f"{legacy_state.lower()}.db"
    _seed_forecast(db_path)
    outcome_id = _seed_legacy_outcome(db_path, legacy_state)
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    assessment = resolver.resolve(
        "forecast-p15-2",
        assessed_at=NOW,
        explanation=f"Legacy {legacy_state} stays non-binary.",
        legacy_outcome_id=outcome_id,
    )
    assert assessment.resolution_state == expected_resolution


def test_resolution_sequence_is_append_only_and_monotonic(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    first = resolver.resolve(
        "forecast-p15-2", assessed_at=NOW, explanation="Initial unresolved assessment."
    )
    second = resolver.resolve(
        "forecast-p15-2", assessed_at=NOW, explanation="Second unresolved assessment."
    )
    assert (first.assessment_sequence, second.assessment_sequence) == (1, 2)


def test_resolution_does_not_write_semantic_verification_state(tmp_path):
    db_path = tmp_path / "kgm.db"
    _seed_forecast(db_path)
    resolver = ProvenanceBoundOutcomeResolver(db_path)
    with sqlite3.connect(db_path) as connection:
        before = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    resolver.resolve(
        "forecast-p15-2", assessed_at=NOW, explanation="Outcome lifecycle only."
    )
    with sqlite3.connect(db_path) as connection:
        after = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
    assert after == before
