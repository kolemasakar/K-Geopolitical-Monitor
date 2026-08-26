# LOCAL_DEVELOPMENT_SETUP

Version: 0.2
Status: REVIEW_REQUIRED

## Purpose

Define the reproducible local setup procedure for the current implementation baseline.

## Prerequisites

- Git
- Python >=3.10
- pip

## Setup

From the repository root:

```text
python -m venv .venv
```

Activate the environment using the command appropriate for the operating system, then run:

```text
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

## Database Initialization

```text
python -c "from kgeopolitical_monitor.database import initialize_database; initialize_database()"
```

This creates the local SQLite database and applies all unapplied migrations from migrations/.

## Test Execution

Full test suite:

```text
python -m pytest -q
```

M4 acceptance gate only:

```text
python -m pytest -q tests/test_m4_validation.py
```

## Configuration

No mandatory external service credentials are approved for the current baseline.
Do not add secrets or service credentials to repository files.

## Troubleshooting

- Run commands from the repository root.
- Verify that the active interpreter satisfies the Python requirement.
- Reinstall with `python -m pip install -e ".[test]"` after environment recreation.
- Database initialization is designed to be repeatable; applied migrations are tracked in `schema_migrations`.

## Current State

Local development procedure: IMPLEMENTED_BASELINE
Approval status: REVIEW_REQUIRED
