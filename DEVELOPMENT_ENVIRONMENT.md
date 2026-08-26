# DEVELOPMENT_ENVIRONMENT

Version: 0.2
Status: REVIEW_REQUIRED

## Purpose

Define reproducible development environment requirements.

## Baseline Runtime

- Python: >=3.10
- CI baseline: Python 3.11
- Project metadata and dependencies: pyproject.toml
- Test runner: pytest
- Primary local database: SQLite
- Schema changes: versioned SQL files under migrations/

## Reproducibility Contract

A clean environment must be able to execute:

```text
python -m pip install -e ".[test]"
python -m pytest -q
```

Database initialization must apply canonical migrations through:

```text
kgeopolitical_monitor.database.initialize_database
```

## Environment Layers

- Local development
- Test environment
- Validation environment
- Production environment

Only local development and CI test baselines are currently implemented.
Validation and production environment definitions remain future work.

## Rules

- Dependencies must be declared in pyproject.toml.
- Tests must not depend on undocumented local paths or manually prepared databases.
- Database initialization must be repeatable and migration-aware.
- External credentials must not be committed to the repository.

## Current State

Reproducible local/test baseline: IMPLEMENTED
CI workflow definition: IMPLEMENTED
CI execution evidence: PENDING
Production environment: NOT_DEFINED
