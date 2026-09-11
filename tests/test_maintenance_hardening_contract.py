from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

CHECKOUT_V5_SHA = "fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09"
SETUP_PYTHON_V6_SHA = "ece7cb06caefa5fff74198d8649806c4678c61a1"


def test_workflows_do_not_use_node20_checkout_or_setup_python_generations():
    offenders = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for legacy in ("actions/checkout@v4", "actions/setup-python@v5"):
            if legacy in text:
                offenders.append(f"{path.name}: {legacy}")

    assert offenders == []


def test_ci_constraints_pin_compatibility_critical_stack():
    constraints = (ROOT / "constraints" / "ci.txt").read_text(encoding="utf-8")
    expected = {
        "fastapi==0.141.1",
        "uvicorn==0.52.4",
        "psycopg==3.3.5",
        "psycopg-binary==3.3.5",
        "pytest==9.1.1",
        "httpx2==2.12.0",
        "starlette==1.6.0",
        "anyio==4.14.2",
        "pydantic==2.13.5",
        "pydantic-core==2.46.5",
    }
    actual = {
        line.strip()
        for line in constraints.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert actual == expected


def test_primary_ci_workflows_enforce_constraints_and_pip_check():
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    arm64 = (ROOT / ".github/workflows/e4-arm64-validation.yml").read_text(encoding="utf-8")

    for text in (ci, arm64):
        assert "PIP_CONSTRAINT: constraints/ci.txt" in text
        assert "python -m pip check" in text

    # The post-P19 hardening branch deliberately pins the primary CI workflow
    # to immutable upstream SHAs. The ARM64 workflow remains outside this
    # staged high-sensitivity pinning scope and is covered by the repository-wide
    # `uses:` sweep required before merge.
    assert f"actions/checkout@{CHECKOUT_V5_SHA}" in ci
    assert f"actions/setup-python@{SETUP_PYTHON_V6_SHA}" in ci
    assert "actions/checkout@v5" in arm64
    assert "actions/setup-python@v6" in arm64


def test_test_dependency_contract_uses_httpx2_and_compatible_anyio_window():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert '"httpx2>=2.12,<3"' in pyproject
    assert '"anyio>=4.14.2,<4.15"' in pyproject
    assert '"httpx>=0.28,<1"' not in pyproject
    assert '"error::DeprecationWarning"' in pyproject
    assert '"error::starlette.exceptions.StarletteDeprecationWarning"' in pyproject
