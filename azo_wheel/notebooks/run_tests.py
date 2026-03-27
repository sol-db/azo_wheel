# Databricks notebook source
# MAGIC %md
# MAGIC # azo_wheel — Test Runner
# MAGIC
# MAGIC Run the full pytest suite from the Databricks workspace.
# MAGIC Click **Run All** or attach to any cluster/serverless and execute each cell.
# MAGIC
# MAGIC ## CI mode
# MAGIC Set the `junit_volume_path` widget to a UC volume path (e.g. `/Volumes/users/sol_ackerman/wheels`)
# MAGIC to write JUnit XML results there. Azure Pipelines can then download and publish them.

# COMMAND ----------

# MAGIC %pip install pytest pyyaml -q
# dbutils.library.restartPython()  # uncomment if you hit import issues after install

# COMMAND ----------

import sys, os

# Prevent __pycache__ directories from being written into the Repos checkout
sys.dont_write_bytecode = True

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

# Widget for CI integration — set via notebook task parameters or the widget UI.
# When empty, no JUnit XML is written (interactive mode).
try:
    dbutils.widgets.text("junit_volume_path", "", "JUnit output volume path")  # noqa: F821
    junit_volume_path = dbutils.widgets.get("junit_volume_path").strip()  # noqa: F821
except Exception:
    junit_volume_path = ""

# COMMAND ----------

import pytest

# Build pytest args
pytest_args = [
    test_dir,
    "-v",
    "--tb=short",
    "--no-header",
    "-p", "no:cacheprovider",
]

# If a volume path is provided, write JUnit XML to a local temp file first,
# then copy it to the volume so the CI agent can retrieve it.
junit_local_path = None
if junit_volume_path:
    junit_local_path = "/tmp/test-results.xml"
    pytest_args.extend(["--junitxml", junit_local_path])
    print(f"JUnit XML will be written to: {junit_volume_path}/test-results.xml")

# Run pytest programmatically so results render in cell output.
exit_code = pytest.main(pytest_args)

# COMMAND ----------

# Copy JUnit XML to the UC volume (if CI mode is active)
if junit_local_path and os.path.exists(junit_local_path):
    dest = f"{junit_volume_path}/test-results.xml"
    # UC volumes are FUSE-mounted at /Volumes/... so a simple file copy works
    import shutil
    os.makedirs(junit_volume_path, exist_ok=True)
    shutil.copy2(junit_local_path, dest)
    print(f"JUnit XML copied to {dest}")

# COMMAND ----------

if exit_code == 0:
    print("All tests passed!")
else:
    print(f"Some tests failed (exit code {exit_code})")
    # Raise so the notebook job shows as failed if run as a task
    raise SystemExit(exit_code)
