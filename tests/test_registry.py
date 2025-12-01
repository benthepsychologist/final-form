"""Tests for registry modules."""

from pathlib import Path

import pytest

from final_form.registry import BindingRegistry, InstrumentRegistry
from final_form.registry.bindings import BindingNotFoundError
from final_form.registry.instruments import InstrumentNotFoundError


class TestInstrumentRegistry:
    """Tests for InstrumentRegistry."""

    def test_load_phq9(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test loading PHQ-9 instrument spec."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec = registry.get("phq9", "1.0.0")

        assert spec.instrument_id == "phq9"
        assert spec.version == "1.0.0"
        assert spec.name == "Patient Health Questionnaire-9"
        assert spec.kind == "questionnaire"
        assert len(spec.items) == 10  # 9 symptom + 1 severity
        assert len(spec.scales) == 2  # total + severity

    def test_load_gad7(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test loading GAD-7 instrument spec."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec = registry.get("gad7", "1.0.0")

        assert spec.instrument_id == "gad7"
        assert spec.version == "1.0.0"
        assert spec.name == "Generalized Anxiety Disorder-7"
        assert spec.kind == "questionnaire"
        assert len(spec.items) == 8  # 7 symptom + 1 severity
        assert len(spec.scales) == 2  # total + severity

    def test_phq9_items(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test PHQ-9 item details."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec = registry.get("phq9", "1.0.0")

        # Check first item
        item1 = spec.get_item("phq9_item1")
        assert item1 is not None
        assert item1.position == 1
        assert "not at all" in item1.response_map
        assert item1.response_map["not at all"] == 0
        assert item1.response_map["nearly every day"] == 3

        # Check severity item (item 10)
        item10 = spec.get_item("phq9_item10")
        assert item10 is not None
        assert item10.position == 10
        assert "not difficult at all" in item10.response_map

    def test_phq9_scales(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test PHQ-9 scale details."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec = registry.get("phq9", "1.0.0")

        # Check total scale
        total = spec.get_scale("phq9_total")
        assert total is not None
        assert len(total.items) == 9  # items 1-9 only
        assert total.method == "sum"
        assert total.min == 0
        assert total.max == 27
        assert len(total.interpretations) == 5

        # Check interpretation ranges
        interps = {i.label: (i.min, i.max) for i in total.interpretations}
        assert interps["Minimal"] == (0, 4)
        assert interps["Severe"] == (20, 27)

    def test_instrument_not_found(self, instrument_registry_path: Path) -> None:
        """Test error when instrument not found."""
        registry = InstrumentRegistry(instrument_registry_path)
        with pytest.raises(InstrumentNotFoundError):
            registry.get("nonexistent", "1.0.0")

    def test_version_not_found(self, instrument_registry_path: Path) -> None:
        """Test error when version not found."""
        registry = InstrumentRegistry(instrument_registry_path)
        with pytest.raises(InstrumentNotFoundError):
            registry.get("phq9", "99.0.0")

    def test_list_instruments(self, instrument_registry_path: Path) -> None:
        """Test listing available instruments."""
        registry = InstrumentRegistry(instrument_registry_path)
        instruments = registry.list_instruments()
        assert "phq9" in instruments
        assert "gad7" in instruments

    def test_list_versions(self, instrument_registry_path: Path) -> None:
        """Test listing available versions."""
        registry = InstrumentRegistry(instrument_registry_path)
        versions = registry.list_versions("phq9")
        assert "1.0.0" in versions

    def test_get_latest(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test getting latest version."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec = registry.get_latest("phq9")
        assert spec.instrument_id == "phq9"
        assert spec.version == "1.0.0"

    def test_caching(
        self, instrument_registry_path: Path, instrument_schema_path: Path
    ) -> None:
        """Test that specs are cached."""
        registry = InstrumentRegistry(
            instrument_registry_path, schema_path=instrument_schema_path
        )
        spec1 = registry.get("phq9", "1.0.0")
        spec2 = registry.get("phq9", "1.0.0")
        assert spec1 is spec2  # Same object from cache


class TestBindingRegistry:
    """Tests for BindingRegistry."""

    def test_load_example_intake(
        self, binding_registry_path: Path, binding_schema_path: Path
    ) -> None:
        """Test loading example_intake binding spec."""
        registry = BindingRegistry(binding_registry_path, schema_path=binding_schema_path)
        spec = registry.get("example_intake", "1.0.0")

        assert spec.binding_id == "example_intake"
        assert spec.version == "1.0.0"
        assert spec.form_id == "googleforms::1FAIpQLSe_example"
        assert len(spec.sections) == 2

    def test_binding_sections(
        self, binding_registry_path: Path, binding_schema_path: Path
    ) -> None:
        """Test binding section details."""
        registry = BindingRegistry(binding_registry_path, schema_path=binding_schema_path)
        spec = registry.get("example_intake", "1.0.0")

        # Check PHQ-9 section
        phq9_section = spec.get_section_for_instrument("phq9")
        assert phq9_section is not None
        assert phq9_section.instrument_version == "1.0.0"
        assert len(phq9_section.bindings) == 10  # 10 items

        # Check GAD-7 section
        gad7_section = spec.get_section_for_instrument("gad7")
        assert gad7_section is not None
        assert gad7_section.instrument_version == "1.0.0"
        assert len(gad7_section.bindings) == 8  # 8 items

    def test_binding_details(
        self, binding_registry_path: Path, binding_schema_path: Path
    ) -> None:
        """Test individual binding details."""
        registry = BindingRegistry(binding_registry_path, schema_path=binding_schema_path)
        spec = registry.get("example_intake", "1.0.0")

        phq9_section = spec.get_section_for_instrument("phq9")
        assert phq9_section is not None

        # Check first binding
        first_binding = phq9_section.bindings[0]
        assert first_binding.item_id == "phq9_item1"
        assert first_binding.by == "field_key"
        assert first_binding.value == "entry.123456001"

    def test_binding_not_found(self, binding_registry_path: Path) -> None:
        """Test error when binding not found."""
        registry = BindingRegistry(binding_registry_path)
        with pytest.raises(BindingNotFoundError):
            registry.get("nonexistent", "1.0.0")

    def test_list_bindings(self, binding_registry_path: Path) -> None:
        """Test listing available bindings."""
        registry = BindingRegistry(binding_registry_path)
        bindings = registry.list_bindings()
        assert "example_intake" in bindings

    def test_get_latest(
        self, binding_registry_path: Path, binding_schema_path: Path
    ) -> None:
        """Test getting latest version."""
        registry = BindingRegistry(binding_registry_path, schema_path=binding_schema_path)
        spec = registry.get_latest("example_intake")
        assert spec.binding_id == "example_intake"
        assert spec.version == "1.0.0"
