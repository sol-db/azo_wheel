# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Databricks Python utility library (`azo_wheel`) deployed as a wheel to a Unity Catalog volume (`/Volumes/users/sol_ackerman/wheels/`) for use in ETL pipelines. CI/CD is Azure DevOps. Built with the default-python DAB template.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run tests (requires Databricks authentication)
uv run pytest

# Build wheel
uv build --wheel

# Bump version (SemVer)
python azo_wheel/scripts/bump_version.py patch  # or minor / major

# Deploy via DAB
databricks bundle deploy --target dev    # dev is default, --target optional
databricks bundle deploy --target prod

# Run a deployed job
databricks bundle run
```

## Architecture

All project code lives under `azo_wheel/`:

- `src/azo_wheel/` — Shared Python package deployed as a wheel artifact. Entry point: `main:main`
- `resources/*.yml` — Databricks job/pipeline resource definitions
- `tests/` — pytest tests using Databricks Connect (runs Spark against a remote cluster or serverless)
- `fixtures/` — JSON/CSV test data loaded via the `load_fixture` pytest fixture
- `databricks.yml` — Bundle config with `dev` (development mode, user-prefixed) and `prod` targets on `e2-demo-field-eng.cloud.databricks.com`
- `scripts/bump_version.py` — SemVer version bump script (major/minor/patch)
- `notebooks/run_tests.py` — Workspace-friendly test runner notebook
- `azure-pipelines.yml` — CI (lint/build/test on PR) and Release (bump, build, upload to UC volume, tag) pipeline

## Testing

Tests require Databricks authentication and a compute target. The test framework automatically falls back to serverless compute if none is specified. Two key fixtures in `conftest.py`:
- `spark` — provides a DatabricksSession
- `load_fixture` — loads JSON/CSV files from `fixtures/` into DataFrames

**From the workspace:** Open `notebooks/run_tests.py` in Databricks Repos and click Run All.
**From CLI:** `uv run pytest` (requires local Databricks auth).
**From Azure DevOps:** Tests run automatically on PR via `azure-pipelines.yml`.

## CI/CD (Azure DevOps)

`azure-pipelines.yml` defines two stages:
- **CI** — Runs on every PR/push to main. Lints with Black, builds the wheel, runs pytest.
- **Release** — Manually triggered. Bumps version (set `BUMP_PART` variable to `major`/`minor`/`patch`), builds wheel, uploads to `/Volumes/users/sol_ackerman/wheels/`, commits and tags `vX.Y.Z`.

Pipeline variables to configure in ADO:
- `DATABRICKS_HOST` — workspace URL
- `DATABRICKS_TOKEN` — PAT or service principal token (mark as secret)

## Code Style

- Formatter: Black, line length 125 (`pyproject.toml`)
- Python: >=3.10, <3.13
- Type checking is disabled in editor settings
