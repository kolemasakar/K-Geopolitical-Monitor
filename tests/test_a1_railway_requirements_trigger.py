from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _non_comment_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_railway_requirements_matches_canonical_production_dependencies() -> None:
    requirements = _non_comment_lines(ROOT / "requirements.txt")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = list(pyproject["project"]["dependencies"])

    assert requirements == dependencies
    assert "." not in requirements


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
