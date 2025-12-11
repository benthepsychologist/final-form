---
version: "0.1"
tier: C
title: Rename project from final-form to finalform
owner: benthepsychologist
goal: Remove hyphen from project name across all references
labels: []
project_slug: finalform
spec_version: 1.0.0
created: 2025-12-11T21:30:00.000000+00:00
updated: 2025-12-11T22:00:00.000000+00:00
orchestrator_contract: "standard"
repo:
  working_branch: "feat/rename-to-finalform"
---

# Rename project from final-form to finalform

## Objective

> Rename the project from `final-form` to `finalform`, removing the hyphen from the package name, CLI command, repository name, and all references throughout the codebase.

## Acceptance Criteria

- [ ] `pyproject.toml` updated with new package name and URLs
- [ ] Package directory renamed from `final_form/` to `finalform/`
- [ ] All code references updated (imports, version string, error messages, docstrings)
- [ ] All documentation updated (README, FINAL-FORM-ARCH, FINAL-FORM-BUILD-PLAN)
- [ ] All spec/AIP files updated with new project_slug and URLs
- [ ] CLI command changed from `final-form` to `finalform`
- [ ] Config directory changed from `~/.config/final-form` to `~/.config/finalform`
- [ ] CI green (lint + unit)
- [ ] GitHub repository renamed from `final-form` to `finalform` *(do last - breaks local session)*
- [ ] Git remote updated to point to new repository *(do last - after repo rename)*

## Context

### Background

The project is currently named `final-form` but the hyphen is inconvenient for:
1. Python imports (underscores required: `final_form` vs `finalform`)
2. CLI usage (typing `final-form` vs `finalform`)
3. Overall consistency (single word is cleaner)

### Scope

**Package Files:**
- `pyproject.toml` - package name `final-form` → `finalform`, CLI entry point, GitHub URLs
- `uv.lock` - package name reference

**Source Directory (rename):**
- `final_form/` → `finalform/`
- All internal imports updated

**Source Files (content updates):**
- `final_form/__init__.py:1` - docstring `final-form:` → `finalform:`
- `final_form/cli.py:1` - docstring `CLI for final-form` → `CLI for finalform`
- `final_form/cli.py:24` - typer app name `final-form` → `finalform`
- `final_form/cli.py:33` - version output `final-form version` → `finalform version`
- `final_form/cli.py:44` - help text `final-form:` → `finalform:`
- `final_form/cli.py:64-76` - init command help text and paths
- `final_form/cli.py:110,140,232` - output messages
- `final_form/config.py:14,16,19,25` - docstrings, comments, and default path `~/.config/final-form` → `~/.config/finalform`
- `final_form/core/__init__.py:1` - docstring `Core shared infrastructure for final-form`
- `final_form/domains/__init__.py:1` - docstring `Domain-specific processors for final-form`
- `final_form/builders/__init__.py:4` - docstring mentioning `final-form`
- `final_form/input/__init__.py:1` - docstring `Form input handling for final-form`
- `final_form/input/client.py:3` - docstring `that tell final-form which`
- `final_form/input/process.py:4-5` - docstrings mentioning `final-form`

**Environment Variables:**
- `FINAL_FORM_HOME` (config.py:17) - keep as-is for backwards compat OR rename to `FINALFORM_HOME`
- `FINAL_FORM_MEASURE_REGISTRY` (cli.py:167,193) - keep as-is for backwards compat OR rename to `FINALFORM_MEASURE_REGISTRY`
- `FINAL_FORM_BINDING_REGISTRY` (cli.py:175,202) - keep as-is for backwards compat OR rename to `FINALFORM_BINDING_REGISTRY`

**Decision needed:** Keep env vars with underscores for backwards compatibility, or rename them to match new naming?

**Tests (import paths):**
- All test files in `tests/` - update `from final_form` → `from finalform`
- 17 test files with 52 total import occurrences
- `tests/conftest.py` - fixtures and imports

**Documentation:**
- `README.md` - title, install instructions, CLI usage (~15 occurrences)
- `FINAL-FORM-ARCH.md` - architecture description (~25 occurrences)
- `FINAL-FORM-BUILD-PLAN.md` - build plan (~5 occurrences)

**Schemas:**
- `schemas/measurement_event.schema.json:74,80,82,84` - `final_form_version` field name and `final-form` descriptions

**Scripts:**
- `scripts/convert_registry.py:5,129` - comments and paths

**Spec Files (2 files):**
- `.specwright/specs/final-form-initial-spec.md` - project_slug, goal, references
- `.specwright/specs/domain-modular-architecture-refactor.md` - project_slug, goal, references

**AIP Files (2 files):**
- `.specwright/aips/final-form-initial-spec.yaml` - aip_id, project_slug, repo URL, paths
- `.specwright/aips/domain-modular-architecture-refactor.yaml` - aip_id, project_slug, repo URL

**Other:**
- `.specwright.yaml:11-12` - current spec/AIP path references *(update after repo rename in Step 12)*
- `.aip_artifacts/execution_history.jsonl` - historical records (leave as-is, historical data)

## Plan

> **Note:** Rename the package directory first, then update all references. Rename repo/remote last.

### Step 1: Rename Package Directory

Rename the source directory:
```bash
mv final_form finalform
```

### Step 2: Update pyproject.toml

Update `pyproject.toml`:
- `name = "final-form"` → `name = "finalform"`
- `final-form = "final_form.cli:app"` → `finalform = "finalform.cli:app"`
- `packages = ["final_form"]` → `packages = ["finalform"]`
- `testpaths` and `addopts` references
- GitHub URLs if present

### Step 3: Update Source Files

Update all source files in `finalform/`:
- Docstrings and comments mentioning `final-form`
- Config paths `~/.config/final-form` → `~/.config/finalform`
- CLI app name and output strings
- Environment variables (decide on one approach):
  - **Option A (backwards compat):** Keep `FINAL_FORM_HOME`, `FINAL_FORM_MEASURE_REGISTRY`, `FINAL_FORM_BINDING_REGISTRY`
  - **Option B (full rename):** Rename to `FINALFORM_HOME`, `FINALFORM_MEASURE_REGISTRY`, `FINALFORM_BINDING_REGISTRY`

### Step 4: Update All Imports

Update all import statements across the codebase:
- `from final_form` → `from finalform`
- `import final_form` → `import finalform`
- `final_form.` → `finalform.`

Files affected:
- All files in `finalform/` (internal imports)
- All files in `tests/` (test imports)

### Step 5: Update Documentation

Replace all `final-form` references with `finalform` in:
- `README.md` (~15 occurrences)
- `FINAL-FORM-ARCH.md` (~25 occurrences)
- `FINAL-FORM-BUILD-PLAN.md` (~5 occurrences)

Consider renaming doc files:
- `FINAL-FORM-ARCH.md` → `FINALFORM-ARCH.md`
- `FINAL-FORM-BUILD-PLAN.md` → `FINALFORM-BUILD-PLAN.md`

### Step 6: Update Schemas

Update `schemas/measurement_event.schema.json`:
- Line 74: `final_form_version` field in required array (keep underscore - it's a field name)
- Line 80: description `When final-form processed` → `When finalform processed`
- Line 82: `final_form_version` property name (keep underscore - it's a field name)
- Line 84: description `Version of final-form` → `Version of finalform`

**Note:** Keep `final_form_version` as the field name (underscores are standard in JSON field names).

### Step 7: Update Spec/AIP Files

Update spec files:
- `.specwright/specs/final-form-initial-spec.md` - `project_slug: final-form` → `project_slug: finalform`, all references
- `.specwright/specs/domain-modular-architecture-refactor.md` - same updates

Update AIP files:
- `.specwright/aips/final-form-initial-spec.yaml` - `aip_id: AIP-final-form-*` → `AIP-finalform-*`, repo URL, project_slug
- `.specwright/aips/domain-modular-architecture-refactor.yaml` - same updates

**Note:** Do NOT update `.specwright.yaml` current spec/AIP paths yet - wait until Step 12 after repo rename.

### Step 8: Update Scripts

Update `scripts/convert_registry.py`:
- Comment on line 5
- Path on line 129

### Step 9: Regenerate Lock File

```bash
uv lock
```

### Step 10: Run CI Checks

```bash
uv run ruff check .
uv run pytest -q
```

### Step 10b: Verify No Remaining References

Run a final check for any remaining `final-form` or `final_form` references:
```bash
grep -r "final-form" --include="*.py" --include="*.md" --include="*.json" --include="*.yaml" . | grep -v ".git" | grep -v ".specwright.yaml"
grep -r "final_form" --include="*.py" . | grep -v ".git"
```

Any remaining references should be intentional (e.g., historical data in `.aip_artifacts/`).

### Step 11: Rename GitHub Repository *(do last)*

Rename the GitHub repository from `benthepsychologist/final-form` to `benthepsychologist/finalform` via GitHub settings.

**Warning:** This will break the local git remote until Step 12 is completed.

### Step 12: Update Git Remote *(do immediately after Step 11)*

```bash
git remote set-url origin git@github.com:benthepsychologist/finalform.git
```

### Step 13: Update .specwright.yaml Paths

After repo rename is complete, update `.specwright.yaml`:
- Line 11: `spec: .specwright/specs/rename-to-finalform.md` (current spec path - update if needed)
- Line 12: `aip: .specwright/aips/rename-to-finalform.yaml` (current AIP path - update if needed)

## Models & Tools

**Tools:** bash, git, gh

## Repository

**Branch:** `feat/rename-to-finalform`

**Merge Strategy:** squash
