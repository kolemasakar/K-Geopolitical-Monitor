import json
import sqlite3
from datetime import datetime, timezone

import pytest

from kgeopolitical_monitor.advanced_graph import SQLiteAdvancedGraphRepository
from kgeopolitical_monitor.graph_projection import (
    CanonicalActorReference,
    project_actor_references,
    project_canonical_events,
    project_live_analysis_claim_references,
    project_operational_finding_references,
)


NOW = datetime(2026, 8, 26, 13, 30, tzinfo=timezone.utc)


def test_actor_projection_is_idempotent_and_survives_restart(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    actors = (
        CanonicalActorReference("ua", "Ukraine", "country", {"region": "Europe"}),
        CanonicalActorReference("person-1", "Explicit Person", "person", {"role": "official"}),
    )

    first = project_actor_references(actors, repo, observed_at=NOW)
    second = project_actor_references(actors, repo, observed_at=NOW)

    assert [node.node_id for node in first] == [node.node_id for node in second]
    assert {node.attributes["actor_type"] for node in first} == {"COUNTRY", "PERSON"}

    restarted = SQLiteAdvancedGraphRepository(db)
    ukraine = restarted.get_node_by_canonical("ACTOR", "ua")
    person = restarted.get_node_by_canonical("ACTOR", "person-1")
    assert ukraine is not None
    assert ukraine.label == "Ukraine"
    assert ukraine.attributes == {"actor_type": "COUNTRY", "region": "Europe"}
    assert person is not None
    assert person.attributes["actor_type"] == "PERSON"

    with sqlite3.connect(db) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE canonical_ref_type = 'ACTOR'"
        ).fetchone()[0] == 2


def test_conflicting_actor_references_are_rejected(tmp_path):
    repo = SQLiteAdvancedGraphRepository(tmp_path / "project.db")
    actors = (
        CanonicalActorReference("same", "Actor A", "ORGANIZATION"),
        CanonicalActorReference("same", "Actor B", "ORGANIZATION"),
    )

    with pytest.raises(ValueError, match="conflicting canonical actor reference"):
        project_actor_references(actors, repo, observed_at=NOW)


def test_canonical_event_projection_updates_same_graph_node_without_mutating_truth(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    with sqlite3.connect(db) as connection:
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-1", "Initial title", "DETECTED", "MEDIUM"),
        )
        connection.execute(
            "INSERT INTO events(id, title, status, importance) VALUES (?, ?, ?, ?)",
            ("event-2", "Other event", "DETECTED", "LOW"),
        )

    first = project_canonical_events(db, repo, observed_at=NOW, event_ids=("event-1",))
    assert len(first) == 1
    assert first[0].canonical_ref_type == "EVENT"
    assert first[0].canonical_ref_id == "event-1"
    assert repo.get_node_by_canonical("EVENT", "event-2") is None

    with sqlite3.connect(db) as connection:
        connection.execute(
            "UPDATE events SET title = ?, status = ?, importance = ? WHERE id = ?",
            ("Updated title", "CONFIRMED", "HIGH", "event-1"),
        )

    second = project_canonical_events(db, repo, observed_at=NOW, event_ids=("event-1",))
    assert second[0].node_id == first[0].node_id
    loaded = repo.get_node_by_canonical("EVENT", "event-1")
    assert loaded is not None
    assert loaded.label == "Updated title"
    assert loaded.attributes == {"importance": "HIGH", "status": "CONFIRMED"}

    with sqlite3.connect(db) as connection:
        canonical = connection.execute(
            "SELECT title, status, importance FROM events WHERE id = 'event-1'"
        ).fetchone()
        graph_count = connection.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE canonical_ref_type = 'EVENT'"
        ).fetchone()[0]
    assert canonical == ("Updated title", "CONFIRMED", "HIGH")
    assert graph_count == 1


def test_projection_rejects_cross_project_database_path(tmp_path):
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    repo_a = SQLiteAdvancedGraphRepository(db_a)
    SQLiteAdvancedGraphRepository(db_b)

    with pytest.raises(ValueError, match="project-local graph database"):
        project_canonical_events(db_b, repo_a, observed_at=NOW)


def test_live_analysis_claim_projection_is_scoped_to_one_explicit_analysis_run(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    with sqlite3.connect(db) as connection:
        connection.executemany(
            """
            INSERT INTO live_analysis_runs(
                analysis_run_id, collection_id, watch_id, status,
                claim_count, finding_count, created_at
            ) VALUES (?, ?, ?, 'COMPLETED', 1, 0, ?)
            """,
            [
                ("analysis-a", "collection-a", "watch-a", NOW.isoformat()),
                ("analysis-b", "collection-b", "watch-b", NOW.isoformat()),
            ],
        )
        connection.executemany(
            """
            INSERT INTO live_analysis_claims(
                claim_id, analysis_run_id, claim_key, title, verification_status,
                confidence, importance, independent_origin_count,
                source_class_count, origins_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("claim-a", "analysis-a", "key-a", "Claim A", "PARTLY_VERIFIED", 0.7, 0.6, 2, 2, "[]"),
                ("claim-b", "analysis-b", "key-b", "Claim B", "DETECTED", 0.4, 0.5, 1, 1, "[]"),
            ],
        )

    projected = project_live_analysis_claim_references(
        db,
        repo,
        analysis_run_id="analysis-a",
        observed_at=NOW,
    )

    assert [node.canonical_ref_id for node in projected] == ["claim-a"]
    claim_a = repo.get_node_by_canonical("M8_CLAIM", "claim-a")
    claim_b = repo.get_node_by_canonical("M8_CLAIM", "claim-b")
    assert claim_a is not None
    assert claim_a.attributes["watch_id"] == "watch-a"
    assert claim_a.attributes["independent_origin_count"] == 2
    assert claim_b is None


def test_operational_finding_projection_requires_explicit_finding_ids(tmp_path):
    db = tmp_path / "project.db"
    repo = SQLiteAdvancedGraphRepository(db)
    with sqlite3.connect(db) as connection:
        connection.executemany(
            """
            INSERT INTO operational_findings(
                finding_id, run_id, watch_id, title, summary, importance,
                confidence, evidence_refs, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("finding-a", "run-a", "watch-a", "Finding A", "Summary A", 0.8, 0.7, json.dumps(["claim:claim-a"]), "Explanation A", NOW.isoformat()),
                ("finding-b", "run-b", "watch-b", "Finding B", "Summary B", 0.5, 0.4, json.dumps(["claim:claim-b"]), "Explanation B", NOW.isoformat()),
            ],
        )

    projected = project_operational_finding_references(
        db,
        repo,
        finding_ids=("finding-a",),
        observed_at=NOW,
    )

    assert [node.canonical_ref_id for node in projected] == ["finding-a"]
    finding_a = repo.get_node_by_canonical("OPERATIONAL_FINDING", "finding-a")
    finding_b = repo.get_node_by_canonical("OPERATIONAL_FINDING", "finding-b")
    assert finding_a is not None
    assert finding_a.attributes["watch_id"] == "watch-a"
    assert finding_a.attributes["evidence_refs"] == ["claim:claim-a"]
    assert finding_b is None
