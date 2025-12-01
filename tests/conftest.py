"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def schemas_dir(project_root: Path) -> Path:
    """Return the schemas directory."""
    return project_root / "schemas"


@pytest.fixture
def instrument_registry_path(project_root: Path) -> Path:
    """Return the instrument registry path."""
    return project_root / "instrument-registry"


@pytest.fixture
def binding_registry_path(project_root: Path) -> Path:
    """Return the form binding registry path."""
    return project_root / "form-binding-registry"


@pytest.fixture
def instrument_schema_path(schemas_dir: Path) -> Path:
    """Return the instrument spec schema path."""
    return schemas_dir / "instrument_spec.schema.json"


@pytest.fixture
def binding_schema_path(schemas_dir: Path) -> Path:
    """Return the form binding spec schema path."""
    return schemas_dir / "form_binding_spec.schema.json"
