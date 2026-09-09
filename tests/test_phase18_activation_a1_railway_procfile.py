from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCFILE = ROOT / "Procfile"


def test_railway_procfile_targets_only_preflight_fastapi_entrypoint():
    text = PROCFILE.read_text(encoding="utf-8").strip()

    assert text == (
        "web: uvicorn "
        "kgeopolitical_monitor.shared_runtime_preflight_app:create_app_from_env "
        "--factory --app-dir src --host 0.0.0.0 --port $PORT"
    )


def test_railway_procfile_preserves_src_layout_without_installing_project_package():
    text = PROCFILE.read_text(encoding="utf-8")

    assert "--app-dir src" in text
    assert "PYTHONPATH=" not in text
    assert "pip install" not in text


def test_railway_procfile_contains_no_secrets_or_canonical_runtime_activation():
    text = PROCFILE.read_text(encoding="utf-8").casefold()

    forbidden = (
        "postgresql://",
        "postgres://",
        "bearer",
        "password",
        "secret",
        "workspace_id",
        "project_id",
        "sqlite",
        "migration_033",
        "shared_runtime_active = yes",
        "production_live",
    )
    assert all(token not in text for token in forbidden)
