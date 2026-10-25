import importlib.util
from pathlib import Path
import sqlite3
import tempfile

MODULE = Path(__file__).resolve().parents[1] / "ops/o1_diag/kgm-o1-operational-aggregates.py"
spec = importlib.util.spec_from_file_location("kgm_o1_aggregates", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_date_parsing_and_status_map():
    assert module.date_value("2026-10-25T18:00:00Z") == "2026-10-25T18:00:00+00:00"
    assert module.date_value("confidential") is None
    assert module.STATUS_MAP["failed"] == "FAIL"


def test_schema_scoped_aggregates_synthetic_only():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "fixture.sqlite"
        c = sqlite3.connect(db)
        c.execute("create table monitoring_runs (status text, completed_at text, source text)")
        c.executemany("insert into monitoring_runs values (?, ?, ?)", [
            ("success", "2026-10-25T18:00:00Z", "GDACS"),
            ("failed", "2026-10-25T19:00:00Z", "GDELT"),
        ])
        c.commit()
        c.close()
        ro = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True)
        ro.execute("PRAGMA query_only=ON")
        row = module.table_summary(ro, "monitoring_runs")
        assert row["rows"] == 2
        assert row["status_groups"]["SUCCESS"] == 1
        assert row["status_groups"]["FAIL"] == 1
        assert row["specific_source_counts"]["GDACS"]["rows"] == 1
        assert row["specific_source_counts"]["GDELT"]["rows"] == 1
        ro.close()
