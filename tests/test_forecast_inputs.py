from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.advanced_forecasting import (
    ForecastRecord,
    ScenarioVersion,
    SQLiteAdvancedForecastRepository,
    forecast_version_id,
)
from kgeopolitical_monitor.forecast_inputs import (
    ANALYST_ASSUMPTION,
    CANONICAL_EVENT,
    GRAPH_RELATIONSHIP,
    OPERATIONAL_FINDING,
    SOURCE_EVIDENCE,
    ForecastInputRef,
    SQLiteForecastInputRepository,
    create_forecast_version_with_inputs,
    provenance_tokens,
)
from kgeopolitical_monitor.forecast_preparation import ForecastHorizon
from kgeopolitical_monitor.probabilistic_forecasting import ScenarioType


NOW = datetime(2026, 8, 26, 16, 30, tzinfo=timezone.utc)
DEADLINE = NOW + timedelta(days=30)
CONSTRAINTS = ("No external forecasting provider", "Negotiations remain active")


def _forecast():
    return ForecastRecord.create(
        "ua-security-inputs-30d",
        "Will a material Ukraine security agreement be announced within 30 days?",
        ForecastHorizon.SHORT,
        DEADLINE,
        created_at=NOW,
    )


def _seed_canonical_refs(db):
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO sources(id, name, source_class, reliability) VALUES (?, ?, ?, ?)",
            ("source-1", "Official Source", "Official sources", "official"),
        )
        connection.execute(
            "INSERT INTO raw_items(id, source_id, title, content, collected_at) VALUES (?, ?, ?, ?, ?)",
            ("raw-1", "source-1", "Security update", "content", NOW.isoformat()),
        )
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-1", "Security negotiations", "ACTIVE", "0.8"),
        )
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-2", "Alternative event", "ACTIVE", "0.5"),
        )
        connection.execute(
            """
            INSERT INTO operational_findings(
                finding_id, run_id, watch_id, title, summary, importance,
                confidence, evidence_refs, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "finding-1",
                "run-1",
                "watch-1",
                "Negotiation finding",
                "Negotiations continue",
                0.8,
                0.7,
                '["raw-1"]',
                "Observed negotiation activity",
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO graph_edges(
                edge_id, source_node_id, target_node_id, relation_type,
                relation_class, confidence, status, valid_from, valid_to,
                first_observed_at, last_observed_at, explanation,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "edge-1",
                "node-a",
                "node-b",
                "INFLUENCES",
                "INFLUENCE",
                0.75,
                "ACTIVE",
                NOW.isoformat(),
                None,
                NOW.isoformat(),
                NOW.isoformat(),
                "Graph-layer influence relation",
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title,
                verification_status, confidence, importance,
                independent_origin_count, source_class_count, origins_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "claim-1",
                "analysis-1",
                "security-negotiations",
                "Security negotiations",
                "PARTLY_VERIFIED",
                0.67,
                0.8,
                2,
                2,
                '["official.example", "media.example"]',
            ),
        )


def _inputs(version_id):
    return (
        ForecastInputRef.durable(
            version_id,
            SOURCE_EVIDENCE,
            "raw-1",
            metadata={"role": "supporting source observation"},
            created_at=NOW,
        ),
        ForecastInputRef.durable(
            version_id,
            CANONICAL_EVENT,
            "event-1",
            created_at=NOW,
        ),
        ForecastInputRef.durable(
            version_id,
            GRAPH_RELATIONSHIP,
            "edge-1",
            metadata={"role": "analytical graph input", "independent_evidence": False},
            created_at=NOW,
        ),
        ForecastInputRef.durable(
            version_id,
            OPERATIONAL_FINDING,
            "finding-1",
            created_at=NOW,
        ),
        ForecastInputRef.assumption(
            version_id,
            "Negotiations continue through the evaluation window",
            metadata={"owner": "analyst"},
            created_at=NOW,
        ),
    )


def _scenarios(version_id):
    return (
        ScenarioVersion.create(
            version_id,
            ScenarioType.BASELINE,
            "Agreement announced",
            0.65,
            0.60,
            0.70,
        ),
        ScenarioVersion.create(
            version_id,
            ScenarioType.NEGATIVE,
            "No agreement announced",
            0.35,
            0.40,
            0.65,
        ),
    )


def _persist_version(db):
    forecast_repo = SQLiteAdvancedForecastRepository(db)
    _seed_canonical_refs(db)
    forecast = _forecast()
    forecast_repo.save_forecast(forecast)
    version_id = forecast_version_id(forecast.forecast_id, 1)
    inputs = _inputs(version_id)
    version = create_forecast_version_with_inputs(
        forecast.forecast_id,
        1,
        inputs=inputs,
        constraints=CONSTRAINTS,
        change_reason="Initial provenance-bound forecast",
        created_at=NOW,
    )
    forecast_repo.save_version(version, _scenarios(version.forecast_version_id))
    return forecast_repo, forecast, version, inputs


def test_typed_forecast_inputs_are_durable_restart_safe_and_idempotent(tmp_path):
    db = tmp_path / "project.db"
    _, _, version, inputs = _persist_version(db)
    input_repo = SQLiteForecastInputRepository(db)

    first = input_repo.bind(version, inputs, constraints=CONSTRAINTS)
    second = input_repo.bind(version, reversed(inputs), constraints=reversed(CONSTRAINTS))

    restarted = SQLiteForecastInputRepository(db)
    loaded = restarted.list_inputs(version.forecast_version_id)
    expected = tuple(
        sorted(
            inputs,
            key=lambda item: (
                item.input_kind,
                item.reference_id or item.statement or "",
                item.input_id,
            ),
        )
    )

    assert first == expected
    assert second == expected
    assert loaded == expected
    assert version.input_snapshot["constraints"] == sorted(CONSTRAINTS)
    assert version.provenance_refs == provenance_tokens(inputs)
    assert version.assumptions == (
        "Negotiations continue through the evaluation window",
    )


@pytest.mark.parametrize(
    ("input_kind", "missing_reference"),
    [
        (SOURCE_EVIDENCE, "raw-missing"),
        (CANONICAL_EVENT, "event-missing"),
        (GRAPH_RELATIONSHIP, "edge-missing"),
        (OPERATIONAL_FINDING, "finding-missing"),
    ],
)
def test_unknown_durable_forecast_references_fail_closed(tmp_path, input_kind, missing_reference):
    db = tmp_path / "project.db"
    forecast_repo = SQLiteAdvancedForecastRepository(db)
    _seed_canonical_refs(db)
    forecast = _forecast()
    forecast_repo.save_forecast(forecast)
    version_id = forecast_version_id(forecast.forecast_id, 1)
    inputs = (
        ForecastInputRef.durable(version_id, input_kind, missing_reference, created_at=NOW),
        ForecastInputRef.assumption(version_id, "Explicit analyst assumption", created_at=NOW),
    )
    version = create_forecast_version_with_inputs(
        forecast.forecast_id,
        1,
        inputs=inputs,
        constraints=("Explicit constraint",),
        change_reason="Unknown reference test",
        created_at=NOW,
    )
    forecast_repo.save_version(version, _scenarios(version.forecast_version_id))

    with pytest.raises(ValueError, match="unknown canonical reference"):
        SQLiteForecastInputRepository(db).bind(
            version,
            inputs,
            constraints=("Explicit constraint",),
        )

    assert SQLiteForecastInputRepository(db).list_inputs(version.forecast_version_id) == ()


def test_analyst_assumption_is_explicit_and_does_not_require_upstream_reference(tmp_path):
    db = tmp_path / "project.db"
    forecast_repo = SQLiteAdvancedForecastRepository(db)
    forecast = _forecast()
    forecast_repo.save_forecast(forecast)
    version_id = forecast_version_id(forecast.forecast_id, 1)
    assumption = ForecastInputRef.assumption(
        version_id,
        "Private negotiations continue",
        created_at=NOW,
    )
    version = create_forecast_version_with_inputs(
        forecast.forecast_id,
        1,
        inputs=(assumption,),
        constraints=("Assumption is not evidence",),
        change_reason="Assumption-only analytical baseline",
        created_at=NOW,
    )
    forecast_repo.save_version(version, _scenarios(version.forecast_version_id))

    bound = SQLiteForecastInputRepository(db).bind(
        version,
        (assumption,),
        constraints=("Assumption is not evidence",),
    )

    assert bound == (assumption,)
    assert bound[0].input_kind == ANALYST_ASSUMPTION
    assert bound[0].reference_id is None


def test_immutable_snapshot_rejects_changed_typed_input_set(tmp_path):
    db = tmp_path / "project.db"
    _, _, version, inputs = _persist_version(db)
    input_repo = SQLiteForecastInputRepository(db)
    input_repo.bind(version, inputs, constraints=CONSTRAINTS)

    changed = tuple(
        ForecastInputRef.durable(
            version.forecast_version_id,
            CANONICAL_EVENT,
            "event-2",
            created_at=NOW,
        )
        if item.input_kind == CANONICAL_EVENT
        else item
        for item in inputs
    )

    with pytest.raises(ValueError, match="immutable input_snapshot"):
        input_repo.bind(version, changed, constraints=CONSTRAINTS)

    assert len(input_repo.list_inputs(version.forecast_version_id)) == len(inputs)


def test_forecast_input_binding_does_not_mutate_m8_or_m11_truth(tmp_path):
    db = tmp_path / "project.db"
    _, _, version, inputs = _persist_version(db)

    with sqlite3.connect(db) as connection:
        claim_before = connection.execute(
            """
            SELECT verification_status, confidence, independent_origin_count, origins_json
            FROM live_analysis_claims WHERE claim_id = 'claim-1'
            """
        ).fetchone()
        edge_before = connection.execute(
            """
            SELECT relation_type, relation_class, confidence, status, explanation
            FROM graph_edges WHERE edge_id = 'edge-1'
            """
        ).fetchone()

    SQLiteForecastInputRepository(db).bind(version, inputs, constraints=CONSTRAINTS)

    with sqlite3.connect(db) as connection:
        claim_after = connection.execute(
            """
            SELECT verification_status, confidence, independent_origin_count, origins_json
            FROM live_analysis_claims WHERE claim_id = 'claim-1'
            """
        ).fetchone()
        edge_after = connection.execute(
            """
            SELECT relation_type, relation_class, confidence, status, explanation
            FROM graph_edges WHERE edge_id = 'edge-1'
            """
        ).fetchone()

    assert claim_after == claim_before
    assert edge_after == edge_before
