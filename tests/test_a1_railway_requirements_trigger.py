from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_railway_requirements_installs_canonical_project() -> None:
    lines = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    assert lines == ["."]


def test_railway_requirements_contains_no_runtime_or_secret_material() -> None:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8").casefold()

    for forbidden in (
        "password",
        "bearer",
        "database_url",
        "postgresql://",
        "railway.internal",
        "render.com",
        "kgm_shared",
        "migration 033",
    ):
        assert forbidden not in text
