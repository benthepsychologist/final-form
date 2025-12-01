"""Instrument registry for loading and caching instrument specifications."""

import json
from pathlib import Path

import jsonschema

from final_form.registry.models import InstrumentSpec


class InstrumentNotFoundError(Exception):
    """Raised when an instrument specification is not found."""

    pass


class InstrumentValidationError(Exception):
    """Raised when an instrument specification fails validation."""

    pass


class InstrumentRegistry:
    """Registry for loading and caching instrument specifications.

    Loads instrument specs from a directory structure:
        <registry_path>/instruments/<instrument_id>/<version>.json

    Where version uses dashes instead of dots (e.g., 1-0-0.json for 1.0.0).
    """

    def __init__(
        self,
        registry_path: Path | str,
        schema_path: Path | str | None = None,
    ) -> None:
        """Initialize the instrument registry.

        Args:
            registry_path: Path to the instrument registry directory.
            schema_path: Optional path to the instrument_spec schema for validation.
        """
        self.registry_path = Path(registry_path)
        self.instruments_path = self.registry_path / "instruments"
        self._cache: dict[tuple[str, str], InstrumentSpec] = {}
        self._schema: dict | None = None

        if schema_path:
            with open(schema_path) as f:
                self._schema = json.load(f)

    def _version_to_filename(self, version: str) -> str:
        """Convert version string to filename (1.0.0 -> 1-0-0.json)."""
        return version.replace(".", "-") + ".json"

    def _get_spec_path(self, instrument_id: str, version: str) -> Path:
        """Get the path to an instrument spec file."""
        filename = self._version_to_filename(version)
        return self.instruments_path / instrument_id / filename

    def get(self, instrument_id: str, version: str) -> InstrumentSpec:
        """Get an instrument specification by ID and version.

        Args:
            instrument_id: The instrument identifier (e.g., 'phq9').
            version: The version string (e.g., '1.0.0').

        Returns:
            The loaded InstrumentSpec.

        Raises:
            InstrumentNotFoundError: If the instrument spec file doesn't exist.
            InstrumentValidationError: If the spec fails schema validation.
        """
        cache_key = (instrument_id, version)
        if cache_key in self._cache:
            return self._cache[cache_key]

        spec_path = self._get_spec_path(instrument_id, version)
        if not spec_path.exists():
            raise InstrumentNotFoundError(
                f"Instrument spec not found: {instrument_id}@{version} "
                f"(expected at {spec_path})"
            )

        with open(spec_path) as f:
            data = json.load(f)

        # Validate against schema if available
        if self._schema:
            try:
                jsonschema.validate(data, self._schema)
            except jsonschema.ValidationError as e:
                raise InstrumentValidationError(
                    f"Instrument spec validation failed for {instrument_id}@{version}: {e.message}"
                ) from e

        spec = InstrumentSpec.model_validate(data)
        self._cache[cache_key] = spec
        return spec

    def list_instruments(self) -> list[str]:
        """List all available instrument IDs."""
        if not self.instruments_path.exists():
            return []
        return [d.name for d in self.instruments_path.iterdir() if d.is_dir()]

    def list_versions(self, instrument_id: str) -> list[str]:
        """List all available versions for an instrument."""
        instrument_path = self.instruments_path / instrument_id
        if not instrument_path.exists():
            return []
        versions = []
        for f in instrument_path.glob("*.json"):
            # Convert filename back to version (1-0-0.json -> 1.0.0)
            version = f.stem.replace("-", ".")
            versions.append(version)
        return sorted(versions)

    def get_latest(self, instrument_id: str) -> InstrumentSpec:
        """Get the latest version of an instrument.

        Args:
            instrument_id: The instrument identifier.

        Returns:
            The latest InstrumentSpec.

        Raises:
            InstrumentNotFoundError: If no versions exist.
        """
        versions = self.list_versions(instrument_id)
        if not versions:
            raise InstrumentNotFoundError(f"No versions found for instrument: {instrument_id}")
        # Simple string sort works for semver if all have same number of digits
        latest = versions[-1]
        return self.get(instrument_id, latest)
