# azo_wheel

Reusable Spark utility library deployed as a wheel to a Unity Catalog volume for use in ETL pipelines.

* `src/azo_wheel/`: Shared Python code that can be used by jobs and pipelines.
* `resources/`:  Resource configurations (jobs, pipelines, etc.)
* `tests/`: Unit tests for the shared Python code.
* `fixtures/`: Fixtures for data sets (primarily used for testing).
* `scripts/`: CI/CD helper scripts (version bumping, etc.)
* `notebooks/`: Workspace-friendly test runner.


## Getting started

Choose how you want to work on this project:

(a) Directly in your Databricks workspace, see
    https://docs.databricks.com/dev-tools/bundles/workspace.

(b) Locally with an IDE like Cursor or VS Code, see
    https://docs.databricks.com/dev-tools/vscode-ext.html.

(c) With command line tools, see https://docs.databricks.com/dev-tools/cli/databricks-cli.html

If you're developing with an IDE, dependencies for this project should be installed using uv:

*  Make sure you have the UV package manager installed.
   It's an alternative to tools like pip: https://docs.astral.sh/uv/getting-started/installation/.
*  Run `uv sync --dev` to install the project's dependencies.


## Running tests

**From the workspace:** Open `notebooks/run_tests.py` in Databricks Repos and click Run All.

**From CLI:** `uv run pytest` (requires local Databricks auth).

**From Azure DevOps:** Tests run automatically on PR via `azure-pipelines.yml`.


## Using the CLI

1. Authenticate to your Databricks workspace, if you have not done so already:
    ```
    $ databricks configure
    ```

2. To deploy a development copy of this project, type:
    ```
    $ databricks bundle deploy --target dev
    ```
    (Note that "dev" is the default target, so the `--target` parameter
    is optional here.)

3. Similarly, to deploy a production copy, type:
   ```
   $ databricks bundle deploy --target prod
   ```

4. To run a job or pipeline, use the "run" command:
   ```
   $ databricks bundle run
   ```


## Azure DevOps CI/CD setup

The pipeline is defined in `azure-pipelines.yml`. It has two stages:

- **CI** — runs on every PR and push to `main`. Lints with Black, builds the wheel, runs pytest.
- **Release** — manually triggered. Bumps the version, builds the wheel, uploads it to the UC volume, and tags the commit.

### Setup steps

1. **Create an Azure DevOps project**
   - Go to https://dev.azure.com and create a new project (or use an existing one).

2. **Connect your Git repository**
   - In the ADO project, go to **Project Settings > Repos > Repositories** and import or connect your Git repo.
   - If using GitHub, go to **Pipelines > New Pipeline > GitHub** and authorize the connection.

3. **Create the pipeline**
   - Go to **Pipelines > New Pipeline**.
   - Select your repository.
   - Choose **Existing Azure Pipelines YAML file**.
   - Set the path to `azo_wheel/azure-pipelines.yml`.
   - Save (don't run yet — you need to set variables first).

4. **Configure pipeline variables**
   - Edit the pipeline and go to **Variables**.
   - Add the following:

     | Variable            | Value                                              | Secret? |
     |---------------------|----------------------------------------------------|---------|
     | `DATABRICKS_HOST`   | `https://e2-demo-field-eng.cloud.databricks.com`   | No      |
     | `DATABRICKS_TOKEN`  | Your PAT or service principal token                 | **Yes** |

5. **Grant Git push permissions (for releases)**
   - The Release stage commits the version bump and pushes a tag. The pipeline needs write access to the repo.
   - In ADO: **Project Settings > Repos > Security**, grant the build service account **Contribute** and **Create Tag** permissions on your repository.

6. **Run it**
   - **CI** triggers automatically on PR or push to `main`.
   - **Release**: queue a manual run and set the variable `BUMP_PART` to `major`, `minor`, or `patch` (defaults to `patch`). This will:
     1. Bump the version in `pyproject.toml`
     2. Build the wheel
     3. Upload it to `/Volumes/users/sol_ackerman/wheels/`
     4. Commit and tag `vX.Y.Z`

### Consuming the wheel in ETL pipelines

Once published, install the wheel in any Databricks notebook or job:

```python
%pip install /Volumes/users/sol_ackerman/wheels/azo_wheel-X.Y.Z-py3-none-any.whl
```

Or pin it in a cluster init script or job environment definition.
