"""Binding registry for loading and caching form binding specifications."""

import json
from pathlib import Path

import jsonschema

from final_form.registry.models import FormBindingSpec


class BindingNotFoundError(Exception):
    """Raised when a binding specification is not found."""

    pass


class BindingValidationError(Exception):
    """Raised when a binding specification fails validation."""

    pass


class BindingRegistry:
    """Registry for loading and caching form binding specifications.

    Loads binding specs from a directory structure:
        <registry_path>/bindings/<binding_id>/<version>.json

    Where version uses dashes instead of dots (e.g., 1-0-0.json for 1.0.0).
    """

    def __init__(
        self,
        registry_path: Path | str,
        schema_path: Path | str | None = None,
    ) -> None:
        """Initialize the binding registry.

        Args:
            registry_path: Path to the form binding registry directory.
            schema_path: Optional path to the form_binding_spec schema for validation.
        """
        self.registry_path = Path(registry_path)
        self.bindings_path = self.registry_path / "bindings"
        self._cache: dict[tuple[str, str], FormBindingSpec] = {}
        self._schema: dict | None = None

        if schema_path:
            with open(schema_path) as f:
                self._schema = json.load(f)

    def _version_to_filename(self, version: str) -> str:
        """Convert version string to filename (1.0.0 -> 1-0-0.json)."""
        return version.replace(".", "-") + ".json"

    def _get_spec_path(self, binding_id: str, version: str) -> Path:
        """Get the path to a binding spec file."""
        filename = self._version_to_filename(version)
        return self.bindings_path / binding_id / filename

    def get(self, binding_id: str, version: str) -> FormBindingSpec:
        """Get a form binding specification by ID and version.

        Args:
            binding_id: The binding identifier (e.g., 'example_intake').
            version: The version string (e.g., '1.0.0').

        Returns:
            The loaded FormBindingSpec.

        Raises:
            BindingNotFoundError: If the binding spec file doesn't exist.
            BindingValidationError: If the spec fails schema validation.
        """
        cache_key = (binding_id, version)
        if cache_key in self._cache:
            return self._cache[cache_key]

        spec_path = self._get_spec_path(binding_id, version)
        if not spec_path.exists():
            raise BindingNotFoundError(
                f"Binding spec not found: {binding_id}@{version} "
                f"(expected at {spec_path})"
            )

        with open(spec_path) as f:
            data = json.load(f)

        # Validate against schema if available
        if self._schema:
            try:
                jsonschema.validate(data, self._schema)
            except jsonschema.ValidationError as e:
                raise BindingValidationError(
                    f"Binding spec validation failed for {binding_id}@{version}: {e.message}"
                ) from e

        spec = FormBindingSpec.model_validate(data)
        self._cache[cache_key] = spec
        return spec

    def list_bindings(self) -> list[str]:
        """List all available binding IDs."""
        if not self.bindings_path.exists():
            return []
        return [d.name for d in self.bindings_path.iterdir() if d.is_dir()]

    def list_versions(self, binding_id: str) -> list[str]:
        """List all available versions for a binding."""
        binding_path = self.bindings_path / binding_id
        if not binding_path.exists():
            return []
        versions = []
        for f in binding_path.glob("*.json"):
            # Convert filename back to version (1-0-0.json -> 1.0.0)
            version = f.stem.replace("-", ".")
            versions.append(version)
        return sorted(versions)

    def get_latest(self, binding_id: str) -> FormBindingSpec:
        """Get the latest version of a binding.

        Args:
            binding_id: The binding identifier.

        Returns:
            The latest FormBindingSpec.

        Raises:
            BindingNotFoundError: If no versions exist.
        """
        versions = self.list_versions(binding_id)
        if not versions:
            raise BindingNotFoundError(f"No versions found for binding: {binding_id}")
        # Simple string sort works for semver if all have same number of digits
        latest = versions[-1]
        return self.get(binding_id, latest)
