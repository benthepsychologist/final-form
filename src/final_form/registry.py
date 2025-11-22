"""
Registry loaders for questionnaire measures and form mappings.

Loads canonical measure definitions from questionnaire-registry and
validates against schemas from canonizer-registry.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from .models import QuestionnaireMeasure, FormMapping


class QuestionnaireRegistry:
    """
    Loader for questionnaire measure definitions.

    Loads measures from questionnaire-registry/measures.json and provides
    lookup by measure_id (e.g., 'phq_9', 'gad_7').
    """

    def __init__(self, registry_path: Path):
        """
        Initialize registry loader.

        Args:
            registry_path: Path to questionnaire-registry directory
        """
        self.registry_path = Path(registry_path)
        self.measures: Dict[str, QuestionnaireMeasure] = {}
        self._load_measures()

    def _load_measures(self):
        """Load all measures from measures.json."""
        measures_file = self.registry_path / "measures.json"

        if not measures_file.exists():
            raise FileNotFoundError(
                f"Measures file not found: {measures_file}\n"
                f"Expected questionnaire-registry structure with measures.json"
            )

        with open(measures_file, "r") as f:
            data = json.load(f)

        # Parse and validate each measure
        measures_dict = data.get("measures", {})
        for measure_id, measure_data in measures_dict.items():
            try:
                self.measures[measure_id] = QuestionnaireMeasure(**measure_data)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse measure '{measure_id}' from {measures_file}: {e}"
                )

    def get_measure(self, measure_id: str) -> Optional[QuestionnaireMeasure]:
        """
        Get a measure by ID.

        Args:
            measure_id: Measure identifier (e.g., 'phq_9', 'gad_7')

        Returns:
            QuestionnaireMeasure or None if not found
        """
        return self.measures.get(measure_id)

    def list_measures(self) -> list[str]:
        """Get list of all available measure IDs."""
        return list(self.measures.keys())


class FormMappingLoader:
    """
    Loader for form mapping definitions.

    Loads form-to-measure mappings from questionnaire-registry/mappings/
    """

    def __init__(self, registry_path: Path):
        """
        Initialize mapping loader.

        Args:
            registry_path: Path to questionnaire-registry directory
        """
        self.registry_path = Path(registry_path)
        self.mappings_dir = self.registry_path / "mappings"

    def load_mapping(self, mapping_file: Path) -> FormMapping:
        """
        Load a form mapping from a JSON file.

        Args:
            mapping_file: Path to mapping JSON file (absolute or relative to mappings/)

        Returns:
            FormMapping instance

        Raises:
            FileNotFoundError: If mapping file doesn't exist
            ValueError: If mapping fails validation
        """
        # Try as absolute path first
        if Path(mapping_file).is_absolute():
            file_path = Path(mapping_file)
        else:
            # Try relative to mappings directory
            file_path = self.mappings_dir / mapping_file

        if not file_path.exists():
            raise FileNotFoundError(
                f"Mapping file not found: {file_path}\n"
                f"Tried: {mapping_file} (absolute) and {self.mappings_dir / mapping_file} (relative)"
            )

        with open(file_path, "r") as f:
            data = json.load(f)

        try:
            return FormMapping(**data)
        except Exception as e:
            raise ValueError(f"Failed to parse mapping from {file_path}: {e}")

    def list_mappings(self, platform: Optional[str] = None) -> list[Path]:
        """
        List available mapping files.

        Args:
            platform: Optional platform filter (e.g., 'google_forms')

        Returns:
            List of mapping file paths
        """
        if not self.mappings_dir.exists():
            return []

        if platform:
            platform_dir = self.mappings_dir / platform
            if platform_dir.exists():
                return list(platform_dir.glob("*.json"))
            return []

        # List all mappings across all platforms
        mappings = []
        for platform_dir in self.mappings_dir.iterdir():
            if platform_dir.is_dir():
                mappings.extend(platform_dir.glob("*.json"))
        return mappings
