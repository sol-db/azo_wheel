# Publishing to Azure Artifacts — Setup Guide

This guide walks through publishing the `azo_wheel` package to a private Azure Artifacts Python feed.

## Prerequisites

- An Azure DevOps project with an existing pipeline for this repo
- Permission to create Artifacts feeds in your ADO org/project

---

## Step 1: Create the Azure Artifacts Feed

1. In Azure DevOps, navigate to **Artifacts** in the left sidebar
2. Click **+ Create Feed**
3. Configure the feed:
   - **Name:** `azo-python-feed`
   - **Visibility:** Members of your organization (or scoped to project)
   - **Upstream sources:** Enable if you want the feed to proxy packages from PyPI
4. Click **Create**

> **Note:** The feed name must match the `artifactsFeed` variable in `azure-pipelines.yml` (currently set to `azo-python-feed`). If you choose a different name, update the variable accordingly.

---

## Step 2: Grant Pipeline Permissions

The build agent needs **Contributor** access to publish packages.

1. Go to **Artifacts → azo-python-feed → Feed settings** (gear icon)
2. Select **Permissions**
3. Click **Add users/groups**
4. Search for **`[Project Name] Build Service ([Org Name])`**
5. Set the role to **Contributor**
6. Click **Save**

---

## Step 3: Verify Pipeline Configuration

The pipeline (`azo_wheel/azure-pipelines.yml`) already includes the publish steps. Confirm:

- **Line 30** — `artifactsFeed` variable matches your feed name:
  ```yaml
  artifactsFeed: azo-python-feed
  ```
- If the feed is **org-scoped** (not project-scoped), use the format:
  ```yaml
  artifactsFeed: my-org/azo-python-feed
  ```

The Release stage has two steps that handle publishing:

```yaml
- task: TwineAuthenticate@1
  displayName: Authenticate with Azure Artifacts
  inputs:
    artifactFeed: $(artifactsFeed)

- pwsh: |
    pip install twine
    twine upload -r $(artifactsFeed) --config-file $(PYPIRC_PATH) dist\*
  displayName: Publish wheel to Azure Artifacts
```

`TwineAuthenticate@1` generates a temporary `.pypirc` with feed credentials — no PAT or secrets needed for the pipeline itself.

---

## Step 4: Run a Release

1. Go to **Pipelines** in Azure DevOps
2. Select the pipeline and click **Run pipeline**
3. Set the `BUMP_PART` variable to `patch`, `minor`, or `major`
4. Click **Run**

The Release stage will:
1. Bump the version in `pyproject.toml`
2. Build the wheel
3. Upload to the UC volume (existing behavior)
4. **Publish to Azure Artifacts** (new)
5. Commit the version bump and tag the release

---

## Step 5: Install the Package from the Feed

### Option A: Local Development (recommended)

Install the `artifacts-keyring` package for automatic authentication:

```bash
pip install keyring artifacts-keyring
```

Then install normally with the feed as an extra index:

```bash
pip install azo_wheel \
  --extra-index-url https://pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/
```

The keyring will prompt you to authenticate via browser on first use.

To make this permanent, add to `pip.conf` (macOS/Linux: `~/.config/pip/pip.conf`, Windows: `%APPDATA%\pip\pip.ini`):

```ini
[global]
extra-index-url = https://pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/
```

### Option B: CI Pipelines or Scripts (PAT-based)

Generate a **Personal Access Token** with **Packaging (Read)** scope, then:

```bash
pip install azo_wheel \
  --extra-index-url https://{PAT}@pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/
```

### Option C: Databricks Notebooks / Jobs

```python
%pip install azo_wheel \
  --extra-index-url https://{PAT}@pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/
```

For cluster-wide access, add the `--extra-index-url` to a **cluster init script** or set the `PIP_EXTRA_INDEX_URL` environment variable in the cluster configuration.

### Option D: uv (if using uv locally)

```bash
uv pip install azo_wheel \
  --extra-index-url https://pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/
```

Or add to `pyproject.toml` in downstream projects:

```toml
[tool.uv]
extra-index-url = ["https://pkgs.dev.azure.com/{ORG}/{PROJECT}/_packaging/azo-python-feed/pypi/simple/"]
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `403 Forbidden` on publish | Ensure Build Service has **Contributor** role on the feed |
| `409 Conflict` on publish | The version already exists in the feed — bump the version first |
| `401 Unauthorized` on install | Check your PAT has **Packaging (Read)** scope and hasn't expired |
| `artifacts-keyring` not prompting | Run `pip install --upgrade keyring artifacts-keyring` and retry |
| Feed not found | Verify the feed URL — org-scoped feeds omit the project segment |

---

## Reference

- [Azure Artifacts docs](https://learn.microsoft.com/en-us/azure/devops/artifacts/quickstarts/python-packages)
- [TwineAuthenticate task](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/twine-authenticate-v1)
- [artifacts-keyring](https://github.com/microsoft/artifacts-keyring)
