# Databricks notebook source
# MAGIC %md
# MAGIC # azo_wheel — Test Runner
# MAGIC
# MAGIC Run the full pytest suite from the Databricks workspace.
# MAGIC Click **Run All** or attach to any cluster/serverless and execute each cell.

# COMMAND ----------

# MAGIC %pip install pytest -q
# dbutils.library.restartPython()  # uncomment if you hit import issues after install

# COMMAND ----------

import subprocess, sys, os

# Point pytest at the tests directory relative to the repo root.
# When this notebook is in the workspace via Repos, the repo root is two levels up.
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else "/Workspace/Repos"

# If running from Databricks Repos, __file__ is set automatically.
# Otherwise, update this path to match your Repos checkout location.
if repo_root == "/Workspace/Repos":
    # Fallback: try to detect from notebook context
    try:
        notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()  # noqa: F821
        # notebook_path looks like /Repos/<user>/osc/azo_wheel/notebooks/run_tests
        repo_root = "/Workspace" + "/".join(notebook_path.split("/")[:4])
    except Exception:
        pass

test_dir = os.path.join(repo_root, "azo_wheel", "tests")
src_dir = os.path.join(repo_root, "azo_wheel", "src")

print(f"Test dir:   {test_dir}")
print(f"Source dir: {src_dir}")

# Make sure azo_wheel is importable
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# COMMAND ----------

import pytest

# Run pytest programmatically so results render in cell output.
# -v for verbose, --tb=short for concise tracebacks, --no-header to reduce noise.
exit_code = pytest.main([
    test_dir,
    "-v",
    "--tb=short",
    "--no-header",
])

# COMMAND ----------

if exit_code == 0:
    print("All tests passed!")
else:
    print(f"Some tests failed (exit code {exit_code})")
    # Raise so the notebook job shows as failed if run as a task
    raise SystemExit(exit_code)
